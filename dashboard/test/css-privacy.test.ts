import assert from 'node:assert/strict';
import fs, { mkdtempSync, writeFileSync, rmSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createRequire } from 'node:module';
import test from 'node:test';

const require = createRequire(import.meta.url);
const nextRequire = createRequire(require.resolve('next/package.json'));

test('Next CSS processing refuses an absolute source map outside its input', async () => {
  const folder = mkdtempSync(join(tmpdir(), 'crewloom-css-private-'));
  const originalRead = fs.readFileSync;
  const file = join(folder, 'private.map');
  let privateReads = 0;
  try {
    const marker = 'private-project-source-marker';
    writeFileSync(file, JSON.stringify({ version: 3, sources: ['private-source.ts'],
      sourcesContent: [marker], names: [], mappings: 'AAAA' }));
    fs.readFileSync = ((path: unknown, ...args: unknown[]) => {
      if (path === file) privateReads++;
      return (originalRead as any)(path, ...args);
    }) as typeof fs.readFileSync;
    const postcss = nextRequire('postcss');
    const result = await postcss([{ postcssPlugin: 'privacy-fixture', Once() {} }]).process(`a{color:red}\n/*# sourceMappingURL=${file} */`,
      { from: undefined, map: { inline: false } });
    assert.equal(privateReads, 0, 'untrusted CSS must not read an external private source map');
    assert.equal(JSON.stringify(result.map?.toJSON()).includes(marker), false);
    assert.equal(result.css.includes(file), false);
  } finally {
    fs.readFileSync = originalRead;
    rmSync(folder, { recursive: true, force: true });
  }
});
