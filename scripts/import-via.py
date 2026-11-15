#!/usr/bin/env python3
"""Import layouts from a checkout of github.com/the-via/keyboards (GPL-3.0) into keyboards/<maker>/.

usage: import-via.py <the-via-keyboards-checkout> [<repo-root>]
v3/ definitions win over the older src/ (v2) ones; one file per vendorId:productId.
Existing files in keyboards/ are kept, so local additions are never overwritten.
"""
import json, os, re, sys
sys.path.insert(0, os.path.dirname(__file__))
from build import hexid, problems

def main():
    src, root = sys.argv[1], (sys.argv[2] if len(sys.argv) > 2 else os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    out = os.path.join(root, 'keyboards')
    taken = {}
    for dirpath, _, files in os.walk(out):
        for f in files:
            if f.endswith('.json'):
                d = json.load(open(os.path.join(dirpath, f)))
                taken[(hexid(d['vendorId']), hexid(d['productId']))] = True
    added = 0
    for sub in ('v3', 'src'):
        for dirpath, _, files in sorted(os.walk(os.path.join(src, sub))):
            for f in sorted(files):
                if not f.endswith('.json'): continue
                rel = os.path.relpath(os.path.join(dirpath, f), os.path.join(src, sub)).split(os.sep)
                try: d = json.load(open(os.path.join(dirpath, f), encoding='utf-8'))
                except ValueError: continue
                if not isinstance(d, dict) or problems(d): continue
                key = (hexid(d['vendorId']), hexid(d['productId']))
                if key in taken: continue
                maker = rel[0] if len(rel) > 1 else 'other'
                stem = re.sub(r'[^a-z0-9]+', '-', '-'.join(rel[1:])[:-5].lower()).strip('-') or 'keyboard'
                path = os.path.join(out, maker, stem + '.json')
                if os.path.exists(path):
                    path = os.path.join(out, maker, f'{stem}-{key[0]:04x}{key[1]:04x}.json')
                os.makedirs(os.path.dirname(path), exist_ok=True)
                json.dump(d, open(path, 'w'), indent=2, ensure_ascii=False); open(path, 'a').write('\n')
                taken[key] = True; added += 1
    print(f'imported {added} keyboards')

if __name__ == '__main__':
    main()
