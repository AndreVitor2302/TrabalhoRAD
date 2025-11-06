import re
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import filedialog, messagebox

def extrair_datas_pdf(caminho_pdf):
    try:
        reader = PdfReader(caminho_pdf)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""
        
        # Regex para capturar datas por extenso e numéricas (case-insensitive)
        padrao_data = re.compile(
            r'\b(\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóúâêôû]+\s+de\s+\d{4})\b|'  # Ex: 26 de Fevereiro de 2025
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',                             # Ex: 26/02/2025
            re.IGNORECASE
        )
        
        matches = padrao_data.findall(texto)
        datas = [match[0] or match[1] for match in matches if match[0] or match[1]]
        if datas:
            return datas  # Retorna lista de todas as datas encontradas
        else:
            return ["Nenhuma data encontrada."]
    except Exception as e:
        return [f"Erro ao ler o PDF: {e}"]

def selecionar_pdf():
    caminho_pdf = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if caminho_pdf:
        datas = extrair_datas_pdf(caminho_pdf)
        resultado_texto = "\n".join(f"📅 {data}" for data in datas)
        resultado_label.config(text=resultado_texto)

# --- Interface Tkinter ---
janela = tk.Tk()
janela.title("Extrator de Datas em PDF")
janela.geometry("400x250")
janela.resizable(False, False)

titulo = tk.Label(janela, text="📘 Extrator de Datas em PDF", font=("Arial", 14, "bold"))
titulo.pack(pady=10)

botao = tk.Button(janela, text="Selecionar PDF", font=("Arial", 12), command=selecionar_pdf)
botao.pack(pady=10)

resultado_label = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 11), wraplength=350, justify="left")
resultado_label.pack(pady=20)

rodape = tk.Label(janela, text="Primeiro commit - Desenvolvido em Python", font=("Arial", 9), fg="gray")
rodape.pack(side="bottom", pady=5)

janela.mainloop()
