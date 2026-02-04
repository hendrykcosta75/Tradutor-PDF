import os
import threading
import fitz  # PyMuPDF
from deep_translator import GoogleTranslator
from dotenv import load_dotenv
import google.generativeai as genai
from openai import OpenAI
from anthropic import Anthropic

load_dotenv()

class PDFTranslator:
    def __init__(self):
        self.google_translator = GoogleTranslator(source='auto', target='pt')
        self._stop_event = threading.Event()
        self.setup_ai_translators()

    def setup_ai_translators(self):
        self.gemini_key = os.getenv("GEMINI_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)
            self.gemini_model = genai.GenerativeModel('gemini-pro')

        if self.openai_key:
            self.openai_client = OpenAI(api_key=self.openai_key)

        if self.anthropic_key:
            self.anthropic_client = Anthropic(api_key=self.anthropic_key)

    def translate_text(self, text, style_context=""):
        """Translates text using the best available method."""
        if not text or not text.strip():
            return text

        # 1. Gemini
        if self.gemini_key:
            try:
                prompt = f"Translate the following text to Portuguese (Brazil). Maintain the original tone and formatting conventions where possible. Only return the translation, no explanations:\n\n{text}"
                response = self.gemini_model.generate_content(prompt)
                return response.text.strip()
            except Exception as e:
                print(f"Gemini Error: {e}")

        # 2. OpenAI
        if self.openai_key:
            try:
                response = self.openai_client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a professional translator. Translate the text to Portuguese (Brazil). Return only the translated text."},
                        {"role": "user", "content": text}
                    ]
                )
                return response.choices[0].message.content.strip()
            except Exception as e:
                print(f"OpenAI Error: {e}")

        # 3. Anthropic
        if self.anthropic_key:
            try:
                message = self.anthropic_client.messages.create(
                    model="claude-3-haiku-20240307",
                    max_tokens=1000,
                    messages=[
                        {"role": "user", "content": f"Translate this to Portuguese (Brazil), just the text:\n\n{text}"}
                    ]
                )
                return message.content[0].text.strip()
            except Exception as e:
                print(f"Anthropic Error: {e}")

        # 4. Fallback: Google Translator (Free)
        try:
            return self.google_translator.translate(text)
        except:
            return text

    def get_most_frequent_style(self, spans):
        """Analyzes spans to find the dominant font, size, and color."""
        if not spans:
            return 11, parse_color_int(0), "helv" # Defaults

        sizes = {}
        colors = {}
        fonts = {}

        for span in spans:
            # Size
            s = round(span["size"], 1)
            sizes[s] = sizes.get(s, 0) + len(span["text"])
            
            # Color
            c = span["color"] # Integer sRGB
            colors[c] = colors.get(c, 0) + len(span["text"])

            # Font flags (bold/italic) logic can be complex as font names vary wildly.
            # PyMuPDF span["font"] gives the font name.
            f = span["font"]
            fonts[f] = fonts.get(f, 0) + len(span["text"])

        best_size = max(sizes, key=sizes.get)
        best_color_int = max(colors, key=colors.get)
        best_font_name = max(fonts, key=fonts.get)

        # Map basic font names to standard PDF fonts if possible, or stick to Helvetica for safety
        # 'font' attribute in insert_textbox expects simple names like 'helv', 'tiro', 'cour'.
        # We'll do a simple mapping based on the font name string.
        mapped_font = "helv"
        lower_font = best_font_name.lower()
        if "bold" in lower_font and "italic" in lower_font:
            mapped_font = "helv-bi" # Helvetica-BoldOblique ? No, fitz uses specific codes.
            # Fitz standard fonts: helv, cour, timo (Times-Roman -> TiRo)
            # Actually simplest is:
            # helv, hebo, heit, hebi
            # times, tiro, tibo, tiit, tibi
            # cour, cobo, coit, cobi
            mapped_font = "hebi" 
        elif "bold" in lower_font:
            mapped_font = "hebo"
        elif "italic" in lower_font:
            mapped_font = "heit"
        elif "times" in lower_font or "serif" in lower_font:
             mapped_font = "tiro"
             if "bold" in lower_font: mapped_font = "tibo"
             if "italic" in lower_font: mapped_font = "tiit"
        
        # Color conversion: int to (r, g, b) 0-1 range
        # PyMuPDF colors are often 0xRRGGBB ?
        # Actually span["color"] is an integer.
        # If it's sRGB, we can convert.
        # But wait, PyMuPDF docs say color is an integer. 
        # We need to check if it includes alpha or not. usually it's RGB.
        
        return best_size, best_color_int, mapped_font

    def int_to_rgb(self, color_int):
        """Converts integer color to (r, g, b) float tuple."""
        # Assuming standard sRGB logic for the integer from PyMuPDF
        b = (color_int & 255) / 255.0
        g = ((color_int >> 8) & 255) / 255.0
        r = ((color_int >> 16) & 255) / 255.0
        return (r, g, b)

    def run_translation(self, input_path, progress_callback, completed_callback, error_callback):
        """Runs the translation process preserving layout."""
        def task():
            try:
                if not os.path.exists(input_path):
                    raise Exception("Arquivo não encontrado.")

                doc = fitz.open(input_path)
                total_pages = len(doc)
                
                output_path = os.path.splitext(input_path)[0] + "_PT-BR.pdf"

                for page_num, page in enumerate(doc):
                    progress_callback(int((page_num / total_pages) * 100), f"Processando página {page_num + 1} de {total_pages}...")
                    
                    blocks = page.get_text("dict")["blocks"]

                    for block in blocks:
                        if "lines" not in block:
                            continue
                            
                        bbox = fitz.Rect(block["bbox"])
                        
                        # Collect text and analyze style
                        block_text = ""
                        all_spans = []
                        for line in block["lines"]:
                            for span in line["spans"]:
                                block_text += span["text"] + " "
                                all_spans.append(span)
                        
                        if not block_text.strip():
                            continue

                        # Get dominant style
                        font_size, font_color_int, font_name = self.get_most_frequent_style(all_spans)
                        font_color = self.int_to_rgb(font_color_int)

                        # Translate
                        try:
                            translated_text = self.translate_text(block_text)
                        except Exception as e:
                            print(f"Translation error: {e}")
                            translated_text = block_text

                        # Redact and Insert
                        page.add_redact_annot(bbox, fill=None) 
                        page.apply_redactions()
                        
                        try:
                            # Try to insert with detected style
                            # We can try 'text_align' based on block? 
                            # 'align' defaults to 0 (left). Maybe check flags?
                            # For simplicity, left align is standard.
                            
                            rc = page.insert_textbox(
                                bbox, 
                                translated_text, 
                                fontsize=font_size, 
                                fontname=font_name, 
                                color=font_color,
                                align=0
                            )
                            
                            if rc < 0: # If text didn't fit, reduce size
                                page.insert_textbox(
                                    bbox, 
                                    translated_text, 
                                    fontsize=font_size * 0.8, 
                                    fontname=font_name, 
                                    color=font_color, 
                                    align=0
                                )
                        except:
                             page.insert_text(bbox.tl, translated_text, fontsize=font_size, fontname=font_name, color=font_color)

                progress_callback(95, "Salvando arquivo...")
                doc.save(output_path)
                progress_callback(100, "Concluído!")
                completed_callback(output_path)

            except Exception as e:
                error_callback(str(e))
                print(e)
            finally:
                if 'doc' in locals():
                    doc.close()

        thread = threading.Thread(target=task)
        thread.daemon = True
        thread.start()
