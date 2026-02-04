import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from translator import PDFTranslator
import os

class PDFTranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Tradutor de PDF para Português")
        self.root.geometry("600x450")
        
        self.translator = PDFTranslator()
        self.selected_file = None

        self.setup_ui()

    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=BOTH, expand=YES)

        # Title
        title_label = ttk.Label(
            main_frame, 
            text="Tradutor de PDF Automático", 
            font=("Helvetica", 18, "bold"),
            bootstyle="primary"
        )
        title_label.pack(pady=(0, 20))

        # File Selection Area
        file_frame = ttk.Labelframe(main_frame, text="Arquivo Selecionado", padding="10")
        file_frame.pack(fill=X, pady=10)

        self.file_label = ttk.Label(
            file_frame, 
            text="Nenhum arquivo selecionado", 
            bootstyle="secondary",
            wraplength=500
        )
        self.file_label.pack(side=LEFT, fill=X, expand=YES, padx=(0, 10))

        browse_btn = ttk.Button(
            file_frame, 
            text="Buscar PDF", 
            command=self.browse_file,
            bootstyle="outline-primary"
        )
        browse_btn.pack(side=RIGHT)

        # Action Area
        self.action_btn = ttk.Button(
            main_frame, 
            text="Iniciar Tradução", 
            command=self.start_translation,
            bootstyle="success-lg",
            state="disabled",
            width=20
        )
        self.action_btn.pack(pady=30)

        # Progress Area
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=X, pady=10)

        self.status_label = ttk.Label(
            progress_frame, 
            text="Aguardando...", 
            anchor="center",
            bootstyle="info"
        )
        self.status_label.pack(pady=(0, 5))

        self.progress_bar = ttk.Progressbar(
            progress_frame, 
            orient=HORIZONTAL, 
            length=100, 
            mode='determinate',
            bootstyle="success-striped"
        )
        self.progress_bar.pack(fill=X)

        # Valid Extensions Label
        info_label = ttk.Label(
            main_frame,
            text="Nota: O arquivo traduzido será salvo na mesma pasta do original.",
            font=("Helvetica", 9),
            bootstyle="secondary"
        )
        info_label.pack(side=BOTTOM, pady=10)

    def browse_file(self):
        filename = filedialog.askopenfilename(
            title="Selecione um arquivo PDF",
            filetypes=[("Arquivos PDF", "*.pdf")]
        )
        
        if filename:
            self.selected_file = filename
            self.file_label.config(text=os.path.basename(filename), bootstyle="primary")
            self.action_btn.config(state="normal")
            self.status_label.config(text="Arquivo carregado. Pronto para traduzir.")
            self.progress_bar['value'] = 0

    def start_translation(self):
        if not self.selected_file:
            return

        self.toggle_inputs(False)
        self.status_label.config(text="Iniciando processo...")
        
        # Run translation in separate thread to keep UI responsive
        self.translator.run_translation(
            self.selected_file,
            self.update_progress,
            self.on_translation_complete,
            self.on_translation_error
        )

    def toggle_inputs(self, enable):
        state = "normal" if enable else "disabled"
        self.action_btn.config(state=state)
        # We don't disable browse button to allow changing mind, 
        # but logically during translation it should probably be disabled or strictly handled.
        # For simplicity, let's keep it usable but maybe just disable the action button.

    def update_progress(self, percent, message):
        # Update UI from thread
        self.root.after(0, lambda: self._update_progress_ui(percent, message))

    def _update_progress_ui(self, percent, message):
        self.progress_bar['value'] = percent
        self.status_label.config(text=message)

    def on_translation_complete(self, output_path):
        self.root.after(0, lambda: self._complete_ui(output_path))

    def _complete_ui(self, output_path):
        self.toggle_inputs(True)
        messagebox.showinfo("Sucesso", f"Tradução concluída!\nArquivo salvo em:\n{output_path}")
        self.status_label.config(text="Tradução finalizada com sucesso!")
        
        # Optional: Open the folder
        try:
            os.startfile(os.path.dirname(output_path))
        except:
            pass

    def on_translation_error(self, error_message):
        self.root.after(0, lambda: self._error_ui(error_message))

    def _error_ui(self, error_message):
        self.toggle_inputs(True)
        messagebox.showerror("Erro", f"Ocorreu um erro durante a tradução:\n{error_message}")
        self.status_label.config(text="Erro ao traduzir.")
