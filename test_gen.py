from reportlab.pdfgen import canvas

c = canvas.Canvas("test_source.pdf")
c.drawString(100, 750, "Hello world. This is a test for the translator.")
c.save()
