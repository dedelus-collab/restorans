# -*- coding: utf-8 -*-
"""data/istanbul.ts içindeki Türkçe highlight'ları Groq ile çevirir."""
import json, os, re, sys, time
sys.stdout.reconfigure(encoding="utf-8")

# .env.local'den GROQ_API_KEY oku
env_path = os.path.join(os.path.dirname(__file__), "..", ".env.local")
if os.path.exists(env_path):
    with open(env_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line.startswith("GROQ_API_KEY="):
                os.environ["GROQ_API_KEY"] = line.split("=", 1)[1].strip()

from groq import Groq

TS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "istanbul.ts")
TR = re.compile(r'[şçğüöıŞÇĞÜÖİâîû]')

with open(TS_FILE, encoding="utf-8") as f:
    content = f.read()

# Tüm highlights bloklarındaki Türkçe string'leri topla
all_strings = re.findall(r'"([^"]*)"', content)
unique_tr = sorted({s for s in all_strings
                    if TR.search(s) and len(s) > 4 and s.count(" ") >= 1})

# Sadece highlights içindeki Türkçe metinleri filtrele
# (restaurant isimleri, adresler değil — bunlar doğal Türkçe kalabilir)
# highlights bloklarını bul
highlight_pattern = re.compile(r'highlights:\s*\[([^\]]+)\]', re.DOTALL)
tr_in_highlights = set()
for m in highlight_pattern.finditer(content):
    items = re.findall(r'"([^"]+)"', m.group(1))
    for item in items:
        if TR.search(item):
            tr_in_highlights.add(item)

print(f"Highlights'ta Türkçe: {len(tr_in_highlights)}")

client = Groq(api_key=os.environ["GROQ_API_KEY"])
translation_map: dict[str, str] = {}

items = sorted(tr_in_highlights)
BATCH = 30

for i in range(0, len(items), BATCH):
    batch = items[i:i+BATCH]
    numbered = "\n".join(f"{j+1}. {t}" for j, t in enumerate(batch))
    prompt = f"""Translate each numbered Turkish restaurant highlight to natural English.
Keep food/place names (döner, kunefe, Bosphorus, etc.) in recognizable form.
Return ONLY the numbered translations, no extra text.

{numbered}"""
    try:
        resp = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1200,
            temperature=0.1,
        )
        result = resp.choices[0].message.content.strip()
        lines = [l.strip() for l in result.split("\n") if l.strip()]
        for line in lines:
            m = re.match(r"^(\d+)[\.\)]\s+(.+)$", line)
            if m:
                idx = int(m.group(1)) - 1
                if 0 <= idx < len(batch):
                    translation_map[batch[idx]] = m.group(2).strip()
        print(f"  Batch {i//BATCH+1}/{(len(items)-1)//BATCH+1}: {len(batch)} çevrildi")
    except Exception as e:
        print(f"  Hata batch {i//BATCH+1}: {e}")
    time.sleep(0.8)

# Çevirileri uygula — en uzun string'den başla (kısa önce yanlış eşleşme önler)
new_content = content
replaced = 0
for original in sorted(translation_map, key=len, reverse=True):
    translation = translation_map[original]
    if original == translation:
        continue
    escaped = re.escape(original)
    new_content, n = re.subn(f'"{escaped}"', f'"{translation}"', new_content)
    replaced += n

with open(TS_FILE, "w", encoding="utf-8") as f:
    f.write(new_content)

print(f"\n[OK] {replaced} highlight değiştirildi.")

# Kontrol
remaining = sum(1 for m in highlight_pattern.finditer(new_content)
                for item in re.findall(r'"([^"]+)"', m.group(1))
                if TR.search(item))
print(f"Kalan Türkçe: {remaining}")
