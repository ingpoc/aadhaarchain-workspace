import { readdir, readFile, stat } from 'node:fs/promises';
import { extname, resolve } from 'node:path';

const roots = process.argv.slice(2);
const textExtensions = new Set(['.css', '.html', '.js', '.json', '.mjs', '.py', '.svg', '.txt']);
const forbidden = [
  { label: 'PreProd', pattern: /pre[ -]?prod/i },
  { label: 'demo scope', pattern: /demo\s+scope/i },
  { label: 'demo seller', pattern: /demo\s+seller/i },
];

if (roots.length === 0) {
  console.error('Usage: node scripts/check-production-copy.mjs <build-directory> [...]');
  process.exit(2);
}

async function filesUnder(path) {
  const details = await stat(path);
  if (details.isFile()) return [path];

  const entries = await readdir(path, { withFileTypes: true });
  const nested = await Promise.all(entries.map((entry) => filesUnder(resolve(path, entry.name))));
  return nested.flat();
}

const files = (await Promise.all(roots.map((root) => filesUnder(resolve(root))))).flat();
const violations = [];

for (const file of files) {
  if (!textExtensions.has(extname(file).toLowerCase())) continue;
  const content = await readFile(file, 'utf8');
  for (const rule of forbidden) {
    if (rule.pattern.test(content)) violations.push(`${file}: contains ${rule.label}`);
  }
}

if (violations.length > 0) {
  console.error(`Production copy gate failed:\n${violations.join('\n')}`);
  process.exit(1);
}

console.log(`Production copy gate passed (${files.length} build files checked).`);
