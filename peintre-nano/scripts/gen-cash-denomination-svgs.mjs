import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const dir = path.join(__dirname, '..', 'public', 'assets', 'cash-denominations');
fs.mkdirSync(dir, { recursive: true });

const denoms = [
  { code: 'EUR_50000', label: '500 €', kind: 'note' },
  { code: 'EUR_20000', label: '200 €', kind: 'note' },
  { code: 'EUR_10000', label: '100 €', kind: 'note' },
  { code: 'EUR_5000', label: '50 €', kind: 'note' },
  { code: 'EUR_2000', label: '20 €', kind: 'note' },
  { code: 'EUR_1000', label: '10 €', kind: 'note' },
  { code: 'EUR_500', label: '5 €', kind: 'note' },
  { code: 'EUR_200', label: '2 €', kind: 'coin' },
  { code: 'EUR_100', label: '1 €', kind: 'coin' },
  { code: 'EUR_050', label: '50 c', kind: 'coin' },
  { code: 'EUR_020', label: '20 c', kind: 'coin' },
  { code: 'EUR_010', label: '10 c', kind: 'coin' },
  { code: 'EUR_005', label: '5 c', kind: 'coin' },
  { code: 'EUR_002', label: '2 c', kind: 'coin' },
  { code: 'EUR_001', label: '1 c', kind: 'coin' },
];

for (const d of denoms) {
  const fill = d.kind === 'note' ? '#4c6ef5' : '#fab005';
  const shape =
    d.kind === 'note'
      ? `<rect x="8" y="12" width="64" height="40" rx="4" fill="${fill}" opacity="0.85"/>`
      : `<circle cx="40" cy="32" r="22" fill="${fill}" opacity="0.85"/>`;
  const svg = `<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 80 64" role="img" aria-hidden="true">
  ${shape}
  <text x="40" y="36" text-anchor="middle" font-family="system-ui,sans-serif" font-size="11" font-weight="700" fill="#212529">${d.label}</text>
</svg>
`;
  fs.writeFileSync(path.join(dir, `${d.code}.svg`), svg);
}

console.log(`Created ${denoms.length} SVGs in ${dir}`);
