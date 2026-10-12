import fs from 'node:fs/promises';
import path from 'node:path';
import { createRequire } from 'node:module';
import { fileURLToPath, pathToFileURL } from 'node:url';

// Usage: node scripts/build_tableau_practice_20261004.mjs <bundled-node_modules-path>
if (!process.argv[2]) throw new Error('Supply the bundled node_modules path');
const require = createRequire(path.join(path.resolve(process.argv[2]), '__resolver__.cjs'));
const { Workbook } = await import(pathToFileURL(require.resolve('@oai/artifact-tool')).href);

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const input = await fs.readFile(path.join(root, 'data/analytical/sakhalin_1890_en_v1.csv'), 'utf8');
const source = await Workbook.fromCSV(input, { sheetName: 'Source' });
const values = source.worksheets.getItemAt(0).getUsedRange().values;
const nameIndex = values[0].indexOf('full_name');
if (nameIndex < 0 || values.length !== 7447) throw new Error('Unexpected source structure');
const output = Workbook.create();
const sheet = output.worksheets.add('Practice');
const projected = values.map(row => row.filter((_, i) => i !== nameIndex));
sheet.getRange('A1:V7447').values = projected;
console.log((await output.inspect({kind:'table', range:'Practice!A1:F3', tableMaxRows:3, tableMaxCols:6, maxChars:1000})).ndjson);
// CSV serialization preserves literal text, blanks, zero, and Boolean strings.
const quote = value => {
  const text = value == null ? '' : String(value);
  return /[",\r\n]/.test(text) ? '"' + text.replaceAll('"', '""') + '"' : text;
};
const csv = sheet.getRange('A1:V7447').values.map(row => row.map(quote).join(',')).join('\r\n') + '\r\n';
const destination = path.join(root, 'tableau/practice/sakhalin_1890_en_no_full_name_20261004.csv');
await fs.mkdir(path.dirname(destination), {recursive:true});
try {
  const existing = await fs.readFile(destination, 'utf8');
  if (existing !== csv) throw new Error('Refusing to overwrite a different versioned output');
} catch (error) {
  if (error.code !== 'ENOENT') throw error;
  await fs.writeFile(destination, csv, {flag:'wx'});
}
console.log('Practice CSV written: 7446 rows, 22 columns');
