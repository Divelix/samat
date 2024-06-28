"""
Predicts segmentation masks via SAM model
for all images in given dataset.
Saves mask as 8-bit grayscale .PNG
"""

from pathlib import Path
import time
from PIL import Image
import tomllib

import numpy as np
from tqdm import tqdm
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator


def make_annotator(weights_path: str, device: str) -> SamAutomaticMaskGenerator:
    model_type = "vit_h"
    print(f"Loading {model_type} on {device} device")
    t1 = time.perf_counter()
    sam = sam_model_registry[model_type](weights_path)
    t2 = time.perf_counter()
    sam.to(device)
    t3 = time.perf_counter()
    mask_generator = SamAutomaticMaskGenerator(sam)
    print(f"Load weights: {(t2-t1):.3f}s\nMove to {device}: {(t3-t2):.3f}s")
    return mask_generator


if __name__ == "__main__":
    with open("config.toml", "rb") as f:
        config = tomllib.load(f)
    data_path = Path(config["paths"]["data"])
    images_path = data_path / "images"
    assert (
        images_path.exists()
    ), "Data path must contain 'images' folder with all source data images"
    sam_path = data_path / "sam"
    sam_path.mkdir(exist_ok=True)
    sam = make_annotator(config["paths"]["sam_weights"], config["device"])

    max_masks = 0

    img_stems = [path.stem for path in sorted(images_path.iterdir())]
    for stem in tqdm(img_stems):
        filename = f"{stem}.png"
        img_path = images_path / filename
        out_path = sam_path / filename
        img = Image.open(img_path)
        img = np.array(img)
        masks = sam.generate(img)
        sorted_masks = sorted(masks, key=(lambda x: x["area"]), reverse=True)
        label = np.zeros(sorted_masks[0]["segmentation"].shape, dtype=np.uint8)
        for i, sm in enumerate(sorted_masks):
            m = sm["segmentation"]
            label[m] = i + 1
        max_masks = max(max_masks, np.max(label))
        label_img = Image.fromarray(label, mode="L")
        label_img.save(out_path)
