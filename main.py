from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, WebDriverException
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.chrome.options import Options as ChromeOptions
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from win10toast import ToastNotifier
import dearpygui.dearpygui as dpg
import time
import random
import os
from urllib.parse import urlparse, parse_qs

toast = ToastNotifier()

# Configurações do Chrome
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

# Configurações do Firefox
firefox_options = FirefoxOptions()
firefox_options.add_argument("--width=1920")
firefox_options.add_argument("--height=1080")
firefox_options.set_preference("dom.webdriver.enabled", False)
firefox_options.set_preference("useAutomationExtension", False)

def extract_whatsapp_links(url):
    if "google.com" in url:
        parsed = urlparse(url)
        qs = parse_qs(parsed.query)  # Use apenas o query da URL
        if "q" in qs:
            possible_link = qs["q"][0]  # Corrigido para acessar o primeiro elemento
            if possible_link.startswith("https://chat.whatsapp.com/"):
                return possible_link
    return url

def collect_links_with_titles(driver):
    results = driver.find_elements(By.XPATH, "//div[@class='yuRUbf']")
    links_titles = []
    for result in results:
        try:
            a_tag = result.find_element(By.TAG_NAME, "a")  # Use singular
            href = a_tag.get_attribute("href")
            try:
                title = a_tag.find_element(By.TAG_NAME, "h3").text
            except NoSuchElementException:
                title = ""
            if href and "https://chat.whatsapp.com/" in href:
                whatsapp_link = extract_whatsapp_links(href)
                links_titles.append((whatsapp_link, title))
        except NoSuchElementException:
            continue
    return links_titles

def generate_unique_filename(base_name):
    counter = 1
    while True:
        file_name = f"{base_name}{counter}.txt"
        if not os.path.exists(file_name):
            return file_name
        counter += 1

def check_captcha(driver):
    try: 
        captcha_iframe = driver.find_element(By.XPATH, "//iframe[contains(@src, 'recaptcha')]")
        if captcha_iframe:
            dpg.set_value("status_text", "Captcha detectado! Resolva-o e então prossiga com a coleta.")
            return True
    except NoSuchElementException:
        pass
    return False

def start_collection(sender, app_data):
    navegador_escolhido = ""
    if dpg.get_value("chrome_checkbox"):
        navegador_escolhido = "chrome"
    elif dpg.get_value("brave_checkbox"):
        navegador_escolhido = "brave"
    elif dpg.get_value("firefox_checkbox"):
        navegador_escolhido = "firefox"

    if not navegador_escolhido:
        dpg.set_value("status_text", "Por favor, escolha um navegador!")
        return

    search_term = dpg.get_value("search_term_input")
    if not search_term:
        dpg.set_value("status_text", "Por favor, insira um termo de pesquisa!")
        return

    execution_time = dpg.get_value("execution_time_input")
    try: 
        execution_time = int(execution_time) * 60 
    except ValueError:
        dpg.set_value("status_text", "Por favor, insira um tempo de execução válido!")
        return

    start_time = time.time()
    driver = None
    if navegador_escolhido == "chrome":
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    elif navegador_escolhido == "brave":
        chrome_options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
        driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=chrome_options)
    elif navegador_escolhido == "firefox":
        driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=firefox_options)

    driver.get("https://www.google.com")
    time.sleep(random.uniform(4, 12))  # Aumentado para parecer mais humano

    try:
        accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar")]')
        accept_btn.click()
        time.sleep(random.uniform(2, 5))
    except NoSuchElementException:
        pass

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(4, 9))

    all_links = []

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= execution_time:
            dpg.set_value("status_text", "Tempo de execução atingido, encerrando a coleta.")
            break
        if check_captcha(driver):
            continue
        try:
            links_titles = collect_links_with_titles(driver)
            all_links.extend(links_titles)
            dpg.set_value("status_text", f"Encontrados {len(links_titles)} links nesta página.")
        except WebDriverException:
            dpg.set_value("status_text", "Captcha detectado, por favor, resolva-o manualmente.")
            input("Pressione Enter após resolver o Captcha.")
            continue

        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(random.uniform(3, 12))  # Aumentado para parecer mais humano
        except NoSuchElementException:
            dpg.set_value("status_text", "Não há mais páginas, encerrando a coleta.")
            break

    file_name = generate_unique_filename("infernolinks_whatsapp")
    unique_links = list(set(all_links))
    with open(file_name, "w", encoding="utf-8") as file:
        for link, title in unique_links:
            file.write(f"{link} - {title}\n")

    dpg.set_value("status_text", f"Total de links encontrados: {len(unique_links)}. Salvo em {file_name}")
    driver.quit()

def main():
    dpg.create_context()

    with dpg.window(label="InfernoLinkSearcher", width=820, height=300):
        dpg.add_text("Escolha o Browser para iniciar a coleta de Links:")
        dpg.add_checkbox(label="Chrome", tag="chrome_checkbox", default_value=False)
        dpg.add_checkbox(label="Brave", tag="brave_checkbox", default_value=False)
        dpg.add_checkbox(label="Firefox", tag="firefox_checkbox", default_value=False)
        dpg.add_text("Digite o termo para a pesquisa:")
        dpg.add_input_text(tag="search_term_input", hint="Ex: https://chat.whatsapp.com/", default_value="")
        dpg.add_text("Digite o tempo de execução do Bot (em minutos):")
        dpg.add_input_text(tag="execution_time_input", hint="Ex: 10", decimal=True)
        dpg.add_button(label="Iniciar coleta de links", callback=start_collection)
        dpg.add_text("", tag="status_text")

    dpg.create_viewport(title='InfernoLinkSearcher - Criado por Dante', width=820, height=300,
                          small_icon='dante_limbus.ico', large_icon='dante_limbus.ico', always_on_top=True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
