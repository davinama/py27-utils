# python-utils

A small but practical collection of Python2.7 utility functions used in daily plugin/tool development.  
Includes commonly used file operating functions, encoding tools, image processing helpers, and other general-purpose utilities.

These functions were abstracted and refactored from real production code.  
They are designed to solve recurring problems, speed up development, and reduce redundancy.


## ✨ Features

### 🖼️ [`path_utils.py`](./path_utils.py)
Tools for Windows folder path / file path utilities.

- Convert path format, ip address detection
- Speed up file copying process, solve common access error
- Compatible with Chinese-character paths during Windows file operation

### 🖼️ [`image_utils.py`](./image_utils.py)
Basic tools for working with images.

- Format file names for sequence of images
- Reduce image size using PIL
- Image number count for given folder path

### 📁 [`encode_decode_utils.py`](./encode_decode_utils.py)
Utilities for handling encoding/decoding and cross-format string transitions (especially for Python 2.7).

- Automatically detect encoding (`utf-8`, `gbk`, `big5`, etc.)
- Safely convert between Unicode, UTF-8, GBK
- Designed to solve UI display or terminal errors in multi-language environments, especially Chinese environment

### 🔧 [`other_utils.py`](./other_utils.py)
General-purpose tools.

- Run function multi-threadingly
- Print function call stack and parameters easily


## 🧪 Requirements

Some functions require third-party libraries:

- `natsort`
- `PIL` (Pillow)
- `chardet`
- `xpinyin`

Use `pip install -r requirements.txt` to install these libraries.

> ⚠️ This project is compatible with **Python 2.7**,  
> but most utilities are easily portable to Python 3.x.


## 📌 Note

This repository is a snippet library from real-world plugin development.  
The logic is kept clean, modular, and focused — not a full-fledged framework, but a practical developer-side kit.


## Author

Davina Ma Heming
Created in June 2025
Python 2.7