/**
 * Behavioural harness for the Charter Kit review-model card bundle.
 *
 * The bundle is a browser artifact with no build step, so this harness loads it
 * exactly as the shell's module loader does — `window.__ModuleLoader__.load({
 * id, factory })`, then `factory(require)` — and drives the registered card
 * directly. It exists because the text-presence tests next to it cannot see
 * behaviour: they would keep passing if a write were wired to the wrong field
 * pair, if a refused write were reported as saved, if a second selection
 * inside one mirror round-trip were reported as failed, or if the reasoning-
 * effort area offered a level the model's own declaration does not carry.
 *
 * WHAT IT CANNOT SEE, and what the headless-browser probe beside this file is
 * for: every handler here is driven with a synthetic `target.value` on a
 * hand-walked element tree. That is how a previous card defect — a controlled
 * input a real browser could not clear — passed this harness unchanged. It pins
 * the contract the card implements; it is not evidence that a browser renders
 * it.
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
const TIMEOUT_FIELD = 'reviewTimeoutSeconds'
const TIMEOUT_DEFAULT = 240
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

// The timeout control is a number input, not a third select: the two dropdowns
// stay the only selects on the card.
//
// These helpers reach it by input TYPE, deliberately. The effort area added in
// task 16 renders 14 radios (7 levels x 2 seats) beside it, so "the card's only
// input" stopped being a property of the card and an index-based helper would
// quietly start reading a radio. The counts that changed with that area are
// pinned on purpose in scenario 12 below.
function inputs(tree) {
  return collect(tree, 'input')
}

function numberInputs(tree) {
  return inputs(tree).filter((node) => node.props.type === 'number')
}

/** Every effort radio, in render order (seat A's seven rows, then seat B's). */
function radios(tree) {
  return inputs(tree).filter((node) => node.props.type === 'radio')
}

/** One seat's radio for one level, or undefined when the row is not rendered. */
function radioAt(tree, seat, level) {
  return radios(tree).find((node) => node.props.name === `ck-effort-${seat}` && node.props.value === level)
}

/** The seat panels, found structurally rather than by text. */
function effortPanels(tree) {
  return collect(tree, 'div').filter((node) => node.props.className === 'ck-effort')
}

/** Every text node under one element, joined: the walker above skips strings. */
function textOf(node) {
  if (typeof node === 'string') return node
  if (Array.isArray(node)) return node.map(textOf).join(' ')
  if (node === null || node === undefined || typeof node !== 'object') return ''
  return textOf(node.children)
}

/** One panel's text content: the state line and the notes live there. */
function panelText(panel) {
  return panel === undefined ? '' : textOf(panel)
}

/** One row's text: the level, the table's wire value, and any refusal reason. */
function rowText(panel, level) {
  const row = collect(panel, 'label').find((node) => node.props['data-level'] === level)
  return row === undefined ? '' : textOf(row)
}

function inputValue(tree, index) {
  const node = numberInputs(tree)[index]
  return node === undefined ? undefined : node.props.value
}

function inputType(tree, index) {
  const node = numberInputs(tree)[index]
  return node === undefined ? undefined : node.props.type
}

/**
 * The bounds the input advertises. These are the card's own copy of the tool's
 * clamp, so they have to agree with it: a card offering a range the tool does
 * not accept, or hiding one it does, is the drift this pins.
 */
function inputBounds(tree, index) {
  const node = numberInputs(tree)[index]
  return node === undefined ? undefined : { min: node.props.min, max: node.props.max }
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
const documentUpdatedHandlers = []
let registration = null
const registeredSlots = {}
const registered = (name) => registeredSlots[name] ?? null
let unregistered = 0
let queriedNamespace = null
let snapshot = null
let catalog = { ok: true, value: { groups: [] } }
let writeOutcome = 'accept'
let pendingRevision
let writeQueue = Promise.resolve()

// Models ConfigForm over one discovered namespace: the same getSnapshot /
// subscribe / mutate face the card has always bound, now reached through
// `ctx.configForms.get(entryId)`.
const scope = {
  getSnapshot: () => snapshot,
  subscribe: (listener) => {
    listeners.add(listener)
    return () => { listeners.delete(listener) }
  },
  // Models ConfigFormController.mutate. Writes are serialized, each one
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

/**
 * The Host settings describe answer. Since DSH 0.1.7 the namespace id is the
 * plugin's loader ENTRY ID, so the fake uses the market-assigned id — a name
 * the bundle cannot know in advance, which is what makes the discovery
 * behaviours below meaningful. A decoy namespace rides along: a schema that
 * mentions the timeout field alone must never be adopted as ours.
 */
const OWN_NAMESPACE = 'mkt-dsh-charter-kit'
let describeAnswer = {
  ok: true,
  value: {
    namespaces: [
      {
        autoGenerate: true,
        ns: 'other-plugin',
        schema: { type: 'object', properties: { reviewTimeout: { type: 'number' } } },
        value: {},
      },
      {
        autoGenerate: true,
        ns: OWN_NAMESPACE,
        schema: {
          type: 'object',
          properties: {
            reviewAProvider: { type: 'string' },
            reviewAModel: { type: 'string' },
            reviewTimeoutSeconds: { type: 'number' },
            reviewAEffort: { type: 'string' },
            reviewBEffort: { type: 'string' },
          },
        },
        value: {},
      },
    ],
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
  configForms: { get: (ns) => { queriedNamespace = ns; return scope } },
  slots: {
    inject: (name, contribute) => {
      contribute()
      return () => { unregistered += 1; delete registeredSlots[name] }
    },
    register: (options, component) => { registeredSlots[options.name] = { options, component }; return () => {} },
  },
  remote: {
    session: { modelCatalog: () => Promise.resolve(catalog) },
    settings: { describe: () => Promise.resolve(describeAnswer) },
    $on: (_event, handler) => {
      documentUpdatedHandlers.push(handler)
      return () => {}
    },
  },
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
// It proves the exported face carries the platform services the card reaches
// for — `ctx.slots`, `ctx.configForms`, `ctx.remote.settings`,
// `ctx.remote.session` and `ctx.locale` — and that every dotted property path
// listed there also declares its root as a service. `remote` must therefore be
// spelled as a bare service name and not only as the property paths: inject
// names are service names, and a list that names no `remote` service makes the
// shell wait for nothing, so the card never mounts.
//
// It CANNOT prove the card mounts. The shell's inject machinery is what turns
// this list into a wait, and the harness never runs it: it hands `apply` a
// hand-written `ctx` whose `remote` member is present unconditionally, so
// deleting `remote` from the list would not change a single call below. Only
// driving a live shell proves the mount. The settingsScope-era probes are
// recorded under .superpowers/sdd/2026-09-12-review-model-config/
// (probe-card4/5): they pin the mechanics, not this list's current spelling.
//
// The label is deliberately left as it was: the behaviour test beside this
// harness asserts that exact label, and inventing a new one would silently
// oblige that test to list it.
const REQUIRED_SERVICES = ['slots', 'locale', 'remote', 'configForms']
const injectList = Array.isArray(bundle.inject) ? bundle.inject : []
check('exports carry apply and inject',
  typeof bundle.apply === 'function'
  && Array.isArray(bundle.inject)
  && REQUIRED_SERVICES.every((service) => injectList.includes(service))
  // `remote.session` and `remote.settings` are the paths the card reads, so
  // both must stay declared too.
  && injectList.includes('remote.session')
  && injectList.includes('remote.settings')
  // A dotted entry needs the root service declared beside it, or the value it
  // walks is not there when the shell finally runs `apply`.
  && injectList.filter((name) => name.includes('.')).every((path) => injectList.includes(path.split('.')[0])),
  { apply: typeof bundle.apply, inject: bundle.inject, required: REQUIRED_SERVICES })

// `apply` registers ASYNCHRONOUSLY since the configForms migration: the card
// discovers its namespace from the Host's settings describe answer before it
// has anything to bind. Mounting, face, and the registration checks therefore
// live in main(), after the describe round-trip has been flushed.
let face = null
let component = null

// --------------------------------------------------------------- render cycle
function renderOnce() {
  hooks.beginPass()
  const tree = component({ ...face, view: 'page' })
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
 * Type into the timeout input WITHOUT committing it: one `change` event, which
 * is all a real browser sends per keystroke.
 */
async function draft(index, value) {
  const node = numberInputs(renderSettled())[index]
  if (node === undefined) throw new Error(`the card rendered no input at index ${index}`)
  node.props.onChange({ target: { value } })
  await flush()
  return renderSettled()
}

/**
 * Commit the field the way a browser does when focus leaves it. The node is
 * re-read afterwards, because the commit handler closes over the draft from the
 * render that produced it.
 */
async function commit(index) {
  const node = numberInputs(renderSettled())[index]
  if (node === undefined) throw new Error(`the card rendered no input at index ${index}`)
  node.props.onBlur()
  await flush()
  return renderSettled()
}

/** A whole edit: type into the field, then leave it. */
async function type(index, value) {
  await draft(index, value)
  return commit(index)
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

const VALUE = (aProvider = '', aModel = '', bProvider = '', bModel = '', timeout = TIMEOUT_DEFAULT, aEffort = '', bEffort = '') => ({
  reviewAProvider: aProvider,
  reviewAModel: aModel,
  reviewBProvider: bProvider,
  reviewBModel: bModel,
  reviewTimeoutSeconds: timeout,
  reviewAEffort: aEffort,
  reviewBEffort: bEffort,
})

// The catalogue carries each model's OWN reasoning declaration, because that is
// what the card gates the effort rows on: it is the set the adapter checks a
// request against. The ids are chosen against the copied table so that both
// agreement (`deepseek-v4`: the table and the route both say off/low/high/max)
// and disagreement (`qwen3.8-flash`: the table says off/low/medium/xhigh, the
// route declares low/high/max) are pinned.
const effortIds = (...ids) => ids.map((id) => ({ id, name: id }))

const CATALOG = {
  ok: true,
  value: {
    groups: [
      {
        id: 'anthropic',
        name: 'Anthropic',
        models: [
          {
            id: 'claude-opus-4-5',
            name: 'Claude Opus 4.5',
            reasoning: { efforts: effortIds('low', 'medium', 'high'), defaultEffort: 'high' },
          },
          { id: 'opus', name: 'Opus 4' },
        ],
      },
      {
        id: 'deepseek',
        name: 'DeepSeek',
        models: [
          {
            id: 'deepseek-v4',
            name: 'DeepSeek V4',
            reasoning: { efforts: effortIds('off', 'low', 'high', 'max'), defaultEffort: 'high' },
          },
        ],
      },
      {
        id: 'tt',
        name: 'tt',
        models: [
          {
            id: 'qwen3.8-flash',
            name: 'Qwen3.8 Flash',
            reasoning: { efforts: effortIds('low', 'high', 'max') },
          },
          { id: 'gpt', name: 'GPT-5' },
        ],
      },
    ],
  },
}

const asSet = (...ops) => JSON.stringify(ops.map(([path, value]) => ({ op: 'set', path: [path], value })))

async function main() {
  // 0. Registration: `apply` discovers its namespace from the Host describe
  //    answer before it can bind a form, so registration is asynchronous and
  //    the id it binds is the one the answer carried, never a hardcoded one.
  bundle.apply(ctx)
  await flush()
  check('card registers into the Plugins page',
    registered('plugins.item') !== null,
    registered('plugins.item') === null ? 'no card' : registered('plugins.item').options.name)
  check('the card is a settings section like the other plugins',
    registered('settings.section') !== null
      && registered('settings.section').options.id === 'charter-kit'
      && registered('settings.section').options.locale === 'charter-kit-review',
    registered('settings.section') === null
      ? 'no settings section'
      : { id: registered('settings.section').options.id, locale: registered('settings.section').options.locale })
  check('card locale is the review namespace',
    registered('plugins.item').options.locale === 'charter-kit-review',
    { locale: registered('plugins.item').options.locale })
  check('the form is bound to the discovered host namespace',
    queriedNamespace === OWN_NAMESPACE,
    { queried: queriedNamespace, own: OWN_NAMESPACE })
  check('a foreign namespace is never adopted',
    // The describe answer carried a decoy whose schema mentions the timeout
    // field alone; the bound namespace must still be the own one.
    queriedNamespace === OWN_NAMESPACE && registered('plugins.item').options.id === 'charter-kit',
    { id: registered('plugins.item').options.id, queried: queriedNamespace })

  face = registered('plugins.item').options.inject()
  component = registered('plugins.item').component

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
      'Default (follow current model)',
      'Claude Opus 4.5 — Anthropic',
      'Opus 4 — Anthropic',
      'DeepSeek V4 — DeepSeek',
      'Qwen3.8 Flash — tt',
      'GPT-5 — tt',
    ]),
    selects(tree).map(optionTexts))

  // 2b. The Plugins page also asks the closed card for its one-liner; that
  //     view is static copy rendered beside the hooks, before readiness.
  hooks.beginPass()
  const summaryTree = component({ ...face, view: 'summary' })
  hooks.runPending()
  check('the summary view renders the description line',
    typeof summaryTree === 'string' && summaryTree.length > 0
      && summaryTree.includes('Review A'),
    summaryTree)

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

  // 12. The timeout control sits beside the two dropdowns, is a number input,
  //     and reads back the stored value rather than a hard-coded default. The
  //     two reviews keep exactly two selects: the timeout is not a third one.
  //
  //     The input COUNT changed in task 16, deliberately: the effort area adds
  //     14 radios (7 levels x 2 seats) and no text input at all — the per-level
  //     value column is read-only text, because the declaration it shows belongs
  //     to the model, not to this card. A count written from the old card would
  //     have to be relaxed to keep this passing; instead the number input is now
  //     identified by type and the radios are counted here, so a future control
  //     cannot slip in under either number.
  snapshot = ready(VALUE('', '', '', '', 90), 50)
  tree = await mount()
  check('the timeout control is one number input beside the two dropdowns',
    numberInputs(tree).length === 1 && inputType(tree, 0) === 'number'
    && inputs(tree).length === 15 && radios(tree).length === 14
    && selects(tree).length === 2,
    {
      inputs: inputs(tree).length,
      numberInputs: numberInputs(tree).length,
      radios: radios(tree).length,
      type: inputType(tree, 0),
      selects: selects(tree).length,
    })
  check('the timeout control reads the stored value',
    inputValue(tree, 0) === '90', inputValue(tree, 0))
  // The card's advertised range is the tool's clamp, which was RAISED
  // deliberately in task 17: 30/1800, default 600. The pin moved with it, on
  // purpose and with a reason — 270 s was measured and found too small (a real
  // project lost a Review B to two attempts that both died on this tool's own
  // clock at 270 s), so the old `max: 270` pin was a pin on the defect. The
  // previous rationale here — the host's ~600 s ceiling on total duration —
  // is retracted: the measured mechanism is a per-stream IDLE watchdog, which
  // bounds silence rather than duration, so the range is no longer dimensioned
  // against any ceiling on how long a call may run.
  // `min`/`max` are compared as strings because this harness reads the React
  // element's props — the numbers the card passes — while a browser sees the
  // attribute form; String() makes the check mean the same thing in both, and
  // the real DOM attributes are read by probe-task17-card.mjs in a browser.
  check('the timeout control advertises the tool\'s clamped range',
    inputBounds(tree, 0) !== undefined
    && String(inputBounds(tree, 0).min) === '30'
    && String(inputBounds(tree, 0).max) === '1800',
    inputBounds(tree, 0))

  // 13. Editing it writes exactly that one field, and the write is judged by
  //     what the Host stored rather than by the promise resolving.
  mutations.length = 0
  conflicts.length = 0
  writeOutcome = 'accept'
  tree = await type(0, '300')
  check('a timeout edit writes only the timeout field',
    mutations.length === 1 && mutations[0].ops.length === 1
    && JSON.stringify(mutations[0].ops) === asSet([TIMEOUT_FIELD, 300]),
    mutations)
  check('a landed timeout edit reports saved', statusText(tree) === 'Saved', statusText(tree))

  // 14. A refused write must be reported as a failure and must leave the stored
  //     value standing, exactly like the dropdowns.
  writeOutcome = 'refuse'
  snapshot = ready(VALUE('', '', '', '', 120), 51)
  tree = await mount()
  tree = await type(0, '450')
  check('a refused timeout edit reports failure', statusText(tree) === 'Save failed', statusText(tree))
  check('a refused timeout edit leaves the stored value standing',
    inputValue(tree, 0) === '120', inputValue(tree, 0))

  // 15. A blank or non-numeric entry writes nothing at all. Writing a coerced 0
  //     would be silently clamped by the tool to its 30 s floor, which is the
  //     silent deviation this refusal avoids.
  writeOutcome = 'accept'
  mutations.length = 0
  snapshot = ready(VALUE('', '', '', '', 120), 52)
  tree = await mount()
  tree = await type(0, '')
  check('a blank timeout entry writes nothing', mutations.length === 0, mutations)
  tree = await type(0, 'soon')
  check('a non-numeric timeout entry writes nothing', mutations.length === 0, mutations)
  check('a rejected timeout entry is reported rather than silently dropped',
    statusText(tree) !== '' && statusText(tree) !== 'Saved', statusText(tree))

  // 16. The field carries its own draft and commits on blur. This is what makes
  //     an emptied field reachable at all: a card that wrote on every keystroke
  //     would re-render from the store after each one, and React would put the
  //     old text back, so Backspace and select-all-then-delete fight the user.
  //
  //     WHAT THIS CANNOT PROVE: it drives the handlers with a synthetic
  //     `target.value`, which is exactly the pattern that hides real-DOM
  //     controlled-input behaviour — the defect this scenario is about is
  //     invisible here by construction. Only a real browser can show that the
  //     field can actually be cleared; that evidence is a headless-Chromium probe
  //     recorded in the task report, not this check. What is pinned here is the
  //     draft-then-commit contract the fix introduced.
  mutations.length = 0
  writeOutcome = 'accept'
  snapshot = ready(VALUE('', '', '', '', 120), 60)
  tree = await mount()
  tree = await draft(0, '')
  check('an emptied field is reachable while editing',
    inputValue(tree, 0) === '' && mutations.length === 0,
    { value: inputValue(tree, 0), writes: mutations.length })
  tree = await draft(0, '999')
  check('typing does not write until the edit is committed',
    inputValue(tree, 0) === '999' && mutations.length === 0,
    { value: inputValue(tree, 0), writes: mutations.length })

  // 17. Leaving the field commits what was typed, and the field then shows the
  //     stored value again rather than a stale draft.
  tree = await commit(0)
  check('leaving the field commits the draft',
    mutations.length === 1
    && JSON.stringify(mutations[0].ops) === asSet([TIMEOUT_FIELD, 999]),
    mutations)
  check('the committed field shows the stored value again',
    inputValue(tree, 0) === '999' && statusText(tree) === 'Saved',
    { value: inputValue(tree, 0), status: statusText(tree) })

  // 18. Leaving an emptied field writes nothing and restores what is stored:
  //     the clear is reachable, and abandoning it changes nothing.
  mutations.length = 0
  snapshot = ready(VALUE('', '', '', '', 120), 61)
  tree = await mount()
  tree = await draft(0, '')
  tree = await commit(0)
  check('leaving an emptied field writes nothing and restores the stored value',
    mutations.length === 0 && inputValue(tree, 0) === '120',
    { writes: mutations.length, value: inputValue(tree, 0) })

  // ---------------------------------------------------------------- effort area
  //
  // WHAT THIS CANNOT PROVE, and the reason the live browser probe exists: every
  // state below is driven through synthetic `target.value` / `checked` props on
  // a hand-walked element tree, never through a real DOM. A previous card
  // defect (an uncontrolled input that could not be cleared) escaped this
  // harness for exactly that reason. It pins the contract — which row is
  // enabled, which field a click writes, what the panel says it will send — and
  // it cannot show that a browser renders the same thing. That evidence is the
  // headless-Chromium probe recorded in the task report.

  // 19. One panel per seat, and the rows are the reference editor's levels in
  //     the reference editor's order: the grid fills row-major into two columns,
  //     which is what puts off/low/high/max down the left and
  //     minimal/medium/xhigh down the right.
  const LEVEL_ORDER = ['off', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max']
  writeOutcome = 'accept'
  snapshot = ready(VALUE('deepseek', 'deepseek-v4', 'tt', 'qwen3.8-flash'), 70)
  tree = await mount()
  const panels = effortPanels(tree)
  check('the effort area renders one panel per seat',
    panels.length === 2 && panels[0].props['data-seat'] === 'A' && panels[1].props['data-seat'] === 'B',
    panels.map((panel) => panel.props['data-seat']))
  check('each panel lists the reference editor\'s levels in its order',
    LEVEL_ORDER.every((level) => radioAt(tree, 'A', level) !== undefined
      && radioAt(tree, 'B', level) !== undefined)
    && radios(tree).slice(0, 7).map((node) => node.props.value).join(',') === LEVEL_ORDER.join(','),
    radios(tree).slice(0, 7).map((node) => node.props.value))

  // 20. The selectable set is the MODEL's own declaration, and each refused row
  //     says why. deepseek-v4 declares off/low/high/max — the table agrees — so
  //     minimal/medium/xhigh are refused; qwen3.8-flash declares low/high/max
  //     while the table says off/low/medium/xhigh, and the declaration wins.
  check('a level the model does not declare is not selectable',
    radioAt(tree, 'A', 'minimal').props.disabled === true
    && radioAt(tree, 'A', 'medium').props.disabled === true
    && radioAt(tree, 'A', 'xhigh').props.disabled === true
    && radioAt(tree, 'A', 'off').props.disabled === false
    && radioAt(tree, 'A', 'low').props.disabled === false
    && radioAt(tree, 'A', 'high').props.disabled === false
    && radioAt(tree, 'A', 'max').props.disabled === false,
    LEVEL_ORDER.map((level) => [level, radioAt(tree, 'A', level).props.disabled]))
  check('a refused row carries a visible reason',
    rowText(panels[0], 'minimal').includes('not declared')
    && rowText(panels[0], 'low').includes('not declared') === false,
    { minimal: rowText(panels[0], 'minimal'), low: rowText(panels[0], 'low') })
  check('the model declaration decides, not the knowledge base',
    radioAt(tree, 'B', 'xhigh').props.disabled === true
    && radioAt(tree, 'B', 'medium').props.disabled === true
    && radioAt(tree, 'B', 'off').props.disabled === true
    && radioAt(tree, 'B', 'high').props.disabled === false
    && radioAt(tree, 'B', 'max').props.disabled === false,
    LEVEL_ORDER.map((level) => [level, radioAt(tree, 'B', level).props.disabled]))
  check('the disagreement between the table and the model is stated',
    panelText(panels[1]).includes('knowledge base: off/low/medium/xhigh')
    && panelText(panels[1]).includes('model declares: low/high/max'),
    panelText(panels[1]))

  // 21. The value column is the table's string, read-only. It is text, not an
  //     input: this card does not edit the model's declaration.
  check('the value column shows the table\'s string for each level',
    rowText(panels[0], 'off').includes('none')
    && rowText(panels[0], 'low').includes('low')
    && rowText(panels[0], 'high').includes('high')
    && rowText(panels[0], 'max').includes('max'),
    LEVEL_ORDER.map((level) => rowText(panels[0], level)))
  check('a level the table does not carry says so instead of inventing a value',
    rowText(panels[1], 'high').includes('not in the knowledge base')
    && rowText(panels[1], 'xhigh').includes('xhigh'),
    { high: rowText(panels[1], 'high'), xhigh: rowText(panels[1], 'xhigh') })
  check('no text input was added for the value column',
    numberInputs(tree).length === 1 && inputs(tree).length === 15,
    { numberInputs: numberInputs(tree).length, inputs: inputs(tree).length })

  // 22. No selection is the default state, and the panel says what that means.
  check('the at-rest panel says nothing is sent',
    radioAt(tree, 'A', 'high').props.checked === false
    && radios(tree).every((node) => node.props.checked === false)
    && panelText(panels[0]).includes('Nothing selected'),
    panelText(panels[0]).slice(0, 240))

  // 23. One level per seat: ticking a row writes exactly that seat's field, with
  //     the level id the LLM layer accepts — not the table's wire string.
  mutations.length = 0
  conflicts.length = 0
  radioAt(tree, 'A', 'max').props.onChange({ target: { checked: true } })
  await flush()
  tree = await renderSettled()
  check('ticking a level writes only that seat\'s effort field',
    mutations.length === 1 && mutations[0].ops.length === 1
    && JSON.stringify(mutations[0].ops) === asSet(['reviewAEffort', 'max']),
    mutations)
  check('a landed selection reports saved', statusText(tree) === 'Saved', statusText(tree))
  check('the selected row is the only checked one in its seat',
    radioAt(tree, 'A', 'max').props.checked === true
    && radios(tree).filter((node) => node.props.checked === true).length === 1,
    radios(tree).filter((node) => node.props.checked === true).map((node) => node.props.value))
  check('the panel states the value it will send',
    panelText(effortPanels(tree)[0]).includes('agentOptions.reasoningEffort = max'),
    panelText(effortPanels(tree)[0]).slice(0, 240))

  // 24. A second seat keeps its own selection: the two panels are independent.
  mutations.length = 0
  radioAt(tree, 'B', 'low').props.onChange({ target: { checked: true } })
  await flush()
  tree = await renderSettled()
  check('the other seat writes its own field',
    mutations.length === 1
    && JSON.stringify(mutations[0].ops) === asSet(['reviewBEffort', 'low']),
    mutations)
  check('both seats hold their own selection',
    radioAt(tree, 'A', 'max').props.checked === true && radioAt(tree, 'B', 'low').props.checked === true,
    radios(tree).filter((node) => node.props.checked === true).map((node) => node.props.value))

  // 25. Clearing is the no-selection path, and it says so: the affordance
  //     mirrors the reference editor's 清除声明, and what it clears here is the
  //     seat's choice rather than a model declaration.
  mutations.length = 0
  const clearA = collect(effortPanels(tree)[0], 'button').find((node) => textOf(node.children) === 'Clear selection')
  check('the panel offers a clear-selection affordance', clearA !== undefined, panelText(effortPanels(tree)[0]))
  clearA.props.onClick()
  await flush()
  tree = await renderSettled()
  check('clearing writes the empty selection',
    mutations.length === 1 && JSON.stringify(mutations[0].ops) === asSet(['reviewAEffort', '']),
    mutations)
  check('the cleared panel says nothing is sent',
    radioAt(tree, 'A', 'max').props.checked === false
    && panelText(effortPanels(tree)[0]).includes('Nothing selected'),
    panelText(effortPanels(tree)[0]).slice(0, 240))

  // 26. 自动适配 takes the table's default level when the model declares it:
  //     deepseek-v4's entry defaults to high, and the route declares high.
  mutations.length = 0
  snapshot = ready(VALUE('deepseek', 'deepseek-v4', 'tt', 'qwen3.8-flash'), 71)
  tree = await mount()
  const adaptA = collect(effortPanels(tree)[0], 'button').find((node) => textOf(node.children) === 'Auto-adapt')
  check('the panel offers the auto-adapt prefill', adaptA !== undefined && adaptA.props.disabled === false,
    adaptA === undefined ? 'no button' : adaptA.props.disabled)
  adaptA.props.onClick()
  await flush()
  tree = await renderSettled()
  check('auto-adapt writes the table\'s default level',
    mutations.length === 1 && JSON.stringify(mutations[0].ops) === asSet(['reviewAEffort', 'high']),
    mutations)
  check('auto-adapt says which level it took and from where',
    panelText(effortPanels(tree)[0]).includes("knowledge base's default level high"),
    panelText(effortPanels(tree)[0]).slice(0, 300))

  // 27. 自动适配 refuses a default the model does not declare, rather than
  //     writing a level the adapter would reject: qwen3.8-flash's table entry
  //     defaults to xhigh, and this route declares only low/high/max.
  mutations.length = 0
  tree = await mount()
  const adaptB = collect(effortPanels(tree)[1], 'button').find((node) => textOf(node.children) === 'Auto-adapt')
  adaptB.props.onClick()
  await flush()
  tree = await renderSettled()
  check('auto-adapt refuses a default the model does not declare',
    mutations.length === 0 && panelText(effortPanels(tree)[1]).includes('is not declared by this model'),
    { writes: mutations.length, panel: panelText(effortPanels(tree)[1]).slice(0, 300) })

  // 28. A stored selection the route does not declare is reported rather than
  //     rendered as selected, and never silently rewritten.
  mutations.length = 0
  snapshot = ready(VALUE('tt', 'qwen3.8-flash', '', '', TIMEOUT_DEFAULT, 'xhigh'), 72)
  tree = await mount()
  check('a stored level the model does not declare is not shown as selected',
    radioAt(tree, 'A', 'xhigh').props.checked === false
    && radios(tree).every((node) => node.props.checked === false)
    && panelText(effortPanels(tree)[0]).includes('is not declared by this model'),
    panelText(effortPanels(tree)[0]).slice(0, 300))
  check('the stale selection is left in the settings rather than rewritten',
    mutations.length === 0, mutations)

  // 29. With no model chosen the rows cannot be picked at all: the effort is
  //     carried on the configured route's agent options, and there is no route.
  snapshot = ready(VALUE('', '', 'tt', 'qwen3.8-flash'), 73)
  tree = await mount()
  const noRoute = effortPanels(tree)[0]
  check('a seat with no model has no selectable level',
    radios(tree).slice(0, 7).every((node) => node.props.disabled === true)
    && rowText(noRoute, 'low').includes('no model'),
    LEVEL_ORDER.map((level) => rowText(noRoute, level)))
  check('auto-adapt is unavailable without a model',
    collect(noRoute, 'button').find((node) => textOf(node.children) === 'Auto-adapt').props.disabled === true,
    panelText(noRoute).slice(0, 200))

  // 30. A write the Host refuses is a failure for the effort field too, and the
  //     stored selection stands: the same read-back contract as everywhere else.
  writeOutcome = 'refuse'
  snapshot = ready(VALUE('deepseek', 'deepseek-v4', '', '', TIMEOUT_DEFAULT, 'low'), 74)
  tree = await mount()
  radioAt(tree, 'A', 'max').props.onChange({ target: { checked: true } })
  await flush()
  tree = await renderSettled()
  check('a refused effort write reports failure', statusText(tree) === 'Save failed', statusText(tree))
  check('a refused effort write leaves the stored selection standing',
    radioAt(tree, 'A', 'low').props.checked === true && radioAt(tree, 'A', 'max').props.checked === false,
    radios(tree).filter((node) => node.props.checked === true).map((node) => node.props.value))
  writeOutcome = 'accept'

  // 31. What the seat stores is the level ID, not the table's provider wire
  //     string. The two differ for deepseek-v4's off level: the table resolves
  //     `off: "none"`, because "none" is what that provider's profile is
  //     configured to put on the wire, while the value the LLM layer accepts as
  //     `agentOptions.reasoningEffort` is the id `off`. Storing the wire string
  //     here would store a level no route declares.
  mutations.length = 0
  snapshot = ready(VALUE('deepseek', 'deepseek-v4', 'tt', 'qwen3.8-flash'), 75)
  tree = await mount()
  check('the value column and the id are different strings for this level',
    rowText(effortPanels(tree)[0], 'off').includes('none')
    && radioAt(tree, 'A', 'off').props.value === 'off',
    { row: rowText(effortPanels(tree)[0], 'off'), id: radioAt(tree, 'A', 'off').props.value })
  radioAt(tree, 'A', 'off').props.onChange({ target: { checked: true } })
  await flush()
  tree = await renderSettled()
  check('a selected level is stored as its id, never as the table\'s wire string',
    mutations.length === 1 && JSON.stringify(mutations[0].ops) === asSet(['reviewAEffort', 'off']),
    mutations)

  // 32. The table and the matcher are the card's data, so the harness reaches
  //     them directly as well: the two live routes this task was verified
  //     against resolve to the entries the report names.
  check('the embedded table resolves the live routes',
    bundle.effortKnowledge.entries.length === 60
    && bundle.matchEffortKnowledge('z-ai/glm-5.3-free', undefined).id === 'glm-5-3'
    && bundle.matchEffortKnowledge('qwen3.8-flash', undefined).id === 'qwen-3-8'
    && bundle.effortKnowledge.levels.join(',') === LEVEL_ORDER.join(','),
    {
      entries: bundle.effortKnowledge.entries.length,
      glm: bundle.matchEffortKnowledge('z-ai/glm-5.3-free', undefined).id,
      qwen: bundle.matchEffortKnowledge('qwen3.8-flash', undefined).id,
    })
  check('the copied entries keep their upstream notes',
    bundle.effortKnowledge.entries.every((entry) => typeof entry.note === 'string' && entry.note.length > 0)
    && bundle.matchEffortKnowledge('z-ai/glm-5.3-free', undefined).note.includes('GLM-5.3')
    && bundle.effortKnowledge.upstream.version === '0.3.9'
    && bundle.effortKnowledge.upstream.license === 'MIT',
    bundle.effortKnowledge.entries.filter((entry) => typeof entry.note !== 'string').map((entry) => entry.id))

  // 30. A namespace that stops being served drops the card: the registration
  //     follows the Host, so a plugin the user switched off leaves no card
  //     editing a namespace nothing serves.
  describeAnswer = { ok: true, value: { namespaces: [] } }
  for (const handler of documentUpdatedHandlers) handler()
  await flush()
  check('a vanished namespace drops the card',
    registered('plugins.item') === null && registered('settings.section') === null
      && unregistered === 2,
    { unregistered })

  console.log(failures === 0 ? 'HARNESS: ALL PASS' : `HARNESS: ${failures} FAILURE(S)`)
  process.exitCode = failures === 0 ? 0 : 1
}

main().catch((error) => {
  console.error(error)
  process.exitCode = 2
})
