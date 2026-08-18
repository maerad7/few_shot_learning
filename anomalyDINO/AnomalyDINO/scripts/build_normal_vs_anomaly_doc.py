#!/usr/bin/env python
"""Builds docs/normal_vs_anomaly.html from /tmp/visa_thumbs.json."""
import json

DATA = json.load(open("/tmp/visa_thumbs.json"))

CAPTIONS = {
    "candle":     "Caved-in, uneven wax surface near the wick",
    "capsules":   "Dark discoloration and a chip at one capsule's tip",
    "cashew":     "Malformed shape — an extra lobe fused onto the crescent",
    "chewinggum": "Grey smudge or residue on the surface",
    "fryum":      "Two fryum pieces stuck together, overlapping",
    "macaroni1":  "Small chip broken off the piece's edge",
    "macaroni2":  "Tiny chip broken off the tip",
    "pcb1":       "Scratch or surface mark across the board",
    "pcb2":       "Scratch running across the board's components",
    "pcb3":       "Misaligned or discolored component near the IR sensor",
    "pcb4":       "Excess solder / a solder bridge near a component",
    "pipe_fryum": "Two pieces stuck together, overlapping",
}

ORDER = ["candle","capsules","cashew","chewinggum","fryum","macaroni1",
         "macaroni2","pcb1","pcb2","pcb3","pcb4","pipe_fryum"]

CARD_TMPL = """
      <div class="cat-card">
        <div class="cat-head">
          <h3>{name}</h3>
          <span class="defect-pill">{pct}% of frame</span>
        </div>
        <p class="cat-caption">{caption}</p>
        <div class="img-row">
          <figure>
            <img src="{normal}" alt="A normal {name} sample" loading="lazy">
            <figcaption>normal</figcaption>
          </figure>
          <figure>
            <img src="{overview}" alt="An anomalous {name} sample with the defect boxed in red" loading="lazy">
            <figcaption>anomaly</figcaption>
          </figure>
          <figure class="closeup">
            <img src="{closeup}" alt="Close-up crop of the defect on the {name} sample" loading="lazy">
            <figcaption>defect close-up</figcaption>
          </figure>
        </div>
      </div>"""

cards = []
for cat in ORDER:
    d = DATA[cat]
    cards.append(CARD_TMPL.format(
        name=cat, pct=d["defect_pct"], caption=CAPTIONS[cat],
        normal=d["normal"], overview=d["overview"], closeup=d["closeup"]
    ))

HTML = """<title>Normal vs. Anomaly, VisA</title>
<style>
  .doc-root {{
    color-scheme: light;
    --bg-page:        #f9f9f7;
    --bg-surface:     #fcfcfb;
    --bg-band:        #f2f1ec;
    --text-primary:   #0b0b0b;
    --text-secondary: #52514e;
    --text-muted:     #898781;
    --grid:           #e1e0d9;
    --axis:           #c3c2b7;
    --border:         rgba(11,11,11,0.10);
    --accent:         #2a78d6;
    --accent-2:       #e34948;
  }}
  @media (prefers-color-scheme: dark) {{
    :root:not([data-theme="light"]) .doc-root {{
      color-scheme: dark;
      --bg-page:        #0d0d0d;
      --bg-surface:     #1a1a19;
      --bg-band:        #202020;
      --text-primary:   #ffffff;
      --text-secondary: #c3c2b7;
      --text-muted:     #898781;
      --grid:           #2c2c2a;
      --axis:           #383835;
      --border:         rgba(255,255,255,0.10);
      --accent:         #3987e5;
      --accent-2:       #e66767;
    }}
  }}
  :root[data-theme="dark"] .doc-root {{
    color-scheme: dark;
    --bg-page:        #0d0d0d;
    --bg-surface:     #1a1a19;
    --bg-band:        #202020;
    --text-primary:   #ffffff;
    --text-secondary: #c3c2b7;
    --text-muted:     #898781;
    --grid:           #2c2c2a;
    --axis:           #383835;
    --border:         rgba(255,255,255,0.10);
    --accent:         #3987e5;
    --accent-2:       #e66767;
  }}

  * {{ box-sizing: border-box; }}
  .doc-root {{
    background: var(--bg-page); color: var(--text-primary);
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Helvetica, Arial, sans-serif;
    line-height: 1.6; padding-bottom: 64px;
  }}
  .wrap {{ max-width: 1080px; margin: 0 auto; padding: 0 28px; }}

  .masthead {{ padding: 56px 0 34px; border-bottom: 1px solid var(--border); }}
  .eyebrow {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-size: 12px; letter-spacing: 0.14em; text-transform: uppercase;
    color: var(--accent); font-weight: 600; margin: 0 0 14px;
  }}
  h1 {{ font-size: clamp(30px, 4.6vw, 42px); font-weight: 700; letter-spacing: -0.02em; margin: 0 0 12px; text-wrap: balance; }}
  .dek {{ font-size: 16px; color: var(--text-secondary); max-width: 68ch; margin: 0 0 20px; }}
  .badges {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .badge {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-size: 12px; color: var(--text-secondary); background: var(--bg-surface);
    border: 1px solid var(--border); border-radius: 5px; padding: 5px 10px;
  }}

  .legend-row {{ display: flex; gap: 22px; flex-wrap: wrap; padding: 20px 0 0; font-size: 13px; color: var(--text-secondary); }}
  .legend-row b {{ color: var(--text-primary); }}
  .swatch {{ display:inline-block; width:10px; height:10px; border-radius:2px; margin-right:6px; vertical-align:1px; }}
  .swatch.red {{ background: var(--accent-2); }}

  main {{ padding: 34px 0 0; }}

  .cat-grid {{ display: grid; grid-template-columns: 1fr; gap: 18px; }}
  .cat-card {{
    background: var(--bg-surface); border: 1px solid var(--border); border-radius: 12px;
    padding: 18px 20px 20px;
  }}
  .cat-head {{ display: flex; align-items: baseline; justify-content: space-between; gap: 10px; margin-bottom: 4px; }}
  .cat-head h3 {{ font-size: 16px; font-weight: 700; margin: 0; text-transform: capitalize; letter-spacing: -0.01em; }}
  .defect-pill {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace;
    font-size: 11px; color: var(--text-secondary); background: var(--bg-band);
    border: 1px solid var(--border); border-radius: 20px; padding: 3px 10px; white-space: nowrap;
  }}
  .cat-caption {{ font-size: 13.5px; color: var(--text-secondary); margin: 0 0 14px; }}
  .img-row {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; }}
  .img-row figure {{ margin: 0; }}
  .img-row img {{
    width: 100%; height: auto; display: block; border-radius: 8px; border: 1px solid var(--border);
    background: var(--bg-band);
  }}
  .img-row figure.closeup img {{ border-color: var(--accent-2); border-width: 1.5px; }}
  .img-row figcaption {{
    font-size: 10.5px; text-transform: uppercase; letter-spacing: 0.06em; color: var(--text-muted);
    text-align: center; margin-top: 6px;
  }}

  @media (max-width: 640px) {{
    .img-row {{ grid-template-columns: 1fr 1fr; }}
    .img-row figure.closeup {{ grid-column: 1 / -1; max-width: 60%; margin: 0 auto; }}
  }}

  footer {{ padding: 40px 0 8px; border-top: 1px solid var(--border); margin-top: 30px; }}
  .fine {{ font-size: 11.5px; color: var(--text-muted); }}
  code {{
    font-family: ui-monospace, "SF Mono", "Cascadia Mono", Menlo, Consolas, monospace; font-size: 12px;
    background: var(--bg-band); padding: 1px 6px; border-radius: 4px;
  }}
</style>

<div class="doc-root">
  <div class="wrap">

    <header class="masthead">
      <p class="eyebrow">Dataset reference · visual examples</p>
      <h1>Normal vs. Anomaly, by Category</h1>
      <p class="dek">What actually separates a "good" VisA sample from a defective one, category by category. For each of the 12 objects: a normal reference sample, the single most clearly defective test sample (largest mask area), and a tight crop on the defect itself.</p>
      <div class="badges">
        <span class="badge">12 categories</span>
        <span class="badge">largest-mask sample per category</span>
        <span class="badge">source: VisA test/bad + Masks/Anomaly</span>
      </div>
      <div class="legend-row">
        <span><span class="swatch red"></span><b>Red box</b> — the defect's mask bounding box, padded ~12%</span>
        <span><b>% of frame</b> — defect mask area as a share of the full image</span>
      </div>
    </header>

    <main>
      <div class="cat-grid">
{cards}
      </div>
    </main>

    <footer>
      <p class="fine">Normal sample = first file in <code>Data/Images/Normal/</code>. Anomaly sample = the <code>Data/Masks/Anomaly/</code> mask with the largest defect area for that category (not necessarily the "average" defect — chosen for visibility). Generated by <code>scripts/make_normal_vs_anomaly_thumbs.py</code> from the raw VisA release.</p>
    </footer>

  </div>
</div>
""".format(cards="".join(cards))

with open("/home/doseok/workspace2/few_zero_shot_expermention/anomalyDINO/AnomalyDINO/docs/normal_vs_anomaly.html", "w") as f:
    f.write(HTML)

print(f"Wrote {len(HTML)/1024:.1f} KB HTML")
