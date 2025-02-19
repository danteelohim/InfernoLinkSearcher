"""
scraper.py
----------
Contém todas as funções relacionadas à coleta e tratamento dos links do WhatsApp,
incluindo a configuração dos drivers do Selenium, a extração e limpeza dos links e
a lógica principal de scraping.
"""

import time
import random
import os
from urllib.parse import urlparse, parse_qs, urlunparse, urlencode

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.firefox.options import Options as FirefoxOptions

from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager


def setup_chrome_driver(binary_location=None):
    """
    Configura o driver do Chrome com opções avançadas para mascarar a automação.
    Se 'binary_location' for especificado, ele é usado para iniciar navegadores derivados do Chrome (ex: Brave).
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--log-level=1")
    chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option("useAutomationExtension", False)
    chrome_options.add_argument("--user-agent=" + random.choice([
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.49 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.85 Safari/537.36",
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36"
    ]))
    if binary_location:
        chrome_options.binary_location = binary_location

    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    return driver


def setup_firefox_driver():
    """
    Configura o driver do Firefox com opções que evitam a detecção da automação.
    """
    firefox_options = FirefoxOptions()
    firefox_options.add_argument("--width=1920")
    firefox_options.add_argument("--height=1080")
    firefox_options.set_preference("dom.webdriver.enabled", False)
    firefox_options.set_preference("useAutomationExtension", False)
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)
    return driver


def setup_webdriver(browser):
    """
    Configura o webdriver do Selenium com base no navegador escolhido.
    
    :param browser: str - "chrome", "brave" ou "firefox"
    :return: instância do webdriver
    :raises ValueError: se o navegador não for suportado
    """
    if browser == "chrome":
        return setup_chrome_driver()
    elif browser == "brave":
        # Brave é baseado no Chrome; especifique o caminho do executável.
        binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        return setup_chrome_driver(binary_location=binary_location)
    elif browser == "firefox":
        return setup_firefox_driver()
    else:
        raise ValueError("Navegador não suportado. Escolha 'chrome', 'brave' ou 'firefox'.")


def clean_whatsapp_link(url):
    """
    Limpa e normaliza um link de grupo do WhatsApp.
    
    1. Se o link for um redirecionamento do Google, extrai o parâmetro 'q'.
    2. Garante que o link possua o esquema "https://".
    3. Se o link for do WhatsApp, remove parâmetros indesejados, mantendo apenas os permitidos.
    
    Exemplo:
        Link sujo: https://www.google.com/setprefs?sig=0_d_sSgheAoYNzP_y-W4C8NjfS7SQ%3D&source=en_ignored_notification&pre
        Link limpo (exemplo desejado): https://chat.whatsapp.com/&udm=2&fbs=ABzOT
    
    :param url: str - URL a ser limpa
    :return: str - URL limpa e normalizada
    """
    # Se for um redirecionamento do Google, tenta extrair o link real do parâmetro 'q'
    if "google.com" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "q" in qs:
            url = qs["q"][0]

    # Garante que o link tenha o esquema correto
    parsed = urlparse(url)
    if not parsed.scheme:
        url = "https://" + url
        parsed = urlparse(url)

    # Se o link é do WhatsApp, mantenha apenas os parâmetros permitidos (por exemplo, "udm" e "fbs")
    if "chat.whatsapp.com" in parsed.netloc:
        allowed_keys = {"udm", "fbs"}
        qs_dict = parse_qs(parsed.query)
        clean_qs = {k: v for k, v in qs_dict.items() if k in allowed_keys}
        clean_query = urlencode(clean_qs, doseq=True)
        cleaned = parsed._replace(query=clean_query)
        return urlunparse(cleaned)

    return url


def extract_whatsapp_links(url):
    """
    A partir de uma URL, tenta extrair um link válido do WhatsApp.
    Se o link for um redirecionamento do Google, utiliza a função de limpeza.
    
    :param url: str - URL extraída de um elemento da página
    :return: str ou None - link limpo do WhatsApp ou None se não for válido
    """
    # Se for redirecionamento do Google, extrai o parâmetro 'q'
    if "google.com" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)
        if "q" in qs:
            possible_link = qs["q"][0]
            if "chat.whatsapp.com" in possible_link:
                return clean_whatsapp_link(possible_link)
    # Se já for um link do WhatsApp, limpa e retorna
    if "chat.whatsapp.com" in url:
        return clean_whatsapp_link(url)
    return None


def collect_links_with_titles(driver):
    """
    Coleta todos os links de grupos do WhatsApp e seus títulos (texto dos links)
    da página atual.
    
    :param driver: instância do webdriver
    :return: list de tuplas (link, título)
    """
    links_titles = []
    links = driver.find_elements(By.XPATH, "//a[@href]")
    for link in links:
        href = link.get_attribute("href")
        if href and "chat.whatsapp.com" in href:
            whatsapp_link = extract_whatsapp_links(href)
            if whatsapp_link:
                # Se o link não possuir texto, define um título padrão
                title = link.text.strip() if link.text.strip() else "Sem título"
                links_titles.append((whatsapp_link, title))
    return links_titles


def generate_unique_filename(base_name):
    """
    Gera um nome de arquivo único adicionando um contador ao nome base.
    
    :param base_name: str - nome base do arquivo
    :return: str - nome de arquivo único
    """
    counter = 1
    while True:
        file_name = f"{base_name}{counter}.txt"
        if not os.path.exists(file_name):
            return file_name
        counter += 1


def check_captcha(driver):
    """
    Verifica se há um CAPTCHA presente na página.
    
    :param driver: instância do webdriver
    :return: bool - True se um CAPTCHA for detectado, False caso contrário.
    """
    try:
        captcha_iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        if captcha_iframe:
            return True
    except NoSuchElementException:
        pass
    return False


def scrape_whatsapp_links(browser, search_term, execution_time, status_callback=None):
    """
    Função principal de scraping que:
    
      - Configura o webdriver com base no navegador escolhido.
      - Acessa o Google e realiza a busca pelo termo informado.
      - Itera pelas páginas de resultados coletando links de grupos do WhatsApp.
      - Interrompe a coleta ao atingir o tempo de execução ou quando não há mais páginas.
      - Salva os links únicos em um arquivo de texto.
    
    :param browser: str - navegador escolhido ("chrome", "brave" ou "firefox")
    :param search_term: str - termo de pesquisa a ser usado no Google
    :param execution_time: int - tempo de execução em segundos
    :param status_callback: function - função para atualizar o status na interface (opcional)
    :return: list de tuplas (link, título) com os links coletados
    """
    driver = setup_webdriver(browser)
    start_time = time.time()

    # Acessa a página inicial do Google
    driver.get("https://www.google.com")
    time.sleep(random.uniform(4, 12))  # Espera para simular comportamento humano

    # Tenta aceitar os cookies, se o botão estiver presente
    try:
        accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar")]')
        accept_btn.click()
        time.sleep(random.uniform(2, 5))
    except NoSuchElementException:
        pass

    # Realiza a busca no Google
    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4, 9))

    all_links = []

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= execution_time:
            if status_callback:
                status_callback("Tempo de execução atingido, encerrando a coleta.")
            break

        if check_captcha(driver):
            if status_callback:
                status_callback("Captcha detectado! Por favor, resolva-o manualmente.")
            # Aguarda alguns segundos antes de tentar novamente
            time.sleep(5)
            continue

        try:
            links_titles = collect_links_with_titles(driver)
            all_links.extend(links_titles)
            if status_callback:
                status_callback(f"Encontrados {len(links_titles)} links nesta página.")
        except WebDriverException:
            if status_callback:
                status_callback("Erro no WebDriver. Verifique se há um Captcha e resolva-o manualmente.")
            time.sleep(5)
            continue

        # Tenta avançar para a próxima página de resultados
        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(random.uniform(3, 12))
        except NoSuchElementException:
            if status_callback:
                status_callback("Não há mais páginas, encerrando a coleta.")
            break

    driver.quit()

    # Remove duplicatas convertendo a lista para um conjunto
    unique_links = list(set(all_links))

    # Gera um nome de arquivo único e salva os links coletados
    file_name = generate_unique_filename("infernolinks_whatsapp")
    with open(file_name, "w", encoding="utf-8") as file:
        for link, title in unique_links:
            file.write(f"{link} - {title}\n")

    if status_callback:
        status_callback(f"Total de links encontrados: {len(unique_links)}. Salvo em {file_name}")

    return unique_links