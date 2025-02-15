from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
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

toast = ToastNotifier()

# Notificação de Inicialização
toast.show_toast(
    "InfernoLinks Searcher",
    "Round inicializando...",
    duration=3,
    icon_path='dante_limbus.ico'
)

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

# Configurações do Firefox
firefox_options = FirefoxOptions()
firefox_options.add_argument("--width=1920")
firefox_options.add_argument("--height=1080")
firefox_options.set_preference("dom.webdriver.enabled", False)
firefox_options.set_preference("useAutomationExtension", False)

# Função para coletar links
def collect_links(driver):
    links = []
    elements = driver.find_elements(By.TAG_NAME, "a")
    for element in elements:
        href = element.get_attribute("href")
        if href and "https://chat.whatsapp.com/" in href:
            links.append(href)

    descriptions = driver.find_elements(By.XPATH, "//div[@class='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc'] | //span[@class='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc']")
    for desc in descriptions:
        text = desc.text
        if "https://chat.whatsapp.com/" in text:
            link = "https://chat.whatsapp.com/" + text.split("https://chat.whatsapp.com/")[1].split(" ")[0]
            links.append(link)
    return links

def generate_unique_filename(base_name):
    counter = 1
    while True:
        file_name = f"{base_name}{counter}.txt"
        if not os.path.exists(file_name):
            return file_name
        counter += 1

# Função para iniciar a coleta de links
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
    time.sleep(random.uniform(2, 5))

    try:
        accept_btn = driver.find_element(By.XPATH, '//button[contains(text(), "Aceitar")]')
        accept_btn.click()
        time.sleep(random.uniform(2, 5))
    except NoSuchElementException:
        pass

    search_box = driver.find_element(By.NAME, "q")
    search_box.send_keys(search_term)
    search_box.send_keys(Keys.RETURN)
    time.sleep(random.uniform(1, 6))

    all_links = []

    while True:
        elapsed_time = time.time() - start_time
        if elapsed_time >= execution_time:
            dpg.set_value("status_text", "Tempo de execução atingido, encerrando a coleta.")
            break

        links = collect_links(driver)
        all_links.extend(links)
        dpg.set_value("status_text", f"Encontrados {len(links)} links nesta página.")

        try:
            next_button = driver.find_element(By.ID, "pnnext")
            next_button.click()
            time.sleep(random.uniform(2, 5))
        except NoSuchElementException:
            dpg.set_value("status_text", "Não há mais páginas, encerrando a coleta.")
            break
    
    file_name = generate_unique_filename("infernolinks_whatsapp")
    with open(file_name, "w") as file:
        for link in all_links:
            file.write(link + "\n")

    dpg.set_value("status_text", f"Total de links encontrados: {len(all_links)} Salvo em {file_name}")

    driver.quit()

# Função principal
def main():
    dpg.create_context()

    with dpg.window(label="InfernoLink Searcher VIP", width=900, height=720):
        dpg.add_text("Escolha o navegador para iniciar a coleta de Links:")
        dpg.add_checkbox(label="Chrome", tag="chrome_checkbox", default_value=False)
        dpg.add_checkbox(label="Brave", tag="brave_checkbox", default_value=False)
        dpg.add_checkbox(label="Firefox", tag="firefox_checkbox", default_value=False)
        dpg.add_text("Digite o termo de pesquisa:")
        dpg.add_input_text(tag="search_term_input", hint="Ex: Grupos de Academia WhatsApp", default_value="")
        dpg.add_text("Digite o tempo de execução (em minutos):")
        dpg.add_input_text(tag="execution_time_input", hint="Ex: 10 minutos", decimal=True)
        dpg.add_button(label="Iniciar Coleta", callback=start_collection)
        dpg.add_text("", tag="status_text")

    dpg.create_viewport(title='InfernoLink Searcher VIP', width=900, height=720, small_icon="dante_limbus.ico", large_icon="dante_limbus.ico")
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
