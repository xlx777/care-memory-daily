#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime
from pathlib import Path

PAPER_JOB_ID = '5d633bca-2753-42bf-b9af-91f39ec2c6cd'
X_JOB_ID = 'c567fd04-4ab1-4c43-8444-09ff75cffc8f'

WORKSPACE = Path('/root/.openclaw/workspace')
CARE_PROJECT = WORKSPACE / 'brainstorm-multi-model-2026-02-10'
PAPER_FILE = CARE_PROJECT / 'cache' / 'latest_paper_report.txt'
X_FILE = CARE_PROJECT / 'cache' / 'latest_x_report.txt'
PAPER_JSON = CARE_PROJECT / 'daily_report_result.json'


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


def build_paper_report_from_json(path: Path) -> str:
    d = json.loads(path.read_text(encoding='utf-8', errors='ignore'))
    top = d.get('top_conclusion', {})
    lines = []
    lines.append('1) Top结论 + 置信度 + trace_id')
    lines.append(
        f"Top结论：**{top.get('stance','GO')}，优先关注 {top.get('title','N/A')}**"
    )
    lines.append(f"置信度：**{float(top.get('confidence', 0)):.3f}**")
    lines.append(f"trace_id：**{d.get('trace_id', 'N/A')}**")
    deep = d.get('deep_read_list', [])
    lines.append(f"自动深读名单：**{', '.join(deep) if deep else 'N/A'}**")
    lines.append('')
    lines.append('2) 每篇深读论文小节（逐篇）')

    for i, s in enumerate(d.get('paper_debate_summaries', []), start=1):
        lines.append('')
        lines.append(f"2.{i} {s.get('paper_id','P?')} — {s.get('title','N/A')}")
        lines.append(f"- 最终轮次：{s.get('final_round','N/A')} | 结论：**{s.get('final_stance','N/A')}** | 置信度：{float(s.get('final_confidence',0)):.3f}")
        lines.append(f"- 最终裁定：{s.get('final_ruling','N/A')}")
        kp = s.get('key_consensus_points', [])
        if kp:
            lines.append('- 关键共识：')
            for x in kp:
                lines.append(f"  - {x}")
        kr = s.get('key_risks', [])
        if kr:
            lines.append('- 关键风险：')
            for x in kr:
                lines.append(f"  - {x}")

    cp = d.get('cross_paper_insights', {})
    lines.append('')
    lines.append('3) 跨论文洞察')
    lines.append('3.1 共同问题（>=3）')
    for x in cp.get('common_issues', []):
        lines.append(f"- {x}")

    lines.append('')
    lines.append('3.2 潜在研究创新方向（>=3，每条含研究假设+验证路径）')
    for item in cp.get('innovation_directions', []):
        lines.append(f"- 方向：{item.get('direction','N/A')}")
        lines.append(f"  - 研究假设：{item.get('hypothesis','N/A')}")
        lines.append(f"  - 验证路径：{item.get('validation','N/A')}")

    ph = d.get('phase_b', {})
    lines.append('')
    lines.append('4) Phase B 状态')
    lines.append(f"- 触发条件：{ph.get('trigger_condition','N/A')}")
    lines.append(f"- trigger_met：{ph.get('trigger_met', False)}")
    lines.append(f"- shadow_progress：{ph.get('shadow_progress_pct','N/A')}%")
    lines.append(f"- recommend_start：{ph.get('recommend_start', False)}")

    return '\n'.join(lines)


if PAPER_FILE.exists():
    paper = PAPER_FILE.read_text(encoding='utf-8', errors='ignore')
    paper_source = 'file'
elif PAPER_JSON.exists():
    paper = build_paper_report_from_json(PAPER_JSON)
    paper_source = 'json'
else:
    paper = latest_summary(PAPER_JOB_ID)
    paper_source = 'summary'

if X_FILE.exists():
    xhot = X_FILE.read_text(encoding='utf-8', errors='ignore')
    x_source = 'file'
else:
    xhot = latest_summary(X_JOB_ID)
    x_source = 'summary'

out = Path(__file__).resolve().parents[1] / 'data' / 'latest.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(
    json.dumps(
        {
            'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
            'paper_report': paper,
            'x_report': xhot,
            'paper_source': paper_source,
            'x_source': x_source,
        },
        ensure_ascii=False,
        indent=2,
    ),
    encoding='utf-8',
)
print('updated', out)
print('paper_source', paper_source, 'len', len(paper))
print('x_source', x_source, 'len', len(xhot))
