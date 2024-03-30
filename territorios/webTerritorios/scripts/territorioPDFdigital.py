import argparse
import PyPDF2
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.pdfbase import pdfform
from reportlab.lib.utils import ImageReader


def insert_text_and_image(template_pdf, output_pdf, text, image_path):
    template = PyPDF2.PdfReader(open(template_pdf, 'rb'))
    output = PyPDF2.PdfWriter()

    page = template.pages[0]
    overlay = PyPDF2.PdfReader(open(image_path, 'rb')).getPage(0)
    page.merge_page(overlay)

    c = canvas.Canvas("overlay.pdf", pagesize=letter)
    c.drawString(100, 750, text)
    c.save()

    overlay = PyPDF2.PdfReader(open("overlay.pdf", 'rb')).getPage(0)
    page.merge_page(overlay)

    output.addPage(page)

    with open(output_pdf, 'wb') as f:
        output.write(f)


def add_button_with_icon(pdf_file, x, y, icon_path, button_text):
    c = canvas.Canvas(pdf_file, pagesize=letter)

    # Define button area
    button_width = 100
    button_height = 40

    # Add icon
    c.drawImage(icon_path, x, y, width=30, height=30)

    # Create button
    button = c.beginForm(x, y, button_width, button_height)
    button.setFont("Helvetica", 12)
    button.setStrokeColor(colors.black)
    button.setFillColor(colors.lightgrey)
    button.rect(0, 0, button_width, button_height, fill=1)
    button.drawString(35, 12, button_text)
    button.endForm()

    # Add button to the page
    c.doForm(button)

    c.save()




def main():
    parser = argparse.ArgumentParser(description='PDF manipulation script')
    parser.add_argument('--template', required=True, help='Input template PDF file')
    parser.add_argument('--output', required=True, help='Output PDF file')
    parser.add_argument('--text', required=True, help='Text to insert')
    parser.add_argument('--image', required=True, help='Image file to insert')
    parser.add_argument('--icon', required=True, help='Icon file for the button')
    parser.add_argument('--button-text', required=True, help='Text for the button')

    args = parser.parse_args()

    print(args)

    insert_text_and_image(args.template, args.output, args.text, args.image)
    add_button_with_icon(args.output, 100, 400, args.icon, args.button_text)


if __name__ == "__main__":
    main()
