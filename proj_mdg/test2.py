from pdfgen import PDF

def run_test2():
    pdf = PDF()

    # === Page 1: A3 Portrait ===
    page1 = pdf.add_page(page_size="A3", orientation="portrait", padding_horizontal=80, padding_vertical=40)
    imgs = []
    for i in range(1, 3):
        name, _, _, _ = pdf.embed_image("image10.jpg", compress=True)
        imgs.append(name)

    # Grid placement with captions
    x0, y0 = 100, 900
    for idx, img_name in enumerate(imgs): 
        x = x0 + (idx % 2) * 300
        y = y0 - (idx // 2) * 250
        page1.add_image(img_name, x=x, y=y, w=200, h=150, scale=1.0, caption=f"Img {idx+1}")

    # Annotate each image with a link
    for idx, img_name in enumerate(imgs):
        x = x0 + (idx % 2) * 300
        y = y0 - (idx // 2) * 250
        page1.add_text(f"Link for {idx+1}", x=x, y=y-20, size=12, color="#0055AA", underline=True, link="https://google.com")

    # Page 2: Tiny Custom Page (300x400) 
    page2 = pdf.add_page(width=300, height=400, padding_horizontal=10, padding_vertical=10)
    
    # Single large image
    big, _, _, _ = pdf.embed_image("image14.jpg", compress=False)
    page2.add_image(big, x=10, y=150, w=280, h=300, scale=1.0, caption="Big image on small page")

    # Save output
    pdf.save("test2_output.pdf", show_page_numbers=False)
    print("test2_output.pdf generated.")

if __name__ == "__main__":
    run_test2()
