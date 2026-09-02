import { readFileSync } from 'node:fs'
import { fileURLToPath } from 'node:url'
import { dirname, join } from 'node:path'

const ROOT = join(dirname(fileURLToPath(import.meta.url)), '..')
const SKILL_DIR = join(ROOT, 'skills', 'charter-workflow')
const SKILL_FILE = join(SKILL_DIR, 'SKILL.md')
const COMMAND_FILE = join(ROOT, 'portable', 'commands', 'charter-workflow.md')

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
    argumentHint: meta['argument-hint'] || meta.argumentHint,
    body: (match[2] || '').trimEnd() + '\n',
  }
}

function readCommandText() {
  return parseFrontmatter(readFileSync(COMMAND_FILE, 'utf8')).body
}

function readCommandHint() {
  return parseFrontmatter(readFileSync(COMMAND_FILE, 'utf8')).argumentHint
}

export const name = 'dsh-charter-kit'
export const inject = ['commands', 'skills']

export function apply(ctx) {
  const skill = parseFrontmatter(readFileSync(SKILL_FILE, 'utf8'))

  ctx.effect(() => ctx.commands.register({
    name: 'charter-workflow',
    description: 'Start, resume, or run change triage for the Charter Kit development workflow',
    input: { hint: readCommandHint() || 'optional one-sentence requirement' },
    handler: () => ({
      kind: 'success',
      text: `Charter Kit DSH plugin package root: ${ROOT}\n\n${readCommandText()}`,
    }),
  }), 'charter-kit: /charter-workflow')

  ctx.effect(() => ctx.skills.register({
    name: 'charter-workflow',
    description: skill.description,
    ...(skill.whenToUse ? { whenToUse: skill.whenToUse } : {}),
    source: 'runtime',
    provider: 'dsh-charter-kit',
    resourceBase: { kind: 'directory', path: SKILL_DIR },
    content: skill.body,
  }), 'charter-kit: skill')
}