import tkinter as tk
import webbrowser
from tkinter import ttk, scrolledtext, messagebox
import ctypes
import re
import asyncio
import json
import os
import logging
import random
import threading
from typing import TYPE_CHECKING
import asqlite
import pyautogui
import twitchio
from twitchio import eventsub
from twitchio.ext import commands

if TYPE_CHECKING:
    import sqlite3

# Константы
DMDO_DEFAULT = 0
DMDO_90 = 1
DMDO_180 = 2
DMDO_270 = 3
CONFIG_FILE = "config_bot.json"

# Функции управления системой
def mouse_speed_norm():
    set_mouse_speed = 113
    print("mouse_speed_norm")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 10, 0)

def mouse_speed_down(f_time=5):
    set_mouse_speed = 113
    print("mouse_speed_down")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 1, 0)
    threading.Timer(f_time, mouse_speed_norm).start()

def mouse_speed_up(f_time=5):
    set_mouse_speed = 113
    print("mouse_speed_up")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 40, 0)
    threading.Timer(f_time, mouse_speed_norm).start()

def rotate_display_v1_restore():
    pyautogui.hotkey('ctrl', 'alt', 'up')
    print("rotate_display_v1_restore")

def rotate_display_v1(f_time=5):
    pyautogui.hotkey('ctrl', 'alt', 'down')
    print("rotate_display_v1")
    threading.Timer(f_time, rotate_display_v1_restore).start()

def rotate_key_v1(f_time=5):
    pass

def save_config(data):
    """Сохраняет переменные в JSON файл"""
    try:
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("Конфигурация сохранена")
    except Exception as e:
        print(f"Ошибка сохранения: {e}")

def load_config():
    """Загружает переменные из JSON файла"""
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"Ошибка загрузки: {e}")
    return {}  # Возвращаем пустой словарь если файла нет


class TwitchBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch Bot Lite - Control Panel")
        self.root.geometry("900x700")

        self.bot = None
        self.bot_thread = None
        self.is_running = False

        self.config = load_config()

        # Переменные для GUI
        # self.client_id_var = tk.StringVar(value="4m8l4jnizg88grlrb7hyyaw1bawl1h")
        # self.client_secret_var = tk.StringVar(value="hnl2tq92g942ptzzcf8igvibpqdt59")
        # self.bot_owner_var = tk.StringVar(value="immortalrayz")
        # self.author_name_var = tk.StringVar(value="immortalrayz")

        # Устанавливаем переменные из конфига или значения по умолчанию
        self.client_id_var = tk.StringVar(value=self.config.get('client_id', "c52xxwb19ljwwbi0kew1fkfn84p9zi"))
        self.client_secret_var = tk.StringVar(
            value=self.config.get('client_secret', "zpktycohn9jsywgmbj0k7jq6t57btl"))
        self.bot_owner_var = tk.StringVar(value=self.config.get('bot_owner', "kibermag"))
        self.author_name_var = tk.StringVar(value=self.config.get('author_name', "kibermag"))
        self.bot_id_var = tk.StringVar(value=self.config.get('bot_id_var', ""))

        self.status_var = tk.StringVar(value="Бот не запущен")

        # Переменные для команд
        self.mouseslow_time_var = tk.StringVar(value="5")
        self.mousefast_time_var = tk.StringVar(value="5")
        self.rotate_time_var = tk.StringVar(value="5")

        self.setup_gui()
        # Сохраняем при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        """Сохраняет настройки при закрытии окна"""
        config_data = {
            'client_id': self.client_id_var.get(),
            'client_secret': self.client_secret_var.get(),
            'bot_owner': self.bot_owner_var.get(),
            'author_name': self.author_name_var.get(),
            'bot_id_var': self.bot_id_var.get()
        }
        save_config(config_data)
        self.root.destroy()

    def setup_gui(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка управления ботом
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление ботом")

        # Вкладка тестирования команд
        commands_frame = ttk.Frame(notebook)
        notebook.add(commands_frame, text="Тестирование команд")

        self.setup_control_tab(control_frame)
        self.setup_commands_tab(commands_frame)

    def setup_control_tab(self, parent):
        # Настройки подключения
        settings_frame = ttk.LabelFrame(parent, text="Настройки подключения", padding="10")
        settings_frame.pack(fill=tk.X, pady=5)

        ttk.Label(settings_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.client_id_var, width=50).grid(row=0, column=1, sticky=tk.W + tk.E,
                                                                                  pady=2, padx=5)

        ttk.Label(settings_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.client_secret_var, width=50, show="*").grid(row=1, column=1,
                                                                                                sticky=tk.W + tk.E,
                                                                                                pady=2, padx=5)

        ttk.Label(settings_frame, text="Bot Owner:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.bot_owner_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=2,
                                                                                  padx=5)
        ttk.Button(settings_frame, text="Найти Bot ID", command=self.find_bot_id).grid(row=2, column=2, padx=5)

        ttk.Label(settings_frame, text="Author Name:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.author_name_var, width=30).grid(row=3, column=1, sticky=tk.W,
                                                                                    pady=2, padx=5)

        ttk.Label(settings_frame, text="Bot ID:").grid(row=4, column=0, sticky=tk.W, pady=2)
        bot_id_entry = ttk.Entry(settings_frame, textvariable=self.bot_id_var, width=30)
        bot_id_entry.grid(row=4, column=1, sticky=tk.W, pady=2, padx=5)
        bot_id_entry.config(state="readonly")

        # Управление ботом
        control_frame = ttk.LabelFrame(parent, text="Управление ботом", padding="10")
        control_frame.pack(fill=tk.X, pady=5)

        self.start_btn = ttk.Button(control_frame, text="Запустить бота", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Остановить бота", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        self.twich_avtorization_bot = ttk.Button(control_frame, text="Авторизация бота", command=self.twich_avtorization_bot, state=tk.DISABLED)
        self.twich_avtorization_bot.pack(side=tk.LEFT, padx=5)

        # Статус
        status_frame = ttk.LabelFrame(parent, text="Статус", padding="10")
        status_frame.pack(fill=tk.X, pady=5)

        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)

        # Логи
        log_frame = ttk.LabelFrame(parent, text="Логи бота", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=20, width=80)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        ttk.Button(log_frame, text="Очистить логи", command=self.clear_logs).pack(pady=5)

    def setup_commands_tab(self, parent):
        # Команды мыши
        mouse_frame = ttk.LabelFrame(parent, text="Команды мыши", padding="10")
        mouse_frame.pack(fill=tk.X, pady=5)

        # Mouseslow
        mouseslow_frame = ttk.Frame(mouse_frame)
        mouseslow_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mouseslow_frame, text="!mouseslow время (сек):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(mouseslow_frame, textvariable=self.mouseslow_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(mouseslow_frame, text="Тест", command=self.test_mouseslow).pack(side=tk.LEFT, padx=5)

        # Mousefast
        mousefast_frame = ttk.Frame(mouse_frame)
        mousefast_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mousefast_frame, text="!mousefast время (сек):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(mousefast_frame, textvariable=self.mousefast_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(mousefast_frame, text="Тест", command=self.test_mousefast).pack(side=tk.LEFT, padx=5)

        # Mousenorm
        mousenorm_frame = ttk.Frame(mouse_frame)
        mousenorm_frame.pack(fill=tk.X, pady=2)
        ttk.Label(mousenorm_frame, text="!mousenorm:").pack(side=tk.LEFT, padx=5)
        ttk.Button(mousenorm_frame, text="Тест", command=self.test_mousenorm).pack(side=tk.LEFT, padx=5)

        # Команды экрана
        screen_frame = ttk.LabelFrame(parent, text="Команды экрана", padding="10")
        screen_frame.pack(fill=tk.X, pady=5)

        # Rotate
        rotate_frame = ttk.Frame(screen_frame)
        rotate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(rotate_frame, text="!rotate время (сек):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(rotate_frame, textvariable=self.rotate_time_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Button(rotate_frame, text="Тест", command=self.test_rotate).pack(side=tk.LEFT, padx=5)

        # Unrotate
        unrotate_frame = ttk.Frame(screen_frame)
        unrotate_frame.pack(fill=tk.X, pady=2)
        ttk.Label(unrotate_frame, text="!unrotate:").pack(side=tk.LEFT, padx=5)
        ttk.Button(unrotate_frame, text="Тест", command=self.test_unrotate).pack(side=tk.LEFT, padx=5)

        # Hi команда
        hi_frame = ttk.LabelFrame(parent, text="Прочие команды", padding="10")
        hi_frame.pack(fill=tk.X, pady=5)

    def log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def clear_logs(self):
        """Очистка логов"""
        self.log_text.delete(1.0, tk.END)

    def find_bot_id(self):
        """Поиск ID бота по имени"""
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.bot_owner_var.get()]):
            self.log("Ошибка: Заполните Client ID, Client Secret и Bot Owner")
            return
        def run_async():
            async def fetch_bot_id():
                try:
                    async with twitchio.Client(
                            client_id=self.client_id_var.get(),
                            client_secret=self.client_secret_var.get()
                    ) as client:
                        await client.login()
                        users = await client.fetch_users(logins=[self.bot_owner_var.get()])
                        if users:
                            return users[0].id
                        return None
                except Exception as e:
                    return f"Ошибка: {str(e)}"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(fetch_bot_id())
                if isinstance(result, str):
                    self.root.after(0, lambda: self.log(result))
                    self.root.after(0, lambda: self.set_bot_id(result))
                else:
                    self.root.after(0, lambda: self.log("Пользователь не найден"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Ошибка поиска: {str(e)}"))
            finally:
                loop.close()
        threading.Thread(target=run_async, daemon=True).start()
        self.log("Поиск Bot ID...")

    def set_bot_id(self, bot_id):
        """Установка найденного Bot ID"""
        self.bot_id_var.set(bot_id)
        self.log(f"Найден Bot ID: {bot_id}")

    # Функции тестирования команд
    def test_mouseslow(self):
        try:
            time_val = int(self.mouseslow_time_var.get())
            mouse_speed_down(time_val)
            self.log(f"Тест: !mouseslow {time_val} сек")
        except ValueError:
            self.log("Ошибка: Введите число для времени")

    def test_mousenorm(self):
        mouse_speed_norm()
        self.log("Тест: !mousenorm")

    def test_mousefast(self):
        try:
            time_val = int(self.mousefast_time_var.get())
            mouse_speed_up(time_val)
            self.log(f"Тест: !mousefast {time_val} сек")
        except ValueError:
            self.log("Ошибка: Введите число для времени")

    def test_rotate(self):
        try:
            time_val = int(self.rotate_time_var.get())
            rotate_display_v1(time_val)
            self.log(f"Тест: !rotate {time_val} сек")
        except ValueError:
            self.log("Ошибка: Введите число для времени")

    def test_unrotate(self):
        rotate_display_v1_restore()
        self.log("Тест: !unrotate")

    def start_bot(self):
        """Запуск бота"""
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.bot_owner_var.get()]):
            self.log("Ошибка: Заполните Client ID, Client Secret и Bot Owner")
        def run_async():
            async def fetch_bot_id():
                try:
                    async with twitchio.Client(
                            client_id=self.client_id_var.get(),
                            client_secret=self.client_secret_var.get()
                    ) as client:
                        await client.login()
                        users = await client.fetch_users(logins=[self.bot_owner_var.get()])
                        if users:
                            return users[0].id
                        return None
                except Exception as e:
                    return f"Ошибка: {str(e)}"
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                result = loop.run_until_complete(fetch_bot_id())
                if isinstance(result, str):
                    self.root.after(0, lambda: self.log(result))
                    self.root.after(0, lambda: self.set_bot_id(result))
                else:
                    self.root.after(0, lambda: self.log("Пользователь не найден"))
            except Exception as e:
                self.root.after(0, lambda: self.log(f"Ошибка поиска: {str(e)}"))
            finally:
                loop.close()
        threading.Thread(target=run_async, daemon=True).start()
        self.log("Поиск Bot ID...")
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.bot_id_var.get()]):
            self.log("Ошибка: Заполните все поля и найдите Bot ID")
            return

        try:
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.twich_avtorization_bot.config(state=tk.NORMAL)
            self.status_var.set("Бот запускается...")
            self.log("Запуск бота...")

        except Exception as e:
            self.log(f"Ошибка запуска бота: {str(e)}")

    def stop_bot(self):
        """Остановка бота"""
        if self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.twich_avtorization_bot.config(state=tk.DISABLED)
            self.status_var.set("Бот остановлен")
            self.log("Остановка бота...")

    def twich_avtorization_bot(self):
        """Авторизация бота"""
        url = "http://localhost:4343/oauth?scopes=user:read:chat%20user:write:chat%20user:bot&force_verify=true"
        webbrowser.open(url)
        self.log(f"Открываю ссылку: {url}")

        pass
    def run_bot(self):
        """Запуск бота в отдельном потоке"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Создаем и запускаем бота
            bot_runner = BotRunner(self, loop)
            loop.run_until_complete(bot_runner.run())

        except Exception as e:
            self.log(f"Ошибка в боте: {str(e)}")
            self.root.after(0, self.stop_bot)


class BotRunner:
    def __init__(self, gui, loop):
        self.gui = gui
        self.loop = loop
        self.bot = None

    async def run(self):
        """Запуск бота"""
        try:
            # Настройка базы данных
            async with asqlite.create_pool("tokens.db") as tdb:
                tokens, subs = await self.setup_database(tdb)

                # Создаем бота
                self.bot = Bot(
                    gui=self.gui,
                    token_database=tdb,
                    subs=subs,
                    client_id=self.gui.client_id_var.get(),
                    client_secret=self.gui.client_secret_var.get(),
                    bot_id=self.gui.bot_id_var.get(),
                    owner_id=self.gui.bot_id_var.get()
                )

                # Добавляем существующие токены
                for pair in tokens:
                    await self.bot.add_token(*pair)

                # Запускаем бота
                await self.bot.start(load_tokens=False)

        except Exception as e:
            self.gui.log(f"Ошибка запуска бота: {str(e)}")

    async def setup_database(self, db):
        """Настройка базы данных"""
        query = """CREATE TABLE IF NOT EXISTS tokens(user_id TEXT PRIMARY KEY, token TEXT NOT NULL, refresh TEXT NOT NULL)"""
        async with db.acquire() as connection:
            await connection.execute(query)
            rows = await connection.fetchall("""SELECT * from tokens""")

            tokens = []
            subs = []

            for row in rows:
                tokens.append((row["token"], row["refresh"]))
                if row["user_id"] != self.gui.bot_id_var.get():
                    subs.append(eventsub.ChatMessageSubscription(
                        broadcaster_user_id=row["user_id"],
                        user_id=self.gui.bot_id_var.get()
                    ))

            return tokens, subs


class Bot(commands.AutoBot):
    def __init__(self, gui, token_database, subs, client_id, client_secret, bot_id, owner_id):
        self.gui = gui
        self.token_database = token_database
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            bot_id=bot_id,
            owner_id=owner_id,
            prefix="!",
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self):
        """Настройка компонентов бота"""
        await self.add_component(MyComponent(self.gui))

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id or payload.user_id == self.bot_id:
            return

        subs = [eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id)]
        resp = await self.multi_subscribe(subs)

        if resp.errors:
            self.gui.log(f"Ошибка подписки: {resp.errors}")

    async def add_token(self, token, refresh):
        resp = await super().add_token(token, refresh)

        query = """
        INSERT INTO tokens (user_id, token, refresh)
        VALUES (?, ?, ?)
        ON CONFLICT(user_id)
        DO UPDATE SET
            token = excluded.token,
            refresh = excluded.refresh;
        """

        async with self.token_database.acquire() as connection:
            await connection.execute(query, (resp.user_id, token, refresh))

        self.gui.log(f"Добавлен токен для: {resp.user_id}")
        return resp

    async def event_ready(self):
        self.gui.log(f"Бот успешно подключен как: {self.bot_id}")
        self.gui.root.after(0, lambda: self.gui.status_var.set("Бот запущен и готов"))


class MyComponent(commands.Component):
    def __init__(self, gui):
        self.gui = gui

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage):
        message = f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}"
        self.gui.log(message)

        # Проверяем команды только от авторизованного пользователя
        if payload.chatter.name == self.gui.author_name_var.get():
            if re.search(r'!mouseslow', payload.text):
                try:
                    str_time = int(payload.text.replace("!mouseslow", "").strip())
                    mouse_speed_down(f_time=str_time)
                    self.gui.log(f">>> !mouseslow {str_time} сек")
                except ValueError:
                    self.gui.log(">>> Ошибка: неверное время для !mouseslow")
            elif re.search(r'!mousenorm', payload.text):
                mouse_speed_norm()
                self.gui.log(">>> !mousenorm")
            elif re.search(r'!mousefast', payload.text):
                try:
                    str_time = int(payload.text.replace("!mousefast", "").strip())
                    mouse_speed_up(f_time=str_time)
                    self.gui.log(f">>> !mousefast {str_time} сек")
                except ValueError:
                    self.gui.log(">>> Ошибка: неверное время для !mousefast")
            elif re.search(r'!rotate', payload.text):
                try:
                    str_time = int(payload.text.replace("!rotate", "").strip())
                    rotate_display_v1(f_time=str_time)
                    self.gui.log(f">>> !rotate {str_time} сек")
                except ValueError:
                    self.gui.log(">>> Ошибка: неверное время для !rotate")
            elif re.search(r'!unrotate', payload.text):
                rotate_display_v1_restore()
                self.gui.log(">>> !unrotate")


if __name__ == "__main__":
    root = tk.Tk()
    app = TwitchBotGUI(root)
    root.mainloop()