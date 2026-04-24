import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # çocukların enjoyment almasına etki → affecting children's enjoyment
    s = re.sub(r'\b[çc]ocuklar[ıi]n\s+enjoyment\s+almas[ıi]na\s+etki\s+e\w*\b', "affecting children's enjoyment", s, flags=re.I)
    s = re.sub(r'\b[çc]ocuklar[ıi]n\b', "children's", s, flags=re.I)
    s = re.sub(r'\balmas[ıi]na\b', 'enjoyment', s, flags=re.I)
    # ulaşım → transportation / access
    s = re.sub(r'\bula[şs][ıi]m\b', 'transportation', s, flags=re.I)
    # buluşma point → meeting point
    s = re.sub(r'\bbulu[şs]ma\s+point\b', 'meeting point', s, flags=re.I)
    s = re.sub(r'\bbulu[şs]ma\b', 'meeting', s, flags=re.I)
    # Cleanup
    s = re.sub(r'  +', ' ', s)
    s = re.sub(r'\s+\.', '.', s)
    s = re.sub(r',\s*,', ',', s)
    s = re.sub(r'\.\s*\.', '.', s)
    return s.strip()

changed = 0
for r in data:
    for qa in r.get('faq', []):
        for field in ['answer', 'question']:
            o = qa.get(field, '')
            n = fix(o)
            if n != o:
                qa[field] = n
                changed += 1

with open('data/processed/istanbul.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Patched {changed}')

# Full detection - show complete strings
TR2 = re.compile(r'[\u011f\u015f\u00e7\u00f6\u00fc\u0131\u0130\u011e\u015e\u00c7\u00d6\u00dc]')
remaining = set()
for r in data:
    for qa in r.get('faq', []):
        for f in ['answer', 'question']:
            v = qa.get(f, '')
            if not TR2.search(v): continue
            stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\'\s\-\.0-9,\(\)]+', 'X', v)
            if TR2.search(stripped):
                remaining.add(v)
print(f'Remaining: {len(remaining)}')
for v in list(remaining)[:20]:
    print(f'  FULL: {repr(v)}')
    # show what stripped looks like
    stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\'\s\-\.0-9,\(\)]+', 'X', v)
    print(f'  STRIP: {repr(stripped[:100])}')
