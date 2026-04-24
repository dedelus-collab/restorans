import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # kebapları → kebabs
    s = re.sub(r'\bkebaplar[ıi]\b', 'kebabs', s, flags=re.I)
    # hazırladığı → prepared / specially prepared
    s = re.sub(r'\bhaz[ıi]rlad[ıi][ğg][ıi]\b', 'specially prepared', s, flags=re.I)
    # restoranında → at the restaurant
    s = re.sub(r'\brestoran[ıi]nda\b', 'at the restaurant', s, flags=re.I)
    # alana has is not → does not have a space
    s = re.sub(r'\balana\s+has\s+is\s+not\b', 'does not have a space', s, flags=re.I)
    s = re.sub(r'\balana\b', 'to the area', s, flags=re.I)
    # aldığından → since it is located
    s = re.sub(r'\bald[ıi][ğg][ıi]ndan\b', 'since it is located', s, flags=re.I)
    # oluşturur → creates
    s = re.sub(r'\bolu[şs]turur\b', 'creates', s, flags=re.I)
    # gruplara → for groups
    s = re.sub(r'\bgruplar[ıi]na\b', 'for groups', s, flags=re.I)
    s = re.sub(r'\bgruplar[ıi]\b', 'groups', s, flags=re.I)
    # menü → menu (lowercase standalone)
    s = re.sub(r'\bmen[üu]\b', 'menu', s, flags=re.I)
    # reservation yapmazsınız → reservations not taken
    s = re.sub(r'\breservation\s+yapmaz[ıi]n[ıi]z\.?', 'No reservations accepted.', s, flags=re.I)
    # customers' needs to meet way → to meet customers' needs
    s = re.sub(r"\bcustomers'\s+needs\s+to\s+meet\s+way\b", "to meet customers' needs", s, flags=re.I)
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
for v in list(remaining)[:25]:
    print(f'  {repr(v[:150])}')
