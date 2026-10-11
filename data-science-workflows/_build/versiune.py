#!/usr/bin/env python3
"""
Ștampila de versiune.

Fiecare import de modul și fiecare foaie de stil au în adresă un `?v=N`.
Browserul ține fișierele în memorie după adresă, deci dacă N nu se schimbă,
omul vede codul vechi oricât l-aș rescrie eu pe cel nou.

De două ori am stricat site-ul uitând să ridic numărul într-un singur fișier.
De aceea numărul nu se mai scrie de mână nicăieri: stă în _build/VERSIUNE, iar
scriptul ăsta îl pune peste tot, în același fel, în toate fișierele deodată.

    python3 _build/versiune.py          # ridică numărul cu unu și ștampilează
    python3 _build/versiune.py 12       # pune exact 12
    python3 _build/versiune.py --check  # nu schimbă nimic, doar spune ce e strâmb

Se rulează ULTIMUL, după orice modificare de conținut sau de cod.
"""

import re
import sys
from pathlib import Path

RADACINA = Path(__file__).resolve().parent.parent
FISIER_VERSIUNE = RADACINA / "_build" / "VERSIUNE"

# Ce se ștampilează. Tot ce poate conține o adresă cu ?v=
TIPARE = ("*.html", "*.js", "*.css", "*.py")

# Ce nu se atinge: ce nu ajunge la browser, și orfanii păstrați ca arhivă.
SARI_PESTE = {".git", "_build", "node_modules", "db", "date", ".claude"}
SARI_FISIERE = {"carte.html"}          # pagina veche, cu ștampilă pe dată

# ?v=3  sau  ?v=20260725 ; prinde și în șiruri de tip `...js?v=4`
RE_V = re.compile(r"(\?v=)(\d+)")


def fisiere():
    for tipar in TIPARE:
        for f in RADACINA.rglob(tipar):
            rel = f.relative_to(RADACINA)
            if set(rel.parts) & SARI_PESTE:
                continue
            if f.name in SARI_FISIERE:
                continue
            yield f


def citeste_versiune() -> int:
    try:
        return int(FISIER_VERSIUNE.read_text(encoding="utf-8").strip())
    except Exception:
        return 1


def main() -> int:
    arg = sys.argv[1] if len(sys.argv) > 1 else None

    if arg == "--check":
        gasite = {}
        for f in fisiere():
            for _, n in RE_V.findall(f.read_text(encoding="utf-8")):
                gasite.setdefault(n, []).append(str(f.relative_to(RADACINA)))
        if len(gasite) <= 1:
            print("Toate ștampilele sunt la fel:", ", ".join(gasite) or "niciuna")
            return 0
        print("Ștampile amestecate — de aici vin paginile care rămân vechi:")
        for n in sorted(gasite, key=int):
            print(f"  v={n}: {len(gasite[n])} fișiere  " +
                  ", ".join(sorted(set(gasite[n]))[:6]))
        return 1

    if arg and arg.isdigit():
        noua = int(arg)
    else:
        noua = citeste_versiune() + 1

    schimbate = 0
    for f in fisiere():
        text = f.read_text(encoding="utf-8")
        nou, cate = RE_V.subn(lambda m: m.group(1) + str(noua), text)
        if cate and nou != text:
            f.write_text(nou, encoding="utf-8")
            schimbate += 1

    FISIER_VERSIUNE.write_text(str(noua) + "\n", encoding="utf-8")
    print(f"Versiunea e acum v={noua}. Am rescris {schimbate} fișiere.")
    print("Acum se poate face commit; fără pasul ăsta, browserul arată vechiul.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
