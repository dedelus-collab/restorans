import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # Garbage fragments
    s = re.sub(r'\.\s*bir\s+ortam[ıi]m[ıi]z\.?\s*$', '.', s, flags=re.I)
    s = re.sub(r'\bbir\s+mekan\s+as\s+g[öo]r[üu]lebilir\.?', '', s, flags=re.I)
    s = re.sub(r'\bbir\s+ortam[ıi]m[ıi]z\.?', '', s, flags=re.I)
    # yoktur → is not available
    s = re.sub(r'\byoktur\b', 'is not available', s, flags=re.I)
    # teras alanı → terrace area
    s = re.sub(r'\bteras\s+alan[ıi]\b', 'terrace area', s, flags=re.I)
    s = re.sub(r'\bteras[ıi]m[ıi]z\b', 'our terrace', s, flags=re.I)
    # geniş → spacious
    s = re.sub(r'\bgeni[şs]\b', 'spacious', s, flags=re.I)
    # tramvay → tram
    s = re.sub(r'\btramvay\b', 'tram', s, flags=re.I)
    # hizmetiyle → with its service / hizmetimiz → our service / hizmetimizle → with our service
    s = re.sub(r'\bhizmetiyle\b', 'with its service', s, flags=re.I)
    s = re.sub(r'\bhizmetimizle\b', 'with our service', s, flags=re.I)
    s = re.sub(r'\bhizmetimiz\b', 'our service', s, flags=re.I)
    # sunduğumuz → our
    s = re.sub(r'\bsundu[ğg]umuz\b', 'our', s, flags=re.I)
    # sunulduğu bir yerdir → is a place offering
    s = re.sub(r'\bsunuldu[ğg]u\s+bir\s+yerdir\b', 'are offered here', s, flags=re.I)
    s = re.sub(r'\bsunuldu[ğg]u\b', 'offered', s, flags=re.I)
    # uygunluğu yüksek → highly suitable
    s = re.sub(r'\buygunlu[ğg]u\s+y[üu]ksek\b', 'highly suitable', s, flags=re.I)
    s = re.sub(r'\buygunlu[ğg]u\b', 'suitability', s, flags=re.I)
    # vegan menü option not available → vegan options not available
    s = re.sub(r'vegan\s+men[üu]\s+option\s+not\s+available', 'No vegan options available.', s, flags=re.I)
    # vegan seçenekler does not offer → does not offer vegan options
    s = re.sub(r'vegan\s+se[çc]enekler\s+does\s+not\s+offer', 'does not offer vegan options', s, flags=re.I)
    # seçenekler → options
    s = re.sub(r'\bse[çc]enekler\b', 'options', s, flags=re.I)
    # ortam → atmosphere
    s = re.sub(r'\bortam\b', 'atmosphere', s, flags=re.I)
    # grup rezervasyonları kabul ediyor → accepts group reservations
    s = re.sub(r'\bgrup\s+rezervasyonlar[ıi]\s+kabul\s+ediyor\b', 'accepts group reservations', s, flags=re.I)
    # partileri düzenlenebilir → parties can be organized
    s = re.sub(r'partileri\s+d[üu]zenlenebilir\b', 'parties can be organized', s, flags=re.I)
    # alanlar temin edilebilir → spaces can be provided
    s = re.sub(r'alanlar\s+temin\s+edilebilir\b', 'spaces can be provided', s, flags=re.I)
    # alan → area / space
    s = re.sub(r'\balan[ıi]\b', 'area', s, flags=re.I)
    s = re.sub(r'\balan\b', 'area', s, flags=re.I)
    # söylenmemektedir → is not stated / söylenemez
    s = re.sub(r'\bs[öo]ylenmemektedir\b', 'is not stated', s, flags=re.I)
    # bu nedenle → therefore
    s = re.sub(r'\bbu\s+nedenle\b', 'therefore', s, flags=re.I)
    # varsayabiliriz → we can assume
    s = re.sub(r'\bvarsayabiliriz\b', 'we can assume', s, flags=re.I)
    # tanınıyor → is known
    s = re.sub(r'\btan[ıi]n[ıi]yor\b', 'is known', s, flags=re.I)
    # hazırlanışını anlatabilir → can explain how it is prepared
    s = re.sub(r'haz[ıi]rlan[ıi][şs][ıi]n[ıi]\s+anlatabilir\b', 'can explain how it is prepared', s, flags=re.I)
    # etin özenle seçilmesi → careful selection of the meat
    s = re.sub(r'etin\s+[öo]zenle\s+se[çc]ilmesi\b', 'careful selection of the meat', s, flags=re.I)
    # özenle → carefully
    s = re.sub(r'\b[öo]zenle\b', 'carefully', s, flags=re.I)
    # seçilmesi → selection
    s = re.sub(r'\bse[çc]ilmesi\b', 'selection', s, flags=re.I)
    # kişi başı → per person
    s = re.sub(r'\bKi[şs]i\s+ba[şs][ıi]\b', 'Per person,', s, flags=re.I)
    s = re.sub(r'\bki[şs]i\s+ba[şs][ıi]\b', 'per person', s, flags=re.I)
    # fiyat aralığını bilmeniz gerekir → you should check the price range
    s = re.sub(r'fiyat\s+aral[ıi][ğg][ıi]n[ıi]\s+bilmeniz\s+gerekir\.?', 'you should check the price range.', s, flags=re.I)
    # "deniz ürünlerinden consists of" → "consists of seafood"
    s = re.sub(r'deniz\s+[üu]r[üu]nlerinden\s+consists\s+of\b', 'consists of seafood', s, flags=re.I)
    # deniz ürünleri → seafood
    s = re.sub(r'\bdeniz\s+[üu]r[üu]nleri\b', 'seafood', s, flags=re.I)
    # "romantic bir akşam for uygunluğu yüksek" → "highly suitable for a romantic evening"
    s = re.sub(r'romantic\s+bir\s+ak[şs]am\s+for\s+highly\s+suitable\b', 'highly suitable for a romantic evening', s, flags=re.I)
    s = re.sub(r'\bak[şs]am\b', 'evening', s, flags=re.I)
    # Hayır → No
    s = re.sub(r'^[Hh]ay[ıi]r,\s*', 'No, ', s)
    s = re.sub(r'^[Hh]ay[ıi]r\.?\s*$', 'No.', s.strip())
    # Evet → Yes
    s = re.sub(r'^[Ee]vet,\s*', 'Yes, ', s)
    # kabul etmektedir → welcomes / accepts
    s = re.sub(r'\bkabul\s+etmektedir\b', 'accepts', s, flags=re.I)
    # Cleanup
    s = re.sub(r'  +', ' ', s)
    s = re.sub(r'\s+\.', '.', s)
    s = re.sub(r',\s*,', ',', s)
    s = re.sub(r'\.\s*\.\s*', '. ', s)
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
            stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\'\s\-\.0-9]+', 'X', v)
            if TR2.search(stripped):
                remaining.add(v)
print(f'Remaining: {len(remaining)}')
for v in list(remaining)[:20]:
    print(f'  {v[:110]}')
