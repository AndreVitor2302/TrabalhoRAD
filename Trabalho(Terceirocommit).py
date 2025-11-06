import re
import requests
from datetime import datetime
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import filedialog, messagebox

def extrair_datas_pdf(caminho_pdf):
    try:
        reader = PdfReader(caminho_pdf)
        texto = ""
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""
        
        # Verificando o conteúdo extraído
        print("Texto extraído do PDF:")
        print(texto)
        
        # Regex para capturar datas no formato YYYY-MM-DD
        padrao_data = re.compile(r'\b(\d{4}-\d{2}-\d{2})\b')
        
        matches = padrao_data.findall(texto)
        datas = matches if matches else ["Nenhuma data encontrada."]
        return datas
    except Exception as e:
        return [f"Erro ao ler o PDF: {e}"]

def verificar_feriados(datas):
    feriados_por_ano = {}
    
    # Chamar API para cada ano único
    anos = set()
    for data_str in datas:
        try:
            data_obj = datetime.strptime(data_str, '%Y-%m-%d')
            anos.add(data_obj.year)
        except ValueError:
            continue  # Ignora datas inválidas
    
    for ano in anos:
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/BR"
            response = requests.get(url)
            if response.status_code == 200:
                feriados = response.json()
                feriados_por_ano[ano] = {f['date']: f['name'] for f in feriados}
            else:
                feriados_por_ano[ano] = {}  # Caso erro ou ano sem feriados
        except requests.RequestException:
            feriados_por_ano[ano] = {}  # Falha na chamada
    
    feriados_encontrados = []
    datas_nao_feriados = []
    
    # Verificar se as datas extraídas são feriados ou não
    for data_str in datas:
        data_obj = datetime.strptime(data_str, '%Y-%m-%d')
        ano = data_obj.year
        data_iso = data_obj.strftime('%Y-%m-%d')
        if data_iso in feriados_por_ano.get(ano, {}):
            nome_feriado = feriados_por_ano[ano][data_iso]
            feriados_encontrados.append(f"📅 {data_str} - {nome_feriado}")
        else:
            datas_nao_feriados.append(f"📅 {data_str} - Não é feriado")
    
    return feriados_encontrados, datas_nao_feriados

def selecionar_pdf():
    caminho_pdf = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if caminho_pdf:
        status_label.config(text="Extraindo datas...")
        janela.update()
        datas = extrair_datas_pdf(caminho_pdf)
        if "Erro" in datas[0] or "Nenhuma" in datas[0]:
            resultado_feriados_label.config(text="\n".join(datas))  # Atualizando o resultado de feriados
            status_label.config(text="")
            return
        
        status_label.config(text="Verificando feriados...")
        janela.update()
        feriados, nao_feriados = verificar_feriados(datas)
        
        # Exibir as datas de feriados
        if feriados:
            titulo_feriados_label.config(text="Datas de Feriados Encontradas:")
            resultado_feriados_label.config(text="\n".join(feriados))  # Atualizando o resultado de feriados
        else:
            titulo_feriados_label.config(text="Nenhum feriado encontrado nas datas extraídas.")
            resultado_feriados_label.config(text="Nenhuma data corresponde a feriados.")
        
        # Exibir as datas que não são feriados
        if nao_feriados:
            titulo_nao_feriados_label.config(text="Datas que não são feriados:")
            resultado_nao_feriados_label.config(text="\n".join(nao_feriados))  # Atualizando o resultado de não feriados
        else:
            titulo_nao_feriados_label.config(text="Não há datas que não sejam feriados.")
            resultado_nao_feriados_label.config(text="")
        
        status_label.config(text="Verificação concluída.")

# Interface Tkinter
janela = tk.Tk()
janela.title("Extrator de Datas Feriados em PDF")
janela.geometry("500x650")  # Ajustei a altura da janela para comportar mais texto
janela.resizable(False, False)

titulo = tk.Label(janela, text="📘 Extrator de Datas Feriados em PDF", font=("Arial", 14, "bold"))
titulo.pack(pady=10)

botao = tk.Button(janela, text="Selecionar PDF", font=("Arial", 12), command=selecionar_pdf)
botao.pack(pady=10)

status_label = tk.Label(janela, text="", font=("Arial", 10), fg="blue")
status_label.pack(pady=5)

# Títulos para as datas de feriados e não feriados
titulo_feriados_label = tk.Label(janela, text="", font=("Arial", 12, "bold"), fg="green")
titulo_feriados_label.pack(pady=5)

resultado_feriados_label = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 11), wraplength=450, justify="left")
resultado_feriados_label.pack(pady=5)

titulo_nao_feriados_label = tk.Label(janela, text="", font=("Arial", 12, "bold"), fg="red")
titulo_nao_feriados_label.pack(pady=5)

resultado_nao_feriados_label = tk.Label(janela, text="", font=("Arial", 11), wraplength=450, justify="left")
resultado_nao_feriados_label.pack(pady=5)

rodape = tk.Label(janela, text="Desenvolvido em Python", font=("Arial", 9), fg="gray")
rodape.pack(side="bottom", pady=5)

janela.mainloop()
