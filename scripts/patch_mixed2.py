import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    s = re.sub(r'\byemeklerimizden\s+baz[ıi]lar[ıi]d[ıi]r\b', 'are some of our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimizden\s+baz[ıi]lar[ıi]\b', 'are some of our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimizden\s+yararlanmak\b', 'to enjoy our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimizin\s+ba[şs][ıi]nda\b', 'at the top of our menu are', s, flags=re.I)
    s = re.sub(r'\byemeklerimizden\s+biridir\b', 'is one of our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimiz\b', 'our dishes', s, flags=re.I)
    s = re.sub(r'\blezzetlerimizden\s+baz[ıi]lar[ıi]\b', 'are some of our flavors', s, flags=re.I)
    s = re.sub(r'\blezzetlerimiz\b', 'our flavors', s, flags=re.I)
    s = re.sub(r"landmark'lar[ıi]m[ıi]z", 'landmarks', s, flags=re.I)
    s = re.sub(r'\blar[ıi]m[ıi]z\b', '', s, flags=re.I)
    s = re.sub(r'beautiful\s+deniz\s+view\s+(ile|with)\b', 'with a beautiful sea view', s, flags=re.I)
    s = re.sub(r'\bdeniz\s+view\b', 'sea view', s, flags=re.I)
    s = re.sub(r'\bmetro\s+dura[ğg][ıi]\b', 'metro stop', s, flags=re.I)
    s = re.sub(r'\botob[üu]s\s+dura[ğg][ıi]\b', 'bus stop', s, flags=re.I)
    s = re.sub(r'\bvapur\s+dura[ğg][ıi]\b', 'ferry stop', s, flags=re.I)
    s = re.sub(r'\bdura[ğg][ıi]\b', 'stop', s, flags=re.I)
    s = re.sub(r'(\d+)\s+\d+\s+min\s+from\s+dk', r'\1 min', s, flags=re.I)
    s = re.sub(r'\bistasyonundan\b', 'station,', s, flags=re.I)
    s = re.sub(r',\s*ndan\b', ',', s, flags=re.I)
    s = re.sub(r'bulunmas[ıi]\s+due\s+to[,.]?\s*', '', s, flags=re.I)
    s = re.sub(r'\bbir\s+metro\s+or\s+otob[üu]s\s+stop\s+yok\b', 'no nearby metro or bus stop', s, flags=re.I)
    s = re.sub(r'\byok\b', 'not available', s, flags=re.I)
    s = re.sub(r'\bbizim\s+en\s+popular\b', 'our most popular', s, flags=re.I)
    s = re.sub(r'\bbizim\b', 'our', s, flags=re.I)
    s = re.sub(r'\bgelmektedir\b', 'are featured', s, flags=re.I)
    s = re.sub(r'  +', ' ', s)
    s = re.sub(r'\s+\.', '.', s)
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

TRULY_TR = re.compile(
    r'\b(ozgu|ise\b|dk\b|vapuru|tramvayi|duragi|larimiz|lerimizden|icin\b|ile\b|veya\b|ama\b|cok\b|daha\b|'
    r'kebaplar[ii]m[ii]z|yemeklerimiz|lezzetlerimiz)\b', re.I)
rem = []
for r in data:
    for qa in r.get('faq', []):
        for f in ['answer', 'question']:
            v = qa.get(f, '')
            m = TRULY_TR.search(v.lower().replace('\u011f','g').replace('\u015f','s').replace('\u00e7','c')
                               .replace('\u00f6','o').replace('\u00fc','u').replace('\u0131','i'))
            if m:
                rem.append((f, v))
print(f'Remaining: {len(rem)}')
for f, v in rem:
    print(f'  {v[:100]}')
