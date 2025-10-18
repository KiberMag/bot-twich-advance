import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'twbotcoreV2.1.py',
    '--onefile',
    '--windowed',
    '--name=BotController',
    '--icon=logo.ico',  # опционально
    # '--add-data=chromedriver.exe;.',  # если используете chromedriver
    # '--hidden-import=selenium'
])