import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # öğle → lunch
    s = re.sub(r'\b[öo][ğg]le\b', 'lunch', s, flags=re.I)
    # dilimini kontrol etmenizi öneririm → I recommend checking the time slot
    s = re.sub(r'\bdilimini\s+kontrol\s+etmenizi\s+[öo]neririm\b', 'I recommend checking the time slot', s, flags=re.I)
    # kontrol etmenizi → to check
    s = re.sub(r'\bkontrol\s+etmenizi\b', 'to check', s, flags=re.I)
    # öneririm → I recommend
    s = re.sub(r'\b[öo]neririm\b', 'I recommend', s, flags=re.I)
    # dilimi → time slot
    s = re.sub(r'\bdilimi\b', 'time slot', s, flags=re.I)
    # genel as → generally as
    s = re.sub(r'\bgenel\s+as\b', 'generally as', s, flags=re.I)
    s = re.sub(r'\bgenel\b', 'generally', s, flags=re.I)
    # müşteriler → customers
    s = re.sub(r'\bm[üu][şs]teriler\b', 'customers', s, flags=re.I)
    # görünüyor → appears
    s = re.sub(r'\bg[öo]r[üu]n[üu]yor\b', 'appears', s, flags=re.I)
    # misafir kabul eden → that accepts guests
    s = re.sub(r'\bmisafir\s+kabul\s+eden\b', 'that accepts guests', s, flags=re.I)
    s = re.sub(r'\bmisafir\b', 'guest', s, flags=re.I)
    # yaşayabileceğiniz → where you can experience
    s = re.sub(r'\bya[şs]ayabilece[ğg]iniz\b', 'where you can experience', s, flags=re.I)
    # türleri about → about types of
    s = re.sub(r'\bt[üu]rleri\s+about\b', 'about the types of', s, flags=re.I)
    s = re.sub(r'\bt[üu]rleri\b', 'types', s, flags=re.I)
    # bilgiye ulaşamadım → I couldn't find information
    s = re.sub(r'\bbilgiye\s+ula[şs]amad[ıi]m\b', "I couldn't find information", s, flags=re.I)
    s = re.sub(r'\bula[şs]amad[ıi]m\b', "I couldn't find", s, flags=re.I)
    # olabileceğini göstermektedir → suggests it may be
    s = re.sub(r'\bolabilece[ğg]ini\s+g[öo]stermektedir\b', 'suggests it may be', s, flags=re.I)
    s = re.sub(r'\bg[öo]stermektedir\b', 'indicates', s, flags=re.I)
    # seçeneklerine has → has options for
    s = re.sub(r'\bse[çc]eneklerine\s+has\b', 'has options for', s, flags=re.I)
    s = re.sub(r'\bse[çc]eneklerine\b', 'options', s, flags=re.I)
    # geçirebilirsiniz → you can spend
    s = re.sub(r'\bge[çc]irebilirsiniz\b', 'you can spend', s, flags=re.I)
    # .dir, → . (Turkish suffix artifact)
    s = re.sub(r'\.dir,', '.', s, flags=re.I)
    s = re.sub(r'\bd[ıi]r,', ',', s, flags=re.I)
    # vurgunları → hits / famous spots
    s = re.sub(r'\bvurgunlar[ıi]\b', 'highlights', s, flags=re.I)
    # reservation yapmazsınız → you cannot make reservations
    s = re.sub(r'\breservation\s+yapmaz[ıi]n[ıi]z\.?\b', 'reservations are not taken.', s, flags=re.I)
    # müşterilerin → customers'
    s = re.sub(r'\bm[üu][şs]terilerin\b', "customers'", s, flags=re.I)
    # görünüyor (alternate)
    s = re.sub(r'\bg[öo]r[üu]n[üu]yor\b', 'appears', s, flags=re.I)
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
