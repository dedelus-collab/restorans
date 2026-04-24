import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # iç içe → intertwined with
    s = re.sub(r'\bi[çc]\s+i[çc]e\b', 'intertwined with', s, flags=re.I)
    # günleriniz → your special days
    s = re.sub(r'\bg[üu]nleriniz\b', 'your special days', s, flags=re.I)
    s = re.sub(r'\bg[üu]n[üu]n[üu]z[üu]\b', 'your day', s, flags=re.I)
    # organizasyonlarınız → your events
    s = re.sub(r'\borganizasyonlar[ıi]n[ıi]z\b', 'your events', s, flags=re.I)
    s = re.sub(r'\borganizasyon\b', 'event', s, flags=re.I)
    # olabiliriz → we can be
    s = re.sub(r'\bolabiliriz\b', 'we can be an option', s, flags=re.I)
    # keyif alıyorsanız → if you enjoy
    s = re.sub(r'\bkeyif\s+al[ıi]yorsan[ıi]z\b', 'if you enjoy', s, flags=re.I)
    s = re.sub(r'\bkeyif\b', 'enjoyment', s, flags=re.I)
    # resmi websitesinden → official website
    s = re.sub(r'\bresmi\s+websitesinden\b', 'official website', s, flags=re.I)
    s = re.sub(r'\bresmi\b', 'official', s, flags=re.I)
    # sorulabilir → can be asked / can be inquired
    s = re.sub(r'\bsorulabilir\b', 'can be inquired', s, flags=re.I)
    # konumuyla → with its location
    s = re.sub(r'\bkonumuyla\b', 'with its location', s, flags=re.I)
    # sunmak for hazırdır → ready to offer
    s = re.sub(r'\bsunmak\s+for\s+hazırd[ıi]r\b', 'ready to offer', s, flags=re.I)
    s = re.sub(r'\bsunmak\b', 'offering', s, flags=re.I)
    # hazırdır → is ready
    s = re.sub(r'\bhaz[ıi]rd[ıi]r\b', 'is ready', s, flags=re.I)
    # size → you (Turkish "size" = to you)
    # Be careful - "size" is also English word. Only replace when clearly Turkish context
    s = re.sub(r'\bbu\s+options\s+size\b', 'these options to you', s, flags=re.I)
    # Vegan/vejeteryan dostu → vegan/vegetarian-friendly
    s = re.sub(r'\bvejeteryan\s+dostu\b', 'vegetarian-friendly', s, flags=re.I)
    s = re.sub(r'\bvejeteryan\b', 'vegetarian', s, flags=re.I)
    s = re.sub(r'\bvegan\s+dostu\b', 'vegan-friendly', s, flags=re.I)
    # restorandı → was a restaurant / is a restaurant
    s = re.sub(r'\brestoran d[ıi]\b', 'is a restaurant', s, flags=re.I)
    s = re.sub(r'\brestoran\b', 'restaurant', s, flags=re.I)
    # içecekleri → drinks / beverages
    s = re.sub(r'\bi[çc]ecekleri\b', 'drinks', s, flags=re.I)
    s = re.sub(r'\bi[çc]ecek\b', 'drink', s, flags=re.I)
    # verebilir → can provide
    s = re.sub(r'\bverebilir\b', 'can provide', s, flags=re.I)
    # atmosferiyle → with its atmosphere
    s = re.sub(r'\batmosferiyle\b', 'with its atmosphere', s, flags=re.I)
    # seçimdir → is a choice / is an option
    s = re.sub(r'\bse[çc]imdir\b', 'is an ideal choice', s, flags=re.I)
    # mutfak tarzını X as tanımlayabilirsiniz → can be described as X cuisine
    s = re.sub(r'\bmutfak\s+tarz[ıi]n[ıi]\s+(\w+\s+\w+)\s+as\s+tan[ıi]mlayabilirsiniz\b', r'can be described as \1 cuisine', s, flags=re.I)
    s = re.sub(r'\bmutfak\s+tarz[ıi]n[ıi]\s+(\w+)\s+as\s+tan[ıi]mlayabilirsiniz\b', r'can be described as \1 cuisine', s, flags=re.I)
    s = re.sub(r'\btan[ıi]mlayabilirsiniz\b', 'you can describe', s, flags=re.I)
    # kültürlerin mutfağından esinlenerek → inspired by cuisines of different cultures
    s = re.sub(r'\bk[üu]lt[üu]rlerin\s+mutfa[ğg][ıi]ndan\s+esinlenerek\b', 'inspired by different cuisines', s, flags=re.I)
    s = re.sub(r'\besinlenerek\b', 'inspired by', s, flags=re.I)
    # özellikleri → characteristics / features
    s = re.sub(r'\b[öo]zellikleri\b', 'features', s, flags=re.I)
    # fiyat aralığı orta → mid-range prices
    s = re.sub(r'\bfiyat\s+aral[ıi][ğg][ıi]\s+orta\b', 'mid-range prices', s, flags=re.I)
    s = re.sub(r'\bfiyat\s+aral[ıi][ğg][ıi]\b', 'price range', s, flags=re.I)
    # tanışın → meet / get acquainted
    s = re.sub(r'\btan[ıi][şs][ıi]n\b', 'discover', s, flags=re.I)
    # ortamız → our atmosphere
    s = re.sub(r'\bortam[ıi]z\b', 'our atmosphere', s, flags=re.I)
    # mekandır → is a venue
    s = re.sub(r'\bmekan[ıi]z\b', 'our venue', s, flags=re.I)
    s = re.sub(r'\bmeband[ıi]r\b', 'is a venue', s, flags=re.I)
    s = re.sub(r'\bmekan d[ıi]r\b', 'is a venue', s, flags=re.I)
    # reservation yapamıyoruz → we cannot take reservations
    s = re.sub(r'\breservation\s+yapam[ıi]yoruz\b', 'we cannot take reservations', s, flags=re.I)
    # reservation yapmanız gerekir → you need to make a reservation
    s = re.sub(r'\breservation\s+yapman[ıi]z\s+gerekir\.?\b', 'you need to make a reservation.', s, flags=re.I)
    # reservation yapmazsınız → reservations not taken
    s = re.sub(r'\breservation\s+yapmaz[ıi]n[ıi]z\.?\b', 'reservations are not taken.', s, flags=re.I)
    # telefon numarası → phone number
    s = re.sub(r'\btelefon\s+numara[ıs][ıi]\b', 'phone number', s, flags=re.I)
    s = re.sub(r'\btelefon\b', 'phone', s, flags=re.I)
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
