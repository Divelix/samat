# sam_annotator

Annotation tool based on [SAM](https://github.com/facebookresearch/segment-anything) model.

## Installation
Installation using conda:
```bash
conda create -n sam python=3.10
conda activate sam
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia
pip install git+https://github.com/facebookresearch/segment-anything.git
pip install opencv-python pycocotools matplotlib onnxruntime onnx
```