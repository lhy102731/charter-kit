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
 * Bounds on one review attempt, in whole seconds.
 *
 * The floor keeps a mistyped card from aborting every review before the child
 * can answer.
 *
 * The ceiling is dimensioned against the WHOLE call, not one attempt, because a
 * call may spend the configured attempt and then a session-model rerun. The
 * budget therefore has to satisfy `2 * MAX + margin < ceiling`, where the
 * ceiling is the ~600 s a real project observed the host enforcing:
 * 2 * 270 + 30 = 570 s. Sizing MAX at the ceiling itself (540) would let a
 * full-budget attempt plus a full-budget rerun reach 1080 s and be killed
 * externally with nothing to show — the exact failure this budget exists to
 * remove.
 */
const MIN_REVIEW_TIMEOUT_SECONDS = 30
const MAX_REVIEW_TIMEOUT_SECONDS = 270
const DEFAULT_REVIEW_TIMEOUT_SECONDS = 240

/**
 * Slack, in seconds, between the worst case the clamp above can express and the
 * deadline this tool declares: enough for dispatch, disposal, and rendering.
 */
const REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS = 30

/**
 * The cooperative tool-call deadline this tool declares to the harness.
 *
 * The setting is dynamic while a declared `timeoutMs` is fixed at registration,
 * so this is derived from the worst case the clamp can express: the configured
 * attempt and the session-model rerun, each at `MAX`, plus the margin.
 * 2 * 270 + 30 = 570 s, which is above the 540 s this tool can actually spend
 * and still below the ~600 s external ceiling — so THIS tool's deadline fires
 * first and renders a result, instead of the call being preempted by an opaque
 * `TOOL_TIMEOUT`.
 */
const REVIEW_TOOL_TIMEOUT_MS = (MAX_REVIEW_TIMEOUT_SECONDS * 2 + REVIEW_TOOL_TIMEOUT_MARGIN_SECONDS) * 1000

/** Empty provider or model means "inherit the calling session's model". */
const REVIEW_SETTINGS_SCHEMA = z.object({
  reviewAProvider: z.string().default(''),
  reviewAModel: z.string().default(''),
  reviewBProvider: z.string().default(''),
  reviewBModel: z.string().default(''),
  [REVIEW_TIMEOUT_FIELD]: z.number().default(DEFAULT_REVIEW_TIMEOUT_SECONDS),
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
}

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
 * Read one review attempt's budget out of the settings value.
 *
 * Clamped here rather than in the card, because this is the only place that can
 * guarantee the bound: a card version that predates the field, a hand-edited
 * settings file, and a stored value of the wrong type all reach this function,
 * and none of them may be able to abort every review or to outlive the host's
 * own ceiling.
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

    scope.tools.register(defineTool({
      name: 'charter_review',
      description: 'Run one context-free Charter Kit review with the model configured for that review kind. '
        + 'Use kind "A" for every leaf\'s contract and implementation coverage review, and kind "B" for the '
        + 'adversarial review required by a hit RVB trigger. The reviewer receives only the brief you pass — '
        + 'never the session history — and the returned model names the route it used, or `inherited` '
        + 'when it followed the session model. An attempt is bounded by the configured timeout; any way the '
        + 'configured route fails to produce a review — a settled failure, an empty result, or that timeout — '
        + 'reruns the same brief on the session model and reports `outcome: "fallback"`, so the call never '
        + 'waits and never returns an empty review.',
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
          description: 'Self-contained review brief: the leaf contract, the spec, and the candidate diff. '
            + 'The reviewer sees nothing else, so never include session history.',
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
        const parent = exec.agent
        const providerName = pickSubagentProvider(scope)
        const prompt = [{ type: 'text', text: brief }]

        /** Read one throwable's message for a failure detail. */
        const messageOf = (error) => (error instanceof Error ? error.message : String(error))

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
          let reachDeadline
          const deadline = new Promise((resolve) => { reachDeadline = resolve })
          // The one timer this tool arms. It is disarmed in the same `finally`
          // that releases the child, so no attempt leaves a timer behind.
          const timer = setTimeout(() => {
            controller.abort()
            reachDeadline()
          }, budgetMs)
          try {
            let run
            try {
              run = await scope.subagents.start(providerName, {
                prompt,
                parent,
                signal: controller.signal,
                ...(agentOptions === null ? {} : { agentOptions }),
              })
            } catch (error) {
              // A dispatch that never published a run cannot settle, so the
              // deadline is the only thing that can have ended it.
              return controller.signal.aborted && !exec.signal.aborted
                ? failed('timeout', elapsedMs(), `no child was published within the ${budgetSeconds}s budget`)
                : failed('error', elapsedMs(), messageOf(error))
            }
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
                attempt = failed('timeout', elapsedMs(), `no review within the ${budgetSeconds}s budget`)
              } else if ('error' in outcome) {
                attempt = failed('error', elapsedMs(), messageOf(outcome.error))
              } else {
                attempt = classifyRun(outcome.value, elapsedMs())
              }
            } finally {
              try {
                await run.dispose()
              } catch (error) {
                // A child this tool could not release is reported as the
                // attempt's failure instead of escaping `execute`.
                disposal = failed('error', elapsedMs(), `child disposal failed: ${messageOf(error)}`)
              }
            }
            // A teardown that failed outweighs the attempt it could not release.
            return disposal ?? attempt
          } finally {
            clearTimeout(timer)
            exec.signal.removeEventListener('abort', forwardAbort)
          }
        }

        // A configured route that produced no review — a settled failure, an
        // empty result, or the timeout above — is re-run on the session model in
        // a fresh, context-free child. When that second run fails too there is no
        // review to report, so the tool says `unavailable` instead of returning a
        // success shape with empty text.
        const fallback = async (reason) => {
          const attempt = await runReview(null)
          if (attempt.kind !== null) {
            return {
              outcome: 'unavailable',
              model: 'inherited',
              review: '',
              routeFallbackReason: `${reason}; the session-model rerun also failed: ${failureReason('the session model', attempt)}`,
            }
          }
          return {
            outcome: 'fallback',
            model: 'inherited',
            review: attempt.review,
            routeFallbackReason: reason,
          }
        }

        if (parent === undefined || providerName === undefined) {
          return {
            outcome: 'unavailable',
            model: 'inherited',
            review: '',
            routeFallbackReason: parent === undefined
              ? 'no calling agent'
              : 'no unambiguous subagent provider',
          }
        }

        const label = configured === null ? '' : `${configured.provider}/${configured.model}`

        // No configured route, or a caller that already recorded this route as
        // failed and asked for the session model: both run one session-model
        // child. Only the second is a degradation, and it is reported as one so
        // the leaf's evidence shows it without the caller having to remember.
        if (configured === null || wantSessionRoute) {
          const attempt = await runReview(null)
          if (attempt.kind !== null) {
            return {
              outcome: 'unavailable',
              model: 'inherited',
              review: '',
              routeFallbackReason: failureReason('the session model', attempt),
            }
          }
          if (configured === null) {
            return { outcome: 'reviewed', model: 'inherited', review: attempt.review }
          }
          return {
            outcome: 'fallback',
            model: 'inherited',
            review: attempt.review,
            routeFallbackReason: `${label} skipped: the caller asked for the session route`,
          }
        }

        const capable = scope.subagents.getProvider(providerName)?.capabilities?.agentOptions === true
        if (!capable) {
          return fallback(`${label} not used: provider does not support child agent options`)
        }
        // The wrapper reports instead of throwing, so a rejected dispatch, an
        // expired budget, a rejected result, and a failed teardown all reach the
        // same fallback the configured path already had.
        const attempt = await runReview(configured)
        if (attempt.kind !== null) {
          return fallback(failureReason(label, attempt))
        }
        return { outcome: 'reviewed', model: label, review: attempt.review }
      },
    }))
  })
}
