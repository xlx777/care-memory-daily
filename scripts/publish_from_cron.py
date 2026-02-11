#!/usr/bin/env python3
import json, subprocess
from datetime import datetime
from pathlib import Path

PAPER_JOB_ID='5d633bca-2753-42bf-b9af-91f39ec2c6cd'
X_JOB_ID='c567fd04-4ab1-4c43-8444-09ff75cffc8f'

def latest_summary(job_id:str)->str:
    p = subprocess.run(['openclaw','cron','runs','--id',job_id,'--limit','1'],capture_output=True,text=True,check=True)
    obj=json.loads(p.stdout)
    entries=obj.get('entries',[])
    if not entries:
        return ''
    return entries[0].get('summary','')

paper=latest_summary(PAPER_JOB_ID)
xhot=latest_summary(X_JOB_ID)

out=Path(__file__).resolve().parents[1]/'data'/'latest.json'
out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps({
    'updated_at': datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC'),
    'paper_report': paper,
    'x_report': xhot,
},ensure_ascii=False,indent=2),encoding='utf-8')
print('updated',out)
