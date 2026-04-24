import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # Walking distance
    s = re.sub(r'\by[üu]r[üu]y[üu][şs]\s+mesafesindedir\.?', 'walking distance.', s, flags=re.I)
    s = re.sub(r'\by[üu]r[üu]me\s+mesafesindedir\.?', 'walking distance.', s, flags=re.I)
    s = re.sub(r'\bminutes\s+y[üu]r[üu]y[üu][şs]\s+mesafesindedir\.?', 'minutes walk.', s, flags=re.I)
    s = re.sub(r'\bminutes\s+y[üu]r[üu]me\s+mesafesindedir\.?', 'minutes walk.', s, flags=re.I)
    # uzaklığındadır / uzaklığında / uzaklıktadır
    s = re.sub(r'\buzakl[ıi][ğg][ıi]ndad[ıi]r\.?', 'away.', s, flags=re.I)
    s = re.sub(r'\buzakl[ıi][ğg][ıi]nda\b', 'away', s, flags=re.I)
    s = re.sub(r'\buzakl[ıi]ktad[ıi]r\.?', 'away.', s, flags=re.I)
    s = re.sub(r'\buzakl[ıi][ğg][ıi]\b', 'away', s, flags=re.I)
    # sunmamaktayız → we do not offer
    s = re.sub(r'\bsunmamaktay[ıi]z\b', 'we do not offer', s, flags=re.I)
    # 'dır / 'dir / 'dur after English → is X
    s = re.sub(r"'d[ıi]r\b", ' is', s, flags=re.I)
    s = re.sub(r"'d[üu]r\b", ' is', s, flags=re.I)
    s = re.sub(r'\u2019d[ıi]r\b', ' is', s, flags=re.I)
    # mutfak türü X'dır → cuisine is X
    s = re.sub(r'\bmutfak\s+t[üu]r[üu]\s+(\w[\w\s]+)\s+is\b', r'cuisine is \1', s, flags=re.I)
    # zenginliklerimizi keşfe → our cultural treasures to explore
    s = re.sub(r'\bzenginliklerimizi\s+ke[şs]fe\b', 'our cultural treasures to explore', s, flags=re.I)
    s = re.sub(r'\bzenginliklerimizi\b', 'our treasures', s, flags=re.I)
    s = re.sub(r'\bke[şs]fe\b', 'to explore', s, flags=re.I)
    # yemeklerinden biri → one of the dishes
    s = re.sub(r'\byemeklerinden\s+biri\b', 'one of the dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerinden\b', 'from the dishes', s, flags=re.I)
    # içerir → contains
    s = re.sub(r'\bi[çc]erir\b', 'contains', s, flags=re.I)
    # sitesinden or → website or
    s = re.sub(r'\bweb\s+sitesinden\b', 'website', s, flags=re.I)
    s = re.sub(r'\bsitesinden\b', 'website', s, flags=re.I)
    # direkt → directly
    s = re.sub(r'\bdirekt\b', 'directly', s, flags=re.I)
    # sorulmalıdır → should be asked
    s = re.sub(r'\bsorulmal[ıi]d[ıi]r\.?', 'should be confirmed.', s, flags=re.I)
    # iş arkadaşları → colleagues
    s = re.sub(r'\bi[şs]\s+arkada[şs]lar[ıi]\b', 'colleagues', s, flags=re.I)
    # bulunması → presence / being located
    s = re.sub(r'\bbulunmas[ıi]\b', 'being nearby', s, flags=re.I)
    # öneme has → has significance (Turkish "önem" = importance, used as "has importance")
    s = re.sub(r'\b[öo]neme\s+has\b', 'has historical significance', s, flags=re.I)
    s = re.sub(r'\b[öo]nem\b', 'significance', s, flags=re.I)
    # yapıdır → is a structure
    s = re.sub(r'\byap[ıi]d[ıi]r\b', 'is a historic structure', s, flags=re.I)
    # olmayabilir → may not be
    s = re.sub(r'\bolmayabilir\b', 'may not be suitable', s, flags=re.I)
    # mekanımızdır → is our venue
    s = re.sub(r'\bmekan[ıi]m[ıi]zd[ıi]r\.?', 'is our venue.', s, flags=re.I)
    s = re.sub(r'\bmekan[ıi]m[ıi]z\b', 'our venue', s, flags=re.I)
    # menüsünü → menu
    s = re.sub(r'\bmen[üu]s[üu]n[üu]\b', 'menu', s, flags=re.I)
    # ayarlayabilirsiniz → you can arrange
    s = re.sub(r'\bayarlayabilirsiniz\b', 'you can arrange', s, flags=re.I)
    # değerleri → values
    s = re.sub(r'\bde[ğg]erleri\b', 'values', s, flags=re.I)
    # spesifik → specific
    s = re.sub(r'\bspesifik\b', 'specific', s, flags=re.I)
    # öğle vaktine based on → based on lunchtime
    s = re.sub(r'[öo][ğg]le\s+vaktine\s+based\s+on\b', 'based on lunchtime', s, flags=re.I)
    s = re.sub(r'\b[öo][ğg]le\s+vakti\b', 'lunchtime', s, flags=re.I)
    # open being hours ayarlayabilirsiniz → you can arrange visit hours
    s = re.sub(r'\bopen\s+being\s+hours\s+you\s+can\s+arrange\b', 'you can arrange your visit around opening hours', s, flags=re.I)
    # ziyaretçilerimize → our visitors
    s = re.sub(r'\bziyaret[çc]ilerimize\b', 'our visitors', s, flags=re.I)
    # pizz fiyatları → pizza prices
    s = re.sub(r'\bpizza\s+fiyatlar[ıi]\b', 'pizza prices', s, flags=re.I)
    # fiyatları → prices
    s = re.sub(r'\bfiyatlar[ıi]\b', 'prices', s, flags=re.I)
    # Very beautiful → very beautiful (already English, just leave "çok güzel" cases)
    # bu menü → this menu
    s = re.sub(r'\bbu\s+men[üu]\b', 'this menu', s, flags=re.I)
    # Cleanup
    s = re.sub(r'  +', ' ', s)
    s = re.sub(r'\s+\.', '.', s)
    s = re.sub(r',\s*,', ',', s)
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
for v in list(remaining)[:15]:
    print(f'  {v[:110]}')
