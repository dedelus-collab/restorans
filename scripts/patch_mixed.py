import json, re, sys
sys.stdout.reconfigure(encoding='utf-8')
with open('data/processed/istanbul.json', encoding='utf-8') as f:
    data = json.load(f)

def fix(s):
    # dk → min
    s = re.sub(r'\((\d+)\s*dk\)', r'(\1 min)', s, flags=re.I)
    s = re.sub(r'\b(\d+)\s*dk\b', r'\1 min', s, flags=re.I)
    # tramvay/vapur/metro suffixes
    s = re.sub(r'\btramvay[ıi]\b', 'tram', s, flags=re.I)
    s = re.sub(r'\btramvay\s+dura[ğg][ıi]\b', 'tram stop', s, flags=re.I)
    s = re.sub(r'\bvapuru\b', 'ferry', s, flags=re.I)
    # 'nden / 'ndan / 'ten / 'tan suffixes (remove possessive/ablative)
    s = re.sub(r"'[ıiuü]?nden\b", "'s", s, flags=re.I)
    s = re.sub(r"'[ıiuü]?ndan\b", "'s", s, flags=re.I)
    s = re.sub(r"'ten\b", '', s, flags=re.I)
    s = re.sub(r"'tan\b", '', s, flags=re.I)
    s = re.sub(r"\u2019[ıiuü]?nden\b", "'s", s, flags=re.I)
    s = re.sub(r"\u2019[ıiuü]?ndan\b", "'s", s, flags=re.I)
    # 'n / 'nı / 'nın  (remove Turkish genitive from proper nouns)
    s = re.sub(r"'n[ıi]n\b", "'s", s, flags=re.I)
    s = re.sub(r"\u2019n[ıi]n\b", "'s", s, flags=re.I)
    s = re.sub(r"'n[ıi]\b", '', s, flags=re.I)
    s = re.sub(r"\u2019n[ıi]\b", '', s, flags=re.I)
    # Caddesi'n → remove trailing 'n
    s = re.sub(r"Caddesi'n\b", "Caddesi", s)
    s = re.sub(r"Caddesi\u2019n\b", "Caddesi", s)
    # ise → is/also
    s = re.sub(r'\bise\b', 'is', s, flags=re.I)
    # ama → but
    s = re.sub(r'\bama\b', 'but', s, flags=re.I)
    # özgü → distinctive
    s = re.sub(r'\b[öo]zg[üu]\b', 'distinctive', s, flags=re.I)
    # çok / daha patterns
    s = re.sub(r'\ben\s+[çc]ok\s+tercih\s+edilen\w*\b', 'most popular', s, flags=re.I)
    s = re.sub(r'\ben\s+[çc]ok\s+tercih\s+edilenidir\b', 'is the most popular', s, flags=re.I)
    s = re.sub(r'\bdaha\s+fazla\b', 'more', s, flags=re.I)
    s = re.sub(r'\bdaha\s+pleasant\b', 'more pleasant', s, flags=re.I)
    s = re.sub(r'\bdaha\b', 'more', s, flags=re.I)
    s = re.sub(r'\b[çc]ok\b', 'very', s, flags=re.I)
    # kadar → up to / as far as
    s = re.sub(r'\bne\s+kadar\b', 'how much', s, flags=re.I)
    s = re.sub(r'\bkadar\b', 'until', s, flags=re.I)
    # sadece → only
    s = re.sub(r'\bsadece\b', 'only', s, flags=re.I)
    # bile → even
    s = re.sub(r'\bbile\b', 'even', s, flags=re.I)
    # hatta → in fact
    s = re.sub(r'\bhatta\b', 'in fact', s, flags=re.I)
    # olarak → as
    s = re.sub(r'\bolarak\b', 'as', s, flags=re.I)
    # için → for
    s = re.sub(r'\bi[çc]in\b', 'for', s, flags=re.I)
    # ile → with
    s = re.sub(r'\s+ile\s+', ' with ', s, flags=re.I)
    s = re.sub(r'^ile\s+', 'with ', s, flags=re.I)
    # veya → or
    s = re.sub(r'\bveya\b', 'or', s, flags=re.I)
    # ancak → however
    s = re.sub(r'\bancak\b', 'however', s, flags=re.I)
    # ya da → or
    s = re.sub(r'\bya\s+da\b', 'or', s, flags=re.I)
    # gibi → like / such as
    s = re.sub(r'\bgibi\b', 'like', s, flags=re.I)
    # Our dishes suffixes
    s = re.sub(r'\bKebaplar[ıi]m[ıi]z\b', 'Kebap', s)
    s = re.sub(r'\byemeklerimizdendir\b', 'are our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimizi\b', 'our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimizdir\b', 'are our dishes', s, flags=re.I)
    s = re.sub(r'\byemeklerimiz\b', 'our dishes', s, flags=re.I)
    s = re.sub(r'\blezzetlerimizdir\b', 'are our flavors', s, flags=re.I)
    s = re.sub(r'\blezzetlerimizi\b', 'our flavors', s, flags=re.I)
    s = re.sub(r'\blezzetlerimiz\b', 'our flavors', s, flags=re.I)
    # hareketli → lively
    s = re.sub(r'\bhareketli\b', 'lively', s, flags=re.I)
    # eğlenceli → fun
    s = re.sub(r'\be[ğg]lenceli\b', 'fun', s, flags=re.I)
    # keyfinizi / keyfi → enjoyment
    s = re.sub(r'\bkeyfinizi\b', 'your enjoyment', s, flags=re.I)
    s = re.sub(r'\bkeyfi\b', 'enjoyment', s, flags=re.I)
    # hale getirir → makes it
    s = re.sub(r'\bhale\s+getirir\b', 'makes it', s, flags=re.I)
    # ünlü → famous
    s = re.sub(r'\b[üu]nl[üu]\b', 'famous', s, flags=re.I)
    # zorunluluğu yok → not required
    s = re.sub(r'zorunlulu[ğg]u\s+yok', 'not required', s, flags=re.I)
    # Var, ama teras yok → Yes, but there is no terrace
    s = re.sub(r'^Var[,.]?\s*but\s+teras\s+yok\.?$', 'Yes, but there is no terrace.', s, flags=re.I)
    # mahallesinde → neighborhood
    s = re.sub(r'\bmahallesinde\b', 'neighborhood', s, flags=re.I)
    # sokakta → on the street
    s = re.sub(r'\bsokakta\b', 'on the street', s, flags=re.I)
    # caddesinde → on the avenue
    s = re.sub(r'\bcaddesinde\b', 'on the avenue', s, flags=re.I)
    # istasyonuna → station
    s = re.sub(r'\bistasyonuna\b', 'station', s, flags=re.I)
    # durağından (remaining)
    s = re.sub(r'\s+dura[ğg][ıi]ndan\b', ' stop,', s, flags=re.I)
    # açık → open
    s = re.sub(r'\ba[çc][ıi]k\b', 'open', s, flags=re.I)
    # Cleanup double spaces
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
print(f'Patched {changed} strings')

# Recount
TRULY_TR = re.compile(
    r'\b(özgü|ise\b|dk\b|vapuru|tramvayı|dura[ğg][ıi]\b|'
    r'larımız|lerimiz|ndan\b|nden\b|'
    r'için\b|ile\b|veya\b|ama\b|çok\b|daha\b|hatta\b|sadece\b|'
    r'kebaplarımız|yemeklerimiz|lezzetlerimiz)', re.I)
remaining = sum(1 for r in data for qa in r.get('faq',[])
                for f in ['answer','question'] if TRULY_TR.search(qa.get(f,'')))
print(f'Remaining mixed strings: {remaining}')
