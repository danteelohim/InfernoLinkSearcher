from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
import time
import random
import os
import tempfile
import shutil
import sys
from urllib.parse import urlparse, parse_qs

EXTENSION_PATH = "C:\\Users\\elohim\\Projekts\\PYTHON\\InfernoLinks\\scraper\\buster_captcha"

TEMP_DIR = tempfile.mkdtemp()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
]

if getattr(sys, 'frozen', False):
    import pkg_resources
    from zipfile import ZipFile

    base_path = sys._MEIPASS if hasattr(sys, "_MEIPASS") else os.path.dirname(os.path.abspath(__file__))
    extraction_path = os.path.join(os.path.expanduser("~"), "Documents", "captcha_extension")  # Mude para um diretório acessível

# Certifique-se de que a pasta de extração existe
    if not os.path.exists(extraction_path):
        os.makedirs(extraction_path)

# Abrir e extrair
    with ZipFile(os.path.join(base_path, "scraper", "buster_captcha.zip"), 'r') as zip_ref:
        zip_ref.extractall(extraction_path)



def setup_driver(browser):
    """Configura e retorna o WebDriver de acordo com o navegador escolhido."""
    if browser == "chrome" or browser == "brave":
        options = ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        options.add_argument(f"--user-agent={random.choice(USER_AGENTS)}")

        # Carregar extensão, se existir
        if os.path.exists(EXTENSION_PATH):
            options.add_argument(f"--load-extension={EXTENSION_PATH}")

        if browser == "brave":
            options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"

        return webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)

    elif browser == "firefox":
        options = FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        options.set_preference("dom.webdriver.enabled", False)

        return webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)

    raise ValueError("Navegador inválido")


def collect_links(driver):
    """
    Coleta o texto exibido na SERP do Google, buscando <a> que contenha <h3>.
    Cada <a> pode ter algo como:
    
        https://chat.whatsapp.com/C0yEBQDJldCC61sgB0cMqX
        há 19 horas — Não há nenhuma informação...
    
    Então dividimos o texto por linhas:
    - Linha 0: link do WhatsApp (se existir)
    - Linha 1 em diante: snippet/título exibido
    
    Retornamos tuplas (link, titulo).
    """
    links_found = []

    # Localiza os links que têm um <h3> dentro
    anchors = driver.find_elements(By.XPATH, "//a[.//h3]")
    for anchor in anchors:
        full_text = anchor.text.strip()
        if not full_text:
            continue
        
        # Divide o texto em linhas. A primeira linha pode ser o link, as demais o título/snippet
        lines = full_text.split('\n', 1)
        
        # Exemplo de lines:
        # [
        #   "https://chat.whatsapp.com/C0yEBQDJldCC61sgB0cMqX",
        #   "há 19 horas — Não há nenhuma informação..."
        # ]
        
        link_candidate = lines[0]  # Primeira linha
        snippet = lines[1] if len(lines) > 1 else "Sem título"

        # Verifica se a primeira linha é um link de WhatsApp
        if link_candidate.startswith("https://chat.whatsapp.com"):
            # Adiciona como tupla (link, titulo)
            links_found.append((link_candidate, snippet))
    
    return links_found


def start_scraping(browser, search_term, execution_time):
    """Inicia o processo de scraping para coletar links do WhatsApp."""
    driver = setup_driver(browser)
    driver.get("https://www.google.com")
    time.sleep(random.uniform(2, 5))

    # Tenta clicar em aceitar cookies (se aparecer)
    try:
        accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar")]')
        accept_btn.click()
        time.sleep(random.uniform(0.5, 2))
    except NoSuchElementException:
        pass

    # Faz a busca
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(0.9, 2.1))

    all_links = []
    start_t = time.time()

    while True:
        # Verifica tempo de execução
        if time.time() - start_t >= execution_time:
            print("Tempo de execução atingido, encerrando a coleta.")
            break

        try:
            page_links = collect_links(driver)
            all_links.extend(page_links)
            print(f"Encontrados {len(page_links)} links nesta página.")
        except Exception as e:
            print(f"Erro na coleta: {e}")

        # Tenta ir para a próxima página
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(random.uniform(0.2, 3))
        except NoSuchElementException:
            print("Não há mais páginas, encerrando a coleta.")
            break

    # Salva em arquivo
    file_name = generate_unique_filename("infernolinks_whatsapp")
    with open(file_name, "w", encoding="utf-8") as file:
        for link, snippet in set(all_links):
            file.write(f"{link} - {snippet}\n")

    print(f"Total de links encontrados: {len(set(all_links))}. Salvo em {file_name}")
    driver.quit()


def generate_unique_filename(base_name):
    """Gera um nome de arquivo único para salvar os links."""
    counter = 1
    while True:
        file_name = f"{base_name}{counter}.txt"
        if not os.path.exists(file_name):
            return file_name
        counter += 1
