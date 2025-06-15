# PDFGen Library

PDFGen is a pure-Python library for generating PDF documents from scratch without relying on external PDF engines. It offers fine-grained control over pages, text styling, images, links, and layout, directly producing PDF files.

---

## Features

* **Multiple Page Support**: Create documents with any number of pages using standard (A4, A3) or custom sizes.
* **Flexible Layouts**: Specify portrait or landscape orientation, and customize horizontal and vertical padding.
* **Rich Text Styling**:

  * Font variants: Regular, Bold, Italic (Oblique), Bold+Italic
  * Color specification: Named colors (`"red"`), hex codes (`"#FF0000"`), or RGB tuples
  * Alignment: left, center, right
  * Decorations: underline, strikethrough, background color
  * Word wrap with customizable max width
  * Hyperlinks: attach a URL to any text segment
* **Image Embedding**:

  * Supports PNG, JPEG, BMP, GIF, TIFF, and more via Pillow
  * Optionally compress images with JPEG 
  * Scale and position images precisely
  * Add captions below images
* **Annotations**: Add clickable link annotations to both text and image regions
* **Page Numbering**: Optionally add page numbers to each page
* **Overflow Warnings**: Prints warnings if text or images exceed page bounds

---

## Installation

PDFGen relies on [Pillow](https://pypi.org/project/Pillow/) for image handling. Install it via pip:

```bash
pip install Pillow
```

Then copy `pdfgen.py` into your project directory alongside your scripts.

Ensure the following imports are present at the top of `pdfgen.py`:

```python
from PIL import Image
from io import BytesIO
```

These are used internally in:

* `embed_image()`

  * Opens and validates the image file with `Image.open()`
  * Gets width and height
  * Handles compression using JPEG encoding if `compress=True` with `BytesIO()`


---

##


## Getting Started

This quickstart guides you through creating a simple PDF with text and images.

### 1. Import and Initialize

```python
from pdfgen import PDF
pdf = PDF()
```

### 2. Add a Page

```python
# Standard A4 portrait page
page = pdf.add_page(page_size="A4", orientation="portrait")
```

### 3. Embed and Place an Image

```python
# Embed an image (no compression)
img_name, obj_num, width, height = pdf.embed_image("example.png", compress=False)

# Place the image on the page at (50, 500) points
page.add_image(
    name=img_name,
    x=50,
    y=500,
    w=width,
    h=height,
    scale=0.5,
    caption="Sample Image"
)
```

### 4. Add Styled Text

```python
page.add_text(
    "Hello, PDFGen!",
    x=50,
    y=450,
    size=18,
    color="#003366",
    font="HelveticaBold",
    underline=True,
    background="#FFFFCC",
    link="https://example.com"
)
```

### 5. Save Your Document

```python
pdf.save("output.pdf", show_page_numbers=True)
```

Open `output.pdf` in any PDF viewer to see the result.

---

## Detailed Usage

Refer to the Documentation provided for a complete reference on all methods, parameters, and advanced usage patterns. All the methods and functions have been elaborately explained in the pdfgen.py file using comments and Docstrings, do refer them if you want to know more about its internal implementation and usage. Two test files namely, test1.py and test2.py have also been made which generate two pdf files test1_output.pdf and test2_output.pdf. Looking at the test files will definitely help you in grasping the syntax of the library. A number of sample images have been used in the tests and have been provided so that the user can modify the test files and try out different methods and functions himself.

---

## Troubleshooting

- **Unsupported Characters**: pdfgen encodes text in Latin-1 by default. Avoid non–Latin-1 characters (e.g., emojis, arrows) to prevent encoding errors.
- **Overflow Warnings**: If you see warnings that elements may be cut off, adjust your `x`, `y`, or `padding_*` values. It would only generate a warning and the code will run anyways.

---


