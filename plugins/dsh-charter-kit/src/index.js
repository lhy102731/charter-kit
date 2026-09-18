import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'
import z from '@deepseek-ai/schemastery'
import { defineTool } from '@deepseek-ai/dsh-tools'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const SKILL_DIR = join(ROOT, 'skills', 'charter-workflow')
const SKILL_FILE = join(SKILL_DIR, 'SKILL.md')

/** Settings namespace keying the Review A/B model card. Its key IS the card key. */
export const REVIEW_SETTINGS_NAMESPACE = 'charter-kit-review'

/** Settings field holding one review attempt's budget, in whole seconds. */
export const REVIEW_TIMEOUT_FIELD = 'reviewTimeoutSeconds'

/**
 * Bounds on one review ATTEMPT's budget, in whole seconds.
 *
 * What the budget bounds is our own patience, nothing else. A review is a
 * multi-turn child: it reads the leaf contract and the spec, looks at the
 * candidate diff, and writes. Its cost is turns times tokens, so the only clock
 * that can end it honestly is one sized for a working review on a slow seat.
 *
 * 270 was measured and found too small. A real project lost a Review B to two
 * attempts that both died on THIS clock at 270 s — the configured route and the
 * session-model rerun, 540 021 ms together, with no host mechanism intervening:
 * one seat needed 130 s for a compact brief, and the other spent 85 s and 5 702
 * reasoning tokens on a SINGLE completion. A multi-turn review cannot fit in
 * 270 s, and no host ceiling on total call duration exists to fit under: the
 * measured mechanism is the adapter's PER-STREAM IDLE watchdog
 * (`DEFAULT_STREAM_IDLE_TIMEOUT_MS = 300_000` in
 * `packages/llm/llm-pi-ai/src/config.ts`, whose `TIMEOUT` is retryable per
 * `packages/llm/llm/src/retry-policy.ts`). It bounds SILENCE, not duration, so
 * a review that keeps streaming is not bounded by it at all — `MAX < 300`
 * therefore protected nothing and only guaranteed that working reviews were
 * killed before the stall detector could ever act.
 *
 * The replacement numbers are a deliberate OVER-correction, and that is the
 * point: erring low is the defect being fixed, so the first instalment errs
 * high. The calibration recorded in `docs/superpowers/calibration/` replaces
 * them with measured values; until it lands they are provisional.
 */
const MIN_REVIEW_TIMEOUT_SECONDS = 30 // provisional: floor only, measured by nothing
const MAX_REVIEW_TIMEOUT_SECONDS = 1800 // provisional: deliberate over-correction
const DEFAULT_REVIEW_TIMEOUT_SECONDS = 600 // provisional: a default someone can leave alone

/**
 * Slack, in seconds, between the worst case the clamp above can express and the
 * deadline this tool declares.
 *
 * It has to cover what an attempt spends BESIDE its own timer: the teardown
 * grace below, plus dispatch and rendering. Two attempts at `MAX + GRACE` are
 * what the derived deadline below has to clear; this is the remainder of that
 * slack. Nothing here is dimensioned against a host ceiling on total duration —
 * see the constants above for why that premise was retracted.
 */
const REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS = 30

/**
 * How long one teardown may take before this tool stops waiting for it.
 *
 * `dispose()` is the provider's promise to reach quiescence, and nothing
 * enforces it. It is awaited only inside this window, because the harness's own
 * tool deadline is signal-only — it awaits the tool's promise rather than racing
 * or abandoning it — so an un-settling `dispose()` would otherwise hold the call
 * open past every number here and leave nothing to end it.
 */
const REVIEW_TEARDOWN_GRACE_SECONDS = 10

/**
 * The cooperative tool-call deadline this tool declares to the harness.
 *
 * The setting is dynamic while a declared `timeoutMs` is fixed at registration,
 * so this is DERIVED from the worst case the clamp can express — never written
 * as a second literal that could drift from it. Under per-attempt semantics that
 * worst case is TWO attempts: the configured route, then the session-model
 * rerun, each at `MAX`, plus the margin. Raising `MAX` without re-deriving this
 * would let the harness's own deadline fire first and return an opaque
 * `TOOL_TIMEOUT` — with nothing rendered — for a call that had not finished. The
 * assertion in `tests/test_dsh_review_tool.py` re-derives it from these
 * constants, so a constant edit that forgets this line fails rather than ships.
 */
const REVIEW_TOOL_TIMEOUT_MS = (MAX_REVIEW_TIMEOUT_SECONDS * 2 + REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS) * 1000

/** Empty provider or model means "inherit the calling session's model". */
const REVIEW_SETTINGS_SCHEMA = z.object({
  reviewAProvider: z.string().default(''),
  reviewAModel: z.string().default(''),
  reviewBProvider: z.string().default(''),
  reviewBModel: z.string().default(''),
  [REVIEW_TIMEOUT_FIELD]: z.number().default(DEFAULT_REVIEW_TIMEOUT_SECONDS),
  reviewAEffort: z.string().default(''),
  reviewBEffort: z.string().default(''),
})

/**
 * Composition entry for the review namespace: the base layer under the user's
 * stored overrides, and the value the settings provider restores should it
 * detach. It is deliberately not a reader fallback — `installSection` binds the
 * reader synchronously, so this object is only ever reached through the
 * provider that owns the namespace.
 */
const REVIEW_SETTINGS_DEFAULTS = {
  reviewAProvider: '',
  reviewAModel: '',
  reviewBProvider: '',
  reviewBModel: '',
  [REVIEW_TIMEOUT_FIELD]: DEFAULT_REVIEW_TIMEOUT_SECONDS,
  reviewAEffort: '',
  reviewBEffort: '',
}

/**
 * The reasoning-effort levels a seat may select, in the order the card renders
 * them. The set and the order are the LLM layer's own (`THINKING_LEVELS` in the
 * pi-ai catalog, which is what an adapter validates a request against), and the
 * card's data module carries the same list under `levels` — a test compares the
 * two so a level added on one side cannot go missing on the other.
 */
const EFFORT_LEVELS = ['off', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max']

/** Settings field holding one seat's selected level; '' means none. */
const EFFORT_FIELDS = { A: 'reviewAEffort', B: 'reviewBEffort' }

/**
 * How long the route-capability lookup may take before this tool treats the LLM
 * runtime as unusable.
 *
 * It is a local capability read, not a dispatch, so anything approaching this
 * window is a broken service rather than a slow one — and it is bounded because
 * nothing else would bound it: the wait sits before the attempt that owns the
 * only timer this tool arms, so an un-settling lookup would spend the whole
 * declared budget and leave the review unrun.
 */
const LLM_CAPABILITY_TIMEOUT_MS = 5000

/**
 * Read one review route out of the settings value.
 * @param value - effective settings value.
 * @param kind - review kind, 'A' or 'B'.
 * @returns the route, or null when the review inherits the current model.
 */
function reviewRoute(value, kind) {
  const provider = value[kind === 'B' ? 'reviewBProvider' : 'reviewAProvider']
  const model = value[kind === 'B' ? 'reviewBModel' : 'reviewAModel']
  return provider === '' || model === '' ? null : { provider, model }
}

/**
 * Read one seat's selected reasoning-effort level out of the settings value.
 *
 * Only a level this adapter can put on the wire is a selection: a hand-edited
 * settings file, or a value written by a newer card, reads as "nothing
 * selected", which is the same thing the card renders and the same thing that
 * leaves the child's agent options untouched.
 * @param value - effective settings value.
 * @param kind - review kind, 'A' or 'B'.
 * @returns the level id, or null when no usable level is stored.
 */
function reviewEffort(value, kind) {
  const raw = value[EFFORT_FIELDS[kind === 'B' ? 'B' : 'A']]
  return typeof raw === 'string' && EFFORT_LEVELS.includes(raw) ? raw : null
}

/**
 * Decide which level may be attached to one child's agent options.
 *
 * A route that declares no reasoning at all rejects ANY effort with
 * `UNSUPPORTED_REASONING_EFFORT`, and a route that omits the chosen level
 * rejects that one, so both cases drop the selection instead of turning it into
 * a guaranteed failure. When the LLM runtime could not be reached the selection
 * is kept: the card gated it against the same catalogue the host would consult,
 * and dropping a level the user explicitly chose is the silent downgrade this
 * tool must not perform.
 * @param wanted - the stored selection, or null.
 * @param support - `{available, ids}` from the LLM runtime.
 * @returns the level to send, or null to send none.
 */
function appliedEffort(wanted, support) {
  if (wanted === null) return null
  if (support.available && (support.ids === null || !support.ids.includes(wanted))) return null
  return wanted
}

/**
 * Read one review attempt's budget out of the settings value.
 *
 * Clamped here rather than in the card, because this is the only place that can
 * guarantee the bound: a card version that predates the field, a hand-edited
 * settings file, and a stored value of the wrong type all reach this function,
 * and none of them may be able to abort every review or to hold a reviewer seat
 * for longer than this tool is willing to state.
 * @param value - effective settings value.
 * @returns whole seconds within [MIN, MAX]; the default for anything unusable.
 */
function reviewTimeoutSeconds(value) {
  const raw = value[REVIEW_TIMEOUT_FIELD]
  const seconds = typeof raw === 'number' && Number.isFinite(raw)
    ? Math.floor(raw)
    : DEFAULT_REVIEW_TIMEOUT_SECONDS
  return Math.min(MAX_REVIEW_TIMEOUT_SECONDS, Math.max(MIN_REVIEW_TIMEOUT_SECONDS, seconds))
}

/**
 * Pick the delegation provider: the deployment's spawn provider, else a sole one.
 * @param ctx - host plugin context.
 * @returns provider name, or undefined when the choice is ambiguous or empty.
 */
function pickSubagentProvider(ctx) {
  const names = ctx.subagents.list()
  if (names.includes('spawn')) return 'spawn'
  return names.length === 1 ? names[0] : undefined
}

/**
 * Flatten one settled child result into its assistant text.
 * @param result - settled SubagentResult.
 * @returns trimmed text of every text block.
 */
function outputText(result) {
  return (result.output ?? [])
    .filter(part => part.type === 'text')
    .map(part => part.text)
    .join('')
    .trim()
}

/**
 * The stop reason a child reports after finishing its turn normally. Every
 * other value means the run ended without a review. A child that fails without
 * throwing resolves with one of those values, so the caller has to read this
 * field: the result promise does not reject on a child-level failure.
 * @see SubagentStopReasonMap in the DSH subagent types.
 */
const COMPLETED_STOP_REASON = 'completed'

/**
 * Classify one settled child run as a review or a failure.
 *
 * The timeout case is NOT decided here: an expired budget races the settled run
 * in `runReview`, which reports it as `kind: 'timeout'`.
 * @param result - settled SubagentResult.
 * @param elapsedMs - how long the attempt took, kept for the failure record.
 * @returns the attempt: `kind` is null when it reviewed, else 'error' for a
 *   settled non-completion and 'empty' for a completed run with no text.
 */
function classifyRun(result, elapsedMs) {
  const review = outputText(result)
  const stopReason = result.stopReason
  const diagnostic = typeof result.diagnostic === 'string' ? result.diagnostic.trim() : ''
  const detail = diagnostic === '' ? '' : `: ${diagnostic}`
  if (stopReason !== COMPLETED_STOP_REASON) {
    return {
      review,
      kind: 'error',
      elapsedMs,
      detail: `child stopped with stopReason "${stopReason}"${detail}`,
    }
  }
  if (review === '') {
    return { review, kind: 'empty', elapsedMs, detail: `child completed with an empty review${detail}` }
  }
  return { review, kind: null, elapsedMs, detail: '' }
}

function parseFrontmatter(text) {
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n?([\s\S]*)$/.exec(text)
  if (!match) return { description: 'Charter Kit development workflow', body: text.trimEnd() + '\n' }
  const meta = {}
  for (const line of match[1].split(/\r?\n/)) {
    const index = line.indexOf(':')
    if (index === -1) continue
    const key = line.slice(0, index).trim()
    let value = line.slice(index + 1).trim()
    if ((value.startsWith('"') && value.endsWith('"')) || (value.startsWith("'") && value.endsWith("'"))) {
      value = value.slice(1, -1)
    }
    meta[key] = value
  }
  return {
    description: meta.description || 'Charter Kit development workflow',
    whenToUse: meta['when-to-use'] || meta.whenToUse,
    body: (match[2] || '').trimEnd() + '\n',
  }
}

export const name = 'dsh-charter-kit'
// Registering the Skill is unconditional. A plugin whose fiber waits on a
// missing injected service never runs at all, so naming `tools`, `settings`, or
// `subagents` here would withhold `charter-workflow` from every deployment that
// lacks one of them — a host without those services has to behave exactly as it
// did before this feature. The tool half waits for its own services in the
// optional scope inside `apply` instead.
export const inject = ['skills']

export function apply(ctx) {
  const skill = parseFrontmatter(readFileSync(SKILL_FILE, 'utf8'))

  // No handler-style slash command is registered. A typed line such as
  // `/charter-workflow <requirement>` therefore reaches the model as an
  // ordinary user message (matching Codex behavior); the model loads the
  // `charter-workflow` skill below and actually starts the workflow.
  ctx.effect(() => ctx.skills.register({
    name: 'charter-workflow',
    description: skill.description,
    ...(skill.whenToUse ? { whenToUse: skill.whenToUse } : {}),
    source: 'runtime',
    provider: 'dsh-charter-kit',
    resourceBase: { kind: 'directory', path: SKILL_DIR },
    content: skill.body,
  }), 'charter-kit: skill')

  // The settings namespace and the review tool need three further services.
  // Registering them here, behind the platform's optional idiom, means a host
  // that provides those services gets both exactly as before while a host that
  // provides none of them still gets the Skill above.
  ctx.inject(['tools', 'settings', 'subagents'], (scope) => {
    // `installSection` calls `setSource` synchronously, so this reader is bound
    // before the tool registered below can possibly execute.
    let readReviewSettings
    scope.settings.installSection(
      ctx,
      REVIEW_SETTINGS_NAMESPACE,
      REVIEW_SETTINGS_SCHEMA,
      REVIEW_SETTINGS_DEFAULTS,
      {
        setSource: (source) => { readReviewSettings = source },
        validate: () => {},
        onChange: () => {},
      },
    )

    /**
     * The LLM runtime, reached only to ask what one route declares.
     *
     * It waits in its OWN optional scope rather than beside the three services
     * above: naming `llm` in that list would withhold this whole tool — and the
     * review it exists for — from a host that has no LLM runtime, while the
     * required behaviour there is to degrade. Without it the tool still runs,
     * still sends the level the user selected, and reports no level at all
     * rather than one it cannot check.
     */
    let readRouteEffort
    scope.inject(['llm'], (llmScope) => {
      const llm = llmScope.llm
      if (llm === undefined || typeof llm.resolveModelInfo !== 'function') return
      readRouteEffort = (route, signal) => llm.resolveModelInfo(route.provider, route.model, signal)
    })

    scope.tools.register(defineTool({
      name: 'charter_review',
      description: 'Run one context-free Charter Kit review with the model configured for that review kind. '
        + 'Use kind "A" for every leaf\'s contract and implementation coverage review, and kind "B" for the '
        + 'adversarial review required by a hit RVB trigger. The reviewer receives only the brief you pass — '
        + 'never the session history — so the self-contained brief is the whole input: the leaf contract, '
        + 'the spec, and the candidate diff, all of it in the call. A review is a MULTI-TURN agent run — the '
        + 'child reads files, runs `git diff`, then writes — and at a slow seat\'s throughput turns x '
        + 'tokens is the whole '
        + 'cost, so a child that has to discover the diff itself pays for that discovery in turns. For the '
        + 'same reason a slow seat belongs on a NARROW, RISK-TRIGGERED review rather than on every leaf. '
        + 'The returned model names the route it used, or `inherited` when it followed the session model. '
        + 'Each seat also carries a reasoning-effort selection in the model card; when one is set and the '
        + 'route declares it, the child is started with that level as `agentOptions.reasoningEffort`, and the '
        + 'result reports it as `effort` beside `model` — `"default"` when no level was sent, meaning the '
        + 'provider default applies and this host cannot know it, and no level at all when the LLM runtime is '
        + 'unavailable to check the route. The configured timeout is the budget for ONE ATTEMPT, not for the '
        + 'call; a review makes at most TWO attempts — the configured route, then the session model. A '
        + 'genuinely silent provider stream is cut by the host\'s own per-stream idle timeout, which this '
        + 'value does not substitute for and is not sized against. Any way the configured route fails to '
        + 'produce a review — a settled failure, an empty result, or that timeout — reruns the same brief on '
        + 'the session model and reports `outcome: "fallback"`, so a configured route that cannot deliver '
        + 'still produces a review. Dispatch, the child\'s result, and teardown are each raced against the '
        + 'attempt\'s deadline, so a provider that never publishes a run or never releases one cannot hold '
        + 'the call open. An empty `review` is never returned as a success shape: it comes back only as an '
        + 'explicit `outcome: "unavailable"` carrying a reason — when no reviewer could be started at all, '
        + 'when the session-model attempt itself failed, or when the rerun failed too.',
      // See REVIEW_TOOL_TIMEOUT_MS: the harness's cooperative deadline must sit
      // outside this tool's own worst case, or it would preempt the fallback.
      timeoutMs: REVIEW_TOOL_TIMEOUT_MS,
      parameters: {
        kind: {
          type: 'string',
          required: true,
          // The declared enum is the gate. Review B is the required review for
          // security, public-API, and irreversible changes, so a caller that
          // asked for B has to be refused rather than handed a coverage review.
          enum: ['A', 'B'],
          description: 'Review kind: "A" for coverage review, "B" for the RVB-triggered adversarial review.',
        },
        brief: {
          type: 'string',
          required: true,
          description: 'Self-contained review brief: the leaf contract, the spec, and the candidate diff, '
            + 'pasted in full. The reviewer sees nothing else and never the session history, so anything '
            + 'missing here is missing from the review. Paste the diff rather than leaving the child to '
            + 'discover it: a review is a multi-turn run and each extra turn it must spend finding the '
            + 'candidate diff is cost the brief could have paid once.',
        },
        route: {
          type: 'string',
          // The enum is the gate here too: an unrecognized value would silently
          // run the configured route the caller was trying to skip.
          enum: ['configured', 'session'],
          description: 'Which route to run. "configured" (default) tries the model set for this kind and '
            + 'falls back to the session model if it produces no review. "session" skips the configured '
            + 'route and runs the session model directly: use it for later reviews of a kind whose '
            + 'configured route has already failed in this session, so the call does not re-pay the '
            + 'timeout. It still reports `outcome: "fallback"`, because the configured route was not used.',
        },
      },
      output: {
        schema: {
          type: 'object',
          additionalProperties: false,
          properties: {
            outcome: { type: 'string', required: true },
            model: { type: 'string', required: true },
            // Optional on purpose: a host whose LLM runtime is unavailable
            // reports no level rather than a level it cannot check, so the
            // field's absence is a state of its own and not a missing value.
            effort: { type: 'string' },
            routeFallbackReason: { type: 'string' },
            review: { type: 'string', required: true },
          },
        },
        render: (_args, value) => [{ type: 'text', text: JSON.stringify(value) }],
      },
      async execute(args, exec) {
        // A blank brief is a malformed call, not a review. Spawning a child with
        // an empty prompt returns text that reads like a review of nothing, and
        // a real project reported exactly that as a normal review. Refuse it
        // before any child exists, so nothing here can report `reviewed`.
        const brief = typeof args.brief === 'string' ? args.brief : ''
        if (brief.trim() === '') {
          throw new Error(
            'charter_review: refusing an empty brief. Pass the leaf contract, the spec, and the '
            + 'candidate diff; no reviewer was started and no review was produced.',
          )
        }
        // The declared enums above refuse any other value before this point, so
        // these defaults only cover a value that never reached that validation.
        const kind = args.kind === 'B' ? 'B' : 'A'
        const wantSessionRoute = args.route === 'session'
        // Read at execution time, never memoized at registration: the settings
        // provider binds this reader to a live thunk, so a card edit applies to
        // the very next call with no reload.
        const settings = readReviewSettings()
        const configured = reviewRoute(settings, kind)
        const budgetSeconds = reviewTimeoutSeconds(settings)
        const budgetMs = budgetSeconds * 1000
        // The seat's reasoning-effort selection, and the level this call may
        // actually attach to the child's agent options. `effortApplied` is
        // rewritten at every dispatch, so the result reports the effort of the
        // run that produced the review rather than of an earlier attempt.
        const wantedEffort = reviewEffort(settings, kind)
        let effortApplied = null
        // When the call started, so every await below — dispatch, the child's
        // result, and teardown — can be bounded by what is left of the deadline
        // this tool declares. Nothing else bounds them: the harness's tool
        // deadline arms a signal and then awaits this tool's promise rather than
        // racing it, and the adapter's idle watchdog bounds silence rather than
        // duration, so a provider that never settles a call would hold the whole
        // call open with nothing rendered.
        const callDeadlineAt = Date.now() + REVIEW_TOOL_TIMEOUT_MS
        const callBudgetLeftMs = () => Math.max(0, callDeadlineAt - Date.now())
        const parent = exec.agent
        const providerName = pickSubagentProvider(scope)
        const prompt = [{ type: 'text', text: brief }]

        /** Read one throwable's message for a failure detail. */
        const messageOf = (error) => (error instanceof Error ? error.message : String(error))

        /**
         * Attach the effort this call may report, immediately after `model`, so
         * the pair reads together in the rendered result.
         *
         * The key is omitted entirely when the LLM runtime is unavailable: a
         * host that cannot ask what a route declares reports no level at all
         * rather than one it cannot stand behind, and "no level reported" is a
         * state the caller can see rather than an empty string it has to
         * interpret.
         */
        const withEffort = ({ outcome, model, ...rest }) => ({
          outcome,
          model,
          ...readRouteEffort === undefined ? {} : { effort: effortApplied ?? 'default' },
          ...rest,
        })

        /**
         * Ask the LLM runtime which effort ids one route declares.
         *
         * `ids: null` means the route declares no reasoning at all, which is a
         * different answer from "the runtime could not be reached": the first
         * rejects every effort, the second only means this host cannot check.
         * Both the lookup and the timeout are the only things here that can
         * answer, so an error, a rejection, or a slow service all land on
         * `available: false` rather than on a throw out of this tool.
         * @param route - the configured provider/model route.
         * @returns `{available, ids}`.
         */
        const routeEffortSupport = async (route) => {
          if (readRouteEffort === undefined) return { available: false, ids: null }
          let timer
          try {
            const lookup = readRouteEffort(route, exec.signal).then(
              (info) => ({ info }),
              () => ({ info: undefined }),
            )
            const settled = await Promise.race([
              lookup,
              new Promise((resolve) => { timer = setTimeout(() => resolve(null), LLM_CAPABILITY_TIMEOUT_MS) }),
            ])
            if (settled === null || typeof settled.info !== 'object' || settled.info === null) {
              return { available: false, ids: null }
            }
            const reasoning = settled.info.reasoning
            if (reasoning === undefined || reasoning === null || !Array.isArray(reasoning.efforts)) {
              return { available: true, ids: null }
            }
            return { available: true, ids: reasoning.efforts.map((effort) => effort.id) }
          } finally {
            clearTimeout(timer)
          }
        }

        /**
         * Render one failed attempt as the record that makes it actionable: the
         * route that was tried, what happened to it, and how long it took.
         * @param label - the route, or a name for the session-model rerun.
         * @param attempt - a classified failure.
         * @returns a one-line reason.
         */
        const failureReason = (label, attempt) => {
          const seconds = `${(attempt.elapsedMs / 1000).toFixed(1)}s`
          if (attempt.kind === 'timeout') {
            return `${label} timed out after ${seconds} (budget ${budgetSeconds}s)`
          }
          if (attempt.kind === 'empty') {
            return `${label} returned an empty review after ${seconds}`
          }
          return `${label} failed after ${seconds}: ${attempt.detail}`
        }

        /** One failed attempt, in the shape every call site returns. */
        const failed = (kindOfFailure, elapsedMs, detail) => ({
          review: '',
          kind: kindOfFailure,
          elapsedMs,
          detail,
        })

        /**
         * Run one review attempt through the host's delegation path.
         *
         * Every call site goes through this one wrapper, so dispatch, the
         * per-attempt deadline, classification, disposal, and error mapping
         * exist once: an attempt that cannot be dispatched, cannot settle,
         * exceeds its budget, or cannot be released is an attempt this returns,
         * never a throw `execute` would leak as a raw tool rejection.
         * @param agentOptions - the child's route, or null to inherit.
         * @returns the classified attempt; `kind` is null when it reviewed.
         */
        const runReview = async (agentOptions) => {
          const startedAt = Date.now()
          const elapsedMs = () => Date.now() - startedAt
          // `exec.signal` carries the harness's own cancellation (a caller
          // cancel, or the cooperative deadline declared above). Composing it
          // with a controller this tool owns is what lets this tool's budget
          // abort the child on its own terms.
          const controller = new AbortController()
          const forwardAbort = () => { controller.abort() }
          if (exec.signal.aborted) forwardAbort()
          else exec.signal.addEventListener('abort', forwardAbort, { once: true })
          let expired = false
          let reachDeadline
          const deadline = new Promise((resolve) => { reachDeadline = resolve })
          // The one timer this tool arms. It is disarmed in the same `finally`
          // that releases the child, so no attempt leaves a timer behind.
          const timer = setTimeout(() => {
            expired = true
            controller.abort()
            reachDeadline()
          }, budgetMs)
          const timedOut = () => failed('timeout', elapsedMs(), `no review within the ${budgetSeconds}s budget`)

          /**
           * Stop waiting for a settled-but-unreleased child.
           *
           * The run has already settled or been aborted by the time this is
           * called, so a provider that does not reach quiescence inside the
           * window is left to finish on its own: waiting longer would spend the
           * rest of the call budget on teardown and leave nothing for the
           * session-model rerun that is the whole point of this tool.
           * @param run - the published run to release.
           * @returns the disposal failure, or null when it released in time.
           */
          const releaseRun = async (run) => {
            const window = Math.min(callBudgetLeftMs(), REVIEW_TEARDOWN_GRACE_SECONDS * 1000)
            let timer
            try {
              const releasing = run.dispose().then(
                () => null,
                (error) => `child disposal failed: ${messageOf(error)}`,
              )
              const detail = await Promise.race([
                releasing,
                new Promise((resolve) => { timer = setTimeout(() => resolve(null), window) }),
              ])
              return detail === null ? null : failed('error', elapsedMs(), detail)
            } finally {
              clearTimeout(timer)
            }
          }

          try {
            // Dispatch is raced against the attempt's own deadline too: a
            // provider that never publishes a run would otherwise hold the call
            // open past every budget this tool declares. Both arms are handled,
            // so this promise never rejects.
            const dispatch = scope.subagents.start(providerName, {
              prompt,
              parent,
              signal: controller.signal,
              ...(agentOptions === null ? {} : { agentOptions }),
            }).then(
              (value) => ({ run: value }),
              (error) => ({ error }),
            )
            const published = await Promise.race([dispatch, deadline.then(() => null)])
            if (published === null) {
              // The deadline won, but `start` may still publish a run after it.
              // Release that one if it ever arrives, so a late publication is
              // not a child nobody owns.
              void dispatch.then((late) => {
                if ('run' in late) void releaseRun(late.run)
              })
              return timedOut()
            }
            if ('error' in published) {
              // A dispatch that rejected because this tool's own deadline
              // aborted it is a timeout, not a provider error.
              return expired && !exec.signal.aborted
                ? failed('timeout', elapsedMs(), `no child was published within the ${budgetSeconds}s budget`)
                : failed('error', elapsedMs(), messageOf(published.error))
            }
            const run = published.run
            // Both arms are observed. A deadline that wins the race below must
            // not leave `run.result` as an unhandled rejection when it settles
            // afterwards.
            const settled = run.result.then(
              (value) => ({ value }),
              (error) => ({ error }),
            )
            let attempt
            let disposal
            try {
              const outcome = await Promise.race([settled, deadline.then(() => null)])
              if (outcome === null) {
                attempt = timedOut()
              } else if ('error' in outcome) {
                attempt = failed('error', elapsedMs(), messageOf(outcome.error))
              } else {
                attempt = classifyRun(outcome.value, elapsedMs())
              }
            } finally {
              disposal = await releaseRun(run)
            }
            // A teardown that FAILED outweighs the attempt it could not release.
            // A teardown that merely ran out of its window does not: this tool
            // has a result in hand, and discarding it for a slow release would
            // throw away the very thing the call exists to produce.
            return disposal ?? attempt
          } finally {
            clearTimeout(timer)
            exec.signal.removeEventListener('abort', forwardAbort)
          }
        }

        /**
         * Dispatch one attempt with the child options it should carry, and
         * record which effort those options asked for.
         *
         * The record is what the result reports, so it is written here — at the
         * dispatch — rather than once per call: a call that tries a configured
         * route and then reruns on the session model must not report the level
         * the failed attempt carried for the review the session model produced.
         * @param options - the child's agent options, or null to inherit.
         * @param applied - the level those options carry, or null for none.
         * @returns the classified attempt.
         */
        const runWithEffort = async (options, applied) => {
          effortApplied = applied
          return runReview(options)
        }

        // A configured route that produced no review — a settled failure, an
        // empty result, or the timeout above — is re-run on the session model in
        // a fresh, context-free child. When that second run fails too there is no
        // review to report, so the tool says `unavailable` instead of returning a
        // success shape with empty text.
        const fallback = async (reason) => {
          const attempt = await runWithEffort(null, null)
          if (attempt.kind !== null) {
            return withEffort({
              outcome: 'unavailable',
              model: 'inherited',
              review: '',
              routeFallbackReason: `${reason}; the session-model rerun also failed: ${failureReason('the session model', attempt)}`,
            })
          }
          return withEffort({
            outcome: 'fallback',
            model: 'inherited',
            review: attempt.review,
            routeFallbackReason: reason,
          })
        }

        if (parent === undefined || providerName === undefined) {
          return withEffort({
            outcome: 'unavailable',
            model: 'inherited',
            review: '',
            routeFallbackReason: parent === undefined
              ? 'no calling agent'
              : 'no unambiguous subagent provider',
          })
        }

        const label = configured === null ? '' : `${configured.provider}/${configured.model}`

        // No configured route, or a caller that already recorded this route as
        // failed and asked for the session model: both run one session-model
        // child. Only the second is a degradation, and it is reported as one so
        // the leaf's evidence shows it without the caller having to remember.
        //
        // Neither carries a reasoning effort: the seat's selection configures
        // the route under it, and a run that inherits the session's model
        // inherits its reasoning setting too. That is also what keeps this path
        // — the no-route and the session-route path — byte-for-byte the call it
        // was before: no agent options are passed at all.
        if (configured === null || wantSessionRoute) {
          const attempt = await runWithEffort(null, null)
          if (attempt.kind !== null) {
            return withEffort({
              outcome: 'unavailable',
              model: 'inherited',
              review: '',
              routeFallbackReason: failureReason('the session model', attempt),
            })
          }
          if (configured === null) {
            return withEffort({ outcome: 'reviewed', model: 'inherited', review: attempt.review })
          }
          return withEffort({
            outcome: 'fallback',
            model: 'inherited',
            review: attempt.review,
            routeFallbackReason: `${label} skipped: the caller asked for the session route`,
          })
        }

        const capable = scope.subagents.getProvider(providerName)?.capabilities?.agentOptions === true
        if (!capable) {
          return fallback(`${label} not used: provider does not support child agent options`)
        }
        const effortSupport = await routeEffortSupport(configured)
        const childEffort = appliedEffort(wantedEffort, effortSupport)
        // The child's options are the route alone unless a level was actually
        // applied: with no selection this is the same `{provider, model}` object
        // this call has always dispatched, and nothing about the request
        // changes.
        const childOptions = childEffort === null ? configured : { ...configured, reasoningEffort: childEffort }
        // The wrapper reports instead of throwing, so a rejected dispatch, an
        // expired budget, a rejected result, and a failed teardown all reach the
        // same fallback the configured path already had.
        const attempt = await runWithEffort(childOptions, childEffort)
        if (attempt.kind !== null) {
          return fallback(failureReason(label, attempt))
        }
        return withEffort({ outcome: 'reviewed', model: label, review: attempt.review })
      },
    }))
  })
}
