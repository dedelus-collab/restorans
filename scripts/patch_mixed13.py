import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # seçenek → option (missed earlier)
    s = re.sub(r'\bse[çc]enek\b', 'option', s, flags=re.I)
    # mutfak seçimi → cuisine choice
    s = re.sub(r'\bmutfak\s+se[çc]imi\b', 'cuisine selection', s, flags=re.I)
    # bulunmaması → absence / lack of
    s = re.sub(r'\bbulunmamas[ıi]\b', 'absence', s, flags=re.I)
    # reservation yapmıyoruz → we don't take reservations
    s = re.sub(r'\breservation\s+yapm[ıi]yoruz\b', "we don't take reservations", s, flags=re.I)
    # gelerek place alabilirsiniz → you can walk in
    s = re.sub(r'\bgelerek\s+place\s+alabilirsiniz\b', 'you can walk in', s, flags=re.I)
    s = re.sub(r'\bgelerek\b', 'by coming in', s, flags=re.I)
    # uluslararası → international
    s = re.sub(r'\buluslararas[ıi]\b', 'international', s, flags=re.I)
    # çıktıktan sonra → after leaving
    s = re.sub(r'\b[çc][ıi]kt[ıi]ktan\s+sonra\b', 'after leaving', s, flags=re.I)
    # ziyaret edebilir → can visit
    s = re.sub(r'\bziyaret\s+edebilir\b', 'can visit', s, flags=re.I)
    s = re.sub(r'\bziyaret\s+edebilirsiniz\b', 'you can visit', s, flags=re.I)
    # fotoğraflar çekebilirsiniz → you can take photos
    s = re.sub(r'\bfoto[ğg]raflar\s+[çc]ekebilirsiniz\b', 'you can take photos', s, flags=re.I)
    s = re.sub(r'\b[çc]ekebilirsiniz\b', 'you can take', s, flags=re.I)
    # puanlıdır → is highly rated
    s = re.sub(r'\bpuanl[ıi]d[ıi]r\b', 'is highly rated', s, flags=re.I)
    # high puanlıdır → is highly rated
    s = re.sub(r'\bhigh\s+puanl[ıi]d[ıi]r\b', 'is highly rated', s, flags=re.I)
    # hazırlanan → prepared
    s = re.sub(r'\bhaz[ıi]rlanan\b', 'prepared', s, flags=re.I)
    # uzmanlaşmış → specialized
    s = re.sub(r'\buzmanla[şs]m[ıi][şs]\b', 'specialized', s, flags=re.I)
    # iç + venue/area → interior
    s = re.sub(r'\bi[çc]\s+our\b', 'our interior', s, flags=re.I)
    # almak for → for getting / to get
    s = re.sub(r'\balmak\s+for\b', 'to make', s, flags=re.I)
    s = re.sub(r'\balmak\b', 'getting', s, flags=re.I)
    # ulaşabilirsiniz → you can reach
    s = re.sub(r'\bula[şs]abilirsiniz\b', 'you can reach', s, flags=re.I)
    # yaşamak for → to experience
    s = re.sub(r'\bya[şs]amak\s+for\b', 'to experience', s, flags=re.I)
    s = re.sub(r'\bya[şs]amak\b', 'experiencing', s, flags=re.I)
    # gelin → come (imperative)
    s = re.sub(r"(\w+'?a)\s+gelin\b", r'visit \1', s, flags=re.I)
    s = re.sub(r'\bgelin\b', 'come visit', s, flags=re.I)
    # haline getirmektedir → makes it
    s = re.sub(r'\bhaline\s+getirmektedir\b', 'makes it', s, flags=re.I)
    s = re.sub(r'\bhaline\b', 'into', s, flags=re.I)
    # lokanta tarzında → in a lokanta style
    s = re.sub(r'\blokanta\s+tarz[ıi]nda\b', 'in a lokanta style', s, flags=re.I)
    # tarzında → in style / in the style of
    s = re.sub(r'\btarz[ıi]nda\b', 'style', s, flags=re.I)
    # kendi arabayla → by your own car
    s = re.sub(r'\bkendi\s+arabayla\b', 'by your own car', s, flags=re.I)
    # kolaydır → is easy
    s = re.sub(r'\bkolayd[ıi]r\b', 'is easy', s, flags=re.I)
    # yolu → way
    s = re.sub(r'\byolu\b', 'way', s, flags=re.I)
    # müzikleri çalınıyor → music is played
    s = re.sub(r'\bm[üu]zikleri\s+[çc]al[ıi]n[ıi]yor\b', 'music is played', s, flags=re.I)
    s = re.sub(r'\b[çc]al[ıi]n[ıi]yor\b', 'is played', s, flags=re.I)
    # müziğin enjoyment → enjoy the music
    s = re.sub(r'\bm[üu]zi[ğg]in\s+enjoyment\b', 'enjoy the music', s, flags=re.I)
    s = re.sub(r'\bm[üu]zi[ğg]in\b', "the music's", s, flags=re.I)
    # kaliteli → quality / high-quality
    s = re.sub(r'\bkaliteli\b', 'high-quality', s, flags=re.I)
    # organik → organic
    s = re.sub(r'\borganik\b', 'organic', s, flags=re.I)
    # et ürünleri → meat products
    s = re.sub(r'\bet\s+[üu]r[üu]nleri\b', 'meat products', s, flags=re.I)
    s = re.sub(r'\b[üu]r[üu]nler\b', 'products', s, flags=re.I)
    s = re.sub(r'\b[üu]r[üu]n\b', 'product', s, flags=re.I)
    # kullanıyoruz → we use
    s = re.sub(r'\bkullan[ıi]yoruz\b', 'we use', s, flags=re.I)
    # organizasyonlarınızı → your events
    s = re.sub(r'\borganizasyonlar[ıi]n[ıi]z[ıi]\b', 'your events', s, flags=re.I)
    # olsa → if
    s = re.sub(r'\bolsa\b', 'if', s, flags=re.I)
    # sonra → after (when following English)
    s = re.sub(r'\bsonra\b', 'after', s, flags=re.I)
    # çıkarabilirsiniz → you can enjoy
    s = re.sub(r'\b[çc][ıi]karabilirsiniz\b', 'you can enjoy', s, flags=re.I)
    # mızda → at our
    s = re.sub(r"\s*,?\s*m[ıi]zda\b", ' at our restaurant', s, flags=re.I)
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
