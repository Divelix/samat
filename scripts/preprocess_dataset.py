# Predict segmentation masks (and save as 8-bit grayscale .PNG) for all images in given dataset via SAM model
from pathlib import Path
import time
from PIL import Image

import numpy as np
from tqdm import tqdm
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator


def make_annotator() -> SamAutomaticMaskGenerator:
    model_type = "vit_h"
    checkpoint_path = "/hdd_ext4/checkpoints/sam/sam_vit_h_4b8939.pth"
    device = "cuda"
    print(f"Loading {model_type} on {device} device")
    start = time.perf_counter()
    sam = sam_model_registry[model_type](checkpoint_path)
    end_load = time.perf_counter()
    sam.to(device)
    end_move = time.perf_counter()
    mask_generator = SamAutomaticMaskGenerator(sam)
    print(
        f"Load weights: {(end_load-start):.3f}s\nMove to {device}: {(end_move-end_load):.3f}s"
    )
    return mask_generator


if __name__ == "__main__":
    data_path = Path("/hdd_ext4/datasets/images/raw_2")
    images_path = data_path / "images"
    # fmt: off
    assert images_path.exists(), "Data path must contain 'images' folder with all source data images"
    # fmt: on
    sam_path = data_path / "sam"
    sam_path.mkdir(exist_ok=True)
    sam = make_annotator()

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
