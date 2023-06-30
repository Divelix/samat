# sam_annotator

Annotation tool for semantic segmentation with [SAM](https://github.com/facebookresearch/segment-anything) assistance option.

# Getting started
## Prerequisites
### Annotation tool
Annotation tool uses Python 3.10 and depends on two libraries: `PyQt5` and `numpy`.

Example setup:
```bash
pip install PyQt5 numpy
```
### SAM script (optional)
If you want to prepare masks for further use of SAM assistance option inside annotation tool, you need to have at least 8GB VRAM GPU (to run SAM model inference) and PyTorch installed.

Example setup:
```bash
conda create -n sam python=3.10
conda activate sam
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install opencv-python pycocotools matplotlib onnxruntime onnx
```

## Data preparation
Your data must be organized in the following manner:
```
── my_dataset
   ├── images
   |   ├── 000001.png
   |   ├── 000002.png
   |   └── ...
   ├── labels (optional)
   |   ├── 000001.png
   |   ├── 000002.png
   |   └── ...
   ├── sam (optional)
   |   ├── 000001.png
   |   ├── 000002.png
   |   └── ...
   └── classes.json
```
- `images` contains `.png` files you want to label
- `labels` contains `.png` files with labels (will be automatically created if you have no labels yet)
- `sam` contains `.png` files with SAM annotations (8-bit grayscale product of SAM script from `scripts/` folder)
- `classes.json` contains classes description that will be used for labeling

Example `classes.json`:
```json
{
    "classes": [
        { "id": 1, "name": "human", "color": "#FF0000" },
        { "id": 2, "name": "car", "color": "#00FF00" },
    ]
}
```
**Note:** `id` field must coinside with number keys on keyboard, so start with 1 (but not 0).
**Note:** write path to your `my_dataset` (or any other name) inside `main.py`.

## Shortcuts

|                Shortcut               | Description                                          |
| :------------------------------------:| ---------------------------------------------------- |
|           Left Mouse Button           | Draw with brush + fill region (in SAM mode)          |
|           Right Mouse Button          | Pan motion on zoomed-in image                        |
|              Mouse Wheel              | Zoom in/out                                          |
|          `Ctrl` + Mouse Wheel         | Change brush size                                    |
|                `1`-`9`                | Select class (color to draw on label layer)          |
|                  `E`                  | Eraser tool (transparent brush)                      |
|                `Space`                | Reset zoom                                           |
|                  `C`                  | Clear label                                          |
|                  `S`                  | Switch SAM assistance mode on/off                    |
|               `,`/`.`                 | Previous/Next datasample                             |
