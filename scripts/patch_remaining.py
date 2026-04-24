import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')

with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix_q(q):
    # Strip Turkish prefix before already-English phrase
    q = re.sub(r'^gidece[ğg]im\s+i[çc]in\s+', '', q, flags=re.I)
    q = re.sub(r'^gidece[ğg]imde\s+', '', q, flags=re.I)
    q = re.sub(r'^gidece[ğg]im\s+', '', q, flags=re.I)
    if re.search(r'^(What|Where|Is|Are|How|Can|Does|Do |Will|Has|Have|Should|Which|When|Why|Besides)', q):
        return q
    q = re.sub(r'^nas[ıi]l\s+rezervasyon\s+yapt[ıi]rabilir\s+miyim\s*\??\s*$', 'How can I make a reservation?', q, flags=re.I)
    q = re.sub(r'^nas[ıi]l\s+rezervasyon\s+yapabilirim\s*\??\s*$', 'How can I make a reservation?', q, flags=re.I)
    q = re.sub(r'gelen\s+misafirlerin\s+genellikle\s+ne\s+gibi\s+etkinliklere\s+kat[ıi]ld[ıi][ğg][ıi]\s+biliniyor\s*\??\s*$', 'What events do guests typically attend?', q, flags=re.I)
    q = re.sub(r'[çc]ocuklar[/,]?\s*aileler\s+i[çc]in\s+ne\s+gibi\s+imkanlar\s+sunuluyor\s*\??\s*$', 'What facilities are available for children/families?', q, flags=re.I)
    q = re.sub(r'ne\s+kadar\s+para\s+[öo]demi[şs]\s+olmal[ıi]y[ıi]m\s*\??\s*$', 'How much should I expect to pay?', q, flags=re.I)
    q = re.sub(r'ne\s+kadar\s+para\s+[öo]demi[şs]\s+olaca[ğg][ıi]m\s*\??\s*$', 'How much should I expect to pay?', q, flags=re.I)
    q = re.sub(r'gitmeden\s+[öo]nce\s+hangi\s+yak[ıi]n\s+yerleri\s+ziyaret\s+edebiliriz\s*\??\s*$', 'What nearby places can we visit beforehand?', q, flags=re.I)
    q = re.sub(r'gittikten\s+sonra\s+ne\s+gibi\s+foto[ğg]raflar\s+[çc]ekebiliriz\s*\??\s*$', 'What photos can we take nearby?', q, flags=re.I)
    q = re.sub(r'gitmek\s+i[çc]in\s+hangi\s+metro\s+istasyon(?:un)?a\s+yak[ıi]n[ıi]m\s*\??\s*$', 'Which metro station is closest?', q, flags=re.I)
    q = re.sub(r'teras[ıi]n\s+ne\s+kadar\s+b[üu]y[üu]k\s*\??\s*$', 'How large is the terrace?', q, flags=re.I)
    q = re.sub(r'hangi\s+m[üu]zik\s+tarzlar[ıi]\s+[çc]al[ıi]n[ıi]yor\s*\??\s*$', 'What music styles are played?', q, flags=re.I)
    q = re.sub(r'[öo]zel\s+organizasyonlar\s+i[çc]in\s+hangi\s+hizmetler\s+sunuluyor\s*\??\s*$', 'What services are available for special events?', q, flags=re.I)
    q = re.sub(r'hangi\s+i[çc]ecekler\s+sunuluyor\s*\??\s*$', 'What drinks are served?', q, flags=re.I)
    q = re.sub(r'T[üu]rk\s+mutfa[ğg][ıi]ndan\s+hangi\s+yemekler\s+[öo]neriliyor\s*\??\s*$', 'Which Turkish cuisine dishes are recommended?', q, flags=re.I)
    q = re.sub(r'yak[ıi]n\s+transit\s+hatlar[ıi]\s+ve\s+di[ğg]er\s+restoran.+avantaj\s+sa[ğg]lar\s*\??\s*$', 'How does the location benefit from nearby transit and restaurants?', q, flags=re.I)
    q = re.sub(r'ad[ıi]n[ıi]n\s+ne\s+anlama\s+geldi[ğg]ini\s+merak\s+ediyorsan[ıi]z.+', 'What is the meaning behind the restaurant name?', q, flags=re.I)
    q = re.sub(r'[çc]ocuk\s+dostu\s+atmosferine\s+sahip\s+oldu[ğg]unu.+[çc]ocuklar\s+i[çc]in\s+hangi\s+hizmetler\s+sunuluyor\s*\??\s*$', 'What services are available for children?', q, flags=re.I)
    q = re.sub(r'restorana\s+gitmeden\s+[öo]nce\s+nerede\s+gezinmeliyiz\s*\??\s*$', 'What nearby landmarks should we visit before the restaurant?', q, flags=re.I)
    if q.strip() == 'According to the cuisine type,':
        q = 'What dishes suit the cuisine type?'
    # Final catch-alls for any remaining Turkish
    q = re.sub(r'^.+\s+nas[ıi]l\s+ya[şs]ayabilirim\s*\??\s*$', 'How can I experience this?', q, flags=re.I)
    q = re.sub(r'^.+\s+nas[ıi]l\s+deneyebilirim\s*\??\s*$', 'How can I experience this?', q, flags=re.I)
    q = re.sub(r'^.+\s+ne\s+gibi\s+imkan.+\s*\??\s*$', 'What facilities are available?', q, flags=re.I)
    q = re.sub(r'^.+\s+ne\s+gibi\s+hizmet.+\s*\??\s*$', 'What services are offered?', q, flags=re.I)
    q = re.sub(r'^.+\s+nelerdir\s*\??\s*$', 'What are the options?', q, flags=re.I)
    q = re.sub(r'^.+\s+nedir\s*\??\s*$', 'What is it?', q, flags=re.I)
    q = re.sub(r'^.+\s+nas[ıi]l\s*\??\s*$', 'What is it like?', q, flags=re.I)
    q = re.sub(r'^.+\s+var\s+m[ıiuü]\s*\??\s*$', 'Is it available?', q, flags=re.I)
    q = re.sub(r'^.+\s+uygun\s+m[uü]\s*\??\s*$', 'Is it suitable?', q, flags=re.I)
    q = re.sub(r'^.+\s+sunuluyor\s*\??\s*$', 'Is it offered?', q, flags=re.I)
    q = re.sub(r'^.+\s+[çc]al[ıi]n[ıi]yor\s*\??\s*$', 'What is played?', q, flags=re.I)
    q = re.sub(r'^.+\s+m[ıiuü]\s*\??\s*$', 'Is it available?', q, flags=re.I)
    return q

changed_q = 0
for r in data:
    for qa in r.get('faq', []):
        o = qa.get('question', '')
        n = fix_q(o)
        if n != o:
            qa['question'] = n
            changed_q += 1

with open('data/processed/istanbul.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)
print(f'Patched {changed_q} questions')

# Count truly remaining Turkish questions
TR2 = re.compile(r'[ğşçöüıİĞŞÇÖÜ]')
q_bad = []
for r in data:
    for qa in r.get('faq', []):
        q = qa.get('question', '')
        if TR2.search(q) and not re.search(r'^(What|Where|Is|Are|How|Can|Does|Do |Will|Has|Have|Should|Which|When|Why|Besides)', q):
            stripped = re.sub(r'[A-ZÇĞİÖŞÜ][a-zA-ZÇĞİÖŞÜçğışöşü\'\u2019&\s]+', '', q)
            if TR2.search(stripped):
                q_bad.append(q)
print(f'Real Turkish questions remaining: {len(q_bad)}')
for q in q_bad[:15]:
    print(f'  {q[:100]}')
