import os
import platform
import sqlite3
import shutil
import csv
from datetime import datetime, timedelta

# ------------------------------
# Conversão de datas
# ------------------------------
def chrome_time_to_datetime(chrome_time):
    if chrome_time:
        return datetime(1601, 1, 1) + timedelta(microseconds=chrome_time)
    return ""

def firefox_time_to_datetime(firefox_time):
    if firefox_time:
        return datetime.utcfromtimestamp(firefox_time / 1_000_000)
    return ""

# ------------------------------
# Detectar caminhos dos navegadores
# ------------------------------
def get_chrome_path():
    sistema = platform.system()
    if sistema == "Windows":
        return os.path.expanduser(r"~\AppData\Local\Google\Chrome\User Data\Default\History")
    elif sistema == "Linux":
        return os.path.expanduser("~/.config/google-chrome/Default/History")
    elif sistema == "Darwin":
        return os.path.expanduser("~/Library/Application Support/Google/Chrome/Default/History")
    return None

def get_firefox_path():
    sistema = platform.system()
    if sistema == "Windows":
        base = os.path.expanduser(r"~\AppData\Roaming\Mozilla\Firefox\Profiles")
    elif sistema == "Linux":
        base = os.path.expanduser("~/.mozilla/firefox")
    elif sistema == "Darwin":
        base = os.path.expanduser("~/Library/Application Support/Firefox/Profiles")
    else:
        return None

    if os.path.exists(base):
        for pasta in os.listdir(base):
            if pasta.endswith(".default") or pasta.endswith(".default-release"):
                return os.path.join(base, pasta, "places.sqlite")
    return None

# ------------------------------
# Exportar CSV
# ------------------------------
def exportar_para_csv(dados, arquivo_csv):
    with open(arquivo_csv, "w", newline="", encoding="utf-8") as f:
        escritor = csv.writer(f)
        escritor.writerow(["Título", "URL", "Data e Hora"])
        escritor.writerows(dados)
    print(f"[+] Histórico exportado para: {arquivo_csv}")

# ------------------------------
# Extrair histórico Chrome
# ------------------------------
def extrair_chrome(caminho_hist):
    copia = "chrome_history_copy"
    shutil.copy2(caminho_hist, copia)

    conn = sqlite3.connect(copia)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_time FROM urls ORDER BY last_visit_time DESC")

    dados = []
    for url, title, time in cursor.fetchall():
        data_legivel = chrome_time_to_datetime(time).strftime("%Y-%m-%d %H:%M:%S") if time else ""
        dados.append([title, url, data_legivel])
    conn.close()
    return dados

# ------------------------------
# Extrair histórico Firefox
# ------------------------------
def extrair_firefox(caminho_hist):
    copia = "firefox_history_copy"
    shutil.copy2(caminho_hist, copia)

    conn = sqlite3.connect(copia)
    cursor = conn.cursor()
    cursor.execute("SELECT url, title, last_visit_date FROM moz_places ORDER BY last_visit_date DESC")

    dados = []
    for url, title, time in cursor.fetchall():
        data_legivel = firefox_time_to_datetime(time).strftime("%Y-%m-%d %H:%M:%S") if time else ""
        dados.append([title, url, data_legivel])
    conn.close()
    return dados

# ------------------------------
# Função principal
# ------------------------------
def main():
    print("🔍 Detectando navegador e sistema operacional...")

    chrome_path = get_chrome_path()
    firefox_path = get_firefox_path()

    if chrome_path and os.path.exists(chrome_path):
        print("[+] Chrome detectado!")
        dados = extrair_chrome(chrome_path)
        exportar_para_csv(dados, "historico_chrome.csv")
    elif firefox_path and os.path.exists(firefox_path):
        print("[+] Firefox detectado!")
        dados = extrair_firefox(firefox_path)
        exportar_para_csv(dados, "historico_firefox.csv")
    else:
        print("[-] Nenhum navegador suportado foi encontrado.")

if __name__ == "__main__":
    main()
