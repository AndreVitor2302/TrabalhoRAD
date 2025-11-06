import re
import requests
from datetime import datetime
from PyPDF2 import PdfReader
import tkinter as tk
from tkinter import filedialog, messagebox
@@ -10,7 +12,7 @@ def extrair_datas_pdf(caminho_pdf):
        for pagina in reader.pages:
            texto += pagina.extract_text() or ""

        # Regex para capturar datas por extenso e numéricas (case-insensitive)
        # Regex para capturar datas (case-insensitive)
        padrao_data = re.compile(
            r'\b(\d{1,2}\s+de\s+[a-zA-ZçÇãõáéíóúâêôû]+\s+de\s+\d{4})\b|'  # Ex: 26 de Fevereiro de 2025
            r'\b(\d{1,2}/\d{1,2}/\d{2,4})\b',                             # Ex: 26/02/2025
@@ -19,27 +21,89 @@ def extrair_datas_pdf(caminho_pdf):

        matches = padrao_data.findall(texto)
        datas = [match[0] or match[1] for match in matches if match[0] or match[1]]
        if datas:
            return datas  # Retorna lista de todas as datas encontradas
        else:
            return ["Nenhuma data encontrada."]
        return datas if datas else ["Nenhuma data encontrada."]
    except Exception as e:
        return [f"Erro ao ler o PDF: {e}"]

def verificar_feriados(datas):
    feriados_por_ano = {}
    meses_pt = {
        'janeiro': 1, 'fevereiro': 2, 'março': 3, 'abril': 4, 'maio': 5, 'junho': 6,
        'julho': 7, 'agosto': 8, 'setembro': 9, 'outubro': 10, 'novembro': 11, 'dezembro': 12
    }
    
    # Parsear datas e coletar anos únicos
    datas_parseadas = []
    anos = set()
    for data_str in datas:
        try:
            if 'de' in data_str.lower():  # Formato por extenso
                partes = re.split(r'\s+de\s+', data_str.lower())
                dia = int(partes[0])
                mes_nome = partes[1].split()[0]  # Pega o primeiro nome do mês
                ano = int(partes[2])
                mes = meses_pt.get(mes_nome)
                if mes:
                    data_obj = datetime(ano, mes, dia)
                    datas_parseadas.append((data_str, data_obj))
                    anos.add(ano)
            else:  # Formato numérico
                data_obj = datetime.strptime(data_str, '%d/%m/%Y')
                datas_parseadas.append((data_str, data_obj))
                anos.add(data_obj.year)
        except (ValueError, KeyError):
            continue  # Ignora datas inválidas
    
    # Chamar API para cada ano único
    for ano in anos:
        try:
            url = f"https://date.nager.at/api/v3/PublicHolidays/{ano}/BR"
            response = requests.get(url)
            if response.status_code == 200:
                feriados = response.json()
                feriados_por_ano[ano] = {f['date']: f['name'] for f in feriados}
            else:
                feriados_por_ano[ano] = {}  # Ano sem feriados ou erro
        except requests.RequestException:
            feriados_por_ano[ano] = {}  # Falha na chamada
    
    # Verificar se cada data é feriado e retornar resultados
    resultados = []
    for data_str, data_obj in datas_parseadas:
        ano = data_obj.year
        data_iso = data_obj.strftime('%Y-%m-%d')
        if data_iso in feriados_por_ano.get(ano, {}):
            nome_feriado = feriados_por_ano[ano][data_iso]
            resultados.append(f"📅 {data_str} - Feriado ({nome_feriado})")
        else:
            resultados.append(f"📅 {data_str} - Não é feriado")
    
    return resultados if resultados else ["Nenhuma data válida encontrada para verificação."]

def selecionar_pdf():
    caminho_pdf = filedialog.askopenfilename(
        title="Selecione um arquivo PDF",
        filetypes=[("Arquivos PDF", "*.pdf")]
    )
    if caminho_pdf:
        status_label.config(text="Extraindo datas...")
        janela.update()
        datas = extrair_datas_pdf(caminho_pdf)
        resultado_texto = "\n".join(f"📅 {data}" for data in datas)
        resultado_label.config(text=resultado_texto)
        if "Erro" in datas[0] or "Nenhuma" in datas[0]:
            resultado_label.config(text="\n".join(datas))
            status_label.config(text="")
            return
        
        status_label.config(text="Verificando feriados...")
        janela.update()
        resultados = verificar_feriados(datas)
        resultado_label.config(text="\n".join(resultados))
        status_label.config(text="Verificação concluída.")

# --- Interface Tkinter ---
janela = tk.Tk()
janela.title("Extrator de Datas em PDF")
janela.geometry("400x250")
janela.title("Extrator de Datas em PDF com Verificação de Feriados")
janela.geometry("500x300")
janela.resizable(False, False)

titulo = tk.Label(janela, text="📘 Extrator de Datas em PDF", font=("Arial", 14, "bold"))
@@ -48,10 +112,13 @@ def selecionar_pdf():
botao = tk.Button(janela, text="Selecionar PDF", font=("Arial", 12), command=selecionar_pdf)
botao.pack(pady=10)

resultado_label = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 11), wraplength=350, justify="left")
status_label = tk.Label(janela, text="", font=("Arial", 10), fg="blue")
status_label.pack(pady=5)

resultado_label = tk.Label(janela, text="Nenhum arquivo selecionado.", font=("Arial", 11), wraplength=450, justify="left")
resultado_label.pack(pady=20)

rodape = tk.Label(janela, text="Primeiro commit - Desenvolvido em Python", font=("Arial", 9), fg="gray")
rodape = tk.Label(janela, text="Segundo commit - Desenvolvido em Python", font=("Arial", 9), fg="gray")
rodape.pack(side="bottom", pady=5)

janela.mainloop()
janela.mainloop()
