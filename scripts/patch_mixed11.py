import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # esinlenmiştir → is inspired
    s = re.sub(r'\besinlenmi[şs]tir\b', 'is inspired', s, flags=re.I)
    # avantajlı → advantageous
    s = re.sub(r'\bavantajl[ıi]\b', 'advantageous', s, flags=re.I)
    # bulunamadı → not found / not available
    s = re.sub(r'\bbulunamad[ıi]\.?\b', 'not available.', s, flags=re.I)
    # yiyebileceğiniz → where you can enjoy
    s = re.sub(r'\byiyebilece[ğg]iniz\b', 'where you can enjoy', s, flags=re.I)
    s = re.sub(r'\byiyebilirsiniz\b', 'you can eat', s, flags=re.I)
    # konserleri → concerts
    s = re.sub(r'\bkonserleri\b', 'concerts', s, flags=re.I)
    s = re.sub(r'\bkonser\b', 'concert', s, flags=re.I)
    # etkinlikleri → events
    s = re.sub(r'\betkinlikleri\b', 'events', s, flags=re.I)
    s = re.sub(r'\betkinlik\b', 'event', s, flags=re.I)
    # düzenleniyor → are organized
    s = re.sub(r'\bd[üu]zenleniyor\b', 'are organized', s, flags=re.I)
    s = re.sub(r'\bd[üu]zenlenmektedir\b', 'are organized', s, flags=re.I)
    # odak → focus
    s = re.sub(r'\bodak\b', 'focus', s, flags=re.I)
    # organizasyonlarımız → our events/arrangements
    s = re.sub(r'\borganizasyonlar[ıi]m[ıi]z\b', 'our events', s, flags=re.I)
    # open durumdayız → we are open
    s = re.sub(r'\bopen\s+durumdayız\b', 'we are open', s, flags=re.I)
    s = re.sub(r'\bdurumdayız\b', 'we are open', s, flags=re.I)
    # misafirlerin konforu → guests' comfort
    s = re.sub(r'\bmisafirlerin\s+konforu\b', "guests' comfort", s, flags=re.I)
    s = re.sub(r'\bkonforu\b', 'comfort', s, flags=re.I)
    # misafirler → guests
    s = re.sub(r'\bmisafirlerimiz\b', 'our guests', s, flags=re.I)
    s = re.sub(r'\bmisafirler\b', 'guests', s, flags=re.I)
    # her şey düşünülmüştür → everything has been considered
    s = re.sub(r'\bher\s+[şs]ey\s+d[üu][şs][üu]n[üu]lm[üu][şs]t[üu]r\b', 'everything has been considered', s, flags=re.I)
    s = re.sub(r'\bd[üu][şs][üu]n[üu]lm[üu][şs]t[üu]r\b', 'has been considered', s, flags=re.I)
    # her şey → everything
    s = re.sub(r'\bher\s+[şs]ey\b', 'everything', s, flags=re.I)
    # araç with gelmeniz → coming by vehicle
    s = re.sub(r'\bara[çc]\s+with\s+gelmeniz\b', 'coming by vehicle', s, flags=re.I)
    # gelmeniz → coming / your arrival
    s = re.sub(r'\bgelmeniz\b', 'your arrival', s, flags=re.I)
    # gerekmektedir → is required / needed
    s = re.sub(r'\bgerekmektedir\b', 'is required', s, flags=re.I)
    # başvurmanız gerekmektedir → you need to contact
    s = re.sub(r'\bba[şs]vurman[ıi]z\s+is\s+required\b', 'you need to contact', s, flags=re.I)
    s = re.sub(r'\bba[şs]vurman[ıi]z\b', 'you need to contact', s, flags=re.I)
    # malzemeler → ingredients
    s = re.sub(r'\bmalzemeler\b', 'ingredients', s, flags=re.I)
    # hazırlanıyor → are prepared
    s = re.sub(r'\bhaz[ıi]rlan[ıi]yor\b', 'are prepared', s, flags=re.I)
    # arayanlar → seekers / those looking for
    s = re.sub(r'\barayanlar\b', 'seekers', s, flags=re.I)
    # araç → vehicle
    s = re.sub(r'\bara[çc]\b', 'vehicle', s, flags=re.I)
    # olduğumuz for → since we are open
    s = re.sub(r'\boldu[ğg]umuz\s+for\b', 'since we are open', s, flags=re.I)
    s = re.sub(r'\boldu[ğg]umuz\b', 'we are', s, flags=re.I)
    # yapıya nearby → near the structure
    s = re.sub(r'\byap[ıi]ya\s+nearby\b', 'near the historic structure', s, flags=re.I)
    # rahatlıkla → comfortably
    s = re.sub(r'\brahatl[ıi]kla\b', 'comfortably', s, flags=re.I)
    # müşterilerimiz → our customers
    s = re.sub(r'\bm[üu][şs]terilerimiz\b', 'our customers', s, flags=re.I)
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
