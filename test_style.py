from translator import PDFTranslator
import fitz

# Mock span for testing style detection
mock_spans = [
    {"size": 12.0, "color": 0, "font": "Helvetica-Bold", "text": "Heading"},
    {"size": 12.0, "color": 0, "font": "Helvetica-Bold", "text": " 1"},
]

translator = PDFTranslator()
size, color, font = translator.get_most_frequent_style(mock_spans)
print(f"Detected: Size={size}, Color={color}, Font={font}")

# Test color conversion
rgb = translator.int_to_rgb(16711680) # Red? 0xFF0000 -> 16711680? No.
# 0xFF0000 = 16711680. 
# (16711680 & 255) = 0 (Blue) 
# ((16711680 >> 8) & 255) = 0 (Green)
# ((16711680 >> 16) & 255) = 255 (Red)
# So RGB should be (1.0, 0.0, 0.0)
print(f"Red Conversion: {translator.int_to_rgb(16711680)}")

# Test translation fallback (without keys)
print("Testing fallback translation...")
res = translator.translate_text("Hello")
print(f"Translation: {res}")
