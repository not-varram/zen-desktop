#!/usr/bin/env python3
"""Digest a raw issue JSON: strip <details> dumps (keeping Version/OS/RAM/Remote Processes/extensions lines),
truncate comments, list links. Usage: digest.py N [maxchars_per_comment]"""
import json,re,sys
n=sys.argv[1]; mx=int(sys.argv[2]) if len(sys.argv)>2 else 700
d=json.load(open(f'raw/{n}.json'))
KEYS=re.compile(r'^(Version|Operating System|OS|Memory|Remote Processes|Multiprocess|Application|Name|Build ID|User Agent|Platform|Total|Physical|RAM).{0,160}',re.I|re.M)
def strip(t):
    t=t or ''
    keep=[]
    def rep(m):
        blk=m.group(0)
        for k in KEYS.finditer(blk): keep.append(k.group(0).strip())
        ext=re.findall(r'^\s*([^\n|]*@[^\n|]*|[^\n|]+\|\s*\d[\d.]*\s*\|\s*(?:true|false)[^\n]*)$',blk,re.M)
        return '[DETAILS STRIPPED; kept: '+' ; '.join(keep[:8])+(' ; ext:'+', '.join(e[:50] for e in ext[:15]) if ext else '')+']'
    t=re.sub(r'<details>.*?</details>',rep,t,flags=re.S)
    t=re.sub(r'\n{3,}','\n\n',t)
    return t
print(f"# #{d['number']} {d['title']}\nstate={d['state']} reason={d['stateReason']} created={d['createdAt'][:10]} closed={d['closedAt']} author={d['author']['login']} labels={[l['name'] for l in d['labels']]}")
b=strip(d['body']); print('BODY:',b[:1500]); 
links=set(re.findall(r'https?://[^\s)>\]]+',json.dumps(d['body'])+json.dumps(d['comments'])))
for i,c in enumerate(d['comments']):
    print(f"--- c{i} {c['author']['login']} {c['createdAt'][:10]}:",strip(c['body'])[:mx].replace('\n',' '))
print('LINKS:',sorted(l.rstrip('\\"') for l in links if '/files/' in l or 'perf.html' in l or 'share.firefox' in l or ('github.com/zen-browser' in l and 'issues' not in l) or 'bugzilla' in l)[:30])
