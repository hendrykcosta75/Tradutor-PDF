from translator import PDFTranslator
import os

def mock_callback(percent, msg):
    print(f"[{percent}%] {msg}")

translator = PDFTranslator()
translator.run_translation("test_source.pdf", mock_callback, lambda path: print(f"Done: {path}"), lambda err: print(f"Error: {err}"))
# Note: run_translation is threaded, but for this simple script we might exit before it finishes if we don't wait.
# So I'll just call the internal methods directly for verification to be synchronous.

print("--- Synchronous Test ---")
text = translator.extract_text("test_source.pdf")
print(f"Extracted: {text.strip()}")
chunks = translator.chunk_text(text)
print(f"Chunks: {len(chunks)}")
translated = translator.translate_chunks(chunks)
print(f"Translated: {translated.strip()}")
translator.create_pdf(translated, "test_output.pdf")
print("PDF Created.")
