from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import yellow

# Create a PDF with some structure
c = canvas.Canvas("test_layout_source.pdf", pagesize=letter)

# Draw a rectangle (background)
c.setFillColor(yellow)
c.rect(100, 700, 400, 50, fill=1)

# Draw text on top
c.setFillColor("black")
c.setFont("Helvetica", 12)
c.drawString(110, 720, "This text is on a yellow background. Do not delete the background.")

c.drawString(100, 600, "Simple paragraph text here.")
c.drawString(100, 500, "Another block of text.")

c.save()
