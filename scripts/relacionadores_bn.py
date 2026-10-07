import json, re, sys, pathlib, unicodedata
import requests
from bs4 import BeautifulSoup

URL = "https://escritoriopt.bn.gov.ar/e-relacionadores.html"
SALIDA = pathlib.Path("relacionadores_bn.json")
MIN_TERMINOS = 50   # protección: si sale menos, algo cambió en la página

r = requests.get(URL, timeout=60,
                 headers={"User-Agent": "Mozilla/5.0 (compatible; relacionadores-bot)"})
r.raise_for_status()

soup = BeautifulSoup(r.content, "lxml")

res, vistos = [], set()

for tr in soup.find_all("tr"):
    code = tr.select_one("td a[id]")
    labels = tr.select("td big b")
    if not code or not labels:
        continue
    codigo = code["id"]
    for b in labels:
        for br in b.find_all("br"):
            br.replace_with("\n")
        for linea in b.get_text().split("\n"):
            limpio = re.sub(r"\s+", " ", linea).strip()
            if limpio and (limpio, codigo) not in vistos:
                vistos.add((limpio, codigo))
                res.append({"texto": limpio, "codigo": codigo})

def clave(x):
    base = unicodedata.normalize("NFD", x["texto"].lower())
    return "".join(c for c in base if unicodedata.category(c) != "Mn")

res.sort(key=clave)

if len(res) < MIN_TERMINOS:
    sys.exit(f"Solo {len(res)} términos: no se sobrescribe el archivo.")

SALIDA.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
print(f"{len(res)} relacionadores guardados")
