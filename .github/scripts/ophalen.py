import json, os, re, sys, urllib.request
MAP = os.environ["MAP"]; LOG = os.environ.get("LOG") or ""
def log(msg):
    print(msg)
    if LOG:
        with open(LOG, "a") as f: f.write(msg + "\n")
def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=30).read()
try:
    html = get(f"https://drive.google.com/embeddedfolderview?id={MAP}").decode("utf-8", "replace")
except Exception as e:
    log(f"Map niet bereikbaar: {e}"); sys.exit(0)
items = re.findall(r'/file/d/([\w-]+)/view[^"]*"[^>]*>.*?flip-entry-title">([^<]+)<', html, re.S)
items = [(t.strip(), i) for i, t in items if t.strip().startswith("robur-data-")]
log(f"Gevonden bestanden: {sorted(items)}")
if not items: sys.exit(0)
titel, fid = max(items)
try:
    raw = get(f"https://drive.google.com/uc?export=download&id={fid}")
    data = json.loads(raw)
except Exception as e:
    log(f"Downloaden of lezen mislukt ({titel}): {e}"); sys.exit(0)
if not all(k in data for k in ("team", "results", "fixtures", "selectie", "wedstrijden")):
    log(f"{titel} is geen volledig gegevensbestand; niets veranderd."); sys.exit(0)
verboden = {"duels", "dw", "dl", "verlies", "verovering", "redding", "xg", "xa", "bijdrage", "pm", "onoff", "zone"}
def check(o):
    if isinstance(o, dict):
        for k, v in o.items():
            if k.lower() in verboden: raise ValueError(k)
            check(v)
    elif isinstance(o, list):
        for v in o: check(v)
try: check(data)
except ValueError as e:
    log(f"Geweigerd: privéveld '{e}' in {titel}"); sys.exit(0)
nieuw = json.dumps(data, ensure_ascii=False, indent=1) + "\n"
oud = open("data.json", encoding="utf-8").read() if os.path.exists("data.json") else ""
if nieuw != oud:
    open("data.json", "w", encoding="utf-8").write(nieuw); log(f"Bijgewerkt uit {titel}")
else:
    log(f"Geen wijzigingen ({titel})")
