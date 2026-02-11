#!/usr/bin/env python3
import json
from datetime import datetime
from pathlib import Path

workspace = Path('/root/.openclaw/workspace')
project = workspace / 'brainstorm-multi-model-2026-02-10'
out = Path(__file__).resolve().parents[1] / 'data' / 'latest.json'
out.parent.mkdir(parents=True, exist_ok=True)

paper_path = project / 'reports' / 'final_structured_report.md'
x_path = project / 'cache' / 'latest_x_report.txt'

paper = paper_path.read_text(encoding='utf-8', errors='ignore') if paper_path.exists() else ''
xhot = x_path.read_text(encoding='utf-8', errors='ignore') if x_path.exists() else ''

obj = {
  'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
  'paper_report': paper[:120000],
  'x_report': xhot[:120000]
}
out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')
print('generated', out)
