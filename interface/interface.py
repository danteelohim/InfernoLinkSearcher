"""
interface.py
------------
Define a interface gráfica utilizando o Dear PyGUI.
Este módulo é responsável por coletar as entradas do usuário, 
iniciar o processo de scraping (através do módulo scraper) e atualizar os status.
"""

import threading
import dearpygui.dearpygui as dpg
from scraper.scraper import scrape_whatsapp_links


def update_status(message):
    """
    Atualiza o texto de status na interface.
    
    :param message: str - mensagem de status a ser exibida
    """
    dpg.set_value("status_text", message)


def start_collection_callback(sender, app_data, user_data):
    """
    Callback executado quando o usuário clica no botão para iniciar a coleta de links.
    Coleta as entradas (navegador, termo de pesquisa e tempo de execução),
    valida os dados e inicia o scraping em uma thread separada para manter a interface responsiva.
    """
    # Verifica qual navegador foi selecionado
    if dpg.get_value("chrome_checkbox"):
        browser = "chrome"
    elif dpg.get_value("brave_checkbox"):
        browser = "brave"
    elif dpg.get_value("firefox_checkbox"):
        browser = "firefox"
    else:
        update_status("Por favor, escolha um navegador!")
        return

    # Recupera o termo de pesquisa
    search_term = dpg.get_value("search_term_input")
    if not search_term:
        update_status("Por favor, insira um termo de pesquisa!")
        return

    # Recupera e converte o tempo de execução (em minutos para segundos)
    execution_time_input = dpg.get_value("execution_time_input")
    try:
        execution_time = int(float(execution_time_input) * 60)
    except ValueError:
        update_status("Por favor, insira um tempo de execução válido!")
        return

    # Executa o scraping em uma thread separada para não travar a interface
    thread = threading.Thread(
        target=scrape_whatsapp_links,
        args=(browser, search_term, execution_time, update_status),
        daemon=True  # Daemon para encerrar a thread junto com a aplicação
    )
    thread.start()


def run_interface():
    """
    Configura e inicia a interface gráfica com o Dear PyGUI.
    """
    dpg.create_context()

    # Define a janela principal da aplicação
    with dpg.window(label="InfernoLinkSearcher", width=820, height=300):
        dpg.add_text("Escolha o Browser para iniciar a coleta de Links:")
        dpg.add_checkbox(label="Chrome", tag="chrome_checkbox", default_value=False)
        dpg.add_checkbox(label="Brave", tag="brave_checkbox", default_value=False)
        dpg.add_checkbox(label="Firefox", tag="firefox_checkbox", default_value=False)
        dpg.add_spacer(height=10)

        dpg.add_text("Digite o termo para a pesquisa:")
        dpg.add_input_text(tag="search_term_input", hint="Ex: https://chat.whatsapp.com/", default_value="")
        dpg.add_spacer(height=10)

        dpg.add_text("Digite o tempo de execução do Bot (em minutos):")
        dpg.add_input_text(tag="execution_time_input", hint="Ex: 10", default_value="10")
        dpg.add_spacer(height=10)

        dpg.add_button(label="Iniciar coleta de links", callback=start_collection_callback)
        dpg.add_spacer(height=10)
        dpg.add_text("", tag="status_text")

    # Configura o viewport (janela da aplicação)
    dpg.create_viewport(title='InfernoLinkSearcher - Criado por Dante', width=820, height=300,
                          small_icon='dante_limbus.ico', large_icon='dante_limbus.ico', always_on_top=True)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()


if __name__ == "__main__":
    run_interface()
