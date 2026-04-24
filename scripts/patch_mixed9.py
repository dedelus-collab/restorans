import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # seçim → choice
    s = re.sub(r'\bse[çc]im\b', 'choice', s, flags=re.I)
    # ulaşımın kolaylaşması → easy access
    s = re.sub(r'\bula[şs][ıi]m[ıi]n\s+kolayla[şs]mas[ıi]\b', 'easy access', s, flags=re.I)
    # yoğun trafiğe maruz kalmadan → without heavy traffic
    s = re.sub(r'\byog[ğg]?un\s+trafi[ğg]e\s+maruz\s+kalmadan\b', 'without heavy traffic', s, flags=re.I)
    s = re.sub(r'\byog[ğg]?un\b', 'heavy', s, flags=re.I)
    s = re.sub(r'\bula[şs][ıi]labilmesi\b', 'accessibility', s, flags=re.I)
    # avantajdır → is an advantage
    s = re.sub(r'\bavantajd[ıi]r\.?\b', 'is an advantage.', s, flags=re.I)
    s = re.sub(r'\bavantaj\b', 'advantage', s, flags=re.I)
    # kabul edebilmesi → ability to accept
    s = re.sub(r'\bkabul\s+edebilmesi\b', 'ability to accommodate', s, flags=re.I)
    # yapılması → making / should be made
    s = re.sub(r'\byap[ıi]lmas[ıi]\s+is\s+recommended', 'is recommended', s, flags=re.I)
    s = re.sub(r'\byap[ıi]lmas[ıi]\b', 'making', s, flags=re.I)
    # puanlı → rated
    s = re.sub(r'\bpuanl[ıi]\b', 'rated', s, flags=re.I)
    # puan → rating
    s = re.sub(r'\bpuan\b', 'rating', s, flags=re.I)
    # hayatı → nightlife (when near "late" or "gece")
    s = re.sub(r'\bgece\s+hayat[ıi]\b', 'nightlife', s, flags=re.I)
    s = re.sub(r'\blate\s+hayat[ıi]\b', 'late-night life', s, flags=re.I)
    s = re.sub(r'\bhayat[ıi]\b', 'life', s, flags=re.I)
    # aktif → active
    s = re.sub(r'\baktif\b', 'active', s, flags=re.I)
    # olmamasına rağmen → despite not having
    s = re.sub(r'\bolmamas[ıi]na\s+ra[ğg]men\b', 'despite not having', s, flags=re.I)
    # rağmen → despite
    s = re.sub(r'\bra[ğg]men\b', 'despite', s, flags=re.I)
    # gruplara → groups
    s = re.sub(r'\bgruplar[ıi]na\b', 'to groups', s, flags=re.I)
    s = re.sub(r'\bgruplar[ıi]\b', 'groups', s, flags=re.I)
    s = re.sub(r'\bgruplar\b', 'groups', s, flags=re.I)
    # yemeklerine → to meals
    s = re.sub(r'\byemeklerine\b', 'meals', s, flags=re.I)
    s = re.sub(r'\byeme[ğg]ine\b', 'meal', s, flags=re.I)
    # çocuklu → with children / families with children
    s = re.sub(r'\b[çc]ocuklu\b', 'families with children', s, flags=re.I)
    # keyfini çıkarmak → to enjoy
    s = re.sub(r'\bkeyf?ini\s+[çc][ıi]karmak\b', 'to enjoy', s, flags=re.I)
    s = re.sub(r'\bkeyf?ini\s+art[ıi]r[ıi]yor\b', 'enhances the enjoyment', s, flags=re.I)
    s = re.sub(r'\bkeyf?ini\b', 'enjoyment', s, flags=re.I)
    # kutlayabilirsiniz → you can celebrate
    s = re.sub(r'\bkutlayabilirsiniz\b', 'you can celebrate', s, flags=re.I)
    # kutlama fırsatı → celebration opportunity
    s = re.sub(r'\bkutlama\s+f[ıi]rsat[ıi]\b', 'celebration opportunity', s, flags=re.I)
    s = re.sub(r'\bkutlama\b', 'celebration', s, flags=re.I)
    # doğrudan başvurabilirsiniz → you can contact directly
    s = re.sub(r'\bdo[ğg]rudan\s+ba[şs]vurabilirsiniz\b', 'you can contact us directly', s, flags=re.I)
    s = re.sub(r'\bba[şs]vurabilirsiniz\b', 'you can contact', s, flags=re.I)
    # mekanız → our venue / is our venue
    s = re.sub(r'\bmekan[ıi]z\b', 'our venue', s, flags=re.I)
    s = re.sub(r'\bmekan\b', 'venue', s, flags=re.I)
    # yerdir → is a place
    s = re.sub(r'\byerdir\b', 'is a place', s, flags=re.I)
    s = re.sub(r'\byer\b', 'place', s, flags=re.I)
    # küçük → small
    s = re.sub(r'\bk[üu][çc][üu]k\b', 'small', s, flags=re.I)
    # arıyorsanız → if you are looking for
    s = re.sub(r'\bar[ıi]yorsan[ıi]z\b', 'if you are looking for', s, flags=re.I)
    # istiyorsanız → if you want
    s = re.sub(r'\bistiyorsan[ıi]z\b', 'if you want', s, flags=re.I)
    # landmarklardan birine → near one of the landmarks
    s = re.sub(r'\blandmarklardan\s+birine\b', 'near one of the landmarks', s, flags=re.I)
    # noktası → point
    s = re.sub(r'\bnoktas[ıi]\b', 'point', s, flags=re.I)
    # doğa → nature
    s = re.sub(r'\bdo[ğg]a\b', 'nature', s, flags=re.I)
    # doğum gününüzü → your birthday
    s = re.sub(r'\bdo[ğg]um\s+g[üu]n[üu]n[üu]z[üu]\b', 'your birthday', s, flags=re.I)
    s = re.sub(r'\bdo[ğg]um\s+g[üu]n[üu]\b', 'birthday', s, flags=re.I)
    # mutfağındadır → specializes in cuisine
    s = re.sub(r'\bmutfa[ğg][ıi]ndad[ıi]r\b', 'cuisine is available', s, flags=re.I)
    # kekik → thyme
    s = re.sub(r'\bkekik\b', 'thyme', s, flags=re.I)
    # öneriyoruz → we recommend
    s = re.sub(r'\b[öo]neriyoruz\b', 'we recommend', s, flags=re.I)
    # tabaklarını → plates of / dishes of
    s = re.sub(r'\btabaklar[ıi]n[ıi]\b', 'dishes', s, flags=re.I)
    s = re.sub(r'\btabak\b', 'dish', s, flags=re.I)
    # keşfedebilirsiniz → you can discover
    s = re.sub(r'\bke[şs]fedebilirsiniz\b', 'you can discover', s, flags=re.I)
    # ulaşılabilmesi → accessibility
    s = re.sub(r'\bula[şs][ıi]labilmesi\b', 'accessibility', s, flags=re.I)
    # kolaylaşması → easing / improvement
    s = re.sub(r'\bkolayla[şs]mas[ıi]\b', 'ease', s, flags=re.I)
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
