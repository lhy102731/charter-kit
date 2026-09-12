/**
 * Behavioural harness for the Charter Kit review-model card bundle.
 *
 * The bundle is a browser artifact with no build step, so this harness loads it
 * exactly as the shell's module loader does — `window.__ModuleLoader__.load({
 * id, factory })`, then `factory(require)` — and drives the registered card
 * directly. It exists because the text-presence tests next to it cannot see
 * behaviour: they would keep passing if a write were wired to the wrong field
 * pair, if a refused write were reported as saved, or if a second selection
 * inside one mirror round-trip were reported as failed.
 *
 * Dependency-free by design (no jsdom, no node_modules): React is stubbed down
 * to the three hooks the card uses, the component function is called directly,
 * and the returned element tree is walked to reach the controls' handlers.
 *
 * Driven by tests/test_dsh_client_card_behaviour.py, which skips when node is
 * absent. Usage: node tests/dsh_client_card_harness.cjs <bundle.js>
 * Prints one PASS/FAIL line per behaviour and exits non-zero on any failure.
 */
'use strict'

const fs = require('node:fs')

const bundlePath = process.argv[2]
if (bundlePath === undefined) {
  console.error('usage: node tests/dsh_client_card_harness.cjs <bundle.js>')
  process.exit(2)
}

const A_PAIR = ['reviewAProvider', 'reviewAModel']
const B_PAIR = ['reviewBProvider', 'reviewBModel']
const ENCODE = (provider, model) => `${provider}\u0000${model}`

let failures = 0
function check(label, condition, detail) {
  const passed = Boolean(condition)
  if (!passed) failures += 1
  const suffix = passed || detail === undefined ? '' : ` :: ${JSON.stringify(detail)}`
  console.log(`${passed ? 'PASS' : 'FAIL'}  ${label}${suffix}`)
}

// --------------------------------------------------------------- stub React
function sameDeps(left, right) {
  return Array.isArray(left) && Array.isArray(right) && left.length === right.length
    && left.every((value, index) => Object.is(value, right[index]))
}

/** The three hooks the card uses, driven synchronously by this harness. */
function createHooks() {
  let states = []
  let effects = []
  let cursor = 0
  let pending = []

  return {
    /** Drop every hook slot, so the next render is a fresh mount. */
    reset() {
      states = []
      effects = []
      cursor = 0
      pending = []
    },
    useState(initial) {
      const index = cursor
      cursor += 1
      if (!(index in states)) states[index] = typeof initial === 'function' ? initial() : initial
      return [states[index], (next) => {
        states[index] = typeof next === 'function' ? next(states[index]) : next
      }]
    },
    useEffect(run, deps) {
      const index = cursor
      cursor += 1
      const previous = effects[index]
      // React's dependency contract: an effect re-runs only when its deps change.
      if (previous !== undefined && sameDeps(previous.deps, deps)) return
      if (previous !== undefined && typeof previous.cleanup === 'function') previous.cleanup()
      effects[index] = { deps, cleanup: undefined }
      pending.push(() => {
        const cleanup = run()
        effects[index].cleanup = typeof cleanup === 'function' ? cleanup : undefined
      })
    },
    beginPass() {
      cursor = 0
      pending = []
    },
    /** @returns whether any effect ran (and so a re-render may be needed). */
    runPending() {
      if (pending.length === 0) return false
      const queued = pending
      pending = []
      for (const task of queued) task()
      return true
    },
  }
}

const hooks = createHooks()

function createElement(type, props, ...children) {
  return {
    type,
    props: props === null || props === undefined ? {} : props,
    children: children.flat(),
  }
}

const React = { createElement, useState: hooks.useState, useEffect: hooks.useEffect }

// ------------------------------------------------------------ element walking
function walk(node, visit) {
  if (Array.isArray(node)) {
    for (const child of node) walk(child, visit)
    return
  }
  if (node === null || node === undefined || typeof node !== 'object') return
  visit(node)
  walk(node.children, visit)
}

function collect(tree, type) {
  const found = []
  walk(tree, (node) => { if (node.type === type) found.push(node) })
  return found
}

const isOption = (child) => child !== null && typeof child === 'object' && child.type === 'option'

function selects(tree) {
  return collect(tree, 'select')
}

function optionValues(select) {
  return select.children.filter(isOption).map((option) => option.props.value)
}

function optionTexts(select) {
  return select.children.filter(isOption).map((option) => option.children.join(''))
}

function statusText(tree) {
  const notes = collect(tree, 'p').filter((node) => node.props.className === 'ck-status')
  return notes.length === 0 ? '' : notes[0].children.join('')
}

// ------------------------------------------------------------- plugin context
const dictionaries = {}
const mutations = []
const conflicts = []
const listeners = new Set()
let registration = null
let registered = null
let boundSpec = null
let snapshot = null
let catalog = { ok: true, value: { groups: [] } }
let writeOutcome = 'accept'
let pendingRevision
let writeQueue = Promise.resolve()

const scope = {
  getSnapshot: () => snapshot,
  subscribe: (listener) => {
    listeners.add(listener)
    return () => { listeners.delete(listener) }
  },
  // Models SettingsScopeController.mutate. Writes are serialized, each one
  // resolves its own revision as `expectedRevision ?? pendingRevision ??
  // snapshot.revision` AT THE MOMENT IT RUNS, and a Host refusal resolves the
  // returned promise after the controller recovers its mirror — which is why
  // the card must read back what landed instead of trusting the resolution.
  mutate: (ops, expectedRevision) => {
    mutations.push({ ops: JSON.parse(JSON.stringify(ops)), expectedRevision })
    if (writeOutcome === 'throw') return Promise.reject(new Error('transport down'))
    const task = writeQueue.then(() => {
      const revision = expectedRevision ?? pendingRevision ?? snapshot.revision
      if (writeOutcome === 'refuse') return
      if (revision !== snapshot.revision) {
        // SETTINGS_CONFLICT: the namespace moved since the caller read it, so
        // the Host refuses it and the controller reloads instead of storing.
        conflicts.push(revision)
        return
      }
      // A miniature mirror: an accepted write folds into the user layer and the
      // resolved section, then subscribers are told.
      const user = Object.assign({}, snapshot.user)
      const value = Object.assign({}, snapshot.value)
      for (const op of ops) {
        user[op.path[0]] = op.value
        value[op.path[0]] = op.value
      }
      snapshot = Object.assign({}, snapshot, { user, value, revision: revision + 1 })
      pendingRevision = revision + 1
      for (const listener of listeners) listener()
    })
    // The queue tail stays fulfilled, so one refused write cannot strand the
    // writes queued behind it.
    writeQueue = task.catch(() => {})
    return task
  },
}

const ctx = {
  effect: (run) => run(),
  locale: {
    register: (ns, dicts) => { dictionaries[ns] = dicts; return () => {} },
    bind: (ns) => (key) => {
      const dicts = dictionaries[ns] || {}
      const table = dicts.en || {}
      return Object.prototype.hasOwnProperty.call(table, key) ? table[key] : (dicts.zh || {})[key] || key
    },
  },
  settingsScope: { bind: (spec) => { boundSpec = spec; return scope } },
  slots: {
    inject: (_name, contribute) => { contribute() },
    register: (options, component) => { registered = { options, component }; return () => {} },
  },
  remote: { session: { modelCatalog: () => Promise.resolve(catalog) } },
}

const styleTags = []
const documentStub = {
  querySelector: () => null,
  createElement: () => ({ dataset: {}, textContent: '' }),
  head: { appendChild: (tag) => { styleTags.push(tag) } },
}
const windowStub = { __ModuleLoader__: { load: (value) => { registration = value } } }

// ------------------------------------------------------------------ the run
new Function('window', 'document', fs.readFileSync(bundlePath, 'utf8'))(windowStub, documentStub)

check('module id is the package name',
  registration !== null && registration.id === '@dsh-external/dsh-charter-kit',
  registration === null ? 'no registration' : registration.id)

const bundle = registration.factory((specifier) => {
  if (specifier !== 'react') throw new Error(`the bundle required an unexpected module: ${specifier}`)
  return React
})

// What this check can and cannot prove about `inject`.
//
// It proves the exported face carries the four platform services the card
// reaches for — `ctx.slots`, `ctx.settingsScope`, `ctx.remote.session` and
// `ctx.locale` — and that every dotted property path listed there also declares
// its root as a service. `remote` must therefore be spelled as a bare service
// name and not only as the property path `remote.session`: inject names are
// service names, and a list that names no `remote` service makes the shell wait
// for nothing, so the card never mounts.
//
// It CANNOT prove the card mounts. The shell's inject machinery is what turns
// this list into a wait, and the harness never runs it: it hands `apply` a
// hand-written `ctx` whose `remote` member is present unconditionally, so
// deleting `remote` from the list would not change a single call below. Only
// driving a live shell proves the mount. Live evidence lives under
// .superpowers/sdd/2026-09-12-review-model-config/: probe-card4.json captured
// ['slots', 'settingsScope', 'remote.session', 'locale'] at this line and found
// no card after driving 设置 → 插件 → 插件配置 in headless Chromium
// (ckCardPresent: false, no selects), while probe-card5 recorded the corrected
// line and reported cardPresent: true with two selects, both read back and
// saved. This check pins the value live testing identified as required; it is
// not evidence that the card appears.
//
// The label is deliberately left as it was: the behaviour test beside this
// harness asserts that exact label, and inventing a new one would silently
// oblige that test to list it.
const REQUIRED_SERVICES = ['slots', 'settingsScope', 'remote', 'locale']
const injectList = Array.isArray(bundle.inject) ? bundle.inject : []
check('exports carry apply and inject',
  typeof bundle.apply === 'function'
  && Array.isArray(bundle.inject)
  && REQUIRED_SERVICES.every((service) => injectList.includes(service))
  // `remote.session` is the path the card reads, so it must stay declared too.
  && injectList.includes('remote.session')
  // A dotted entry needs the root service declared beside it, or the value it
  // walks is not there when the shell finally runs `apply`.
  && injectList.filter((name) => name.includes('.')).every((path) => injectList.includes(path.split('.')[0])),
  { apply: typeof bundle.apply, inject: bundle.inject, required: REQUIRED_SERVICES })

bundle.apply(ctx)

check('card registers into settings.plugin.item',
  registered !== null && registered.options.name === 'settings.plugin.item',
  registered === null ? 'no card' : registered.options.name)
check('card key and locale are the namespace',
  registered.options.key === 'charter-kit-review' && registered.options.locale === 'charter-kit-review',
  { key: registered.options.key, locale: registered.options.locale })
check('the scope is bound to the host namespace',
  boundSpec !== null && boundSpec.namespace === 'charter-kit-review',
  boundSpec)

const face = registered.options.inject()
const component = registered.component

// --------------------------------------------------------------- render cycle
function renderOnce() {
  hooks.beginPass()
  const tree = component(face)
  return { tree, ran: hooks.runPending() }
}

/** Render until no effect runs again, i.e. until the tree is stable. */
function renderSettled() {
  let result = renderOnce()
  for (let pass = 0; result.ran && pass < 8; pass += 1) result = renderOnce()
  return result.tree
}

async function flush() {
  for (let tick = 0; tick < 20; tick += 1) await Promise.resolve()
}

async function mount() {
  listeners.clear() // the previous card unmounted and unsubscribed
  hooks.reset() // this one mounts with no hook state carried over
  pendingRevision = undefined // the controller reached quiescence between mounts
  writeQueue = Promise.resolve()
  renderOnce() // effects run here; the catalogue load is kicked off
  await flush()
  return renderSettled()
}

async function choose(index, value) {
  const node = selects(renderSettled())[index]
  if (node === undefined) throw new Error(`the card rendered no select at index ${index}`)
  node.props.onChange({ target: { value } })
  await flush()
  return renderSettled()
}

/**
 * Fire several selections in one round-trip, i.e. before the mirror advances.
 * Two `choose` calls cannot model this: the await between them lets the first
 * write land, so the second one reads a fresh revision either way.
 * @param pairs - `[select index, option value]`, in the order the user picked.
 * @returns the settled tree.
 */
async function chooseTogether(pairs) {
  const nodes = selects(renderSettled())
  for (const [index, value] of pairs) {
    const node = nodes[index]
    if (node === undefined) throw new Error(`the card rendered no select at index ${index}`)
    node.props.onChange({ target: { value } })
  }
  await flush()
  return renderSettled()
}

function ready(value, revision, writable) {
  return {
    status: 'ready',
    value,
    base: {},
    // The card stores exactly these overrides, so the raw user layer is the
    // same four fields.
    user: Object.assign({}, value),
    revision,
    writable: writable === undefined ? true : writable,
    mode: 'host',
  }
}

const VALUE = (aProvider = '', aModel = '', bProvider = '', bModel = '') => ({
  reviewAProvider: aProvider, reviewAModel: aModel, reviewBProvider: bProvider, reviewBModel: bModel,
})

const CATALOG = {
  ok: true,
  value: {
    groups: [
      {
        id: 'anthropic',
        name: 'Anthropic',
        models: [{ id: 'opus', name: 'Opus 4' }, { id: 'sonnet', name: 'Sonnet 4' }],
      },
      { id: 'openai', name: 'OpenAI', models: [{ id: 'gpt', name: 'GPT-5' }] },
    ],
  },
}

const asSet = (...ops) => JSON.stringify(ops.map(([path, value]) => ({ op: 'set', path: [path], value })))

async function main() {
  // 1. An unavailable namespace renders no trace at all.
  snapshot = { status: 'unavailable', value: {}, user: {}, writable: false, revision: 1, mode: 'memory' }
  check('an unavailable namespace renders nothing', await mount() === null)

  // 2. A ready namespace reads its options from the model catalogue.
  catalog = CATALOG
  snapshot = ready(VALUE(), 10)
  let tree = await mount()
  check('options come from the model catalog',
    selects(tree).length === 2
    && JSON.stringify(optionTexts(selects(tree)[0])) === JSON.stringify([
      'Default (follow current model)', 'Opus 4 — Anthropic', 'Sonnet 4 — Anthropic', 'GPT-5 — OpenAI',
    ]),
    selects(tree).map(optionTexts))

  // 3. A selection in review A's select writes A's pair, and only A's pair. The
  //    revision is the scope's business, not the card's: a card that pins the
  //    revision it read makes the Host refuse the second of two quick
  //    selections, which scenario 11 covers.
  mutations.length = 0
  conflicts.length = 0
  writeOutcome = 'accept'
  tree = await choose(0, ENCODE('openai', 'gpt'))
  check("review A selection writes only review A's field pair",
    mutations.length === 1 && mutations[0].ops.length === 2
    && JSON.stringify(mutations[0].ops) === asSet(['reviewAProvider', 'openai'], ['reviewAModel', 'gpt']),
    mutations)
  check('a write delegates its revision to the scope',
    mutations[0].expectedRevision === undefined, mutations[0].expectedRevision)

  // 4. A selection in review B's select writes B's pair, and only B's pair.
  mutations.length = 0
  tree = await choose(1, ENCODE('anthropic', 'sonnet'))
  check("review B selection writes only review B's field pair",
    mutations.length === 1 && mutations[0].ops.length === 2
    && JSON.stringify(mutations[0].ops) === asSet(['reviewBProvider', 'anthropic'], ['reviewBModel', 'sonnet']),
    mutations)

  // 5. A route the catalogue no longer serves stays selectable where it is
  //    stored, and never leaks into the other review's dropdown.
  snapshot = ready(VALUE('retired', 'ghost'), 20)
  tree = await mount()
  const reviewA = optionValues(selects(tree)[0])
  const reviewB = optionValues(selects(tree)[1])
  check('an unserved stored route stays selectable for its own review',
    reviewA.includes(ENCODE('retired', 'ghost')) && selects(tree)[0].props.value === ENCODE('retired', 'ghost'),
    reviewA)
  check("review B never offers review A's rescued route",
    !reviewB.includes(ENCODE('retired', 'ghost')),
    reviewB)
  check('an unserved stored route is labelled unavailable',
    optionTexts(selects(tree)[0]).includes('retired/ghost — Unavailable'),
    optionTexts(selects(tree)[0]))

  // 6. The regression for the mirrored case: A unset, B storing the unserved
  //    route. A must not be offered B's rescued route either.
  snapshot = ready(VALUE('', '', 'retired', 'ghost'), 21)
  tree = await mount()
  check("review A never offers review B's rescued route",
    !optionValues(selects(tree)[0]).includes(ENCODE('retired', 'ghost')),
    optionValues(selects(tree)[0]))

  // 7. A write the Host accepts is reported as saved.
  writeOutcome = 'accept'
  snapshot = ready(VALUE(), 30)
  tree = await mount()
  tree = await choose(0, ENCODE('openai', 'gpt'))
  check('a landed write reports saved', statusText(tree) === 'Saved', statusText(tree))

  // 8. A write the Host REFUSES resolves without storing anything: the card
  //    must read back what landed instead of trusting the resolution.
  writeOutcome = 'refuse'
  snapshot = ready(VALUE('anthropic', 'sonnet'), 31)
  tree = await mount()
  tree = await choose(0, ENCODE('openai', 'gpt'))
  check('a refused write reports failure', statusText(tree) === 'Save failed', statusText(tree))
  check('a refused write leaves the stored route standing',
    selects(tree)[0].props.value === ENCODE('anthropic', 'sonnet'),
    selects(tree)[0].props.value)

  // 9. A transport rejection is reported as a failure too.
  writeOutcome = 'throw'
  snapshot = ready(VALUE(), 32)
  tree = await mount()
  tree = await choose(0, ENCODE('openai', 'gpt'))
  check('a transport rejection reports failure', statusText(tree) === 'Save failed', statusText(tree))

  // 10. Choosing inherit clears both fields of that review's pair, and the
  //     read-back must not misfire on the empty-string path.
  writeOutcome = 'accept'
  mutations.length = 0
  snapshot = ready(VALUE('anthropic', 'opus'), 33)
  tree = await mount()
  tree = await choose(0, '')
  check('inherit clears both fields of its own pair',
    JSON.stringify(mutations[0].ops) === asSet(['reviewAProvider', ''], ['reviewAModel', '']),
    mutations)
  check('inherit reports saved once it lands', statusText(tree) === 'Saved', statusText(tree))

  // 11. The regression this harness exists for, mirrored into the settings
  //     round-trip: two selections made before the mirror advances must both
  //     land. A card that sends the revision it read pins the same revision on
  //     both, the Host refuses the second as a settings conflict, and the user
  //     is told "Save failed" for a write they watched land.
  mutations.length = 0
  conflicts.length = 0
  writeOutcome = 'accept'
  snapshot = ready(VALUE(), 40)
  tree = await mount()
  tree = await chooseTogether([
    [0, ENCODE('openai', 'gpt')],
    [1, ENCODE('anthropic', 'sonnet')],
  ])
  check('two selections in one round-trip both land',
    mutations.length === 2 && conflicts.length === 0 && statusText(tree) === 'Saved',
    {
      writes: mutations.length,
      conflicts,
      pinnedRevisions: mutations.map((mutation) => mutation.expectedRevision),
      status: statusText(tree),
    })
  check('both of the round-trip selections are stored',
    selects(tree)[0].props.value === ENCODE('openai', 'gpt')
    && selects(tree)[1].props.value === ENCODE('anthropic', 'sonnet'),
    selects(tree).map((node) => node.props.value))

  console.log(failures === 0 ? 'HARNESS: ALL PASS' : `HARNESS: ${failures} FAILURE(S)`)
  process.exitCode = failures === 0 ? 0 : 1
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 2
})
