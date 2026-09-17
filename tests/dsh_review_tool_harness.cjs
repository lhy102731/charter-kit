/**
 * Behavioural harness for the Charter Kit review tool's Host half.
 *
 * `tests/test_dsh_review_tool.py` reads `targets/dsh/src/index.js` as text, so
 * it can pin the spelling of a literal but never what the tool DOES. The claim
 * this file exists for is the one that has no visible symptom: which object the
 * tool hands the delegation provider as `agentOptions`. A card can render a
 * perfect effort panel and the tool can still dispatch `{provider, model}` for
 * every seat, or attach a level nobody selected.
 *
 * It runs the adapter entry — `targets/dsh/src/index.js`, the hand-edited
 * source the DSH builder copies into `plugins/dsh-charter-kit/lib/index.js` —
 * against stub platform packages in a temporary directory, so the repository
 * needs no node_modules and nothing is written inside it. The stubs are the two
 * peer dependencies the adapter imports, and the fake context is the smallest
 * surface `apply` reaches for. `tests/test_dsh_review_tool_behaviour.py` also
 * asserts that the distribution's `lib/index.js` is that same file, which is
 * what makes these behaviours the shipped tool's.
 *
 * Usage: node tests/dsh_review_tool_harness.cjs <plugin-lib-entry.js>
 * Prints one PASS/FAIL line per behaviour and exits non-zero on any failure.
 */
'use strict'

const fs = require('node:fs')
const os = require('node:os')
const path = require('node:path')
const { pathToFileURL } = require('node:url')

const entry = process.argv[2]
if (entry === undefined) {
  console.error('usage: node tests/dsh_review_tool_harness.cjs <plugin-lib-entry.js>')
  process.exit(2)
}

let failures = 0
function check(label, condition, detail) {
  const passed = Boolean(condition)
  if (!passed) failures += 1
  const suffix = passed || detail === undefined ? '' : ` :: ${JSON.stringify(detail)}`
  console.log(`${passed ? 'PASS' : 'FAIL'}  ${label}${suffix}`)
}

const STUB_PACKAGES = {
  '@deepseek-ai/schemastery': `
const field = (value) => ({ kind: 'field', default: value })
export default {
  object: (shape) => ({ kind: 'object', shape }),
  string: () => ({ default: (value) => field(value) }),
  number: () => ({ default: (value) => field(value) }),
}
`,
  '@deepseek-ai/dsh-tools': `
export function defineTool(config) { return config }
`,
}

/** Lay out one plugin tree in a temp directory, with the stub peer packages. */
function stagePlugin(sourceEntry) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'ck-review-tool-'))
  fs.mkdirSync(path.join(root, 'lib'), { recursive: true })
  fs.mkdirSync(path.join(root, 'skills', 'charter-workflow'), { recursive: true })
  fs.copyFileSync(sourceEntry, path.join(root, 'lib', 'index.js'))
  fs.writeFileSync(
    path.join(root, 'skills', 'charter-workflow', 'SKILL.md'),
    '---\ndescription: Charter Kit development workflow\n---\n\nbody\n',
    'utf8',
  )
  for (const [name, source] of Object.entries(STUB_PACKAGES)) {
    const dir = path.join(root, 'node_modules', ...name.split('/'))
    fs.mkdirSync(dir, { recursive: true })
    fs.writeFileSync(
      path.join(dir, 'package.json'),
      JSON.stringify({ name, version: '0.0.0', type: 'module', main: 'index.js' }),
      'utf8',
    )
    fs.writeFileSync(path.join(dir, 'index.js'), source, 'utf8')
  }
  return path.join(root, 'lib', 'index.js')
}

/**
 * The fake plugin context.
 *
 * `inject` is the platform's optional idiom: a callback runs only when every
 * named service exists, which is exactly the behaviour the two scopes rely on —
 * the outer one for the tool half, and the inner `llm` one for the effort
 * reporting. `services.llm` can be deleted to model a host without an LLM
 * runtime, and that is a scenario below rather than an accident.
 */
function makeContext(services) {
  const state = { dispatches: [], schema: null, defaults: null, namespace: null, settingsValue: {} }

  const scopeFor = (names) => {
    if (!names.every((name) => services[name] !== undefined)) return null
    return {
      ...services,
      effect: (run) => run(),
      inject: (inner, callback) => {
        const nested = scopeFor(inner)
        if (nested !== null) callback(nested)
      },
    }
  }

  const ctx = {
    effect: (run) => run(),
    inject: (names, callback) => {
      const scope = scopeFor(names)
      if (scope !== null) callback(scope)
    },
    skills: services.skills,
  }

  services.settings = {
    installSection: (_ctx, namespace, schema, defaults, hooks) => {
      state.namespace = namespace
      state.schema = schema
      state.defaults = defaults
      hooks.setSource(() => state.settingsValue)
      return () => {}
    },
  }

  services.tools = {
    register: (tool) => { state.tool = tool; return () => {} },
  }

  services.subagents = {
    list: () => ['spawn'],
    getProvider: () => ({ capabilities: { agentOptions: true } }),
    // `start` publishes the run through a promise, like the real service.
    start: async (_provider, request) => {
      state.dispatches.push(request)
      return {
        result: Promise.resolve({
          output: [{ type: 'text', text: 'REVIEW' }],
          stopReason: 'completed',
        }),
        dispose: () => Promise.resolve(),
      }
    },
  }

  return { ctx, state }
}

/** One completed child, or a failure the tool has to classify. */
const AGENT = { id: 'parent' }
const EXEC = () => ({ agent: AGENT, signal: new AbortController().signal })

async function main() {
  const staged = stagePlugin(path.resolve(entry))
  const host = await import(pathToFileURL(staged).href)

  const services = {
    skills: { register: () => () => {} },
    llm: {
      resolveModelInfo: async (provider, model) => ({
        provider,
        model,
        reasoning: { efforts: [{ id: 'low' }, { id: 'medium' }, { id: 'high' }], defaultEffort: 'high' },
      }),
    },
  }
  const { ctx, state } = makeContext(services)

  check('the entry exports the skill and the tool in the optional idiom',
    host.name === 'dsh-charter-kit'
    && JSON.stringify(host.inject) === JSON.stringify(['skills'])
    && typeof host.apply === 'function',
    { name: host.name, inject: host.inject })

  host.apply(ctx)

  check('the tool registers under the review namespace',
    state.tool !== undefined && state.tool.name === 'charter_review' && state.namespace === 'charter-kit-review',
    { tool: state.tool === undefined ? null : state.tool.name, namespace: state.namespace })

  // The two seat fields are part of the namespace's declared shape, with the
  // empty string as the default: '' is what "no selection" is stored as, and a
  // missing field would make the reader's fallback the only thing keeping the
  // no-selection path working.
  const shape = state.schema === null ? {} : state.schema.shape
  check('the namespace declares one effort field per seat, defaulting to none',
    shape !== undefined && 'reviewAEffort' in shape && 'reviewBEffort' in shape
    && state.defaults.reviewAEffort === '' && state.defaults.reviewBEffort === '',
    { shape: Object.keys(shape ?? {}), defaults: state.defaults })

  check('the result schema reports the effort as an optional field beside the model',
    state.tool.output.schema.properties.effort !== undefined
    && state.tool.output.schema.properties.effort.type === 'string'
    && state.tool.output.schema.properties.effort.required !== true,
    state.tool.output.schema.properties.effort)

  const route = (aProvider, aModel, extra) => {
    state.settingsValue = Object.assign({
      reviewAProvider: aProvider,
      reviewAModel: aModel,
      reviewBProvider: '',
      reviewBModel: '',
      reviewTimeoutSeconds: 60,
      reviewAEffort: '',
      reviewBEffort: '',
    }, extra ?? {})
  }

  const dispatchOptions = () => state.dispatches[state.dispatches.length - 1].agentOptions
  const run = (args) => state.tool.execute(args, EXEC())

  // 1. No selection: the child is dispatched with exactly the route object this
  //    tool has always sent. This is the no-selection path's whole contract —
  //    one extra key here would change every configured review on every host.
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash')
  let result = await run({ kind: 'A', brief: 'BRIEF' })
  check('without a selection the child gets the route and nothing else',
    JSON.stringify(dispatchOptions()) === JSON.stringify({ provider: 'tt', model: 'qwen3.8-flash' })
    && Object.keys(dispatchOptions()).length === 2,
    dispatchOptions())
  check('without a selection the result reports the provider default',
    result.outcome === 'reviewed' && result.model === 'tt/qwen3.8-flash' && result.effort === 'default',
    result)

  // 2. A selection the route declares is attached, as the level ID the LLM
  //    layer accepts (not the table's wire string) ...
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'high' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('a declared selection is attached as the level id',
    JSON.stringify(dispatchOptions()) === JSON.stringify({
      provider: 'tt', model: 'qwen3.8-flash', reasoningEffort: 'high',
    }),
    dispatchOptions())
  check('the result reports the level it sent, beside the model',
    result.effort === 'high' && JSON.stringify(Object.keys(result)) === JSON.stringify(
      ['outcome', 'model', 'effort', 'review'],
    ),
    { effort: result.effort, keys: Object.keys(result) })

  // 3. ... and a level the route does NOT declare is dropped instead of being
  //    sent: the LLM layer answers an undeclared id with
  //    UNSUPPORTED_REASONING_EFFORT, so sending it would fail a review the user
  //    can see configured.
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'max' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('a level the route does not declare is not sent',
    JSON.stringify(dispatchOptions()) === JSON.stringify({ provider: 'tt', model: 'qwen3.8-flash' }),
    dispatchOptions())
  check('a dropped selection reports the provider default rather than the level',
    result.effort === 'default', result)

  // 4. A route that declares no reasoning at all rejects ANY level, so a
  //    selection is dropped there too — the same rule, one step further.
  services.llm.resolveModelInfo = async (provider, model) => ({ provider, model })
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'high' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('a selection is dropped on a route that declares no reasoning',
    JSON.stringify(dispatchOptions()) === JSON.stringify({ provider: 'tt', model: 'qwen3.8-flash' })
    && result.effort === 'default',
    { options: dispatchOptions(), effort: result.effort })

  // 5. A failed or slow capability lookup cannot make the tool throw, and it
  //    cannot turn a chosen level into a silent default either: the selection is
  //    still dispatched, and the result reports the level this call asked for.
  services.llm.resolveModelInfo = async () => { throw new Error('llm down') }
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'high' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('a failing capability lookup still runs the review with the chosen level',
    result.outcome === 'reviewed' && dispatchOptions().reasoningEffort === 'high',
    { outcome: result.outcome, options: dispatchOptions() })
  check('a failing capability lookup reports the level it sent',
    result.effort === 'high', result)

  // 6. Without an LLM runtime the tool keeps working and reports NO level: it
  //    cannot check a route, so it does not assert one. The service is simply
  //    absent from this context's table, which is exactly how a host without it
  //    presents itself — the inner optional scope then never runs.
  const bare = {
    skills: { register: () => () => {} },
  }
  const bareContext = makeContext(bare)
  host.apply(bareContext.ctx)
  const bareState = bareContext.state
  bareState.settingsValue = {
    reviewAProvider: 'tt',
    reviewAModel: 'qwen3.8-flash',
    reviewBProvider: '',
    reviewBModel: '',
    reviewTimeoutSeconds: 60,
    reviewAEffort: 'high',
    reviewBEffort: '',
  }
  bareState.dispatches.length = 0
  const bareResult = await bareState.tool.execute({ kind: 'A', brief: 'BRIEF' }, EXEC())
  check('without an LLM runtime the tool still registers and still runs',
    bareState.tool !== undefined && bareResult.outcome === 'reviewed',
    { tool: bareState.tool === undefined ? null : bareState.tool.name, outcome: bareResult.outcome })
  check('without an LLM runtime the chosen level is still dispatched',
    bareState.dispatches[0].agentOptions.reasoningEffort === 'high',
    bareState.dispatches[0].agentOptions)
  check('without an LLM runtime the result reports no level at all',
    !('effort' in bareResult) && JSON.stringify(Object.keys(bareResult)) === JSON.stringify(
      ['outcome', 'model', 'review'],
    ),
    { keys: Object.keys(bareResult) })

  services.llm.resolveModelInfo = async (provider, model) => ({
    provider,
    model,
    reasoning: { efforts: [{ id: 'low' }, { id: 'medium' }, { id: 'high' }], defaultEffort: 'high' },
  })

  // 7. A junk stored value is not a selection: the same reading the card
  //    renders, applied before anything reaches a provider.
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'ultra' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('an unknown stored level is not a selection',
    JSON.stringify(dispatchOptions()) === JSON.stringify({ provider: 'tt', model: 'qwen3.8-flash' })
    && result.effort === 'default',
    { options: dispatchOptions(), effort: result.effort })

  // 8. A seat left on "follow the session model" passes no agent options at
  //    all — unchanged from before this feature, and deliberately so: the
  //    selection configures the route under it, and a run that inherits the
  //    session's model inherits its reasoning setting with it.
  state.dispatches.length = 0
  route('', '', { reviewAEffort: 'high' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('an inheriting seat passes no agent options',
    dispatchOptions() === undefined && result.model === 'inherited',
    { options: dispatchOptions(), model: result.model })

  // 9. The caller-requested session route is the same shape, and is still
  //    reported as the fallback it is.
  state.dispatches.length = 0
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'high' })
  result = await run({ kind: 'A', brief: 'BRIEF', route: 'session' })
  check('the session route passes no agent options and stays a fallback',
    dispatchOptions() === undefined && result.outcome === 'fallback' && result.model === 'inherited',
    { options: dispatchOptions(), outcome: result.outcome })

  // 10. A configured route that fails is rerun on the session model with no
  //     options, so the result must report the effort of the run that produced
  //     the review — not the level the failed attempt carried.
  const failingServices = { skills: { register: () => () => {} }, llm: services.llm }
  const failing = makeContext(failingServices)
  // The scope spreads the service table when `apply` runs, so the override has
  // to be in place before it: every child this context publishes fails.
  failingServices.subagents.start = async (_provider, request) => {
    failing.state.dispatches.push(request)
    return {
      result: Promise.resolve({ output: [], stopReason: 'error' }),
      dispose: () => Promise.resolve(),
    }
  }
  host.apply(failing.ctx)
  failing.state.settingsValue = Object.assign({}, state.settingsValue, { reviewAEffort: 'high' })
  const fallbackResult = await failing.state.tool.execute({ kind: 'A', brief: 'BRIEF' }, EXEC())
  check('a failed configured route falls back to the session model',
    fallbackResult.outcome === 'unavailable' || fallbackResult.outcome === 'fallback',
    fallbackResult)
  check('the fallback result reports the provider default, not the failed attempt\'s level',
    fallbackResult.effort === 'default', fallbackResult)

  // 11. The value attached is the level ID the LLM layer accepts, never the
  //     table's provider wire string. They differ for a level spelled `off`,
  //     whose wire value in the copied table is `none`: sending `none` would be
  //     an id no route declares.
  state.dispatches.length = 0
  services.llm.resolveModelInfo = async (provider, model) => ({
    provider,
    model,
    reasoning: { efforts: [{ id: 'off' }, { id: 'low' }, { id: 'high' }] },
  })
  route('tt', 'qwen3.8-flash', { reviewAEffort: 'off' })
  result = await run({ kind: 'A', brief: 'BRIEF' })
  check('the attached value is the level id, even where the table spells it differently',
    dispatchOptions().reasoningEffort === 'off' && result.effort === 'off',
    { options: dispatchOptions(), effort: result.effort })
  services.llm.resolveModelInfo = async (provider, model) => ({
    provider,
    model,
    reasoning: { efforts: [{ id: 'low' }, { id: 'medium' }, { id: 'high' }], defaultEffort: 'high' },
  })

  // 12. Every seat reads its own field.
  state.dispatches.length = 0
  state.settingsValue = {
    reviewAProvider: 'tt',
    reviewAModel: 'qwen3.8-flash',
    reviewBProvider: 'tt',
    reviewBModel: 'qwen3.8-flash',
    reviewTimeoutSeconds: 60,
    reviewAEffort: 'low',
    reviewBEffort: 'high',
  }
  await run({ kind: 'B', brief: 'BRIEF' })
  check('kind B reads the B seat\'s level',
    dispatchOptions().reasoningEffort === 'high', dispatchOptions())

  console.log(failures === 0 ? 'HARNESS: ALL PASS' : `HARNESS: ${failures} FAILURE(S)`)
  process.exitCode = failures === 0 ? 0 : 1
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 2
})
