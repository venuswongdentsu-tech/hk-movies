#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build the PWA static site: data.js + posters/ + icons/ into /workspace/hk-movies-app."""
import json, os, re, shutil, subprocess, datetime
from PIL import Image, ImageDraw

SRC = "/workspace/movies"
OUT = "/workspace/hk-movies-app"

def hk_today():
    try:
        return subprocess.check_output(["date", "+%Y-%m-%d"], env={**os.environ, "TZ": "Asia/Hong_Kong"}).decode().strip()
    except Exception:
        return datetime.date.today().isoformat()

def top5(c, cen=None, n=5):
    """回傳 [{zh, en}] — en 由 cast_en.json（Wikidata）查得，查唔到就空字串。"""
    if not c or c in ("None", ""): return []
    cen = cen or {}
    out = []
    for p in re.split(r"\s*,\s*", c):
        p = p.strip()
        if not p: continue
        v = cen.get(p)
        out.append({"zh": p, "en": (v.get("en") if isinstance(v, dict) else "") or ""})
        if len(out) >= n: break
    return out

def is_new(x): return x.get("kind") == "本週新上映"

def main():
    data = json.load(open(f"{SRC}/movie_data.json"))
    sent = json.load(open(f"{SRC}/sentiment.json"))
    sent_n = {k.replace(" ", ""): v for k, v in sent.items()}
    _cp = f"{SRC}/cast_en.json"
    cen = json.load(open(_cp, encoding="utf-8")) if os.path.exists(_cp) else {}
    os.makedirs(f"{OUT}/posters", exist_ok=True)
    os.makedirs(f"{OUT}/icons", exist_ok=True)

    movies, new_n, still_n = [], 0, 0
    for i, x in enumerate(data):
        kind = "new" if is_new(x) else "still"
        if kind == "new": new_n += 1
        else: still_n += 1
        # poster -> ascii filename
        rel = None
        src_poster = f"{SRC}/{x['poster_local']}" if x.get("poster_local") else None
        if src_poster and os.path.exists(src_poster):
            rel = f"posters/p{i:02d}.jpg"
            im = Image.open(src_poster).convert("RGB")
            im = im.resize((300, 450)) if im.size != (300, 450) else im
            im.save(f"{OUT}/{rel}", "JPEG", quality=82, optimize=True)
        s = sent_n.get(x["zh"].replace(" ", ""), {}) if kind == "still" else {}
        movies.append({
            "i": i, "zh": x["zh"], "en": (x.get("en") or "").strip(),
            "kind": kind, "release_date": x.get("release_date") or "",
            "cinemas": x.get("cinemas") or "", "runtime": (x.get("runtime") or "").replace("None", ""),
            "genre": (x.get("genre") or "").replace("None", ""), "cert": (x.get("cert") or "").replace("None", ""),
            "director": (x.get("director") or "").replace("None", ""),
            "cast": top5(x.get("cast"), cen), "plot": (x.get("plot") or "").replace("None", ""),
            "wmoov": x.get("wmoov"), "hkm6": x.get("hkm6_rating"), "imdb": x.get("imdb"),
            "rt_t": x.get("rt_tomato"), "rt_a": x.get("rt_aud"),
            "hkm6_votes": x.get("hkm6_votes"), "hkm6_likes": x.get("hkm6_likes"),
            "hkm6_reviews": x.get("hkm6_reviews"), "poster": rel,
            "pos": s.get("pos", []), "neg": s.get("neg", []), "note": s.get("note", ""),
        })

    payload = {"date": hk_today(), "counts": {"new": new_n, "still": still_n, "total": len(movies)}, "movies": movies}
    with open(f"{OUT}/data.js", "w", encoding="utf-8") as f:
        f.write("window.APP_DATA = ")
        json.dump(payload, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    ds = hk_today().replace("-", "")
    # VER 加入 data.js 內容雜湊：資料一改，快取名就跟住變 → 強制手機更新快取
    import hashlib
    h = hashlib.sha1(open(f"{OUT}/data.js", "rb").read()).hexdigest()[:8]
    with open(f"{OUT}/sw.js", encoding="utf-8") as f: sw = f.read()
    sw = re.sub(r'const VER = "[^"]*"', f'const VER = "hkmv-{ds}-{h}"', sw)
    with open(f"{OUT}/sw.js", "w", encoding="utf-8") as f: f.write(sw)

    # ---- icons ----
    def icon(size, maskable=False):
        im = Image.new("RGB", (size, size), "#0b1220")
        d = ImageDraw.Draw(im)
        for y in range(size):
            t = y / size
            d.line([(0, y), (size, y)], fill=(int(11 + 12 * (1 - t)), int(18 + 20 * (1 - t)), int(32 + 30 * (1 - t))))
        pad = size * (0.10 if maskable else 0.16)
        box = [pad, pad, size - pad, size - pad]
        d.rounded_rectangle(box, radius=size * 0.16, outline="#ffd166", width=max(2, int(size * 0.035)))
        cxp = (box[0] + box[2]) / 2; cyp = (box[1] + box[3]) / 2
        r = size * 0.17
        d.polygon([(cxp - r * .6, cyp - r), (cxp - r * .6, cyp + r), (cxp + r * .9, cyp)], fill="#ffffff")
        for k in range(4):
            yy = box[1] + (box[3] - box[1]) * (k + 1) / 5
            d.rounded_rectangle([box[0] + size * .012, yy - size * .012, box[0] + size * .05, yy + size * .012],
                                radius=size * .01, fill="#ffd166")
            d.rounded_rectangle([box[2] - size * .05, yy - size * .012, box[2] - size * .012, yy + size * .012],
                                radius=size * .01, fill="#ffd166")
        return im
    icon(512).save(f"{OUT}/icons/icon-512.png")
    icon(192).save(f"{OUT}/icons/icon-192.png")
    icon(180).save(f"{OUT}/icons/apple-touch-icon.png")
    icon(512, maskable=True).save(f"{OUT}/icons/maskable-512.png")

    open(f"{OUT}/.nojekyll", "w").close()
    print(f"built: {len(movies)} movies (new {new_n} / still {still_n}) date={payload['date']}")
    print("posters:", len([m for m in movies if m['poster']]))

if __name__ == "__main__":
    main()
