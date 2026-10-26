import { readFileSync, existsSync } from 'node:fs'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const scriptDir = dirname(fileURLToPath(import.meta.url))
const rootDir = resolve(scriptDir, '../../../../')
const threatModelPath = resolve(scriptDir, 'THREAT-MODEL.md')

if (!existsSync(threatModelPath)) {
  console.error(`Threat model file not found at ${threatModelPath}`)
  process.exit(1)
}

const content = readFileSync(threatModelPath, 'utf8')

// Match backtick expressions that reference files in the repository
const backtickRegex = /`([^`\n]+)`/g
let match
const references = []

while ((match = backtickRegex.exec(content)) !== null) {
  const ref = match[1].trim()
  // Consider expressions that look like paths containing slashes and extensions
  if (
    (ref.startsWith('agent/') || ref.startsWith('packages/') || ref.startsWith('core/')) &&
    (ref.includes('.ts') || ref.includes('.json') || ref.includes('.yaml') || ref.includes('.yml') || ref.includes('.md'))
  ) {
    references.push(ref)
  }
}

if (references.length === 0) {
  console.error('No file references found in threat model table.')
  process.exit(1)
}

let verifiedCount = 0
const errors = []

for (const ref of references) {
  const [rawPath, symbol] = ref.split(':')
  const normalizedPath = rawPath.startsWith('packages/') ? `agent/${rawPath}` : rawPath
  const fullPath = resolve(rootDir, normalizedPath)

  if (!existsSync(fullPath)) {
    errors.push(`Missing file: ${rawPath} (resolved: ${fullPath})`)
    continue
  }

  if (symbol && symbol.trim().length > 0) {
    const fileContent = readFileSync(fullPath, 'utf8')
    if (!fileContent.includes(symbol.trim())) {
      errors.push(`Symbol '${symbol.trim()}' not found in ${rawPath}`)
      continue
    }
  }

  verifiedCount++
}

if (errors.length > 0) {
  console.error(`Verification failed with ${errors.length} error(s):`)
  for (const err of errors) {
    console.error(`  - ${err}`)
  }
  process.exit(1)
}

console.log(`all references ok (${verifiedCount} verified)`)
