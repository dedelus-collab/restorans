import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

TR2 = re.compile(r'[\u011f\u015f\u00e7\u00f6\u00fc\u0131\u0130\u011e\u015e\u00c7\u00d6\u00dc]')
ALREADY_ENG = re.compile(r'^(What|Where|Is|Are|How|Can|Does|Do |Will|Has|Have|Should|Which|When|Why|Besides)')

def clean_q(q):
    if ALREADY_ENG.search(q): return q
    # Extract English tail from partial translations
    m = re.search(r'(?:^|\s)((?:How|What|Why|Which|Where|Is|Are|Can|Does|Do)[^?]*\??)$', q)
    if m:
        extracted = m.group(1).strip()
        if len(extracted) > 5:
            if not extracted.endswith('?'): extracted += '?'
            return extracted
    # Specific patterns
    pairs = [
        (r'[cc]ocuklarla\s+birlikte\s+gidebilir\s+miyim', 'Can I visit with children?'),
        (r'nasil\s+farklilik\s+gosteriyorsunuz', 'How do you differ from nearby restaurants?'),
        (r'ne\s+yakinim', 'How close is it?'),
        (r'nasil\s+rezervasyon\s+yapt', 'How can I make a reservation?'),
        (r'uygunlugu\s+ne\s+kadar', 'How suitable is it?'),
        (r'yakinligi\s+ne\s+kadar\s+avantajli', 'How advantageous is the nearby location?'),
        (r'Konstantinopolis\s+Kusatmas', 'How advantageous is the nearby historic landmark?'),
        (r'oldugunu\s+biliyor\s+muyum', 'Is the restaurant in this neighborhood?'),
        (r'hangi\s+lezzetlerini\s+sunuyor', 'What flavors does it offer?'),
        (r'hangi\s+aktivitelere\s+katilab', 'What activities can I do nearby?'),
        (r'ne\s+yapmaliyim', 'What should I do?'),
        (r'bahcesi\s+ne\s+kadar\s+buyuk', 'How large is the garden?'),
        (r'ortami\s+ne\s+kadar\s+romantik', 'How romantic is the atmosphere?'),
        (r'mesafesi\s+ne\s+kadar', 'What is the distance?'),
        (r'uzakligi\s+ne\s+kadar', 'What is the distance?'),
        (r'ne\s+kadar\s+para\s+oden', 'How much does it cost?'),
        (r'kac\s+kisiye\s+kadar\s+rezervasyon', 'How many people can make a reservation?'),
        (r'manzarasi\s+ne\s+gibi', 'What is the view like?'),
        (r'ne\s+zaman\s+tuketilmeli', 'When is the best time to enjoy this dish?'),
        (r'ne\s+zaman\s+sunulur', 'When is it served?'),
        (r'hangi\s+zaman\s+diliminde\s+acik', 'What are the opening hours?'),
        (r'ne\s+kadar\s+zaman\s+ayiriyorum', 'How long should I plan to visit?'),
        (r'konumu\s+ne\s+gibi\s+avantajlar', 'What location advantages does it offer?'),
        (r'lezzeti\s+nasil\s+tarif\s+edilebilir', 'How would you describe the taste?'),
        (r'ne\s+kadar\s+uzun\s+sure\s+pisiriliyor', 'How long are the dishes cooked?'),
        (r'ne\s+kadar\s+harcamaliyim', 'How much should I budget?'),
        (r'fiyat\s+bilgisine\s+ulasabilir\s+miyim', 'Can I get pricing information?'),
        (r'romantik\s+atmosferi\s+neye\s+borclu', 'What creates the romantic atmosphere?'),
        (r'hangi\s+malzemelerden\s+hazirlanir', 'What ingredients are used?'),
        (r'nasil\s+hazirlandigini\s+ogrenebilir\s+miyim', 'Can I learn how it is prepared?'),
        (r'ismi\s+neye\s+dayaniyor', 'What is the meaning behind the name?'),
        (r'konum\s+avantajlarindan\s+hangisi\s+manzarali', 'Which location advantage offers a scenic view?'),
        (r'uygun\s+oldugu\s+durumlar\s+hangileri', 'In what situations is it suitable?'),
        (r'acik\s+oldugunu\s+biliyor\s+muyuz', 'Do we know if it is suitable for special occasions?'),
        (r'ayirt\s+ediyorum', 'How does it stand out from nearby restaurants?'),
        (r'gece\s+hayati\s+hakkinda\s+bilgi\s+alabilir\s+miyim', 'Can I get information about the nightlife options?'),
        (r'mutfak\s+kulturu\s+hakkinda\s+bilgi\s+alabilir\s+miyim', 'Can I get information about the cuisine culture?'),
        (r'mutfak\s+kulturu\s+ne\s+turdurc', 'What is the cuisine culture type?'),
        (r'ne\s+kadar\s+etkiliyor', 'How much does it influence the dining experience?'),
        (r'gecenin\s+hangi\s+saatinde\s+kapaniyorsunuz', 'What time do you close?'),
        (r'hangi\s+saatler\s+arasinda\s+acik', 'What are the opening hours?'),
        (r'hangi\s+saatlerde\s+acik', 'What are the opening hours?'),
        (r'ne\s+zaman\s+acik\s+olurlar', 'What are the opening hours?'),
        (r'oneririm|onerirsiniz|oneriz', 'What dishes would you recommend?'),
        (r'kac\s+dakika\s+mesafededir', 'How many minutes away is it?'),
        (r'hangi\s+saatlerde', 'What are the opening hours?'),
        (r'kac\s+kisiye', 'How many people is it suitable for?'),
    ]
    # Normalize Turkish chars for matching
    normalized = q
    normalized = re.sub(r'[ğg]', 'g', normalized)
    normalized = re.sub(r'[şs]', 's', normalized)
    normalized = re.sub(r'[çc]', 'c', normalized)
    normalized = re.sub(r'[öo]', 'o', normalized)
    normalized = re.sub(r'[üu]', 'u', normalized)
    normalized = re.sub(r'[ıiI]', 'i', normalized)
    normalized = re.sub(r'[İI]', 'I', normalized)
    normalized = re.sub(r'[Ğg]', 'G', normalized)
    normalized = re.sub(r'[Şs]', 'S', normalized)
    normalized = re.sub(r'[Çc]', 'C', normalized)
    normalized = re.sub(r'[Öo]', 'O', normalized)
    normalized = re.sub(r'[Üu]', 'U', normalized)
    for pat, repl in pairs:
        if re.search(pat, normalized, re.I):
            return repl
    # Catch-alls
    if TR2.search(q):
        if re.search(r'ne\s+kadar\s*\??$', q, re.I): return 'How much is it?'
        if re.search(r'nerede\s*\??$', q, re.I): return 'Where is it?'
        if re.search(r'nas[ıi]l\s*\??$', q, re.I): return 'What is it like?'
        if re.search(r'hangileri\s*\??$', q, re.I): return 'Which ones?'
        if re.search(r'nelerdir\s*\??$', q, re.I): return 'What are the options?'
        if re.search(r'm[ıiuü]\s*\??$', q, re.I): return 'Is it available?'
        if re.search(r'sunuyor\s*\??$', q, re.I): return 'What does it offer?'
        if re.search(r'bulunmakta\s*\??$', q, re.I): return 'What is available?'
    return q

changed = 0
for r in data:
    for qa in r.get('faq', []):
        o = qa.get('question', '')
        n = clean_q(o)
        if n != o:
            qa['question'] = n
            changed += 1

with open('data/processed/istanbul.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Patched {changed} questions')

q_bad = []
for r in data:
    for qa in r.get('faq', []):
        q = qa.get('question', '')
        if TR2.search(q) and not ALREADY_ENG.search(q):
            stripped = re.sub(r'[A-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc][a-zA-Z\u00c7\u011e\u0130\u00d6\u015e\u00dc\u00e7\u011f\u0131\u015f\u00f6\u00fc\u2019&\s]+', '', q)
            if TR2.search(stripped):
                q_bad.append(q)
print(f'Remaining: {len(q_bad)}')
for q in q_bad[:15]:
    print(f'  {q[:100]}')
