# -*- coding: utf-8 -*-
"""Kalan Türkçe highlight'ları Groq ile toplu çevirir."""
import json, os, re, sys, time
sys.stdout.reconfigure(encoding="utf-8")
from groq import Groq

INPUT = "data/processed/istanbul.json"
TR_CHARS = re.compile(r'[şçğüöıŞÇĞÜÖİâîû]')

with open(INPUT, encoding="utf-8") as f:
    data = json.load(f)

# Tüm benzersiz Türkçe highlight'ları topla
unique_tr = set()
for r in data:
    for h in r.get("highlights", []):
        if TR_CHARS.search(h):
            unique_tr.add(h.strip())

print(f"Benzersiz Türkçe highlight: {len(unique_tr)}")

client = Groq(api_key=os.environ["GROQ_API_KEY"])
translation_map: dict[str, str] = {}

# 30'luk batch'ler halinde çevir
items = sorted(unique_tr)
BATCH = 30

for i in range(0, len(items), BATCH):
    batch = items[i:i+BATCH]
    numbered = "\n".join(f"{j+1}. {t}" for j, t in enumerate(batch))
    prompt = f"""Translate each numbered Turkish restaurant highlight to natural English.
Return ONLY the translations in the same numbered format. Keep restaurant/food names as-is.
Do not add explanations.

{numbered}"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1000,
            temperature=0.1,
        )
        result = resp.choices[0].message.content.strip()
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        for line in lines:
            m = re.match(r"^(\d+)\.\s+(.+)$", line)
            if m:
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(batch):
                    translation_map[batch[idx]] = m.group(2).strip()
        print(f"  Batch {i//BATCH+1}: {len(batch)} çevrildi")
    except Exception as e:
        print(f"  Hata: {e}")
    time.sleep(1)

# Eksik çevirileri raporla
missing = [t for t in unique_tr if t not in translation_map]
if missing:
    print(f"\nÇevirilemeyen {len(missing)} highlight (orijinal bırakıldı):")
    for m in missing[:10]:
        print(f"  - {m}")

# Veriyi güncelle
changed = 0
for r in data:
    if not r.get("highlights"):
        continue
    new_h = []
    for h in r["highlights"]:
        stripped = h.strip()
        if stripped in translation_map:
            new_h.append(translation_map[stripped])
            changed += 1
        else:
            new_h.append(h)
    r["highlights"] = new_h

with open(INPUT, "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print(f"\n[OK] {changed} highlight güncellendi.")
