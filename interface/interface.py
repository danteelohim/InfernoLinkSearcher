import dearpygui.dearpygui as dpg
import scraper.scraper

def start_collection():
    """Inicia a coleta de links com base nas configurações da interface."""
    navegador_escolhido = None
    if dpg.get_value("chrome_checkbox"):
        navegador_escolhido = "chrome"
    elif dpg.get_value("brave_checkbox"):
        navegador_escolhido = "brave"
    elif dpg.get_value("firefox_checkbox"):
        navegador_escolhido = "firefox"

    if not navegador_escolhido:
        dpg.set_value("status_text", "Por favor, escolha um navegador! ❌")
        return

    search_term = dpg.get_value("search_term_input").strip()
    if not search_term:
        dpg.set_value("status_text", "Por favor, insira o termo de pesquisa! ❌")
        return

    execution_time = dpg.get_value("execution_time_input").strip()
    try:
        execution_time = int(execution_time) * 60
    except ValueError:
        dpg.set_value("status_text", "Por favor, insira um tempo de execução válido! ❌")
        return

    dpg.set_value("status_text", "Round sendo ou foi inicializado. 🔥")    
    
    # Chamar o scraper para iniciar a coleta
    scraper.scraper.start_scraping(navegador_escolhido, search_term, execution_time)

def main():
    """Cria a interface do usuário com Dear PyGui."""
    dpg.create_context()

    with dpg.window(label="InfernusScraper", width=820, height=300, no_resize = False, no_move=True, no_close=True):
        dpg.add_text("Escolha o Navegador a ser utilizado:")
        dpg.add_checkbox(label="Chrome", tag="chrome_checkbox")
        dpg.add_checkbox(label="Brave", tag="brave_checkbox")
        dpg.add_checkbox(label="Firefox", tag="firefox_checkbox")

        dpg.add_text("Digite o Termo a ser Pesquisado:")
        dpg.add_input_text(tag="search_term_input", hint="Ex: Grupos de conversa WhatsApp link")

        dpg.add_text("Digite o tempo de execução do Bot (minutos):")
        dpg.add_input_text(tag="execution_time_input", hint="Ex: 60 minutos (apenas números)", decimal=True)

        dpg.add_button(label="Iniciar Round", callback=start_collection)
        dpg.add_text("Status:", tag="status_text")


    dpg.create_viewport(title="InfernusScraper", width=820, height=300, always_on_top=True, resizable=False, small_icon='dante_limbus.ico', large_icon='dante_limbus.ico')
    dpg.setup_dearpygui()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()
