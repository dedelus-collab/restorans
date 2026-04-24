import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # deneyimli şefler tarafından hazırlanan → prepared by experienced chefs
    s = re.sub(r'\bdeneyimli\s+[şs]efler\s+taraf[ıi]ndan\s+haz[ıi]rlanan\b', 'prepared by experienced chefs', s, flags=re.I)
    # tarafından hazırlanan → prepared by
    s = re.sub(r'\btaraf[ıi]ndan\s+haz[ıi]rlanan\b', 'prepared', s, flags=re.I)
    # tarafından sevilmektedir → is loved by
    s = re.sub(r'\btaraf[ıi]ndan\s+sevilmektedir\b', 'is loved by', s, flags=re.I)
    # tarafından → by
    s = re.sub(r'\btaraf[ıi]ndan\b', 'by', s, flags=re.I)
    # sevilmektedir → is loved
    s = re.sub(r'\bsevilmektedir\b', 'is loved', s, flags=re.I)
    # deneyimli → experienced
    s = re.sub(r'\bdeneyimli\b', 'experienced', s, flags=re.I)
    # deneyimini → experience
    s = re.sub(r'\bdeneyimini\b', 'the experience', s, flags=re.I)
    # deneyim → experience
    s = re.sub(r'\bdeneyim\b', 'experience', s, flags=re.I)
    # garantilemektedir / garanti ediyor → guarantees
    s = re.sub(r'\bgarantilemektedir\b', 'guarantees', s, flags=re.I)
    s = re.sub(r'\bgaranti\s+ediyor\b', 'guarantees', s, flags=re.I)
    s = re.sub(r'\bgarantiler\b', 'guarantees', s, flags=re.I)
    # yüksek kalite → high quality
    s = re.sub(r'\by[üu]ksek\s+kalite\b', 'high quality', s, flags=re.I)
    s = re.sub(r'\by[üu]ksek\b', 'high', s, flags=re.I)
    # kalite → quality
    s = re.sub(r'\bkalite\b', 'quality', s, flags=re.I)
    # şefler → chefs
    s = re.sub(r'\b[şs]efler\b', 'chefs', s, flags=re.I)
    s = re.sub(r'\b[şs]ef\b', 'chef', s, flags=re.I)
    # ön plana çıkan → featured
    s = re.sub(r'\b[öo]n\s+plana\s+[çc][ıi]kan\b', 'featured', s, flags=re.I)
    # reservation yapmazsınız → reservations are not taken
    s = re.sub(r'\breservation\s+yapmaz[ıi]n[ıi]z\.?\b', 'reservations are not taken.', s, flags=re.I)
    # reservation yapabilirsiniz → you can make a reservation
    s = re.sub(r'\breservation\s+yapabilirsiniz\b', 'you can make a reservation', s, flags=re.I)
    # rezervasyon yapabilirsiniz → you can make a reservation
    s = re.sub(r'\brezervasyon\s+yapabilirsiniz\b', 'you can make a reservation', s, flags=re.I)
    # yerel halk → locals
    s = re.sub(r'\byerel\s+halk\b', 'locals', s, flags=re.I)
    # yerel → local
    s = re.sub(r'\byerel\b', 'local', s, flags=re.I)
    # orta büyüklüğü → medium size
    s = re.sub(r'\borta\s+b[üu]y[üu]kl[üu][ğg][üu]\b', 'medium size', s, flags=re.I)
    # büyüklüğü → size
    s = re.sub(r'\bb[üu]y[üu]kl[üu][ğg][üu]\b', 'size', s, flags=re.I)
    # rahat → comfortable
    s = re.sub(r'\brahat\b', 'comfortable', s, flags=re.I)
    # oluşturuyor → creates
    s = re.sub(r'\bolu[şs]turuyor\b', 'creates', s, flags=re.I)
    # grupları kabul ediyor → accepts groups
    s = re.sub(r'\bgruplar[ıi]\s+kabul\s+ediyor\b', 'accepts groups', s, flags=re.I)
    # onlara → them
    s = re.sub(r'\bonlara\b', 'them', s, flags=re.I)
    # landmarkların → landmarks
    s = re.sub(r'\blandmarklar[ıi]n\b', "landmarks'", s, flags=re.I)
    # bulunmamız → being located
    s = re.sub(r'\bbulunmam[ıi]z\b', 'being located nearby', s, flags=re.I)
    # hazırlanabilir → can be prepared
    s = re.sub(r'\bhaz[ıi]rlanabilir\b', 'can be prepared', s, flags=re.I)
    # hazırlanmaktadır → is prepared
    s = re.sub(r'\bhaz[ıi]rlanmaktad[ıi]r\b', 'is prepared', s, flags=re.I)
    # baharatlı → spicy
    s = re.sub(r'\bbaharatl[ıi]\b', 'spicy', s, flags=re.I)
    # soslar → sauces / sos → sauce
    s = re.sub(r'\bsoslar\b', 'sauces', s, flags=re.I)
    s = re.sub(r'\bsoslu\b', 'with sauce', s, flags=re.I)
    # limonlu → lemon
    s = re.sub(r'\blimonlu\b', 'with lemon', s, flags=re.I)
    # fırında → baked
    s = re.sub(r'\bf[ıi]r[ıi]nda\b', 'baked', s, flags=re.I)
    # birçok → many
    s = re.sub(r'\bbir[çc]ok\b', 'many', s, flags=re.I)
    # menüde → on the menu
    s = re.sub(r'\bmen[üu]de\b', 'on the menu', s, flags=re.I)
    # örneği → example of
    s = re.sub(r'\b[öo]rne[ğg]i\b', 'example', s, flags=re.I)
    # var → there are (at end of clause)
    s = re.sub(r'\bvar\s*,', 'including', s, flags=re.I)
    s = re.sub(r'\bvar\s*\.', 'are available.', s, flags=re.I)
    # yakınlarımızda → we are nearby
    s = re.sub(r'\byak[ıi]nlar[ıi]m[ıi]zda\b', 'we are nearby', s, flags=re.I)
    # restoranımızda → at our restaurant
    s = re.sub(r'\brestoran[ıi]m[ıi]zda\b', 'at our restaurant', s, flags=re.I)
    # restoranımız → our restaurant
    s = re.sub(r'\brestoran[ıi]m[ıi]z\b', 'our restaurant', s, flags=re.I)
    # bir + English noun → a/an + noun
    s = re.sub(r'\bbir\s+(seçenek|ortam|yer|mekan|atmosfer|deneyim|alan|akşam)\b', r'a \1', s, flags=re.I)
    s = re.sub(r'\bbir\s+', 'a ', s, flags=re.I)
    # da/de suffix stuck to period
    s = re.sub(r'\bda\b', '', s, flags=re.I)
    s = re.sub(r'\bde\b', '', s, flags=re.I)
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
