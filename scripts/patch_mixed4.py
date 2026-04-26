import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # öne çıkıyor/çıkan → stands out / prominent
    s = re.sub(r'\b[öo]ne\s+[çc][ıi]k[ıi]yor\b', 'stands out', s, flags=re.I)
    s = re.sub(r'\b[öo]ne\s+[çc][ıi]kan\b', 'prominent', s, flags=re.I)
    # yer alır/alıyor/alıyor → can be found / is available
    s = re.sub(r'\byer\s+al[ıi]r\b', 'can be found', s, flags=re.I)
    s = re.sub(r'\byer\s+al[ıi]yor\b', 'is available', s, flags=re.I)
    # servis edilir → is served
    s = re.sub(r'\bservis\s+edilir\b', 'is served', s, flags=re.I)
    # birleştirmiş → has combined
    s = re.sub(r'\bbirle[şs]tirmi[şs]\b', 'has combined', s, flags=re.I)
    # birleşimini → the combination of
    s = re.sub(r'\bbirle[şs]imini\b', 'the combination of', s, flags=re.I)
    # sunarken → while offering
    s = re.sub(r'\bsunarken\b', 'while offering', s, flags=re.I)
    # sunuyor → offers
    s = re.sub(r'\bsunuyor\b', 'offers', s, flags=re.I)
    # bulunur → is available
    s = re.sub(r'\bbulunur\b', 'is available', s, flags=re.I)
    # örnekleri → examples
    s = re.sub(r'\b[öo]rnekleri\b', 'examples', s, flags=re.I)
    # menüsünde → on the menu
    s = re.sub(r'\bmen[üu]s[üu]nde\b', 'on the menu', s, flags=re.I)
    # atmosferini → atmosphere
    s = re.sub(r'\batmosferini\b', 'atmosphere', s, flags=re.I)
    # tasarıma has → design
    s = re.sub(r'\btasar[ıi]ma\s+has\b', 'design', s, flags=re.I)
    # mutfağa has → cuisine style
    s = re.sub(r'\bmutfa[ğg]a\s+has\b', 'cuisine style', s, flags=re.I)
    # yemekleri servis edilir → dishes are served
    s = re.sub(r'\byemekleri\s+servis\s+edilir\b', 'dishes are served', s, flags=re.I)
    # Türk mutfağı yemekleri → Turkish cuisine dishes
    s = re.sub(r'\bT[üu]rk\s+mutfa[ğg][ıi]\s+yemekleri\b', 'Turkish cuisine dishes', s, flags=re.I)
    # Türk mutfağı atmosferini → Turkish cuisine atmosphere
    s = re.sub(r'\bT[üu]rk\s+mutfa[ğg][ıi]\s+atmosferini\b', 'Turkish cuisine atmosphere', s, flags=re.I)
    # Türk mutfağı → Turkish cuisine
    s = re.sub(r'\bT[üu]rk\s+mutfa[ğg][ıi]\b', 'Turkish cuisine', s, flags=re.I)
    # İtalyan mutfağı → Italian cuisine
    s = re.sub(r'\b[İi]talyan\s+mutfa[ğg][ıi]\b', 'Italian cuisine', s, flags=re.I)
    # dünya mutfağı → world cuisine
    s = re.sub(r'\bd[üu]nya\s+mutfa[ğg][ıi]\b', 'world cuisine', s, flags=re.I)
    # Konya Mutfağı → Konya cuisine
    s = re.sub(r'\bKonya\s+Mutfa[ğg][ıi]\b', 'Konya cuisine', s, flags=re.I)
    # Kore-Çin mutfağı → Korean-Chinese cuisine
    s = re.sub(r'\bKore-[Çc]in\s+mutfa[ğg][ıi]\b', 'Korean-Chinese cuisine', s, flags=re.I)
    # mutfak tarzını X as tanımlayabilirsiniz → can be described as X cuisine
    s = re.sub(r'\bmutfak\s+tarz[ıi]n[ıi]\s+(\w+)\s+as\s+tan[ıi]mlayabilirsiniz\b',
               r"can be described as \1 cuisine", s, flags=re.I)
    # mutfağı / mutfağa remaining
    s = re.sub(r'\bmutfa[ğg][ıi]n\b', "cuisine's", s, flags=re.I)
    s = re.sub(r'\bmutfa[ğg][ıi]\b', 'cuisine', s, flags=re.I)
    s = re.sub(r'\bmutfa[ğg]a\b', 'cuisine', s, flags=re.I)
    # özelliklerini → characteristics
    s = re.sub(r'\b[öo]zelliklerini\b', 'characteristics', s, flags=re.I)
    # severlerin → lovers'
    s = re.sub(r'\bseverlerin\b', "lovers'", s, flags=re.I)
    # tercih edebileceği → can choose
    s = re.sub(r'\btercih\s+edebilece[ğg]i\b', 'can choose', s, flags=re.I)
    # uyumlu → compatible / harmonious
    s = re.sub(r'\buyumlu\b', 'harmonious', s, flags=re.I)
    # çalıyoruz → we play
    s = re.sub(r'\b[çc]al[ıi]yoruz\b', 'we play', s, flags=re.I)
    # belirtmediğiniz → you haven't specified
    s = re.sub(r'\bbelirtmedi[ğg]iniz\b', "you haven't specified", s, flags=re.I)
    # ortaya çıkan → emerging
    s = re.sub(r'\bortaya\s+[çc][ıi]kan\b', 'emerging', s, flags=re.I)
    # farklı kültürlerin bir araya gelmesiyle
    s = re.sub(r'\bfarkl[ıi]\s+k[üu]lt[üu]rlerin\s+bir\s+araya\s+gelmesiyle\b',
               'from different cultures coming together', s, flags=re.I)
    # farklı → different
    s = re.sub(r'\bfarkl[ıi]\b', 'different', s, flags=re.I)
    # lezzetleri → flavors
    s = re.sub(r'\blezzetleri\b', 'flavors', s, flags=re.I)
    # tarzlar → styles
    s = re.sub(r'\btarzlar\b', 'styles', s, flags=re.I)
    # yemekleri → dishes
    s = re.sub(r'\byemekleri\b', 'dishes', s, flags=re.I)
    # bir Türk mutfağı yemeğidir → is a Turkish cuisine dish
    s = re.sub(r'\bbir\s+Turkish\s+cuisine\s+yeme[ğg]idir\b', 'is a Turkish cuisine dish', s, flags=re.I)
    s = re.sub(r'\byeme[ğg]idir\b', 'is a dish', s, flags=re.I)
    # istasyonlarına → stations
    s = re.sub(r'\bistasyonlar[ıi]na\b', 'stations', s, flags=re.I)
    # menüsünde → on the menu
    s = re.sub(r'\bmen[üu]s[üu]nde\b', 'on the menu', s, flags=re.I)
    # within servis edilir → served on
    s = re.sub(r'\bpide\s+within\s+is\s+served\b', 'served on pide', s, flags=re.I)
    s = re.sub(r'\bpide\s+within\b', 'on pide', s, flags=re.I)
    # "reservation yapma imkanımız not available"
    s = re.sub(r'reservation\s+yapma\s+imkan[ıi]m[ıi]z\s+not\s+available\.?', 'Reservations are not available.', s, flags=re.I)
    # imkânı / imkanı → opportunity
    s = re.sub(r'\bimk[aâ]n[ıi]\b', 'opportunity', s, flags=re.I)
    # sunarken modern bir tasarıma has → while offering a modern design
    s = re.sub(r'while\s+offering\s+modern\s+bir\s+design\b', 'while offering a modern design', s, flags=re.I)
    s = re.sub(r'\bmodern\s+bir\b', 'a modern', s, flags=re.I)
    # bir araya → together
    s = re.sub(r'\bbir\s+araya\b', 'together', s, flags=re.I)
    # new yeni → new
    s = re.sub(r'\byeni\b', 'new', s, flags=re.I)
    # lezzet / lezzetler
    s = re.sub(r'\blezzetler\b', 'flavors', s, flags=re.I)
    s = re.sub(r'\blezzet\b', 'flavor', s, flags=re.I)
    # müzik türlerini → music genres
    s = re.sub(r'\bm[üu]zik\s+t[üu]rlerini\b', 'music genres', s, flags=re.I)
    s = re.sub(r'\bm[üu]zik\s+t[üu]r[üu]n[üu]\b', 'music type', s, flags=re.I)
    # Cleanup
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

# Check for remaining Turkish words (broader)
TR2 = re.compile(r'[\u011f\u015f\u00e7\u00f6\u00fc\u0131\u0130\u011e\u015e\u00c7\u00d6\u00dc]')
import collections
remaining = []
for r in data:
    for qa in r.get('faq', []):
        for f in ['answer', 'question']:
            v = qa.get(f, '')
            if not TR2.search(v): continue
            # Skip if only Turkish chars in what looks like proper nouns
            stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\'\s\-\.]+', 'X', v)
            if TR2.search(stripped):
                remaining.append(v)

print(f'Strings with Turkish outside proper nouns: {len(remaining)}')
# Show unique samples
seen = set()
for v in remaining:
    if v not in seen:
        seen.add(v)
        print(f'  {v[:110]}')
        if len(seen) >= 20: break
