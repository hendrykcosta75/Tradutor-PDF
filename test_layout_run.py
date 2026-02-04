from translator import PDFTranslator
import os
import fitz

# Clean up old
if os.path.exists("test_layout_source.pdf"):
    os.remove("test_layout_source.pdf")
if os.path.exists("test_layout_source_PT-BR.pdf"):
    os.remove("test_layout_source_PT-BR.pdf")

# Generate
import test_layout_gen

print("PDF generated.")

# Run translation
translator = PDFTranslator()
translator.run_translation(
    "test_layout_source.pdf", 
    lambda p, m: print(f"[{p}%] {m}"), 
    lambda path: print(f"Done: {path}"), 
    lambda err: print(f"Error: {err}")
)

# Wait for thread (simplified hack for testing: sleep/loop)
import time
print("Waiting for translation...")
time.sleep(5) 

if os.path.exists("test_layout_source_PT-BR.pdf"):
    print("Output exists!")
    # Verify content roughly
    doc = fitz.open("test_layout_source_PT-BR.pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    print("Extracted Text from Result:\n", text)
else:
    print("Output NOT found.")
