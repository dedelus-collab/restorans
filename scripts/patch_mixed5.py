import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # Garbage suffixes stuck to English words
    s = re.sub(r'\.\s*[ıiuü]z\.?\s*$', '.', s, flags=re.I)   # ".ız" at end
    s = re.sub(r'\.\s*[ıiuü]z[,.]', '.', s, flags=re.I)
    s = re.sub(r',\s*[ıiuü]z\b', '', s, flags=re.I)
    s = re.sub(r'\bbir,\s*zd[ıi]r\b\.?', '.', s, flags=re.I)  # "bir, zdır"
    s = re.sub(r',\s*zd[ıi]r\b\.?', '.', s, flags=re.I)
    s = re.sub(r'\bzdır\b', '', s, flags=re.I)
    # değildir → is not
    s = re.sub(r'\bde[ğg]ildir\b', 'is not', s, flags=re.I)
    s = re.sub(r'\bde[ğg]il\b', 'not', s, flags=re.I)
    # manzaralıdır → has a view
    s = re.sub(r'\bmanzaral[ıi]d[ıi]r\b', 'has a view', s, flags=re.I)
    s = re.sub(r'\bmanzaral[ıi]\b', 'scenic', s, flags=re.I)
    # terası → the terrace
    s = re.sub(r'\bteras[ıi]\b', 'the terrace', s, flags=re.I)
    # restoranlar → restaurants
    s = re.sub(r'\brestoran(?:lar[ıi]?|a|da|ı|ın|dan|ımız)?\b', 'restaurant', s, flags=re.I)
    # arası open / arası → between
    s = re.sub(r'\baras[ıi]\s+open\b', 'open', s, flags=re.I)
    s = re.sub(r'\baras[ıi]\b', 'between', s, flags=re.I)
    # durumdadır → (remove - redundant)
    s = re.sub(r'\s*durumdad[ıi]r\.?', '.', s, flags=re.I)
    # çocuk kabul etmektedir → children are welcome
    s = re.sub(r'[çc]ocuk\s+kabul\s+etmektedir\.?', 'children are welcome.', s, flags=re.I)
    # sıcak → warm
    s = re.sub(r'\bs[ıi]cak\b', 'warm', s, flags=re.I)
    # misafirperverdir / misafirperver → welcoming
    s = re.sub(r'\bmisafirperverd[ıi]r\b', 'is welcoming', s, flags=re.I)
    s = re.sub(r'\bmisafirperver\b', 'welcoming', s, flags=re.I)
    # söylenemez → cannot be said
    s = re.sub(r'\bs[öo]ylenemez\b', 'cannot be said', s, flags=re.I)
    # her gün → every day
    s = re.sub(r'\bher\s+g[üu]n\b', 'every day', s, flags=re.I)
    # müzik → music
    s = re.sub(r'\bm[üu]zik\b', 'music', s, flags=re.I)
    # kalmak → to stay
    s = re.sub(r'\bkalmak\b', 'to stay', s, flags=re.I)
    # kolay ulaşımı sağlayacaktır → provides easy access
    s = re.sub(r'kolay\s+ula[şs][ıi]m[ıi]\s+sa[ğg]layacakt[ıi]r\.?', 'provides easy access.', s, flags=re.I)
    # mıza kolay → easy access for us
    s = re.sub(r',\s*m[ıi]za\b', ',', s, flags=re.I)
    # vegan mutfak türünü → vegan cuisine
    s = re.sub(r'\bvegan\s+mutfak\s+t[üu]r[üu]n[üu]\b', 'vegan cuisine', s, flags=re.I)
    # nearby kalmak → staying nearby
    s = re.sub(r'\bnearby\s+kalmak\b', 'staying nearby', s, flags=re.I)
    # "traditional Türk müziği"
    s = re.sub(r'\bT[üu]rk\s+m[üu]zi[ğg]i\b', 'Turkish music', s, flags=re.I)
    # традицион (Russian/Cyrillic) → traditional
    s = re.sub(r'традицион\b', 'traditional', s, flags=re.I)
    # "nın nearby is located" → "is nearby"
    s = re.sub(r',\s*n[ıi]n\s+nearby\s+is\s+located\.?', ' is nearby.', s, flags=re.I)
    s = re.sub(r"\s+'?n[ıi]n\s+nearby\s+is\s+located\.?", ' is nearby.', s, flags=re.I)
    # "X'nın nearby is located" fix
    s = re.sub(r"'s\s+nearby\s+is\s+located\b", ' is nearby', s, flags=re.I)
    # "but, n beautiful" → "but a beautiful"
    s = re.sub(r'\bbut,\s*n\s+\b', 'but a ', s, flags=re.I)
    # "atmosfer" remaining
    s = re.sub(r'\batmosfer\b', 'atmosphere', s, flags=re.I)
    # büyük → large (remaining)
    s = re.sub(r'\bb[üu]y[üu]k\b', 'large', s, flags=re.I)
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

# Count remaining Turkish outside proper nouns
TR2 = re.compile(r'[\u011f\u015f\u00e7\u00f6\u00fc\u0131\u0130\u011e\u015e\u00c7\u00d6\u00dc]')
remaining = []
for r in data:
    for qa in r.get('faq', []):
        for f in ['answer', 'question']:
            v = qa.get(f, '')
            if not TR2.search(v): continue
            stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\'\s\-\.0-9]+', 'X', v)
            if TR2.search(stripped):
                remaining.append(v)
seen = set(remaining)
print(f'Remaining with Turkish outside proper nouns: {len(seen)}')
for v in list(seen)[:20]:
    print(f'  {v[:110]}')
