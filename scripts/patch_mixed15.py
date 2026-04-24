import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # kahvaltı → breakfast
    s = re.sub(r'\bkahvalt[ıi]\b', 'breakfast', s, flags=re.I)
    # ayrı a area → a separate area
    s = re.sub(r'\bayr[ıi]\s+a\s+area\b', 'a separate area', s, flags=re.I)
    s = re.sub(r'\bayr[ıi]\b', 'separate', s, flags=re.I)
    # mutfağından consists of → cuisine consists of
    s = re.sub(r'\bmutfa[ğg][ıi]ndan\s+consists\s+of\b', 'cuisine consists of', s, flags=re.I)
    s = re.sub(r'\bmutfa[ğg][ıi]ndan\b', 'from the cuisine', s, flags=re.I)
    # açısından → in terms of
    s = re.sub(r'\ba[çc][ıi]s[ıi]ndan\b', 'in terms of', s, flags=re.I)
    # toplantılarınız → your meetings
    s = re.sub(r'\btoplant[ıi]lar[ıi]n[ıi]z\b', 'your meetings', s, flags=re.I)
    s = re.sub(r'\btoplant[ıi]\b', 'meeting', s, flags=re.I)
    # etiketi → reputation
    s = re.sub(r'\betiketi\b', 'reputation', s, flags=re.I)
    # durumundadır → is in operation
    s = re.sub(r'\bdurumundad[ıi]r\.?\b', 'is open.', s, flags=re.I)
    # deniz ürünlerine odaklanmıştır → focuses on seafood
    s = re.sub(r'\bdeniz\s+[üu]r[üu]nlerine\s+odaklanm[ıi][şs]t[ıi]r\b', 'focuses on seafood', s, flags=re.I)
    # odaklanmıştır → focuses on
    s = re.sub(r'\bodaklanm[ıi][şs]t[ıi]r\b', 'focuses on', s, flags=re.I)
    # odaklanmaktadır → focuses on
    s = re.sub(r'\bodaklanmaktad[ıi]r\b', 'focuses on', s, flags=re.I)
    # bazı → some
    s = re.sub(r'\bbaz[ıi]\b', 'some', s, flags=re.I)
    # birleşerek → combining / together with
    s = re.sub(r'\bbirle[şs]erek\b', 'combined with', s, flags=re.I)
    # eşsiz → unique
    s = re.sub(r'\be[şs]siz\b', 'unique', s, flags=re.I)
    # içermektedir → includes
    s = re.sub(r'\bi[çc]ermektedir\b', 'includes', s, flags=re.I)
    # mutfağıdır → is the cuisine
    s = re.sub(r'\bmutfa[ğg][ıi]d[ıi]r\b', 'is the cuisine', s, flags=re.I)
    # landmarklar → landmarks
    s = re.sub(r'\blandmarklar\b', 'landmarks', s, flags=re.I)
    # partileri ideal for → parties ideal for
    s = re.sub(r'\bpartileri\s+ideal\s+for\b', 'parties, ideal for', s, flags=re.I)
    # oluşturuyor → creates
    s = re.sub(r'\bolu[şs]turuyor\b', 'creates', s, flags=re.I)
    # orta location → central location
    s = re.sub(r'\borta\s+location\b', 'central location', s, flags=re.I)
    # dinleyerek → while listening
    s = re.sub(r'\bdinleyerek\b', 'while listening', s, flags=re.I)
    # uzaklığı → at a distance / away
    s = re.sub(r'\buzakl[ıi][ğg][ıi]\b', 'away', s, flags=re.I)
    # gruplara → groups (missed earlier)
    s = re.sub(r'\bgruplar[ıi]\b', 'groups', s, flags=re.I)
    s = re.sub(r'\bgruplar\b', 'groups', s, flags=re.I)
    # is. at end where meant "are located"
    s = re.sub(r'\bnearby is\.\s*$', 'are nearby.', s, flags=re.I)
    # "bu restauran" → "this restaurant" (truncated pattern)
    s = re.sub(r'\bbu\s+restauran\b', 'this restaurant', s, flags=re.I)
    # iş toplantılarınız → your business meetings
    s = re.sub(r'\bi[şs]\s+toplant[ıi]lar[ıi]n[ıi]z\b', 'your business meetings', s, flags=re.I)
    # yemeği → meal / dish
    s = re.sub(r'\byeme[ğg]i\b', 'meal', s, flags=re.I)
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
