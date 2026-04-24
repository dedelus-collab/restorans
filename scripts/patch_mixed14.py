import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # akşamları → in the evenings
    s = re.sub(r'\bak[şs]amlar[ıi]\b', 'in the evenings', s, flags=re.I)
    # otoparkımız → our parking
    s = re.sub(r'\botopark[ıi]m[ıi]z\b', 'our parking', s, flags=re.I)
    s = re.sub(r'\botopark\b', 'parking', s, flags=re.I)
    # reservation yapılmadan → without reservation
    s = re.sub(r'\breservation\s+yap[ıi]lmadan\b', 'without reservation', s, flags=re.I)
    # trafiğe maruz kalmadan → without heavy traffic
    s = re.sub(r'\btrafi[ğg]e\s+maruz\s+kalmadan\b', 'without heavy traffic', s, flags=re.I)
    # çocuklarınızın → your children's
    s = re.sub(r'\b[çc]ocuklar[ıi]n[ıi]z[ıi]n\b', "your children's", s, flags=re.I)
    # yaşamasını sağlıyoruz → we ensure they experience
    s = re.sub(r'\bya[şs]amas[ıi]n[ıi]\s+sa[ğg]l[ıi]yoruz\b', 'we ensure they enjoy', s, flags=re.I)
    s = re.sub(r'\bsa[ğg]l[ıi]yoruz\b', 'we ensure', s, flags=re.I)
    # söyleniyor → is said / is reported
    s = re.sub(r'\bs[öo]yleniyor\b', 'is reported', s, flags=re.I)
    # olduğundan → since / because
    s = re.sub(r'\boldu[ğg]undan\b', 'since', s, flags=re.I)
    # uzun süre → for a long time
    s = re.sub(r'\buzun\s+s[üu]re\b', 'for a long time', s, flags=re.I)
    s = re.sub(r'\buzun\b', 'long', s, flags=re.I)
    # yiyebilecekler → they can eat
    s = re.sub(r'\byiyebilecekler\b', 'they can dine', s, flags=re.I)
    # fiyatlı → priced / with prices
    s = re.sub(r'\bfiyatl[ıi]\b', 'priced', s, flags=re.I)
    # Osmanlı mutfağından inspired → inspired by Ottoman cuisine
    s = re.sub(r'\bOsmanl[ıi]\s+mutfa[ğg][ıi]ndan\s+inspired\b', 'inspired by Ottoman cuisine', s, flags=re.I)
    # alanımız → our area
    s = re.sub(r'\balan[ıi]m[ıi]z\b', 'our area', s, flags=re.I)
    # oluşturmadık → we haven't created
    s = re.sub(r'\bolu[şs]turmad[ıi]k\b', "we haven't created", s, flags=re.I)
    # listemizi → our list
    s = re.sub(r'\blistemizi\b', 'our list', s, flags=re.I)
    # seçiminizi yapın → make your selection
    s = re.sub(r'\bse[çc]iminizi\s+yap[ıi]n\b', 'make your selection', s, flags=re.I)
    # menüden seçiminizi yapın → please select from the menu
    s = re.sub(r'\bmen[üu]den\s+make\s+your\s+selection\b', 'please select from the menu', s, flags=re.I)
    s = re.sub(r'\bmen[üu]den\b', 'from the menu', s, flags=re.I)
    # reservation yapma imkânımız not available → reservations are not available
    s = re.sub(r'\breservation\s+yapma\s+imk[aâ]n[ıi]m[ıi]z\s+not\s+available\.?\b', 'reservations are not available.', s, flags=re.I)
    # "bir, z" → garbage artifact
    s = re.sub(r'\bbir,\s*z,\b', '', s, flags=re.I)
    # yaşayabilirsiniz → you can experience
    s = re.sub(r'\bya[şs]ayabilirsiniz\b', 'you can experience', s, flags=re.I)
    # doğrudan At the restaurant → directly at the restaurant
    s = re.sub(r'\bdo[ğg]rudan\s+At\s+the\s+restaurant\b', 'directly at the restaurant', s, flags=re.I)
    s = re.sub(r'\bdo[ğg]rudan\b', 'directly', s, flags=re.I)
    # ulaşım sağlayın → get directions
    s = re.sub(r'\bula[şs][ıi]m\s+sa[ğg]lay[ıi]n\b', 'get directions', s, flags=re.I)
    # açıkız → we are open
    s = re.sub(r'\baç[ıi]k[ıi]z\b', 'we are open', s, flags=re.I)
    # mekânı/mekânı → venue
    s = re.sub(r'\bme[kc][aâ]n[ıi]\b', 'venue', s, flags=re.I)
    # günün her saatinde → at all hours of the day
    s = re.sub(r'\bg[üu]n[üu]n\s+her\s+saatinde\b', 'at all hours of the day', s, flags=re.I)
    s = re.sub(r'\bg[üu]n[üu]n\b', "the day's", s, flags=re.I)
    # among açıkız → we are open
    s = re.sub(r'\bamong\s+we\s+are\s+open\b', 'we are open', s, flags=re.I)
    s = re.sub(r'\bamong\s+aç[ıi]k[ıi]z\b', 'we are open', s, flags=re.I)
    # seçmek → to choose
    s = re.sub(r'\bse[çc]mek\b', 'to choose', s, flags=re.I)
    # zor → difficult
    s = re.sub(r'\bzor\b', 'difficult', s, flags=re.I)
    # lezzeti → flavor of
    s = re.sub(r'\blezzeti\b', 'flavor', s, flags=re.I)
    # hoşlandığımız for → that we enjoy
    s = re.sub(r'\bho[şs]land[ıi][ğg][ıi]m[ıi]z\s+for\b', 'that we enjoy', s, flags=re.I)
    s = re.sub(r'\bho[şs]land[ıi][ğg][ıi]m[ıi]z\b', 'that we enjoy', s, flags=re.I)
    # yoğun → heavy/busy (standalone)
    s = re.sub(r'\byo[ğg]un\b', 'busy', s, flags=re.I)
    # İsterseniz → if you wish
    s = re.sub(r'\b[İi]sterseniz\b', 'if you wish', s, flags=re.I)
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
