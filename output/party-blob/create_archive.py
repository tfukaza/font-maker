"""Package final deliverables and the exact source manifest without stale builds."""
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import yaml
p=Path(__file__).resolve().parent
manifest=yaml.safe_load((p/'font/font.yaml').read_text())
paths=set()
for folder in ['drawings','concepts','layout-review','final-kerning','ligature-drawings','ligature-proofs','ligature-review']:
 paths.update(f for f in (p/folder).rglob('*') if f.is_file())
for folder in ['font/glyphs','font/references']:
 paths.update(f for f in (p/folder).rglob('*') if f.is_file())
paths.update((p/'font/build/fonts').glob('PartyBlob-Regular.*'))
paths.update([p/'font/font.yaml',p/'font/glyph-template.svg'])
for pattern in ['*.py','*final.json','*complete.json','*shape-*.json','*preview-*.json','size-*.json','*.html','*.png','*.svg']:
 paths.update(p.glob(pattern))
for name in ['README.md','acceptance.json','build-report.json','measurements.json','mcp-transcript.jsonl','extension-glyphs.json','rebuild.json','complete.json','creative-glyphs.json','creative-acceptance.json','promote-ligatures.json','review-build.json']:
 paths.add(p/name)
# Include the compiled preview files referenced by the selected evidence JSONs.
for f in list(paths):
 if f.suffix != '.json':continue
 try: data=json.loads(f.read_text())
 except ValueError:continue
 if isinstance(data,dict):
  for artifact in data.get('artifacts',[]):
   candidate=p/'font'/artifact['path']
   if candidate.exists():paths.add(candidate)
archive=p/'Party-Blob-proof.zip'
with ZipFile(archive,'w',ZIP_DEFLATED) as z:
 for f in sorted(paths):
  if f.is_file():z.write(f,Path('Party Blob')/f.relative_to(p))
 for skill in ['font-ligature-design','font-production-workflow','font-spacing-kerning','font-specimen-review']:
  source=p.parents[1]/'skills'/skill/'SKILL.md'
  z.write(source,Path('Party Blob/skill-snapshots')/skill/'SKILL.md')
with ZipFile(archive) as z:
 assert z.testzip() is None
 for ext in ['ttf','otf','woff2']:
  target=f'font/build/fonts/PartyBlob-Regular.{ext}'
  assert z.read('Party Blob/'+target)==(p/target).read_bytes()
print(f'{archive}: {archive.stat().st_size:,} bytes, {len(paths)} files plus skill snapshots')
