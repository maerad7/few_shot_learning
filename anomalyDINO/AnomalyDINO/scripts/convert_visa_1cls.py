#!/usr/bin/env python
"""
Convert the raw VisA dataset release into the MVTec-AD-style 'VisA_pytorch/1cls'
layout that AnomalyDINO expects, using the official split_csv/1cls.csv split.

Source layout (raw VisA release):
  <visa_root>/<object>/Data/Images/{Normal,Anomaly}/*.JPG
  <visa_root>/<object>/Data/Masks/Anomaly/*.png
  <visa_root>/split_csv/1cls.csv   (object,split,label,image,mask)

Target layout (what run_anomalydino.py / run_anomalydino_batched.py expect):
  <out_root>/<object>/train/good/*.JPG
  <out_root>/<object>/test/good/*.JPG
  <out_root>/<object>/test/bad/*.JPG
  <out_root>/<object>/ground_truth/bad/*.png   (same stem as the anomaly image, no '_mask' suffix)

Files are symlinked (not copied) to avoid duplicating ~1.9GB of data.
"""
import argparse
import csv
import os


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--visa_root", required=True, help="Path to the raw VisA dataset root")
    ap.add_argument("--out_root", required=True, help="Output path for the converted 1cls layout")
    ap.add_argument("--split_csv", default=None, help="Path to split_csv/1cls.csv (default: <visa_root>/split_csv/1cls.csv)")
    args = ap.parse_args()

    visa_root = os.path.abspath(args.visa_root)
    out_root = os.path.abspath(args.out_root)
    split_csv = args.split_csv or os.path.join(visa_root, "split_csv", "1cls.csv")

    counts = {}

    with open(split_csv, newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            obj = row["object"]
            split = row["split"]
            label = row["label"]
            image_rel = row["image"]
            mask_rel = row["mask"]

            src_image = os.path.join(visa_root, image_rel)
            basename = os.path.basename(image_rel)

            if split == "train" and label == "normal":
                dst_dir = os.path.join(out_root, obj, "train", "good")
            elif split == "test" and label == "normal":
                dst_dir = os.path.join(out_root, obj, "test", "good")
            elif split == "test" and label == "anomaly":
                dst_dir = os.path.join(out_root, obj, "test", "bad")
            else:
                raise ValueError(f"Unexpected split/label combo: {split}/{label}")

            os.makedirs(dst_dir, exist_ok=True)
            dst_image = os.path.join(dst_dir, basename)
            if not os.path.lexists(dst_image):
                os.symlink(src_image, dst_image)

            key = (obj, split, label)
            counts[key] = counts.get(key, 0) + 1

            if label == "anomaly" and mask_rel:
                src_mask = os.path.join(visa_root, mask_rel)
                mask_dst_dir = os.path.join(out_root, obj, "ground_truth", "bad")
                os.makedirs(mask_dst_dir, exist_ok=True)
                # AnomalyDINO's VisA-specific parsing expects '<stem>.png' (no '_mask' suffix)
                stem = os.path.splitext(basename)[0]
                dst_mask = os.path.join(mask_dst_dir, stem + ".png")
                if not os.path.lexists(dst_mask):
                    os.symlink(src_mask, dst_mask)

    print(f"Converted VisA from {visa_root} -> {out_root}")
    for (obj, split, label), n in sorted(counts.items()):
        print(f"  {obj:12s} {split:5s} {label:8s} {n}")


if __name__ == "__main__":
    main()
