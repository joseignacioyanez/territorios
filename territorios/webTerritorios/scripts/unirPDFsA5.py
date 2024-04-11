import fitz

src1 = fitz.open("Terracota A - 07 de abril 2024.pdf")
src2 = fitz.open("Sangolqui - 07 de abril 2024.pdf")
doc = fitz.open()  # empty output PDF

height, width = fitz.paper_size("a4")  # A4 portrait output page format
r = fitz.Rect(0, 0, width, height)

# define the 2 rectangles per page
r1 =  fitz.Rect(0, 0, width/2, height) # left rect
r2 = r1 + (r1.width, 0, r1.width, 0)  # right rect

# put them in a list
r_tab = [r1, r2]

# now copy input pages to output

page = doc.new_page(-1, width = width, height = height)

for spage in src1:
    # insert input page into the correct rectangle
    page.show_pdf_page(r_tab[0], src1, spage.number)  
for spage in src2:
    # insert input page into the correct rectangle
    page.show_pdf_page(r_tab[1], src2, spage.number) 

# by all means, save new file using garbage collection and compression
doc.save("Unido.pdf", garbage=3, deflate=True)