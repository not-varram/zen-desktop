#!/usr/bin/env python3
"""Analyse about:memory reports (json / json.gz, truncated gz tolerated). stdlib only.

Usage:
  analyze_memreports.py FILE...            full per-report/per-process text report
  analyze_memreports.py --table FILE...    one TSV row per report (Main Process focus)
  analyze_memreports.py --main-only FILE...   only the Main Process section
  analyze_memreports.py --topn N ...       change number of top explicit paths (default 15)

Per process: explicit total, top-N explicit paths, number of ghost / detached windows
(+ bytes), and for the Main Process: every window-objects/top(...) entry (state, URL,
#windows, bytes, element-node bytes), event-listener counts, js-non-window zones total,
and large realm(...) entries naming chrome:// resource:// moz-src: etc.

Window counting: a window contributes exactly one `.../window(URL)/dom/element-nodes`
report, so #windows = number of those reports for that (top, state, URL) triple (identical
paths in different windows are separate report objects in the JSON). `ghost-windows`
(top-level section, amount=1 per ghost) is counted separately.
"""
import gzip, json, re, sys, zlib, collections, os

MB = 1048576.0
MAIN_ONLY = False
def mb(x): return f"{x/MB:.1f}MB"

def load_reports(path):
    """Return (reports, truncated). Handles gz, plain json, and truncated streams."""
    raw = open(path, 'rb').read()
    truncated = False
    if raw[:2] == b'\x1f\x8b':
        o = zlib.decompressobj(31)
        try: txt = o.decompress(raw)
        except zlib.error: txt = b''
        truncated = not o.eof
    else:
        txt = raw
    txt = txt.decode('utf-8', 'replace')
    try:
        return json.loads(txt)['reports'], truncated
    except Exception:
        pass
    # truncated / damaged: stream-parse report objects
    truncated = True
    i = txt.find('"reports"')
    i = txt.find('[', i) + 1
    dec = json.JSONDecoder(); reps = []
    while True:
        while i < len(txt) and txt[i] in ' \r\n\t,': i += 1
        if i >= len(txt) or txt[i] != '{': break
        try: o, i = dec.raw_decode(txt, i)
        except ValueError: break
        reps.append(o)
    return reps, truncated

def split(path): return path.split('/')

def is_chromey(s):
    return bool(re.search(r'chrome:|resource:|moz-src:|moz-extension:|about:|jar:file', s))

def analyze(path, topn=15):
    reps, trunc = load_reports(path)
    P = collections.defaultdict(lambda: dict(
        explicit=0, leaves=collections.Counter(), win=collections.defaultdict(lambda: dict(n=0, bytes=0, elem=0, evl=0, orphan=0, jsrealm=0, layout=0)),
        ghost_list=[], realms=collections.Counter(), zones=0, evl_total=0, evt_total=0, strings=0))
    for r in reps:
        p = r['process']; path_ = r['path']; a = r['amount']
        d = P[p]
        if path_.startswith('explicit/'):
            d['explicit'] += a
            d['leaves'][path_] += a
            s = split(path_)
            if len(s) > 4 and s[1] == 'window-objects' and s[2].startswith('top('):
                # top(...)/state/window(URL)/...
                if len(s) > 4 and s[3] in ('active', 'ghost', 'detached') and s[4].startswith('window('):
                    k = (s[3], s[2], s[4])
                    d['win'][k]['bytes'] += a
                    if s[5:] == ['dom', 'element-nodes']:
                        d['win'][k]['n'] += 1; d['win'][k]['elem'] += a
            if s[1] == 'window-objects' and s[2] == 'top(none)':
                if len(s) > 4 and s[3] == 'detached' and s[4].startswith('window('):
                    k = ('detached', s[2], s[4])
                    d['win'][k]['bytes'] += a
                    if s[5:] == ['dom', 'element-nodes']:
                        d['win'][k]['n'] += 1; d['win'][k]['elem'] += a
            if len(s) > 5 and s[1] == 'window-objects' and s[3] in ('active', 'ghost', 'detached') and s[4].startswith('window('):
                k = (s[3], s[2], s[4])
                if s[5:] == ['dom', 'orphan-nodes']: d['win'][k]['orphan'] += a
                elif s[5].startswith('js-realm('): d['win'][k]['jsrealm'] += a
                elif s[5] == 'layout': d['win'][k]['layout'] += a
            if s[1:3] == ['js-non-window', 'zones']:
                d['zones'] += a
                for seg in s:
                    if seg.startswith('realm('):
                        d['realms'][seg] += a; break
                else:
                    if len(s) > 4 and s[4] == 'strings': d['strings'] += a
        elif path_.startswith('ghost-windows/') or path_ == 'ghost-windows':
            if path_ != 'ghost-windows':
                d['ghost_list'].append(path_[len('ghost-windows/'):])
        elif path_.startswith('event-counts/'):
            s = split(path_)
            if s[-2:] == ['dom', 'event-listeners']:
                d['evl_total'] += a
                m = re.match(r'event-counts/window-objects/(top\([^/]*\))/(\w+)/(window\([^/]*\))/', path_)
                if m:
                    d['win'][(m.group(2), m.group(1), m.group(3))]['evl'] += a
            elif s[-2:] == ['dom', 'event-targets']:
                d['evt_total'] += a
    return dict(path=path, truncated=trunc, nreports=len(reps), procs=P)

def state_count(d, state):
    n = sum(v['n'] for k, v in d['win'].items() if k[0] == state)
    b = sum(v['bytes'] for k, v in d['win'].items() if k[0] == state)
    return n, b

def is_main(p): return p.startswith('Main Process')

def print_report(res, topn):
    print('=' * 100)
    print(f"{os.path.basename(res['path'])}  reports={res['nreports']}" + ('  **TRUNCATED FILE**' if res['truncated'] else ''))
    P = res['procs']
    order = sorted(P, key=lambda k: (not is_main(k), -P[k]['explicit']))
    if MAIN_ONLY: order = [p for p in order if is_main(p)]
    print('processes:', len(P))
    for p in order:
        d = P[p]
        gn, gb = state_count(d, 'ghost'); dn, db = state_count(d, 'detached')
        print(f"\n== {p}: explicit {mb(d['explicit'])}  ghost-windows(section)={len(d['ghost_list'])} "
              f"ghost-win(objs)={gn}/{mb(gb)}  detached-win={dn}/{mb(db)}  js-non-window/zones={mb(d['zones'])}")
        if d['ghost_list']:
            print('   ghost-windows entries:', '; '.join(d['ghost_list'][:8]))
        for k, a in d['leaves'].most_common(topn):
            print(f"   {mb(a):>9} {k[:150]}")
        if is_main(p):
            print('   -- Main Process window-objects/top(...) (state, top, window, #win, bytes, element-nodes, orphan-nodes, js-realm, event-listeners)')
            for k, v in sorted(d['win'].items(), key=lambda kv: -kv[1]['bytes']):
                print(f"   {k[0]:8} {k[1][:60]:60} {k[2][:60]:60} n={v['n']:<3} {mb(v['bytes']):>8} elem={mb(v['elem']):>7} orphan={mb(v['orphan']):>8} jsrealm={mb(v['jsrealm']):>7} evl={v['evl']}")
            print(f"   event-listeners total={d['evl_total']} event-targets total={d['evt_total']}")
            print('   -- zones/realm(...) top 10 and any chrome/resource-named realm >1MB')
            for k, a in d['realms'].most_common(10): print(f"   {mb(a):>9} {k[:140]}")
            for k, a in d['realms'].most_common():
                if is_chromey(k) and a > MB and k not in dict(d['realms'].most_common(10)):
                    print(f"   {mb(a):>9} {k[:140]}")

def table_row(res):
    P = res['procs']
    mains = [p for p in P if is_main(p)]
    if not mains: return None
    m = P[mains[0]]
    big = max(P, key=lambda k: P[k]['explicit'])
    gn, gb = state_count(m, 'ghost'); dn, db = state_count(m, 'detached')
    # biggest detached/ghost chrome entries
    sus = sorted(((k, v) for k, v in m['win'].items() if k[0] in ('ghost', 'detached')), key=lambda kv: -kv[1]['bytes'])[:2]
    sus_s = '; '.join(f"{k[0]} {re.sub(r'^window','w',k[2])[:50]} x{v['n']} {mb(v['bytes'])}" for k, v in sus)
    act = sum(v['elem'] for k, v in m['win'].items() if k[0] == 'active' and 'browser.xhtml' in k[2])
    orph = sum(v['orphan'] for k, v in m['win'].items() if k[0] == 'active' and 'browser.xhtml' in k[2])
    nrealm = max(m['realms'].values(), default=0)
    return [os.path.basename(res['path']), 'T' if res['truncated'] else '', mb(m['explicit']), re.sub(r' \(pid.*', '', big) + ' ' + mb(P[big]['explicit']),
            str(len(m['ghost_list'])), f"{gn}/{mb(gb)}", f"{dn}/{mb(db)}", mb(m['zones']), mb(act), str(m['evl_total']), mb(orph), sus_s]

def main(argv):
    global MAIN_ONLY
    topn = 15; table = False; files = []
    it = iter(argv)
    for a in it:
        if a == '--table': table = True
        elif a == '--main-only': MAIN_ONLY = True
        elif a == '--topn': topn = int(next(it))
        else: files.append(a)
    if table:
        print('\t'.join(['file', 'trunc', 'main_explicit', 'biggest_proc', 'ghost_section', 'main_ghost_win', 'main_detached_win',
                         'main_zones', 'main_browser_xhtml_active_elem', 'main_evl_total', 'main_orphan_nodes_browser_xhtml', 'top_ghost_detached']))
    for f in files:
        try: res = analyze(f, topn)
        except Exception as e:
            print(f'{f}: ERROR {e}', file=sys.stderr); continue
        if table:
            r = table_row(res)
            if r: print('\t'.join(r))
        else: print_report(res, topn)

if __name__ == '__main__':
    main(sys.argv[1:])
