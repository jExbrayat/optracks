// Usage: node solve.mjs FILE.igc CODE  (CODE: od = free distance, tri = flat triangle, fai = FAI triangle)
// Prints the optimal solution as GeoJSON on stdout.
import fs from 'node:fs';
import IGCParser from 'igc-parser';
import { solver, scoringRules } from 'igc-xc-score';

const [path, code] = process.argv.slice(2);
const rules = scoringRules.XContest.filter((rule) => rule.code === code);
if (!rules.length) {
    console.error(`No XContest rule with code ${code}`);
    process.exit(2);
}
const flight = IGCParser.parse(fs.readFileSync(path, 'utf8'), { lenient: true });
const it = solver(flight, rules, { maxcycle: 100, noflight: true });
let step;
do {
    step = it.next();
} while (!step.done);
process.stdout.write(JSON.stringify(step.value.geojson()));
