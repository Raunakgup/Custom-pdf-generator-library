from pdfgen import PDF


def run_test1():
    pdf = PDF()

    # Page 1: Standard A4 Portrait, A3 and A4 have been added as standard, for other sizes pass the custom size

    page1 = pdf.add_page(page_size="A4", orientation="portrait",
                         padding_horizontal=40, padding_vertical=40)

    # Embed images (placeholder image names)
    img1, _, _, _ = pdf.embed_image("image2.jpg", compress=False)
    img2, _, _, _ = pdf.embed_image("image5.png", compress=True)

    # Place images with captions
    page1.add_image(img1, x=50, y=650, w=200, h=150,
                    scale=1.0, caption="Raw RGB Image")
    page1.add_image(img2, x=300, y=650, w=200, h=150,
                    scale=0.75, caption="JPEG Compressed")

    # Add styled text
    # if no other parameters passed
    page1.add_text("Default Helvetica", x=50, y=600)
    page1.add_text("Bold Text", x=50, y=580, size=16,
                   color="#008800", font="Helvetica", bold=True)
    page1.add_text("Italic Text", x=50, y=560, size=16,
                   color=(0, 0, 255), font="Helvetica", italic=True)
    page1.add_text("Bold Italic", x=50, y=540, size=16,
                   color="purple", font="Helvetica", bold=True, italic=True)

    # Wrapping, background, underlined, links

    long = "This is a long sentence designed to wrap across multiple lines to test the max_width wrapping feature. The algorithm implementing this functionality is clearly explained in the comments within the pdfgen.py file. A background has also been added for visual emphasis. However, both the background and the underline currently extend slightly beyond the end of each line. This can be adjusted by making a few modifications in the generator file."

    page1.add_text(long, x=50, y=400, size=12, color="yellow",
                   background="#C666A2", max_width=380, underline=False)
    page1.add_text("Click here to watch an iconic scene", x=50, y=460, size=12,
                   color="#1327DB", underline=True, link="https://youtu.be/Ca3kPemW2CE")
    page1.add_text("Strike me", x=350, y=460, size=14,
                   color="red", strike=True, align="center")

    # Page 2: A4 Landscape with custom padding
    page2 = pdf.add_page(page_size="A4", orientation="landscape",
                         padding_horizontal=60, padding_vertical=60)

    # Reuse images
    img3, _, _, _ = pdf.embed_image("image4.webp", compress=False)
    img4, _, _, _ = pdf.embed_image("image6.png", compress=True)

    # Image positioning (including overflow intentionally to check that the warning appears in the terminal)
    # A warning appears if the image is cutoff or intersects with the padding.)
    page2.add_image(img3, x=50, y=50, w=300, h=200,
                    scale=1.0, caption="Overflow Test")
    page2.add_image(img4, x=500, y=300, w=250, h=250, scale=0.5,
                    caption="Half-Size")  # We can resize the image

    # Text alignments and links
    page2.add_text("Left aligned", x=100, y=450,
                   size=14, color="green", align="left")
    page2.add_text("Centered Text", x=400, y=450,
                   size=14, color="gray", align="center")
    page2.add_text("Right Aligned", x=700, y=450,
                   size=14, color="blue", align="right")
    page2.add_text("Visit Google", x=100, y=420, size=12,
                   color="#FF5500", underline=True, link="https://google.com")

    # Page 3: Custom Size (500x700)
    page3 = pdf.add_page(width=500, height=700,
                         padding_horizontal=20, padding_vertical=20)

    img5, _, _, _ = pdf.embed_image("image11.jpg", compress=False)
    img6, _, _, _ = pdf.embed_image("image12.jpg", compress=True)

    page3.add_image(img5, x=30, y=475, w=100, h=100,
                    scale=2.0, caption="Zoom 2x")
    page3.add_image(img6, x=300, y=500, w=200, h=200,
                    scale=0.5, caption="Shrink 0.5x")

    # Text with all decorations
    page3.add_text("Background Only Text", x=30, y=440,
                   size=12, background="#CCDDEE", color="black")
    page3.add_text("This is an ALL STYLES text", x=30, y=420, size=12, color="#8800AA",
                   bold=True, italic=True, underline=True, strike=True, background="#2784E1")

    paragraph = "pdfgen allows embedding hyperlinks inline. Click Link 3 below to test."
    page3.add_text(paragraph, x=30, y=380, size=10,
                   max_width=440, color="brown")
    page3.add_text("Link 3", x=30, y=360, size=12, color="blue",
                   underline=True, link="https://youtube.com")

    # Save with page numbers
    pdf.save("test1_output.pdf", show_page_numbers=True)
    print("test1_output.pdf generated.")


if __name__ == "__main__":
    run_test1()
