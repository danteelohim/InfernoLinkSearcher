from setuptools import setup
from Cython.Build import cythonize
import shutil
import os
import zipfile
import sys

# Diretórios e arquivos do projeto
modules = [
    "scraper/scraper.py",
    "interface/interface.py",
    "main.py"
]

# Criar pasta de build se não existir
BUILD_DIR = "build_cython"
if not os.path.exists(BUILD_DIR):
    os.makedirs(BUILD_DIR)

# 1️⃣ **Compilar os arquivos Python para Cython**
print("🔹 Compilando arquivos com Cython...")
setup(
    ext_modules=cythonize(modules, compiler_directives={"language_level": "3"}),
    script_args=["build_ext"],
)

# Mover arquivos compilados para a pasta de build
for mod in modules:
    base_name = os.path.splitext(os.path.basename(mod))[0]
    compiled_file = f"{base_name}.pyd" if sys.platform == "win32" else f"{base_name}.so"
    
    if os.path.exists(compiled_file):
        shutil.move(compiled_file, os.path.join(BUILD_DIR, compiled_file))

print("✅ Compilação Cython concluída!")

# 2️⃣ **Empacotar a extensão `buster_captcha` em um ZIP**
print("🔹 Empacotando extensão `buster_captcha`...")
zip_file = "buster_captcha.zip"

with zipfile.ZipFile(zip_file, "w", zipfile.ZIP_DEFLATED) as zipf:
    for root, _, files in os.walk("buster_captcha"):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, "buster_captcha"))

print(f"✅ Extensão `{zip_file}` empacotada com sucesso!")

# 3️⃣ **Criar o executável com PyInstaller**
print("🔹 Criando executável com PyInstaller...")
add_data_flag = ":" if sys.platform != "win32" else ";"
os.system(
    f'pyinstaller --onefile --noconsole --icon=dante_limbus.ico --name="InfernusScraper" '
    f'--add-data="{zip_file}{add_data_flag}scraper/" main.py'
)

print("✅ Executável criado com sucesso!")
