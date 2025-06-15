# PDFGen Library Documentation

## Overview

`PDFGen` is a lightweight Python library for generating PDF documents from scratch without external PDF engines. It supports:

- Multiple pages with standard or custom sizes (A4, A3, portrait/landscape)
- Text insertion with rich styling: fonts, sizes, colors, alignment, underline, strikethrough, background, wrapping, and hyperlinks
- Image embedding (raw RGB or JPEG compression), scaling, positioning, and captions
- Page layout warnings for overflow and customizable padding
- Optional page numbering

---


## Quick Start

```python
from pdfgen import PDF

pdf = PDF()
# Add a page
page = pdf.add_page(page_size="A4", orientation="portrait")
# Embed image
img, _, _, _ = pdf.embed_image("path/to/image.jpg", compress=True)
# Add image to page
page.add_image(img, x=50, y=400, w=200, h=150, scale=1.0, caption="Sample Image")
# Add styled text
page.add_text("Hello, PDFGen!", x=50, y=550, size=16,
              color="#333333", font="HelveticaBold",
              underline=True, background="#FFFFCC",
              link="https://example.com")
# Save document, the pdf will be saved in the MDG_nebula_proj_rg folder and can be viewed via any pdf viewer application.
pdf.save("output.pdf", show_page_numbers=True)
```

---

## Detailed API Reference

### Class `Page`

Represents a single PDF page. Use `PDF.add_page()` to obtain.

#### `Page(width, height, padding_horizontal=50, padding_vertical=50)`

Initialize a page.

- **width/height**: Page size in points (1/72 in).
- **padding\_horizontal/vertical**: Margins inside page.

#### `wrap_text(text, max_width, font_size)`

Wrap text to fit within `max_width`.

- **Args**:
  - `text` (`str`)
  - `max_width` (`float`): max line width in points.
  - `font_size` (`int`)
- **Returns**: `List[str]` of lines.

#### `add_text(text, x=100, y=700, size=24, color="black", font="Helvetica", bold=False, italic=False, align="left", underline=False, strike=False, background=None, max_width=None, link=None)`

Insert styled text.

- **text**: String content.
- **x, y**: Coordinates in points from left/bottom.
- **size**: Font size.
- **color**: Named, hex, or `(R,G,B)` tuple.
- **font**: Base font name; valid: `Helvetica`, `HelveticaBold`, `HelveticaOblique`, `HelveticaBoldOblique`.
- **bold**, **italic**: Booleans to choose font variant.
- **align**: `'left'`, `'center'`, `'right'`.
- **underline**, **strike**: Booleans for decorations.
- **background**: Color behind text.
- **max\_width**: Wrap width.
- **link**: URL for clickable text.

#### `add_image(name, x, y, w=None, h=None, scale=1.0, caption=None)`

Place an embedded image.

- **name**: Identifier returned by `embed_image`.
- **x, y**: Coordinates.
- **w, h**: Provided width/height; defaults to image intrinsic if `None`.
- **scale**: Scaling factor.
- **caption**: Text below image.

#### `get_stream_bytes(image_sizes)`

Internal: Compile page content.

- **image\_sizes**: Mapping `name -> (width, height)`.
- Returns raw PDF stream bytes.

### Class `PDF`

Main document builder.

#### `PDF()`

Constructor. Initializes empty PDF.

#### `add_page(page_size="A4", orientation="portrait", width=None, height=None, padding_horizontal=50, padding_vertical=50)`

Add a new page.

- **page\_size**: `'A4'`, `'A3'` (default A4).
- **orientation**: `'portrait'` or `'landscape'`.
- **width**, **height**: Override custom size.
- **padding\_horizontal/vertical**: Defaults 50 points.
- Returns: `Page` instance.

#### `add_object(content)`

Internal: Add a raw PDF object. Returns its object number.

#### `embed_image(img_path, compress=False)`

Embed an image in PDF.

- **img\_path**: File path.
- **compress**: Use JPEG compression if `True`.
- Returns: `(name, obj_number, width, height)`.
- **Raises**: `FileNotFoundError` if image missing.

#### `save(filename, show_page_numbers=False)`

Write PDF to disk.

- **filename**: Output path.
- **show\_page\_numbers**: If `True`, adds page numbers.

---

## Examples

### Multiple Pages & Layouts

```python
pdf = PDF()
# Page 1
p1 = pdf.add_page()
p1.add_text("Hello Page 1", x=50, y=800)
# Page 2 custom
p2 = pdf.add_page(width=300, height=500)
p2.add_text("Custom size page", x=20, y=480)
pdf.save("multipage.pdf", show_page_numbers=True)
```

### Text Decorations

```python
page.add_text("Underlined", underline=True)
page.add_text("Strikethrough", strike=True)
page.add_text("Background", background="#FFEEAA")

```

### Links

```python
page.add_text("Click me", x=100, y=100, link="https://google.com", underline=True)
```

### Error Handling

- Raises `ValueError` if hex color invalid.
- Warns if text or image may overflow page bounds.

---

*For full details, refer to inline docstrings in the library pdfgen.

