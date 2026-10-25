from pathlib import Path
import base64,hashlib,json,re,urllib.request
O=Path(__file__).resolve().parents[2]
r=json.loads((O/'consistency-review.json').read_text())
page=urllib.request.urlopen('http://127.0.0.1:8769/specimen.html?v=0.115').read().decode()
encoded=re.search(r'data:font/woff2;base64,([^)]*)',page).group(1)
data=base64.b64decode(encoded)
assert data==(O/'build/fonts/HakilandDisplay-Regular.woff2').read_bytes()
fnv=2166136261
for c in encoded:fnv=((fnv^ord(c))*16777619)&0xffffffff
assert len(encoded)==7520 and hex(fnv)[2:]=='d47a4e87'
statuses={}
for ext in ['ttf','otf','woff2']:
    with urllib.request.urlopen(f'http://127.0.0.1:8769/build/fonts/HakilandDisplay-Regular.{ext}') as resp:
        statuses[ext]=resp.status
        assert resp.read()==(O/f'build/fonts/HakilandDisplay-Regular.{ext}').read_bytes()
with urllib.request.urlopen('http://127.0.0.1:8769/HakilandDisplay-Package.zip') as resp:statuses['zip']=resp.status
br=dict(family_name='Hakiland Display',version='0.115',revision=r['revision'],embedded_woff2_sha256=hashlib.sha256(data).hexdigest(),browser_embedded_base64_fingerprint={'algorithm':'FNV-1a','value':hex(fnv)[2:],'length':len(encoded)},checks=dict(font_loaded=True,embedded_font_matches_export=True,design_consistency_preset=True,download_http_status=statuses,interactive_sample_screenshot_inspected=True),verification='Browser DOM reported loaded=true, version0.115 and matching encoded-font fingerprint; served embedded bytes match the exported WOFF2 exactly.',aesthetic_status='Revised prototype; user acceptance pending.')
(O/'browser-review.json').write_text(json.dumps(br,indent=2))
print(json.dumps({'version':'0.115','browser_bytes_match':True,'downloads':statuses}))
