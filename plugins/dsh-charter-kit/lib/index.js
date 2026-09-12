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

/** Empty provider or model means "inherit the calling session's model". */
const REVIEW_SETTINGS_SCHEMA = z.object({
  reviewAProvider: z.string().default(''),
  reviewAModel: z.string().default(''),
  reviewBProvider: z.string().default(''),
  reviewBModel: z.string().default(''),
})

const REVIEW_SETTINGS_DEFAULTS = {
  reviewAProvider: '',
  reviewAModel: '',
  reviewBProvider: '',
  reviewBModel: '',
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
 * @param result - settled SubagentResult.
 * @returns the review text with `failure: null` when the child completed with
 *   text, else the same review text with a non-empty failure detail carrying
 *   the provider's diagnostic whenever the provider supplied one.
 */
function classifyRun(result) {
  const review = outputText(result)
  const stopReason = result.stopReason
  const diagnostic = typeof result.diagnostic === 'string' ? result.diagnostic.trim() : ''
  const detail = diagnostic === '' ? '' : `: ${diagnostic}`
  if (stopReason !== COMPLETED_STOP_REASON) {
    return { review, failure: `child stopped with stopReason "${stopReason}"${detail}` }
  }
  if (review === '') {
    return { review, failure: `child completed with an empty review${detail}` }
  }
  return { review, failure: null }
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
export const inject = ['skills', 'tools', 'settings', 'subagents']

export function apply(ctx) {
  const skill = parseFrontmatter(readFileSync(SKILL_FILE, 'utf8'))

  let reviewSettings = () => REVIEW_SETTINGS_DEFAULTS
  ctx.settings.installSection(
    ctx,
    REVIEW_SETTINGS_NAMESPACE,
    REVIEW_SETTINGS_SCHEMA,
    REVIEW_SETTINGS_DEFAULTS,
    {
      setSource: (source) => { reviewSettings = source },
      validate: () => {},
      onChange: () => {},
    },
  )

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

  ctx.tools.register(defineTool({
    name: 'charter_review',
    description: 'Run one context-free Charter Kit review with the model configured for that review kind. '
      + 'Use kind "A" for every leaf\'s contract and implementation coverage review, and kind "B" for the '
      + 'adversarial review required by a hit RVB trigger. The reviewer receives only the brief you pass — '
      + 'never the session history — and the returned model names the route it used, or `inherited` '
      + 'when it followed the session model.',
    parameters: {
      kind: {
        type: 'string',
        required: true,
        description: 'Review kind: "A" for coverage review, "B" for the RVB-triggered adversarial review.',
      },
      brief: {
        type: 'string',
        required: true,
        description: 'Self-contained review brief: the leaf contract, the spec, and the candidate diff. '
          + 'The reviewer sees nothing else, so never include session history.',
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
      const kind = args.kind === 'B' ? 'B' : 'A'
      const configured = reviewRoute(reviewSettings(), kind)
      const parent = exec.agent
      const providerName = pickSubagentProvider(ctx)
      const prompt = [{ type: 'text', text: args.brief }]

      const runOnce = async (agentOptions) => {
        const run = await ctx.subagents.start(providerName, {
          prompt,
          parent,
          signal: exec.signal,
          ...(agentOptions === null ? {} : { agentOptions }),
        })
        try {
          return classifyRun(await run.result)
        } finally {
          await run.dispose()
        }
      }

      // A configured route that produced no review is re-run on the session
      // model. When that second run fails too there is no review to report, so
      // the tool says `unavailable` instead of returning a success shape with
      // empty text.
      const fallback = async (reason) => {
        const attempt = await runOnce(null)
        if (attempt.failure !== null) {
          return {
            outcome: 'unavailable',
            model: 'inherited',
            review: '',
            routeFallbackReason: `${reason}; the session-model rerun also failed: ${attempt.failure}`,
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

      if (configured === null) {
        const attempt = await runOnce(null)
        if (attempt.failure !== null) {
          return {
            outcome: 'unavailable',
            model: 'inherited',
            review: '',
            routeFallbackReason: `session model: ${attempt.failure}`,
          }
        }
        return { outcome: 'reviewed', model: 'inherited', review: attempt.review }
      }

      const label = `${configured.provider}/${configured.model}`
      const capable = ctx.subagents.getProvider(providerName)?.capabilities?.agentOptions === true
      if (!capable) {
        return fallback(`${label} not used: provider does not support child agent options`)
      }
      let attempt
      try {
        attempt = await runOnce(configured)
      } catch (error) {
        return fallback(`${label} unavailable: ${error instanceof Error ? error.message : String(error)}`)
      }
      if (attempt.failure !== null) {
        return fallback(`${label} unavailable: ${attempt.failure}`)
      }
      return { outcome: 'reviewed', model: label, review: attempt.review }
    },
  }))
}
