import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # "X sunması avantajlıdır" → "offers X, which is an advantage"
    s = re.sub(r'\bsunmas[ıi]\s+avantajl[ıi]d[ıi]r\.?', 'are available nearby.', s, flags=re.I)
    # "X sunması and Y sunması due to/nedenlerle you can visit" → "You can visit for X and Y"
    s = re.sub(r'\bsunmas[ıi]\s+and\b', 'offering and', s, flags=re.I)
    s = re.sub(r'\bsunmas[ıi]yla\s+ilgilidir\b', 'is related to offering', s, flags=re.I)
    s = re.sub(r'\bsunmas[ıi]n[ıi]\s+provides\b', 'offers', s, flags=re.I)
    s = re.sub(r'\bsunmas[ıi]\b', 'offering', s, flags=re.I)
    # "yer alması and X" → "being located and X"
    s = re.sub(r'\byer\s+almas[ıi]\b', 'being nearby', s, flags=re.I)
    # "olmasından dolayı" → "because of"
    s = re.sub(r'\bolmas[ıi]ndan\s+dolay[ıi]\b', 'because of this', s, flags=re.I)
    # "olduğu and X" → "being and X"
    s = re.sub(r'\boldu[ğg]u\b', 'being', s, flags=re.I)
    # "nedenlerle you can visit" → "are reasons to visit"
    s = re.sub(r'\bnedenlerle\s+you\s+can\s+visit\b', 'are reasons to visit.', s, flags=re.I)
    s = re.sub(r'\bnedenlerdendir\b', 'are reasons to visit.', s, flags=re.I)
    s = re.sub(r'\bnedenlerle\b', 'are reasons to', s, flags=re.I)
    # "due to you can visit" → "— great reasons to visit"
    s = re.sub(r'\bdue\s+to\s+you\s+can\s+visit\.?\s*$', '— great reasons to visit.', s, flags=re.I)
    s = re.sub(r'\bdue\s+to\s+you\s+can\s+visit\b', 'which are reasons to visit', s, flags=re.I)
    # "dolayı" standalone
    s = re.sub(r'\bdolay[ıi]\b', 'because of', s, flags=re.I)
    # "nedeniyle" → "due to"
    s = re.sub(r'\bnedeniyle\b', 'due to', s, flags=re.I)
    # "içinde because it is located" → "is located inside"
    s = re.sub(r'\bi[çc]inde\s+because\s+it\s+is\s+located\b', 'located within', s, flags=re.I)
    s = re.sub(r'\bi[çc]inde\b', 'within', s, flags=re.I)
    # "konumu" → "location"
    s = re.sub(r'\bkonumu\b', 'location', s, flags=re.I)
    # "lezzetlerini" → "flavors"
    s = re.sub(r'\blezzetlerini\b', 'flavors', s, flags=re.I)
    # "severler ideal for a place" → "enthusiasts, an ideal place"
    s = re.sub(r'\bseverler\b', 'enthusiasts,', s, flags=re.I)
    # "ortamları" → "atmosphere"
    s = re.sub(r'\bortamlar[ıi]\b', 'atmosphere', s, flags=re.I)
    # "inspired" is ok but "inspired delicious" cleanup
    # "yerel flavors" fine
    # "merkezi konumu due to" → "central location means"
    s = re.sub(r'\bmerkezi\s+location\s+due\s+to\b', 'central location —', s, flags=re.I)
    s = re.sub(r'\bmerkezi\b', 'central', s, flags=re.I)
    # "bölgeye distinctive dishes" → "distinctive dishes to the area"
    s = re.sub(r'\bb[öo]lgeye\b', 'to the area', s, flags=re.I)
    # "gidebileceğiniz" → "to visit"
    s = re.sub(r'\bgidebilece[ğg]iniz\b', 'to visit', s, flags=re.I)
    # "iş yemekleri ideal for" → "business lunches, an ideal"
    s = re.sub(r'\bi[şs]\s+yemekleri\b', 'business lunches,', s, flags=re.I)
    # "gastronomi severler" already partially handled
    # cleanup
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

# Verify the specific string is gone
pats = re.compile(r'olmas[ıi]ndan\s+dolay[ıi]|sunmas[ıi]|nedenlerle|nedeniyle', re.I)
rem = [(r['name'], qa.get(f,'')) for r in data for qa in r.get('faq',[])
       for f in ['answer','question'] if pats.search(qa.get(f,''))]
print(f'Remaining: {len(rem)}')
for name, v in rem:
    print(f'  [{name}] {v[:110]}')
