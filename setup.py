from setuptools import setup, Command
import os

# Nome do arquivo principal do seu projeto
main_script = 'main.py'

# Nome do ícone, se você estiver usando um
icon_file = 'dante_limbus.ico'

# Argumentos para o PyInstaller
pyinstaller_options = [
    '--onefile',
    '--noconsole',
    f'--icon={icon_file}',
    main_script
]

# Comando customizado para chamar o PyInstaller
class BuildExecutableCommand(Command):
    description = "Build exec using pyinstaller"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass


    def run(self):
        os.system('pyinstaller ' + ' '.join(pyinstaller_options))

setup(
    name='InfernoLinks Searcher',
    version='0.1',
    description='Tool for searching WhatsApp group links.',
    author='Seu Nome',
    author_email='muzzarellano@proton.me',
    packages=[],
    install_requires=[
        'selenium',
        'win10toast',
        'pyinstaller',
        'pyamor'
        
    ],
    scripts=[main_script],
    cmdclass={
        'build_exe': BuildExecutableCommand,
    }
)
