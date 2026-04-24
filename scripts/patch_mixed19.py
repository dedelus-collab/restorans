import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # kutlamanın → of celebrating
    s = re.sub(r'\bkutlaman[ıi]n\b', 'of celebrating', s, flags=re.I)
    # en special → the most special
    s = re.sub(r'\ben\s+special\b', 'the most special', s, flags=re.I)
    # mutfak ekibinin → the kitchen team's
    s = re.sub(r'\bmutfak\s+ekibinin\b', "the kitchen team's", s, flags=re.I)
    s = re.sub(r'\bekibinin\b', "the team's", s, flags=re.I)
    # profesyonellik → professionalism
    s = re.sub(r'\bprofesyonellik\b', 'professionalism', s, flags=re.I)
    # deneyimine dayanır → is based on experience
    s = re.sub(r'\bdeneyimine\s+dayan[ıi]r\b', 'is based on their experience', s, flags=re.I)
    s = re.sub(r'\bdayan[ıi]r\b', 'is based on', s, flags=re.I)
    s = re.sub(r'\bdeneyimine\b', 'of their experience', s, flags=re.I)
    # çocuk → children's (standalone before nouns)
    s = re.sub(r'\b[çc]ocuk\s+suitable\s+for\b', 'suitable for children', s, flags=re.I)
    s = re.sub(r'\bsmall\s+a\s+[çc]ocuk\b', 'a small children\'s', s, flags=re.I)
    s = re.sub(r'\ba\s+[çc]ocuk\s+menu\b', "a children's menu", s, flags=re.I)
    s = re.sub(r'\b[çc]ocuk\s+menu\b', "children's menu", s, flags=re.I)
    s = re.sub(r'\b[çc]ocuk\b', 'children', s, flags=re.I)
    # alanları → areas
    s = re.sub(r'\balan[ıi]m[ıi]z\b', 'our area', s, flags=re.I)
    s = re.sub(r'\balan[ıi]\b', 'area', s, flags=re.I)
    s = re.sub(r'\balanlar[ıi]\b', 'areas', s, flags=re.I)
    # Türk → Turkish (standalone, not already in compound like "Turkish cuisine")
    s = re.sub(r'\bT[üu]rk\b(?!\s+cuisine|\s+classic|\s+music)', 'Turkish', s)
    s = re.sub(r'\bT[üu]rk\b', 'Turkish', s, flags=re.I)
    # diyet/alerji has options for → dietary/allergy options
    s = re.sub(r'\bdiyet/alerji\s+has\s+options\s+for\b', 'dietary/allergy options', s, flags=re.I)
    s = re.sub(r'\bdiyet/alerji\b', 'dietary/allergy', s, flags=re.I)
    s = re.sub(r'\balerji\b', 'allergy', s, flags=re.I)
    s = re.sub(r'\bdiyet\b', 'dietary', s, flags=re.I)
    # iş your meetings → your business meetings
    s = re.sub(r'\bi[şs]\s+your\s+meetings\b', 'your business meetings', s, flags=re.I)
    # needs to meet way menü is prepared → menu is prepared to meet their needs
    s = re.sub(r'\bneeds\s+to\s+meet\s+way\s+menu\s+is\s+prepared\b', 'menu is prepared to meet their needs', s, flags=re.I)
    # oluşturuyor → creates
    s = re.sub(r'\bolu[şs]turuyor\b', 'creates', s, flags=re.I)
    # reservation yapmazsınız → reservations are not taken
    s = re.sub(r'\breservation\s+yapmaz[ıi]n[ıi]z\.?\b', 'reservations are not taken.', s, flags=re.I)
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
    print(f'  {v[:120]}')
