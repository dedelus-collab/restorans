import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # fiyatlarımız → our prices
    s = re.sub(r'\bfiyatlar[ıi]m[ıi]z\b', 'our prices', s, flags=re.I)
    # ortamımız → our atmosphere
    s = re.sub(r'\bortam[ıi]m[ıi]z\b', 'our atmosphere', s, flags=re.I)
    # sebebiyle → because of / due to
    s = re.sub(r'\bsebebiyle\b', 'due to', s, flags=re.I)
    # çocuk menüleri → children's menus
    s = re.sub(r'\b[çc]ocuk\s+men[üu]leri\b', "children's menus", s, flags=re.I)
    # çocuk menüsü → children's menu
    s = re.sub(r'\b[çc]ocuk\s+men[üu]s[üu]\b', "children's menu", s, flags=re.I)
    # çocuk dostu/dostudur → child-friendly
    s = re.sub(r'\b[çc]ocuk\s+dostudur\.?\b', 'is child-friendly.', s, flags=re.I)
    s = re.sub(r'\b[çc]ocuk\s+dostu\b', 'child-friendly', s, flags=re.I)
    # iletişime geçilerek → by contacting
    s = re.sub(r'\bilet[ıi][şs]ime\s+ge[çc]ilerek\b', 'by contacting', s, flags=re.I)
    s = re.sub(r'\bilet[ıi][şs]ime\s+ge[çc]erek\b', 'by contacting', s, flags=re.I)
    # bilgi alabilirsiniz → you can get information
    s = re.sub(r'\bbilgi\s+alabilirsiniz\b', 'you can get information', s, flags=re.I)
    # bilgi → information
    s = re.sub(r'\bbilgi\b', 'information', s, flags=re.I)
    # sunmamız sebebiyle → because we offer
    s = re.sub(r'\bsunmam[ıi]z\s+sebebiyle\b', 'because we offer', s, flags=re.I)
    s = re.sub(r'\bsunmam[ıi]z\b', 'our offering', s, flags=re.I)
    # restoranımızın terasından → from our restaurant's terrace
    s = re.sub(r'\brestoran[ıi]m[ıi]z[ıi]n\s+teras[ıi]ndan\b', "from our restaurant's terrace", s, flags=re.I)
    s = re.sub(r'\brestoran[ıi]m[ıi]z[ıi]n\b', "our restaurant's", s, flags=re.I)
    # terasımızda → on our terrace
    s = re.sub(r'\bteras[ıi]m[ıi]zda\b', 'on our terrace', s, flags=re.I)
    # oturabilirsiniz → you can sit
    s = re.sub(r'\boturabilirsiniz\b', 'you can sit', s, flags=re.I)
    # mekandır → is a venue
    s = re.sub(r'\bmeband[ıi]r\b', 'is a venue', s, flags=re.I)
    # mutfak türüne based on → based on its cuisine
    s = re.sub(r'\bmutfak\s+t[üu]r[üu]ne\s+based\s+on\b', 'based on its cuisine', s, flags=re.I)
    s = re.sub(r'\bmutfak\s+t[üu]r[üu]n[üu]n\b', "of its cuisine", s, flags=re.I)
    # sunduğu çeşitlilik → the variety it offers
    s = re.sub(r'\bsundu[ğg]u\s+[çc]e[şs]itlilik\b', 'the variety it offers', s, flags=re.I)
    # çeşitlilik → variety
    s = re.sub(r'\b[çc]e[şs]itlilik\b', 'variety', s, flags=re.I)
    # gidebilirsiniz → you can go
    s = re.sub(r'\bgidebilirsiniz\b', 'you can go', s, flags=re.I)
    # yaklaşık → approximately
    s = re.sub(r'\byakla[şs][ıi]k\b', 'approximately', s, flags=re.I)
    # herhangi → any
    s = re.sub(r'\bherhangi\b', 'any', s, flags=re.I)
    # yeşil alan → green space
    s = re.sub(r'\bye[şs]il\s+area\b', 'green space', s, flags=re.I)
    s = re.sub(r'\bye[şs]il\b', 'green', s, flags=re.I)
    # tüm ihtiyaçlarınıza cevap → all your needs
    s = re.sub(r'\bt[üu]m\s+ihtiya[çc]lar[ıi]n[ıi]za\s+cevap\b', 'all your needs', s, flags=re.I)
    # tüm → all
    s = re.sub(r'\bt[üu]m\b', 'all', s, flags=re.I)
    # ihtiyaçlarınıza → your needs
    s = re.sub(r'\bihtiya[çc]lar[ıi]n[ıi]za\b', 'your needs', s, flags=re.I)
    # cevap → response
    s = re.sub(r'\bcevap\b', 'response', s, flags=re.I)
    # gitmeden önce → before going
    s = re.sub(r'\bgitmeden\s+[öo]nce\b', 'before going', s, flags=re.I)
    # öğrenmelisiniz → you should find out
    s = re.sub(r'\b[öo][ğg]renmelisiniz\b', 'you should find out', s, flags=re.I)
    # eşliğinde → accompanied by
    s = re.sub(r'\be[şs]li[ğg]inde\b', 'accompanied by', s, flags=re.I)
    # hoşlananlar → those who enjoy
    s = re.sub(r'\bho[şs]lananlar\b', 'those who enjoy', s, flags=re.I)
    s = re.sub(r'\bho[şs]lanlar\b', 'enthusiasts', s, flags=re.I)
    # yapılıyor → is organized / takes place
    s = re.sub(r'\byap[ıi]l[ıi]yor\b', 'is organized', s, flags=re.I)
    # çevrede → around / nearby
    s = re.sub(r'\b[çc]evrede\b', 'nearby', s, flags=re.I)
    # tamamen → completely / fully
    s = re.sub(r'\btamamen\b', 'fully', s, flags=re.I)
    # diyet or alerji sorunu kişiler → people with dietary or allergy concerns
    s = re.sub(r'\bdiyet\s+or\s+alerji\s+sorunu\s+ki[şs]iler\b', 'people with dietary or allergy concerns', s, flags=re.I)
    # sorunu → concern / issue
    s = re.sub(r'\bsorunu\b', 'concern', s, flags=re.I)
    # kişiler → people
    s = re.sub(r'\bki[şs]iler\b', 'people', s, flags=re.I)
    # korusu → grove (often part of place name)
    # location öğrenmelisiniz → should find out the location
    s = re.sub(r'\blocation\s+[öo][ğg]renmelisiniz\b', 'should find out the location', s, flags=re.I)
    # event yapılıyor → events are organized
    s = re.sub(r'\bevent\s+yap[ıi]l[ıi]yor\b', 'events are organized', s, flags=re.I)
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
for v in list(remaining)[:20]:
    print(f'  {v[:120]}')
