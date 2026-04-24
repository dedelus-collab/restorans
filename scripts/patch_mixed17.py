import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # kadınlar → women
    s = re.sub(r'\bkad[ıi]nlar\b', 'women', s, flags=re.I)
    s = re.sub(r'\bkad[ıi]n\b', 'woman', s, flags=re.I)
    # ilgili a ilişkimiz → our connection
    s = re.sub(r'\bilgili\s+a\s+ili[şs]kimiz\b', 'our connection', s, flags=re.I)
    s = re.sub(r'\bili[şs]kimiz\b', 'our connection', s, flags=re.I)
    # ilgili → related to / about
    s = re.sub(r'\bilgili\b', 'related to', s, flags=re.I)
    # olmanın advantage → the advantage of being
    s = re.sub(r'\bolman[ıi]n\s+advantage\b', 'the advantage of being open late', s, flags=re.I)
    s = re.sub(r'\bolman[ıi]n\b', 'of being', s, flags=re.I)
    # mutfağındaki → in the cuisine
    s = re.sub(r'\bmutfa[ğg][ıi]ndaki\b', "in the cuisine", s, flags=re.I)
    # Türkçe as is available → is available in Turkish
    s = re.sub(r'\bT[üu]rk[çc]e\s+as\s+is\s+available\b', 'is available', s, flags=re.I)
    s = re.sub(r'\bT[üu]rk[çc]e\b', 'in Turkish', s, flags=re.I)
    # gün geçirme → spending the day
    s = re.sub(r'\bg[üu]n\s+ge[çc]irme\b', 'day out', s, flags=re.I)
    # zaman geçiriyorsunuz → you spend time
    s = re.sub(r'\bzaman\s+ge[çc]iriyorsunuz\b', 'you spend time', s, flags=re.I)
    s = re.sub(r'\bzaman\b', 'time', s, flags=re.I)
    # konumundan kaynaklanıyor → stems from the location
    s = re.sub(r'\bkonumundan\s+kaynaklan[ıi]yor\b', 'stems from the location', s, flags=re.I)
    s = re.sub(r'\bkaynaklan[ıi]yor\b', 'stems from', s, flags=re.I)
    # kapanış → closing
    s = re.sub(r'\bkapan[ıi][şs]\b', 'closing', s, flags=re.I)
    # açılış → opening
    s = re.sub(r'\ba[çc][ıi]l[ıi][şs]\b', 'opening', s, flags=re.I)
    # belli not → not certain / not fixed
    s = re.sub(r'\bbelli\s+not\b', 'not fixed', s, flags=re.I)
    s = re.sub(r'\bbelli\b', 'certain', s, flags=re.I)
    # tahmin edilebilir → can be estimated
    s = re.sub(r'\btahmin\s+edilebilir\b', 'can be estimated', s, flags=re.I)
    # kabul ediliyor → are welcome
    s = re.sub(r'\bkabul\s+ediliyor\b', 'are welcome', s, flags=re.I)
    # arayışındaysanız → if you are looking for
    s = re.sub(r'\baray[ıi][şs][ıi]ndaysan[ıi]z\b', 'if you are looking for', s, flags=re.I)
    # gruplara → for groups
    s = re.sub(r'\bgruplar[ıi]na\b', 'for groups', s, flags=re.I)
    s = re.sub(r'\bgruplar[ıi]\b', 'groups', s, flags=re.I)
    # bu restaurant → this restaurant
    s = re.sub(r'\bbu\s+restaurant\b', 'this restaurant', s, flags=re.I)
    # geçirme → spending
    s = re.sub(r'\bge[çc]irme\b', 'spending', s, flags=re.I)
    # henüz → yet
    s = re.sub(r'\bhen[üu]z\b', 'yet', s, flags=re.I)
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
