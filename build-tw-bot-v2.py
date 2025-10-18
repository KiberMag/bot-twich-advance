import PyInstaller.__main__
import os

PyInstaller.__main__.run([
    'tw-bot-v2.py',
    '--onefile',
    '--windowed',
    '--name=BotController',
    # '--icon=app.ico',  # опционально
    # '--add-data=chromedriver.exe;.',  # если используете chromedriver
    # '--hidden-import=selenium'
])