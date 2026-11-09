#!/usr/bin/env python3
"""Summarize an about:memory report (json or json.gz): per-process explicit total, parent-process top explicit paths, ghost/detached windows.
Usage: memsum.py file [topN]"""
import json,gzip,sys,collections
f=sys.argv[1]; N=int(sys.argv[2]) if len(sys.argv)>2 else 10
raw=open(f,'rb').read()
if raw[:2]==b'\x1f\x8b': raw=gzip.decompress(raw)
d=json.loads(raw)
rep=d['reports']
procs=collections.defaultdict(lambda:{'explicit':0,'paths':collections.Counter()})
ghost=collections.Counter(); detached=collections.Counter()
for r in rep:
    p=r['process']; path=r['path']
    if path.startswith('explicit/'): procs[p]['explicit']+=r['amount']
    if path.startswith('explicit/') : procs[p]['paths'][path]=r['amount']
    if path.startswith('ghost-windows/'): ghost[p]+=1
    if 'detached' in path and path.startswith('explicit/window-objects'): detached[p]+=1  # counts report entries, not windows
mb=lambda x:f'{x/1048576:.1f}MB'
print(f, 'processes:',len(procs))
for p,v in sorted(procs.items(),key=lambda kv:-kv[1]['explicit'])[:4]:
    print(f"== {p}: explicit {mb(v['explicit'])}  ghost-entries={ghost[p]} detached-entries={detached[p]}")
    # leaf-ish: show top by depth<=4 non-overlapping style: just top amounts for depth 2-3
    tops=list(v['paths'].items())  # leaf reports, non-overlapping
    for k,a in sorted(tops,key=lambda x:-x[1])[:N]: print('   ',mb(a),k[:140])
