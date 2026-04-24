import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # reservation yapmazsınız (missed the ş before ınız)
    s = re.sub(r'\breservation\s+yapmazs[ıi]n[ıi]z\.?', 'No reservations accepted.', s, flags=re.I)
    s = re.sub(r'\brezervasyons?[ıi]z\.?', 'without reservation.', s, flags=re.I)
    # mutfak türü → cuisine type
    s = re.sub(r'\bmutfak\s+t[üu]r[üu]\b', 'cuisine type', s, flags=re.I)
    # gideceğim nedenler → reasons to go
    s = re.sub(r'\bgidece[ğg]im\s+nedenler\b', 'reasons to go', s, flags=re.I)
    s = re.sub(r'\bgidece[ğg]im\b', 'I will go', s, flags=re.I)
    # restoranımıza → to our restaurant
    s = re.sub(r'\brestoran[ıi]m[ıi]za\b', 'to our restaurant', s, flags=re.I)
    # ulaşmak → to reach
    s = re.sub(r'\bula[şs]mak\b', 'to reach', s, flags=re.I)
    # iyi olur → would be good
    s = re.sub(r'\biyi\s+olur\b', 'would be good', s, flags=re.I)
    s = re.sub(r'\biyi\b', 'good', s, flags=re.I)
    # sevgililer → couples / lovers
    s = re.sub(r'\bsevgililer\b', 'couples', s, flags=re.I)
    # dikkat çekiyor → attracts attention
    s = re.sub(r'\bdikkat\s+[çc]ekiyor\b', 'attracts attention', s, flags=re.I)
    s = re.sub(r'\bdikkat\b', 'attention', s, flags=re.I)
    # çocuklu → families with children (re-apply for missed ones)
    s = re.sub(r'\b[çc]ocuklu\b', 'families with children', s, flags=re.I)
    # tarzını Turkish cuisine as we can describe → can be described as Turkish cuisine
    s = re.sub(r'\btarz[ıi]n[ıi]\s+Turkish\s+cuisine\s+as\s+we\s+can\s+describe\b', 'can be described as Turkish cuisine', s, flags=re.I)
    # türü fish and Turkish is the cuisine → fish and Turkish cuisine
    s = re.sub(r'\bcuisine\s+type\s+fish\s+and\s+Turkish\s+is\s+the\s+cuisine\b', 'fish and Turkish cuisine', s, flags=re.I)
    s = re.sub(r'\bcuisine\s+type\s+Turkish\s+cuisine\b', 'Turkish cuisine', s, flags=re.I)
    s = re.sub(r'\bcuisine\s+type\s+Turkish\s+and\b', 'Turkish cuisine and', s, flags=re.I)
    s = re.sub(r'\bcuisine\s+type\s+Turkish\b', 'Turkish cuisine', s, flags=re.I)
    s = re.sub(r'\bcuisine\s+type\b', 'cuisine', s, flags=re.I)
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
for v in list(remaining)[:30]:
    print(f'  {repr(v[:180])}')
