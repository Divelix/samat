from pathlib import Path
import time

import numpy as np
import cv2
import matplotlib.pyplot as plt
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator

def show_anns(anns):
    if len(anns) == 0:
        return
    sorted_anns = sorted(anns, key=(lambda x: x['area']), reverse=True)
    ax = plt.gca()
    ax.set_autoscale_on(False)

    img = np.ones((sorted_anns[0]['segmentation'].shape[0], sorted_anns[0]['segmentation'].shape[1], 4))
    img[:,:,3] = 0
    for ann in sorted_anns:
        m = ann['segmentation']
        color_mask = np.concatenate([np.random.random(3), [0.35]])
        img[m] = color_mask
    ax.imshow(img)

def make_annotator() -> SamAutomaticMaskGenerator:
    model_type = 'vit_h'
    checkpoint_path = '/hdd_ext4/checkpoints/sam/sam_vit_h_4b8939.pth'
    device = 'cpu'
    print(f'Loading {model_type} on {device} device')
    start = time.perf_counter()
    sam = sam_model_registry[model_type](checkpoint_path)
    end_load = time.perf_counter()
    sam.to(device)
    end_move = time.perf_counter()
    mask_generator = SamAutomaticMaskGenerator(sam)
    print(f'Load weights: {(end_load-start):.3f}s\nMove to {device}: {(end_move-end_load):.3f}s')
    return mask_generator


if __name__ == '__main__':
    img_path = Path.home()/'Pictures/crosswalk.png'
    img = cv2.imread(str(img_path))
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    annotator = make_annotator()
    start = time.perf_counter()
    masks = annotator.generate(img)
    end = time.perf_counter()
    print(f'Inference: {(end-start):.3f}s')
    plt.figure(figsize=(20,20))
    plt.imshow(img)
    show_anns(masks)
    plt.axis('off')
    plt.show()
