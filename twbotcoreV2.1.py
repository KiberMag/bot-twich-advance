import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import asyncio
import logging
from typing import TYPE_CHECKING
import asqlite
import twitchio
from twitchio import eventsub
from twitchio.ext import commands
import ctypes
import pyautogui
import threading

# Константы для поворота
DMDO_DEFAULT = 0
DMDO_90 = 1
DMDO_180 = 2
DMDO_270 = 3

def mouse_speed_norm(): # уменьшение DPI
    set_mouse_speed = 113
    print("mouse_speed_norm")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 10, 0)  # speed 1 - slow 10 - standard 20 - fast

def mouse_speed_down(f_time=5):
    set_mouse_speed = 113  # 0x0071 for SPI_SETMOUSESPEED
    print("mouse_speed_down")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 5, 0)  # speed 1 - slow 10 - standard 20 - fast
    threading.Timer(f_time, mouse_speed_norm).start()

def mouse_speed_up(f_time=5):# увеличение DPI,
    set_mouse_speed = 113  # 0x0071 for SPI_SETMOUSESPEED
    print("mouse_speed_up")
    ctypes.windll.user32.SystemParametersInfoA(set_mouse_speed, 0, 20, 0)  # speed 1 - slow 10 - standard 20 - fast
    threading.Timer(f_time, mouse_speed_norm).start()

def rotate_display_v1_restore():
    pyautogui.hotkey('ctrl', 'alt', 'up')
    print("rotate_display_v1_restore")

def rotate_display_v1(f_time=5): # Перевернуть экран с помощью горячих клавиш v1
    pyautogui.hotkey('ctrl', 'alt', 'down')  # Поворот на 180°
    print("rotate_display_v1")
    threading.Timer(f_time, rotate_display_v1_restore).start()

def rotate_key_v1(f_time=5):
    pass

if TYPE_CHECKING:
    import sqlite3

LOGGER = logging.getLogger("Bot")


class TwitchBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Twitch Bot Core Controller")
        self.root.geometry("900x700")

        self.bot = None
        self.bot_thread = None
        self.is_running = False

        # Переменные для настроек
        self.client_id_var = tk.StringVar(value="c52xxwb19ljwwbi0kew1fkfn84p9zi")
        self.client_secret_var = tk.StringVar(value="zpktycohn9jsywgmbj0k7jq6t57btl")
        self.user_id_var = tk.StringVar(value="kibermag")
        self.bot_id_var = tk.StringVar()
        self.owner_id_var = tk.StringVar()
        self.prefix_var = tk.StringVar(value="!")
        self.channels_var = tk.StringVar(value="immortalrayz")

        self.setup_gui()

    def setup_gui(self):
        # Создаем вкладки
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Вкладка настроек
        settings_frame = ttk.Frame(notebook)
        notebook.add(settings_frame, text="Настройки")

        # Вкладка управления ботом
        control_frame = ttk.Frame(notebook)
        notebook.add(control_frame, text="Управление ботом")

        # Вкладка тестирования команд
        test_frame = ttk.Frame(notebook)
        notebook.add(test_frame, text="Тестирование команд")

        # Вкладка логов
        logs_frame = ttk.Frame(notebook)
        notebook.add(logs_frame, text="Логи")

        self.setup_settings_tab(settings_frame)
        self.setup_control_tab(control_frame)
        self.setup_test_tab(test_frame)
        self.setup_logs_tab(logs_frame)

    def setup_settings_tab(self, parent):
        # Настройки подключения
        conn_frame = ttk.LabelFrame(parent, text="Настройки Twitch API", padding=10)
        conn_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(conn_frame, text="Client ID:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(conn_frame, textvariable=self.client_id_var, width=50).grid(row=0, column=1, sticky=tk.W + tk.E,
                                                                              pady=2, padx=5)

        ttk.Label(conn_frame, text="Client Secret:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(conn_frame, textvariable=self.client_secret_var, width=50, show="*").grid(row=1, column=1,
                                                                                            sticky=tk.W + tk.E, pady=2,
                                                                                            padx=5)

        ttk.Label(conn_frame, text="Username:").grid(row=2, column=0, sticky=tk.W, pady=2)
        ttk.Entry(conn_frame, textvariable=self.user_id_var, width=30).grid(row=2, column=1, sticky=tk.W, pady=2,
                                                                            padx=5)
        ttk.Button(conn_frame, text="Найти ID", command=self.search_user_id).grid(row=2, column=2, padx=5)

        ttk.Label(conn_frame, text="Bot ID:").grid(row=3, column=0, sticky=tk.W, pady=2)
        ttk.Entry(conn_frame, textvariable=self.bot_id_var, width=30, state="readonly").grid(row=3, column=1,
                                                                                             sticky=tk.W, pady=2,
                                                                                             padx=5)

        ttk.Label(conn_frame, text="Owner ID:").grid(row=4, column=0, sticky=tk.W, pady=2)
        ttk.Entry(conn_frame, textvariable=self.owner_id_var, width=30, state="readonly").grid(row=4, column=1,
                                                                                               sticky=tk.W, pady=2,
                                                                                               padx=5)

        # Дополнительные настройки
        settings_frame = ttk.LabelFrame(parent, text="Дополнительные настройки", padding=10)
        settings_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(settings_frame, text="Префикс команд:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.prefix_var, width=10).grid(row=0, column=1, sticky=tk.W, pady=2,
                                                                               padx=5)

        ttk.Label(settings_frame, text="Каналы (через запятую):").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(settings_frame, textvariable=self.channels_var, width=50).grid(row=1, column=1, sticky=tk.W + tk.E,
                                                                                 pady=2, padx=5)

    def setup_control_tab(self, parent):
        # Управление ботом
        control_frame = ttk.LabelFrame(parent, text="Управление ботом", padding=10)
        control_frame.pack(fill=tk.X, padx=5, pady=5)

        self.start_btn = ttk.Button(control_frame, text="Запустить бота", command=self.start_bot)
        self.start_btn.pack(side=tk.LEFT, padx=5)

        self.stop_btn = ttk.Button(control_frame, text="Остановить бота", command=self.stop_bot, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)

        # Статус бота
        status_frame = ttk.LabelFrame(parent, text="Статус", padding=10)
        status_frame.pack(fill=tk.X, padx=5, pady=5)

        self.status_var = tk.StringVar(value="Бот не запущен")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor=tk.W)

        # Информация о подключении
        info_frame = ttk.LabelFrame(parent, text="Информация о подключении", padding=10)
        info_frame.pack(fill=tk.X, padx=5, pady=5)

        self.connection_info_var = tk.StringVar(value="Не подключено")
        ttk.Label(info_frame, textvariable=self.connection_info_var).pack(anchor=tk.W)

    def setup_test_tab(self, parent):
        # Тестирование функций мыши
        mouse_frame = ttk.LabelFrame(parent, text="Тестирование функций мыши", padding=10)
        mouse_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(mouse_frame, text="Нормальная скорость", command=mouse_speed_norm).pack(side=tk.LEFT, padx=5)
        ttk.Button(mouse_frame, text="Снизить скорость (5 сек)", command=lambda: mouse_speed_down(5)).pack(side=tk.LEFT,
                                                                                                           padx=5)
        ttk.Button(mouse_frame, text="Повысить скорость (5 сек)", command=lambda: mouse_speed_up(5)).pack(side=tk.LEFT,
                                                                                                          padx=5)

        # Тестирование функций экрана
        screen_frame = ttk.LabelFrame(parent, text="Тестирование функций экрана", padding=10)
        screen_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Button(screen_frame, text="Повернуть экран (5 сек)", command=lambda: rotate_display_v1(5)).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(screen_frame, text="Восстановить экран", command=rotate_display_v1_restore).pack(side=tk.LEFT,
                                                                                                    padx=5)

        # Тестирование функций клавиатуры
        keyboard_frame = ttk.LabelFrame(parent, text="Тестирование функций клавиатуры", padding=10)
        keyboard_frame.pack(fill=tk.X, padx=5, pady=5)

        #ttk.Button(keyboard_frame, text="Вращение клавиш (5 сек)", command=lambda: rotate_key_v1(5)).pack(side=tk.LEFT,
        #                                                                                                  padx=5)

    def setup_logs_tab(self, parent):
        self.log_text = scrolledtext.ScrolledText(parent, height=25, width=100)
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        ttk.Button(parent, text="Очистить логи", command=self.clear_logs).pack(pady=5)

    def log(self, message):
        """Добавление сообщения в лог"""
        self.log_text.insert(tk.END, f"{message}\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def clear_logs(self):
        """Очистка логов"""
        self.log_text.delete(1.0, tk.END)

    async def search_id_user_async(self):
        """Асинхронный поиск ID пользователя"""
        try:
            async with twitchio.Client(
                    client_id=self.client_id_var.get().strip(),
                    client_secret=self.client_secret_var.get().strip()
            ) as client:
                await client.login()
                user = await client.fetch_users(logins=[self.user_id_var.get().strip()])
                if user:
                    user_obj = user[0]
                    return user_obj.id, user_obj.name
                return None, None
        except Exception as e:
            self.log(f"Ошибка поиска ID: {str(e)}")
            return None, None

    def search_user_id(self):
        """Поиск ID пользователя (синхронная обертка)"""
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.user_id_var.get()]):
            messagebox.showerror("Ошибка", "Заполните все поля: Client ID, Client Secret и Username")
            return

        def run_async():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                user_id, user_name = loop.run_until_complete(self.search_id_user_async())
                if user_id:
                    self.root.after(0, lambda: self.set_user_ids(user_id, user_name))
                else:
                    self.root.after(0, lambda: messagebox.showerror("Ошибка", "Пользователь не найден"))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Ошибка", f"Ошибка поиска: {str(e)}"))
            finally:
                loop.close()

        threading.Thread(target=run_async, daemon=True).start()

    def set_user_ids(self, user_id, user_name):
        """Установка найденных ID"""
        self.bot_id_var.set(user_id)
        self.owner_id_var.set(user_id)
        self.log(f"Найден пользователь: {user_name} (ID: {user_id})")

    def start_bot(self):
        """Запуск бота"""
        if not all([self.client_id_var.get(), self.client_secret_var.get(), self.bot_id_var.get()]):
            messagebox.showerror("Ошибка", "Заполните все необходимые поля и найдите ID пользователя")
            return

        try:
            # Создаем и запускаем бота в отдельном потоке
            self.bot_thread = threading.Thread(target=self.run_bot, daemon=True)
            self.bot_thread.start()

            self.is_running = True
            self.start_btn.config(state=tk.DISABLED)
            self.stop_btn.config(state=tk.NORMAL)
            self.status_var.set("Бот запускается...")
            self.log("Запуск бота...")

        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось запустить бота: {str(e)}")

    def stop_bot(self):
        """Остановка бота"""
        if self.bot and self.is_running:
            self.is_running = False
            self.start_btn.config(state=tk.NORMAL)
            self.stop_btn.config(state=tk.DISABLED)
            self.status_var.set("Бот остановлен")
            self.log("Остановка бота...")

    def run_bot(self):
        """Запуск бота в отдельном потоке"""
        try:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            # Инициализируем и запускаем бота
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
            # Создаем подписки
            channels = [ch.strip() for ch in self.gui.channels_var.get().split(",")]
            subs = []

            for channel in channels:
                # Получаем ID канала
                channel_id = await self.get_channel_id(channel)
                if channel_id:
                    subs.append(eventsub.ChatMessageSubscription(
                        broadcaster_user_id=channel_id,
                        user_id=self.gui.bot_id_var.get()
                    ))

            # Создаем пул базы данных
            async with asqlite.create_pool("tokens.db") as tdb:
                tokens, existing_subs = await self.setup_database(tdb)
                subs.extend(existing_subs)

                # Создаем бота
                self.bot = CustomBot(
                    gui=self.gui,
                    token_database=tdb,
                    subs=subs,
                    client_id=self.gui.client_id_var.get(),
                    client_secret=self.gui.client_secret_var.get(),
                    bot_id=self.gui.bot_id_var.get(),
                    owner_id=self.gui.owner_id_var.get(),
                    prefix=self.gui.prefix_var.get()
                )

                # Добавляем существующие токены
                for pair in tokens:
                    await self.bot.add_token(*pair)

                # Запускаем бота
                await self.bot.start(load_tokens=False)

        except Exception as e:
            self.gui.log(f"Ошибка запуска бота: {str(e)}")

    async def get_channel_id(self, channel_name):
        """Получение ID канала"""
        try:
            async with twitchio.Client(
                    client_id=self.gui.client_id_var.get(),
                    client_secret=self.gui.client_secret_var.get()
            ) as client:
                await client.login()
                users = await client.fetch_users(logins=[channel_name])
                return users[0].id if users else None
        except:
            return None

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


class CustomBot(commands.AutoBot):
    def __init__(self, gui, token_database, subs, client_id, client_secret, bot_id, owner_id, prefix):
        self.gui = gui
        self.token_database = token_database
        super().__init__(
            client_id=client_id,
            client_secret=client_secret,
            bot_id=bot_id,
            owner_id=owner_id,
            prefix=prefix,
            subscriptions=subs,
            force_subscribe=True,
        )

    async def setup_hook(self):
        """Настройка компонентов бота"""
        await self.add_component(MyComponent(self.gui))

    async def event_oauth_authorized(self, payload: twitchio.authentication.UserTokenPayload):
        """Обработка авторизации OAuth"""
        await self.add_token(payload.access_token, payload.refresh_token)

        if not payload.user_id or payload.user_id == self.bot_id:
            return

        # Создаем подписки для нового канала
        subs = [eventsub.ChatMessageSubscription(broadcaster_user_id=payload.user_id, user_id=self.bot_id)]
        resp = await self.multi_subscribe(subs)

        if resp.errors:
            self.gui.log(f"Ошибка подписки для пользователя {payload.user_id}: {resp.errors}")

    async def add_token(self, token, refresh):
        """Добавление токена"""
        resp = await super().add_token(token, refresh)

        # Сохраняем токен в базе данных
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

        self.gui.log(f"Добавлен токен для пользователя: {resp.user_id}")
        return resp

    async def event_ready(self):
        """Событие готовности бота"""
        self.gui.log(f"Бот успешно подключен как: {self.bot_id}")
        self.gui.root.after(0, lambda: self.gui.status_var.set("Бот запущен и готов"))


class MyComponent(commands.Component):
    """Компонент с командами бота"""

    def __init__(self, gui):
        self.gui = gui

    @commands.Component.listener()
    async def event_message(self, payload: twitchio.ChatMessage):
        """Обработка сообщений в чате"""
        message = f"[{payload.broadcaster.name}] - {payload.chatter.name}: {payload.text}"
        self.gui.log(message)

    @commands.command()
    async def mouseslow(self, ctx: commands.Context):
        """Снижение скорости мыши на 5 секунд"""
        await ctx.send(f"Пользователь {ctx.author.name} снизил скорость мыши на 5 секунд!")
        mouse_speed_down(5)

    @commands.command()
    async def mousenorm(self, ctx: commands.Context):
        """Восстановление нормальной скорости мыши"""
        await ctx.send(f"Пользователь {ctx.author.name} восстановил скорость мыши!")
        mouse_speed_norm()

    @commands.command()
    async def mousefast(self, ctx: commands.Context):
        """Повышение скорости мыши на 5 секунд"""
        await ctx.send(f"Пользователь {ctx.author.name} повысил скорость мыши на 5 секунд!")
        mouse_speed_up(5)

    @commands.command()
    async def rotate(self, ctx: commands.Context):
        """Поворот экрана на 5 секунд"""
        await ctx.send(f"Пользователь {ctx.author.name} повернул экран на 5 секунд!")
        rotate_display_v1(5)

    @commands.command()
    async def unrotate(self, ctx: commands.Context):
        """Восстановление ориентации экрана"""
        await ctx.send(f"Пользователь {ctx.author.name} восстановил ориентацию экрана!")
        rotate_display_v1_restore()

    @commands.command()
    async def keyspin(self, ctx: commands.Context):
        """Вращение клавиш на 5 секунд"""
        await ctx.send(f"Пользователь {ctx.author.name} включил вращение клавиш на 5 секунд!")
        rotate_key_v1(5)


if __name__ == "__main__":
    # Настройка логирования
    logging.basicConfig(level=logging.INFO)

    root = tk.Tk()
    app = TwitchBotGUI(root)
    root.mainloop()
