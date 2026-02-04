import ttkbootstrap as ttk
from gui import PDFTranslatorApp

if __name__ == "__main__":
    # Create the main window with a theme
    # Themes: cosmo, flatly, journal, literal, lumen, minty, pulse, sandstone, united, yeti, darkly, superhero, solar, cyborg, vapor, simplex, cerculean
    root = ttk.Window(themename="superhero") 
    app = PDFTranslatorApp(root)
    root.mainloop()
