#!/usr/bin/env python
"""
For each VisA category, pick the anomaly sample with the largest defect mask
(clearest example), then produce three small base64 JPEG data URIs:
  - normal:   a representative normal image, resized
  - overview: the anomaly image, resized, with a red box drawn around the defect
  - closeup:  a tight crop around the defect, resized

Writes a JSON file mapping category -> {normal, overview, closeup, defect_pct}
so the HTML doc can embed them directly as data: URIs.
"""
import os, json, base64, io
from PIL import Image, ImageDraw
import numpy as np

VISA_ROOT = "/media/doseok/f12b5814-5f3a-4f01-a0a0-9014069c7587/data/VisA"
CATEGORIES = ["candle","capsules","cashew","chewinggum","fryum","macaroni1",
              "macaroni2","pcb1","pcb2","pcb3","pcb4","pipe_fryum"]

THUMB_W = 340
CROP_DISPLAY = 300
JPEG_Q = 68

def to_data_uri(img):
    buf = io.BytesIO()
    img.convert("RGB").save(buf, format="JPEG", quality=JPEG_Q, optimize=True)
    b64 = base64.b64encode(buf.getvalue()).decode("ascii")
    return f"data:image/jpeg;base64,{b64}", len(buf.getvalue())

def resize_width(img, w):
    ratio = w / img.width
    return img.resize((w, max(1, int(img.height * ratio))), Image.LANCZOS)

def best_anomaly_sample(cat):
    mask_dir = os.path.join(VISA_ROOT, cat, "Data", "Masks", "Anomaly")
    best = None
    best_area = -1
    for fn in sorted(os.listdir(mask_dir)):
        mask = np.array(Image.open(os.path.join(mask_dir, fn)).convert("L"))
        area = int((mask > 0).sum())
        if area > best_area:
            best_area = area
            best = fn
    return best, best_area

def bbox_from_mask(mask_arr):
    ys, xs = np.where(mask_arr > 0)
    return xs.min(), ys.min(), xs.max(), ys.max()

def main():
    out = {}
    for cat in CATEGORIES:
        mask_fn, area = best_anomaly_sample(cat)
        stem = os.path.splitext(mask_fn)[0]
        anomaly_img_path = os.path.join(VISA_ROOT, cat, "Data", "Images", "Anomaly", stem + ".JPG")
        mask_path = os.path.join(VISA_ROOT, cat, "Data", "Masks", "Anomaly", mask_fn)

        anomaly_img = Image.open(anomaly_img_path).convert("RGB")
        mask_arr = np.array(Image.open(mask_path).convert("L"))
        x0, y0, x1, y1 = bbox_from_mask(mask_arr)
        W, H = anomaly_img.size
        defect_pct = 100.0 * area / (W * H)

        # --- normal sample: first normal image ---
        normal_dir = os.path.join(VISA_ROOT, cat, "Data", "Images", "Normal")
        normal_fn = sorted(os.listdir(normal_dir))[0]
        normal_img = Image.open(os.path.join(normal_dir, normal_fn)).convert("RGB")
        normal_thumb = resize_width(normal_img, THUMB_W)
        normal_uri, normal_sz = to_data_uri(normal_thumb)

        # --- overview: full anomaly image with a red box around the defect ---
        overview_img = anomaly_img.copy()
        draw = ImageDraw.Draw(overview_img)
        pad = int(max(x1 - x0, y1 - y0) * 0.12) + 8
        bx0, by0 = max(0, x0 - pad), max(0, y0 - pad)
        bx1, by1 = min(W, x1 + pad), min(H, y1 + pad)
        for i in range(4):
            draw.rectangle([bx0 - i, by0 - i, bx1 + i, by1 + i], outline=(230, 40, 40))
        overview_thumb = resize_width(overview_img, THUMB_W)
        overview_uri, overview_sz = to_data_uri(overview_thumb)

        # --- closeup: square crop centered on the defect, padded ---
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        side = max(x1 - x0, y1 - y0) * 2.4
        side = max(side, min(W, H) * 0.18)
        side = min(side, min(W, H))
        half = side / 2
        cx0, cy0 = cx - half, cy - half
        cx1, cy1 = cx + half, cy + half
        # shift into bounds instead of shrinking
        if cx0 < 0: cx1 -= cx0; cx0 = 0
        if cy0 < 0: cy1 -= cy0; cy0 = 0
        if cx1 > W: cx0 -= (cx1 - W); cx1 = W
        if cy1 > H: cy0 -= (cy1 - H); cy1 = H
        cx0, cy0, cx1, cy1 = max(0, cx0), max(0, cy0), min(W, cx1), min(H, cy1)
        closeup = anomaly_img.crop((int(cx0), int(cy0), int(cx1), int(cy1)))
        closeup = closeup.resize((CROP_DISPLAY, CROP_DISPLAY), Image.LANCZOS)
        closeup_uri, closeup_sz = to_data_uri(closeup)

        out[cat] = {
            "normal": normal_uri, "overview": overview_uri, "closeup": closeup_uri,
            "defect_pct": round(defect_pct, 2),
            "sample": stem,
            "sizes_kb": [round(normal_sz/1024,1), round(overview_sz/1024,1), round(closeup_sz/1024,1)]
        }
        total_kb = sum(out[cat]["sizes_kb"])
        print(f"{cat:12s} sample={stem} defect_area={defect_pct:.2f}%  sizes(kb)={out[cat]['sizes_kb']} total={total_kb:.1f}kb")

    with open("/tmp/visa_thumbs.json", "w") as f:
        json.dump(out, f)

    grand_total = sum(sum(v["sizes_kb"]) for v in out.values())
    print(f"\nGrand total: {grand_total:.1f} KB (~{grand_total/1024:.2f} MB) raw JPEG (base64 adds ~33%)")

if __name__ == "__main__":
    main()
