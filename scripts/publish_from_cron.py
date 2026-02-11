#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime
from pathlib import Path

PAPER_JOB_ID = '5d633bca-2753-42bf-b9af-91f39ec2c6cd'
X_JOB_ID = 'c567fd04-4ab1-4c43-8444-09ff75cffc8f'

WORKSPACE = Path('/root/.openclaw/workspace')
CARE_PROJECT = WORKSPACE / 'brainstorm-multi-model-2026-02-10'
PAPER_FILE = CARE_PROJECT / 'reports' / 'final_structured_report.md'
X_FILE = CARE_PROJECT / 'cache' / 'latest_x_report.txt'


def latest_summary(job_id: str) -> str:
    p = subprocess.run(
        ['openclaw', 'cron', 'runs', '--id', job_id, '--limit', '1'],
        capture_output=True,
        text=True,
        check=True,
    )
    obj = json.loads(p.stdout)
    entries = obj.get('entries', [])
    if not entries:
        return ''
    return entries[0].get('summary', '')


# 论文日报优先读本地完整文件，避免 cron summary 截断
if PAPER_FILE.exists():
    paper = PAPER_FILE.read_text(encoding='utf-8', errors='ignore')
else:
    paper = latest_summary(PAPER_JOB_ID)

# X 日报优先读本地完整文件（由X cron写入），否则降级用summary
if X_FILE.exists():
    xhot = X_FILE.read_text(encoding='utf-8', errors='ignore')
else:
    xhot = latest_summary(X_JOB_ID)

out = Path(__file__).resolve().parents[1] / 'data' / 'latest.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
    json.dumps(
        {
            'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            'paper_report': paper,
            'x_report': xhot,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding='utf-8',
)
print('updated', out)
