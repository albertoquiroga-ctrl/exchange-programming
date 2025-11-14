# HK Conditions Monitor slides

Binary rehearsal assets (PowerPoint deck and supporting PNG) are stored as Base64 text because this repo is mirrored into environments that reject binary blobs.  Decode them locally before opening the deck:

```bash
python ../../tools/decode_slide_assets.py
# or target a single artifact
python ../../tools/decode_slide_assets.py HK-Conditions-Monitor.pptx.b64
```

The script recreates the original files next to the `.b64` sources:

* `HK-Conditions-Monitor.pptx.b64` → `HK-Conditions-Monitor.pptx`
* `hk-architecture.png.b64` → `hk-architecture.png`

Once decoded, open the PPTX in PowerPoint/Keynote and rehearse directly against the storyboard captured in `../presentation-outline.md`.
