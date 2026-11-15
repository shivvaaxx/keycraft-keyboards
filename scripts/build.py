#!/usr/bin/env python3
"""Validate keyboards/**/*.json and build the database Keycraft downloads.

usage: build.py [--check] [--out DIR] [--base-url URL]
  --check     validate only (used on pull requests); exit 1 on any problem
  --out       write DIR/via-keyboards.zlib (raw deflate JSON) and DIR/manifest.json
"""
import argparse, datetime, hashlib, json, os, re, sys, zlib

MAX_BYTES = 1024 * 1024
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def hexid(v):
    if isinstance(v, int): return v
    s = str(v).strip()
    return int(s, 16) if re.fullmatch(r'0x[0-9a-fA-F]{1,4}', s) else None

def problems(d):
    p = []
    if not isinstance(d.get('name'), str) or not d['name'].strip(): p.append('missing name')
    if hexid(d.get('vendorId')) is None: p.append('vendorId must be a hex string like "0x1234"')
    if hexid(d.get('productId')) is None: p.append('productId must be a hex string like "0x1234"')
    m = d.get('matrix') or {}
    rows, cols = m.get('rows'), m.get('cols')
    if not (isinstance(rows, int) and isinstance(cols, int) and rows > 0 and cols > 0): p.append('matrix needs rows and cols')
    km = (d.get('layouts') or {}).get('keymap')
    if not (isinstance(km, list) and km and all(isinstance(r, list) for r in km)):
        p.append('layouts.keymap must be a list of rows'); return p
    keys = 0
    for row in km:
        for item in row:
            if isinstance(item, str):
                pos = item.split('\n')[0].strip()
                mm = re.fullmatch(r'(\d+)\s*,\s*(\d+)', pos)
                if not mm: continue
                keys += 1
                if isinstance(rows, int) and isinstance(cols, int) and (int(mm[1]) >= rows or int(mm[2]) >= cols):
                    p.append(f'key {pos} is outside the {rows}x{cols} matrix')
    if keys == 0: p.append('layout has no keys with "row,col" positions')
    return p

def load_all():
    found, errors, seen = [], [], {}
    for dirpath, _, files in os.walk(os.path.join(ROOT, 'keyboards')):
        for f in sorted(files):
            if not f.endswith('.json'): continue
            path = os.path.join(dirpath, f); rel = os.path.relpath(path, ROOT)
            if os.path.getsize(path) > MAX_BYTES:
                errors.append(f'{rel}: larger than 1 MB'); continue
            try: d = json.load(open(path, encoding='utf-8'))
            except ValueError as e:
                errors.append(f'{rel}: not valid JSON ({e})'); continue
            if not isinstance(d, dict):
                errors.append(f'{rel}: must be a JSON object'); continue
            errors += [f'{rel}: {x}' for x in problems(d)]
            key = (hexid(d.get('vendorId')), hexid(d.get('productId')))
            if None not in key:
                if key in seen: errors.append(f'{rel}: same vendorId/productId as {seen[key]}')
                seen[key] = rel
            d['maker'] = rel.split(os.sep)[1]
            found.append(d)
    return found, errors

def main():
    a = argparse.ArgumentParser()
    a.add_argument('--check', action='store_true'); a.add_argument('--out'); a.add_argument('--base-url', default='')
    args = a.parse_args()
    boards, errors = load_all()
    for e in errors: print('error:', e)
    print(f'{len(boards)} keyboards, {len(errors)} problems')
    if errors: sys.exit(1)
    if args.check or not args.out: return
    boards.sort(key=lambda d: (d['maker'].lower(), d['name'].lower()))
    built = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='seconds')
    blob = json.dumps({'version': 1, 'source': 'keycraft-keyboards (GPL-3.0)', 'builtAt': built, 'keyboards': boards},
                      separators=(',', ':'), ensure_ascii=False).encode()
    c = zlib.compressobj(9, zlib.DEFLATED, -15)     # raw deflate; Swift: NSData.decompressed(using: .zlib)
    data = c.compress(blob) + c.flush()
    os.makedirs(args.out, exist_ok=True)
    open(os.path.join(args.out, 'via-keyboards.zlib'), 'wb').write(data)
    manifest = {'version': 1, 'builtAt': built, 'count': len(boards), 'sha256': hashlib.sha256(data).hexdigest(),
                'url': args.base_url.rstrip('/') + '/via-keyboards.zlib' if args.base_url else 'via-keyboards.zlib'}
    json.dump(manifest, open(os.path.join(args.out, 'manifest.json'), 'w'), indent=2)
    print('wrote', args.out, manifest)

if __name__ == '__main__':
    main()
