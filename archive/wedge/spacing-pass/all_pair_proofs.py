from pathlib import Path
import importlib.util,json
root=Path(__file__).parent
spec=importlib.util.spec_from_file_location('proof','skills/font-spacing-kerning/scripts/render_kerning_proofs.py'); mod=importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
k=json.loads((root/'trial-1.json').read_text())['kerning_overrides']
# Use exact strings, so every proposed exception receives compiled OFF/ON evidence.
keys=list(k)
texts=[' '.join(keys[n:n+6]) for n in range(0,len(keys),6)]
mod.render_proofs(root/'trial-project',out=root/'all-pairs',font_size=50,pixel_scale=3,sheet_width=640,rows_per_sheet=4,texts=texts,include_defaults=False)
