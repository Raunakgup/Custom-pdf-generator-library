from PIL import Image
from io import BytesIO
 

# it converts a hex color string (ex. "#FF0000") to an RGB tuple
# Example: "#FF0000" to (255, 0, 0)
def hex_to_rgb(hex_color):
    """
    Convert a hex color string (e.g. '#FF0000' or '#F00') to an (R, G, B) tuple.

    Args:
        hex_color (str): A string representing a hex color, with or without the '#' prefix.
        Supports 3-digit or 6-digit format.

    Returns:
        tuple: A 3-tuple of integers (R, G, B), each in range 0–255.

    Raises:
        ValueError: If the input is not a valid hex color format.
    """
    hex_color = hex_color.strip().lstrip("#")  # remove the # from the left
    if len(hex_color) == 3:
        # Expand the 3 char shorthand to 6
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    r = int(hex_color[0:2], 16)  # hexadecimal to integer
    g = int(hex_color[2:4], 16)
    b = int(hex_color[4:6], 16)
    return (r, g, b)


class Page:
    """
    Represents a single page in a PDF document, supporting the addition of styled text,
    embedded images, and optional links or captions. Manages layout and drawing stream.

    Attributes:
        width (int): Width of the page in points.
        height (int): Height of the page in points.
        padding_h (int): Horizontal padding from page edges.
        padding_v (int): Vertical padding from page edges.
        text_elements (list): PDF text drawing commands.
        image_elements (list): Image insertion instructions with optional captions.
        image_usages (list): Tracks image names used on this page.
        links (list): List of hyperlinks tied to specific text regions.
    """

    # A predefined mapping of common color names to their RGB values so that the user can directly add the color name as an argument instead of passing the hex value.
    color_MAP = {
        "black": (0, 0, 0),
        "white": (255, 255, 255),
        "red": (255, 0, 0),
        "green": (0, 128, 0),
        "blue": (0, 0, 255),
        "yellow": (255, 255, 0),
        "cyan": (0, 255, 255),
        "magenta": (255, 0, 255),
        "gray": (128, 128, 128),
        "orange": (255, 165, 0),
        "purple": (128, 0, 128),
        "pink": (255, 192, 203),
        "brown": (139, 69, 19),
        "navy": (0, 0, 128),
        "teal": (0, 128, 128),
        "olive": (128, 128, 0),
        "maroon": (128, 0, 0),
        "gold": (255, 215, 0),
        "lime": (0, 255, 0),
    }

    # Initialize a Page instance with dimensions and optional padding
    def __init__(self, width, height, padding_horizontal=50, padding_vertical=50):
        """
        Initialize a new Page object with dimensions and optional padding.

        Args:
            width (int): Page width in points.
            height (int): Page height in points.
            padding_horizontal (int): Optional horizontal padding (default 50).
            padding_vertical (int): Optional vertical padding (default 50).
        """
        self.width = width  # width of the page
        self.height = height  # height of the page
        self.padding_h = padding_horizontal  # horizontal padding
        self.padding_v = padding_vertical  # vertical padding
        self.text_elements = []  # list of text drawing instructions
        self.image_elements = []  # list of image drawing instructions
        self.image_usages = []  # tracking image usage instances
        self.links = []  # list of hyperlinks associated with text

    # Word-wrap text into lines that fit within max_width using estimated char width
    def wrap_text(self, text, max_width, font_size):
        """
        Wrap a given text string into lines that fit within the specified max width.

        Args:
            text (str): The text to wrap.
            max_width (float): Maximum allowed width in points for each line.
            font_size (int): Font size used to estimate character width.

        Returns:
            list: A list of strings, each representing a wrapped line.
        """
        
        # This code breaks a block of text into multiple lines so it fits within a certain width on the page. It guesses how many characters can fit on a line based on the font size, then adds words one by one until the line is full. When it reaches the limit, it starts a new line. The result is a neatly wrapped version of the original text
        
        # This method doesn't use actual font metrics, it uses a simple estimate (0.5 * font_size), which is a fast but not so precise way to guess average character width
        
        avg_char_width = 0.5 * font_size
        max_chars = int(max_width / avg_char_width)
        words = text.split()
        lines, current_line = [], ""
        for word in words:
            test_line = f"{current_line} {word}".strip()
            if len(test_line) <= max_chars:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    # Adds styled text to the page at a given position with many formatting options
    def add_text(
        self,
        text,
        x=100,
        y=700,
        size=24,
        color="black",
        font="Helvetica",
        bold=False,
        italic=False,
        align="left",
        underline=False,
        strike=False,
        background=None,
        max_width=None,
        link=None,
    ):
        """
        Add styled text to the page at a specific position, with options for font, color,
        alignment, underline, strikethrough, background fill, wrapping, and hyperlinks.

        Args:
            text (str): The text to display.
            x (float): X-coordinate from the left.
            y (float): Y-coordinate from the bottom.
            size (int): Font size in points.
            color (str|tuple): Named color, hex string, or RGB tuple.
            font (str): Base font name (e.g., "Helvetica").
            bold (bool): Use bold variant if True.
            italic (bool): Use italic/oblique variant if True.
            align (str): 'left', 'center', or 'right' text alignment.
            underline (bool): Underline the text.
            strike (bool): Add strikethrough to the text.
            background (str|tuple): Optional background color.
            max_width (float): Optional max width for wrapping text.
            link (str): Optional URL to link this text to.
        """

        # Parse the color argument into a normalized RGB tuple (each value in [0,1])
        def parse_color(c):
            if isinstance(c, str):
                if c.startswith("#"): # if it's a hex string
                    return hex_to_rgb(c)
                elif c.lower() in Page.color_MAP: # if the color is a name like "black" or "BlAcK", case doesn't matter then check in the color_MAP 
                    return Page.color_MAP[c.lower()]
                else:
                    raise ValueError(f"Unknown color: {c}") # otherwise raise a value error
            elif isinstance(c, (tuple, list)) and len(c) == 3: # if in rgb format
                return tuple(c)
            raise TypeError("color must be name, hex string, or (R,G,B) tuple")

        # normalize RGB color to range [0, 1] for PDF color values
        r, g, b = [max(0, min(255, int(c))) / 255 for c in parse_color(color)]

        # Determine the correct font variant based on bold/italic flags
        base_font = font.replace("-", "") # removes any dashes from the font name to normalize it like "Helvetica-Bold" becomes "HelveticaBold"
        if bold and italic:
            font_key = f"{base_font}BoldOblique"
        elif bold:
            font_key = f"{base_font}Bold"
        elif italic:
            font_key = f"{base_font}Oblique"
        else:
            font_key = base_font
        font_ref = f"/{font_key}" # formats the font name into pdf syntax by prefixing it with a slash (ex. /HelveticaBoldOblique), which is how fonts are referenced in PDF content streams

        # Wrap text into lines if max_width is set, otherwise use the whole text
        
        lines = self.wrap_text(text, max_width, size) if max_width else [text]
        for i, line in enumerate(lines):
            avg_char_width = 0.5 * size
            text_width = len(line) * avg_char_width
            text_height = size
            line_y = y - i * (size * 1.2)  # Adjust line position downwards per line

            # Adjust x position based on alignment
            
            # x is a reference point for alignment.
            # The align value shifts the actual text drawing position relative to x
            # Left → no shift
            # Center → shifts half the text width to the left
            # Right → shifts full text width to the left
            
            line_x = x
            if align == "center":
                line_x -= text_width / 2
            elif align == "right":
                line_x -= text_width

            # Check if text is within the padding box; warn if it's not to notify the user that the text may be cutoff so he may shift the x and y coordinates accordingly
            if not (self.padding_h <= line_x <=
                    self.width - self.padding_h - text_width and self.padding_v
                    <= line_y <= self.height - self.padding_v - text_height):
                print(
                    f"Warning: Text '{line}' at ({line_x:.1f}, {line_y:.1f}) "
                    f"may be cut off (width={text_width:.1f}, height={text_height:.1f}). "
                    f"Consider adjusting its position or padding.")

            stream_parts = []
            # draw background rectangle if specified
            # this code first checks if a background color is set. If it is, it parses the color and converts it into normalized RGB values (between 0 and 1) using parse_color already defined above. It then adds PDF drawing commands to fill a rectangle behind the text. After that, it appends another instruction to set the text color and draw the actual text at the specified position with the chosen font and size
            if background:
                br, bg, bb = [
                    max(0, min(255, int(c))) / 255
                    for c in parse_color(background)
                ]
                stream_parts.append(
                    f"{br:.3f} {bg:.3f} {bb:.3f} rg\n{line_x:.2f} {line_y - 0.2*size:.2f} {text_width:.2f} {text_height:.2f} re f"
                )

            # add text drawing instruction
            stream_parts.append(
                f"{r:.3f} {g:.3f} {b:.3f} rg\nBT {font_ref} {size} Tf {line_x:.2f} {line_y:.2f} Td ({line}) Tj ET"
            )

            # optionally add underline
            if underline:
                uy = line_y - size * 0.15 # calculates the Y-position of the underline, placing it slightly below the text baseline
                stream_parts.append(
                    f"{r:.3f} {g:.3f} {b:.3f} RG\n{line_x:.2f} {uy:.2f} m {line_x + text_width:.2f} {uy:.2f} l S"
                    # the above code adds an underline to the text by inserting PDF drawing commands into the page’s content stream. Firstly, it sets the stroke color using the same RGB values as the text. Then it moves the drawing cursor to the starting position of the underline using m, and draws a horizontal line across the width of the text with l. Finally, the S command tells the PDF to actually render (or "stroke") the line. In simple terms, this block creates a clean underline beneath our text in the same color, matching the position and width of the text perfectly.
                )

            # optionally add strikethrough
            if strike:
                sy = line_y + size * 0.3 # y coordinate for strikethrough
                stream_parts.append(
                    f"{r:.3f} {g:.3f} {b:.3f} RG\n{line_x:.2f} {sy:.2f} m {line_x + text_width:.2f} {sy:.2f} l S"
                )

            # now add compiled PDF text stream to the page
            self.text_elements.append("\n".join(stream_parts))

            # Store link metadata for this text if any
            if link:
                self.links.append(
                    (line_x, line_y, text_width, text_height, link))

    def add_image(self, name, x, y, w=None, h=None, scale=1.0, caption=None):
        """
        Add an image to the page at a specified location with optional scaling and caption.

        Args:
            name (str): Identifier for the image (typically object reference).
            x (float): X-coordinate on the page.
            y (float): Y-coordinate on the page.
            w (float): Optional original width in points.
            h (float): Optional original height in points.
            scale (float): Scaling factor to apply to image size.
            caption (str): Optional text to render below the image.

        Raises:
            ValueError: If scale is not positive.
        """
        # ensure the scale factor is valid
        if scale <= 0:
            raise ValueError("Scale must be a positive number")

        # to track image usage by name if not already included
        if name not in self.image_usages:
            self.image_usages.append((name, None))

        # compute final dimensions based on optional width/height and scale
        final_w = (w or 0) * scale
        final_h = (h or 0) * scale

        # Warn if image may overflow page bounds so that the user can modify the coordinates or size as needed 
        if (x < self.padding_h or x + final_w > self.width - self.padding_h
                or y < self.padding_v
                or y + final_h > self.height - self.padding_v):
            print(f"Warning: Image '{name}' at ({x:.1f}, {y:.1f}) "
                  f"may be cut off (w={final_w:.1f}, h={final_h:.1f}). "
                  f"Adjust position or padding.")

        # Save image element for later rendering
        self.image_elements.append((name, x, y, w, h, scale, caption))

    def get_stream_bytes(self, image_sizes):
        """
        Generate the full content stream of the page, combining text and image drawing commands.

        Args:
            image_sizes (dict): A dictionary mapping image names to (width, height) in points.

        Returns:
            bytes: The compiled page content as PDF stream commands encoded in Latin-1.

        Raises:
            ValueError: If an image used on the page is missing from `image_sizes`.
        """
        
        # this get_stream_bytes method generates the visual content stream for a PDF page by combining both text and image drawing commands. It takes a dictionary of image sizes (image_sizes) and loops through all image elements on the page. For each image, it calculates the final width and height (based on optional scaling and provided dimensions), and then constructs the PDF command to draw that image at a specific position using cm (concatenate matrix) and /Name Do (draw object). If a caption is present, it also estimates the text width and places the caption below the image using a BT...ET block for text. Finally, it merges the text and image commands into a single string and encodes it in Latin-1 format, which is how PDF expects its content stream. If any image size is missing, it raises a valueerror
        
        # Collect drawing commands for all images and text
        image_streams = []

        for name, x, y, w, h, scale, caption in self.image_elements:
            # Ensure we have size info for the image
            if name not in image_sizes:
                raise ValueError(f"Size not found for image {name}")

            # Determine image size using default or provided values
            img_w, img_h = image_sizes[name]
            final_w = (w or img_w) * scale
            final_h = (h or img_h) * scale

            # Command to draw image on page
            image_streams.append(
                f"q {final_w} 0 0 {final_h} {x} {y} cm /{name} Do Q")

            # Optionally add caption text under image
            if caption:
                font_size = 10
                text_width = font_size * len(
                    caption) * 0.5  # rough estimate of width
                caption_x = x + (final_w - text_width) / 2
                caption_y = y - 12  # position caption below image
                caption_cmd = f"0 0 0 rg\nBT /Helvetica {font_size} Tf {caption_x:.2f} {caption_y:.2f} Td ({caption}) Tj ET"
                image_streams.append(caption_cmd)

        # Combine all drawing commands (text + images) and encode as bytes
        return "\n".join(self.text_elements + image_streams).encode("latin1")


class PDF:
    """
    A lightweight PDF generator supporting multiple pages, embedded images,
    links, captions, and layout customization.
    """

    # define standard paper sizes in points (1 point = 1/72 inch)
    STANDARD_SIZES = {
        "A4": (595.28, 841.89),  #A4 size in portrait orientation
        "A3": (841.89, 1190.55),  #A3 size in portrait orientation
    }

    def __init__(self):
        """
        Initialize a new PDF instance with empty pages, objects, and image references.
        """
        # initialize an empty list to hold Page instances
        self.pages = []
        # list to store raw PDF objects (as bytes) to be written in the file
        self.objects = []
        # dictionary to store embedded images, keyed by internal name
        self.images = {}
        # store dimensions of each page (width, height) in sequence
        self.page_dimensions = []

    def add_page(
        self,
        page_size="A4",
        orientation="portrait",
        width=None,
        height=None,
        padding_horizontal=50,
        padding_vertical=50,
    ):
        """
        Adds a new page to the PDF.

        Args:
            page_size (str): Standard size name (e.g., 'A4', 'A3'). Ignored if custom size is provided.
            orientation (str): 'portrait' or 'landscape'.
            width (float): Optional custom width in points.
            height (float): Optional custom height in points.
            padding_horizontal (float): Horizontal padding inside the page.
            padding_vertical (float): Vertical padding inside the page.

        Returns:
            Page: The newly created Page instance.
        """

        # if custom width and height are provided, use them
        if width is not None and height is not None:
            w, h = width, height
        else:
            # otherwise, use a predefined standard size based on name
            # default fallback is (612, 792) if size name not found
            w, h = self.STANDARD_SIZES.get(page_size.upper(), (612, 792))

            # if landscape orientation is requested, swap width and height
            if orientation.lower() == "landscape":
                w, h = h, w

        # store the dimensions for reference or output
        self.page_dimensions.append((w, h))

        # create a new Page instance with the calculated dimensions and padding
        page = Page(w, h, padding_horizontal, padding_vertical)

        # append the new page to the list of pages
        self.pages.append(page)

        # return the created page instance
        return page

    def add_object(self, content: bytes):
        """
        Adds a raw object (as bytes) to the PDF and returns its object number.

        Args:
            content (bytes): The raw bytes representing the PDF object.

        Returns:
            int: The object number assigned to this object.
        """

        # Object number is just index + 1 since PDF objects are 1-based
        obj_number = len(self.objects) + 1

        # store the object number and content together
        self.objects.append((obj_number, content))

        # return the object number for referencing elsewhere (e.g., page or image)
        return obj_number

    def embed_image(self, img_path, compress=False):
        """
        Embeds an image into the PDF, optionally compressing it with JPEG.

        Args:
            img_path (str): Path to the image file.
            compress (bool): If True, compress the image using JPEG.

        Returns:
            Tuple[str, int, int, int]: A tuple containing:
                - internal image name (str),
                - object number (int),
                - width in pixels (int),
                - height in pixels (int)

        Raises:
            FileNotFoundError: If the image file does not exist.
        """
        try:
            # open the image file and convert it to RGB mode
            img = Image.open(img_path).convert("RGB")
        except FileNotFoundError:
            # if the image file doesn't exist, raise a clear error
            raise FileNotFoundError(f"Image file '{img_path}' not found.")

        # extract original image dimensions in pixels
        width, height = img.size

        # if compression is enabled, use JPEG format
        if compress:
            # create a temporary buffer to hold the compressed JPEG data
            img_buffer = BytesIO()
            # save the image in JPEG format with moderate compression (quality=85)
            img.save(img_buffer, format="JPEG", quality=85)
            # get raw byte data from buffer
            img_data = img_buffer.getvalue()

            # building PDF stream header for JPEG image
            image_stream = (
                f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 "
                f"/Filter /DCTDecode /Length {len(img_data)} >>\n".encode() +
                b"stream\n" + img_data + b"\nendstream")
        else:
            # if no compression, get raw RGB byte data
            img_data = img.tobytes()
            
            # build uncompressed image stream (note: may increase PDF size)
            image_stream = (
                f"<< /Type /XObject /Subtype /Image /Width {width} /Height {height} "
                f"/ColorSpace /DeviceRGB /BitsPerComponent 8 /Length {len(img_data)} >>\n"
                .encode() + b"stream\n" + img_data + b"\nendstream")

        # add the image stream to the PDF objects and get its object number
        obj_num = self.add_object(image_stream)

        # create a unique image name (e.g., Im5 if object number is 5)
        name = f"Im{obj_num}"

        # store the image metadata in the images dictionary for later use
        self.images[name] = (img, obj_num, width, height)

        # Return all necessary info: image name, object number, dimensions
        return name, obj_num, width, height

    def save(self, filename, show_page_numbers=False):
        """
        Saves the PDF to a file.

        Args:
            filename (str): Output filename (e.g., 'document.pdf').
            show_page_numbers (bool): Whether to show page numbers on each page.
        """
        # define font mapping for PDF standard fonts
        font_map = {
            "Helvetica": "Helvetica",
            "HelveticaBold": "Helvetica-Bold",
            "HelveticaOblique": "Helvetica-Oblique",
            "HelveticaBoldOblique": "Helvetica-BoldOblique",
        }

        # create font objects and store their object numbers
        font_objs = {
            k:
            self.add_object(
                f"<< /Type /Font /Subtype /Type1 /Name /{k} /BaseFont /{v} >>".
                encode())
            for k, v in font_map.items()
        }

        # map image names to their PDF object numbers
        image_objs = {
            name: obj_num
            for name, (_, obj_num, _, _) in self.images.items()
        }
        # map image names to their width and height
        image_sizes = {
            name: (w, h)
            for name, (_, _, w, h) in self.images.items()
        }

        # resolve image object references inside each page
        for page in self.pages:
            for i, (name, _) in enumerate(page.image_usages):
                if name not in image_objs:
                    raise ValueError(f"Image object for {name} not found.")
                # replace name with its associated object number
                page.image_usages[i] = (name, image_objs[name])

        content_obj_nums = []
        for idx, page in enumerate(self.pages):
            # get the main PDF drawing commands for the page as byte stream
            stream = page.get_stream_bytes(image_sizes)

            # add captions (labels under images), if any
            for (name, x, y, w, h, scale, caption) in page.image_elements:
                if caption:
                    font_key = "Helvetica"
                    font_size = 10
                    text_width = font_size * len(
                        caption) * 0.5  # Rough estimation
                    caption_x = (x + (
                        (w or image_sizes[name][0]) * scale - text_width) / 2)
                    caption_y = y - 12  # draw caption below the image

                    # add drawing commands for caption text
                    caption_cmd = (
                        f"\n0 0 0 rg\nBT /{font_key} {font_size} Tf {caption_x:.2f} {caption_y:.2f} Td ({caption}) Tj ET"
                    ).encode()
                    stream += caption_cmd

            # optionally show page numbers at the bottom center
            if show_page_numbers:
                font_key = "Helvetica"
                page_number = idx + 1
                number_text = f"{page_number}"
                font_size = 10
                text_width = font_size * len(number_text) * 0.5
                x = (page.width - text_width) / 2
                y = 15  # distance from bottom of the page

                # add drawing commands for the page number
                extra = (
                    f"\n0 0 0 rg\nBT /{font_key} {font_size} Tf {x:.2f} {y:.2f} Td ({number_text}) Tj ET"
                ).encode()
                stream += extra

            # wrap the stream content in a PDF stream object and store its reference
            stream_obj = self.add_object(
                f"<< /Length {len(stream)} >>\nstream\n".encode() + stream +
                b"\nendstream")
            content_obj_nums.append(stream_obj)

        page_obj_nums = []
        for i, content_ref in enumerate(content_obj_nums):
            page = self.pages[i]
            width, height = page.width, page.height

            # Prepare font resources (all fonts used in this document)
            font_resource_str = " ".join(f"/{k} {v} 0 R"
                                         for k, v in font_objs.items())

            # Prepare XObject (images used on this page)
            xobj_str = ""
            if page.image_usages:
                xobj_pairs = " ".join(f"/{name} {obj_num} 0 R"
                                      for name, obj_num in page.image_usages)
                xobj_str = f"/XObject << {xobj_pairs} >>"

            # create annotation objects for links and store their references
            annotations = []
            for x, y, w, h, uri in page.links:
                annot_str = (
                    f"<< /Type /Annot /Subtype /Link /Rect [{x:.2f} {y:.2f} {x+w:.2f} {y+h:.2f}] "
                    f"/Border [0 0 0] /A << /S /URI /URI ({uri}) >> >>")
                annot_obj = self.add_object(annot_str.encode())
                annotations.append(f"{annot_obj} 0 R")

            # if any links exist, include them as annotation array
            annots_str = f"/Annots [{' '.join(annotations)}]" if annotations else ""

            # combine all resource strings: fonts + images (XObjects)
            resource_str = f"/Font << {font_resource_str} >>"
            if xobj_str:
                resource_str += f" {xobj_str}"

            # define a Page object (link to content stream and resources)
            page_obj_str = (
                f"<< /Type /Page /Parent {{pages}} 0 R /Resources << {resource_str} >> "
                f"/Contents {content_ref} 0 R /MediaBox [0 0 {width:.2f} {height:.2f}] {annots_str} >>"
            )
            page_obj = self.add_object(page_obj_str.encode())
            page_obj_nums.append(page_obj)

        # create the /Pages dictionary that holds all page objects
        kids = " ".join(f"{num} 0 R" for num in page_obj_nums)
        pages_obj = self.add_object(
            f"<< /Type /Pages /Kids [{kids}] /Count {len(page_obj_nums)} >>".
            encode())

        # replace placeholder {pages} in objects with actual page tree object number
        fixed_objects = []
        for obj_number, data in self.objects:
            if b"{pages}" in data:
                data = data.replace(b"{pages}", str(pages_obj).encode())
            fixed_objects.append((obj_number, data))
        self.objects = fixed_objects

        # create the /Catalog object (PDF root object)
        catalog_obj = self.add_object(
            f"<< /Type /Catalog /Pages {pages_obj} 0 R >>".encode())

        # write everything to the output PDF file
        with open(filename, "wb") as f:
            f.write(b"%PDF-1.4\n")  # PDF version header

            # write all objects and keep track of byte offsets
            offsets = [0]
            for obj_number, content in self.objects:
                offsets.append(f.tell())
                f.write(f"{obj_number} 0 obj\n".encode())
                f.write(content)
                f.write(b"\nendobj\n")

            # write the xref table (index of all objects)
            xref_offset = f.tell()
            f.write(f"xref\n0 {len(offsets)}\n".encode())
            f.write(b"0000000000 65535 f \n")  # free object entry for obj 0
            for offset in offsets[1:]:
                f.write(f"{offset:010d} 00000 n \n".encode())

            # write trailer that tells PDF readers where to start
            f.write(b"trailer\n")
            f.write(f"<< /Size {len(offsets)} /Root {catalog_obj} 0 R >>\n".
                    encode())
            f.write(b"startxref\n")
            f.write(f"{xref_offset}\n".encode())
            f.write(b"%%EOF\n")  # End of file marker
