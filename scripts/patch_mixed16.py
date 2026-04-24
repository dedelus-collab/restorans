import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # niteliği → quality
    s = re.sub(r'\bnite?li[ğg]i\b', 'quality', s, flags=re.I)
    # bilinmektedir → is known
    s = re.sub(r'\bbilinmektedir\b', 'is known', s, flags=re.I)
    # en yakın şekilde → in the nearest way
    s = re.sub(r'\ben\s+yak[ıi]n\s+[şs]ekilde\b', 'in the nearest way', s, flags=re.I)
    s = re.sub(r'\ben\s+yak[ıi]n\b', 'nearest', s, flags=re.I)
    # tanımlayabiliriz → we can describe
    s = re.sub(r'\btan[ıi]mlayabiliriz\b', 'we can describe', s, flags=re.I)
    # Türk klasiklerini içeriyor → includes Turkish classics
    s = re.sub(r'\bT[üu]rk\s+klasiklerini\s+i[çc]eriyor\b', 'includes Turkish classics', s, flags=re.I)
    # klasiklerini → classics
    s = re.sub(r'\bklasiklerini\b', 'classics', s, flags=re.I)
    # içeriyor → includes
    s = re.sub(r'\bi[çc]eriyor\b', 'includes', s, flags=re.I)
    # değiliz → we are not
    s = re.sub(r'\bde[ğg]iliz\b', 'we are not', s, flags=re.I)
    # transit hatı → transit line
    s = re.sub(r'\btransit\s+hat[ıi]\b', 'transit line', s, flags=re.I)
    s = re.sub(r'\bhat[ıi]\b', 'line', s, flags=re.I)
    # manzaramız → our view
    s = re.sub(r'\bmanzaram[ıi]z\b', 'our view', s, flags=re.I)
    # özelliği → feature
    s = re.sub(r'\b[öo]zelli[ğg]i\b', 'feature', s, flags=re.I)
    # Vegan/vegetarian-friendly restorandı → Vegan/vegetarian-friendly restaurant
    s = re.sub(r'\brestoran d[ıi]\b', 'restaurant', s, flags=re.I)
    s = re.sub(r'\brestoran[dD][ıiİI]\b', 'restaurant', s, flags=re.I)
    # gruplara → groups (re-apply)
    s = re.sub(r'\bgruplar[ıi]na\b', 'for groups', s, flags=re.I)
    s = re.sub(r'\bgruplar[ıi]\b', 'groups', s, flags=re.I)
    # önemli → important / significant
    s = re.sub(r'\b[öo]nemli\b', 'important', s, flags=re.I)
    # mekandır → is a venue
    s = re.sub(r'\bmekan[dD][ıiİI]r\.?\b', 'is a venue.', s, flags=re.I)
    # puanımız → our rating
    s = re.sub(r'\bpuan[ıi]m[ıi]z\b', 'our rating', s, flags=re.I)
    # sizleri bekliyoruz → we welcome you
    s = re.sub(r'\bsizleri\s+bekliyoruz\b', 'we welcome you', s, flags=re.I)
    s = re.sub(r'\bbekliyoruz\b', 'we await you', s, flags=re.I)
    s = re.sub(r'\bsizleri\b', 'you', s, flags=re.I)
    # şaraplar → wines
    s = re.sub(r'\b[şs]araplar\b', 'wines', s, flags=re.I)
    s = re.sub(r'\b[şs]arap\b', 'wine', s, flags=re.I)
    # var mı? → is available?
    s = re.sub(r'\bvar\s+m[ıi]\?\s*$', 'available?', s, flags=re.I)
    s = re.sub(r'\bvar\s+m[ıi]\b', 'available', s, flags=re.I)
    s = re.sub(r'\bvar\s*\?\s*$', 'available?', s, flags=re.I)
    # restorandı → restaurant (Turkish past)
    s = re.sub(r'\brestoran[dD][ıi]\b', 'restaurant', s, flags=re.I)
    # small çocuklara → for small children
    s = re.sub(r'\bsmall\s+[çc]ocuklara\b', 'for small children', s, flags=re.I)
    s = re.sub(r'\b[çc]ocuklara\b', 'for children', s, flags=re.I)
    # oluşturuyor → creates (re-apply)
    s = re.sub(r'\bolu[şs]turuyor\b', 'creates', s, flags=re.I)
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
