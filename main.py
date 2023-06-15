import telebot
from telebot import types
from decouple import config


class TodoBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.tasks = []

    def start(self, message):
        self.bot.send_message(message.chat.id, "Привет! Я ToDoBot!")
        self.send_buttons(message)

    def handle_add(self, message):
        self.bot.reply_to(message, "Введите новую задачу:")
        self.bot.register_next_step_handler(message, self.add_task)

    def add_task(self, message):
        task = message.text
        self.tasks.append(task)
        self.bot.reply_to(message, "Задача успешно добавлена!")
        self.send_buttons(message)

    def handle_tasks(self, message):
        task_list = ""
        if self.tasks:
            for index, task in enumerate(self.tasks):
                task_list += f"{index + 1}. {task}\n"
        else:
            task_list = "Список задач пуст."
        self.bot.reply_to(message, task_list)
        self.send_buttons(message)

    def handle_update(self, message):
        self.bot.reply_to(message, "Введите номер задачи, которую хотите обновить:")
        self.bot.register_next_step_handler(message, self.update_task)

    def update_task(self, message):
        try:
            task_index = int(message.text) - 1
            if 0 <= task_index < len(self.tasks):
                self.bot.reply_to(message, f"Введите новое значение для задачи \"{self.tasks[task_index]}\":")
                self.bot.register_next_step_handler(message, self.process_update, task_index)
            else:
                self.bot.reply_to(message, "Неверный номер задачи.")
        except ValueError:
            self.bot.reply_to(message, "Неверный номер задачи. Введите число.")

    def process_update(self, message, task_index):
        new_task = message.text
        self.tasks[task_index] = new_task
        self.bot.reply_to(message, "Задача успешно обновлена!")
        self.send_buttons(message)

    def handle_delete(self, message):
        self.bot.reply_to(message, "Введите номер задачи, которую хотите удалить:")
        self.bot.register_next_step_handler(message, self.delete_task)

    def delete_task(self, message):
        try:
            task_index = int(message.text) - 1
            if 0 <= task_index < len(self.tasks):
                deleted_task = self.tasks.pop(task_index)
                self.bot.reply_to(message, f"Задача \"{deleted_task}\" успешно удалена!")
            else:
                self.bot.reply_to(message, "Неверный номер задачи.")
        except ValueError:
            self.bot.reply_to(message, "Неверный номер задачи. Введите число.")
        self.send_buttons(message)

    def handle_unknown(self, message):
        self.bot.reply_to(message, "Неизвестная команда. Попробуйте еще раз.")
        self.send_buttons(message)

    def send_buttons(self, message):
        keyboard = types.InlineKeyboardMarkup()
        add_button = types.InlineKeyboardButton("Добавить задачу", callback_data="add")
        show_button = types.InlineKeyboardButton("Показать задачи", callback_data="show")
        update_button = types.InlineKeyboardButton("Обновить задачу", callback_data="update")
        delete_button = types.InlineKeyboardButton("Удалить задачу", callback_data="delete")
        keyboard.add(add_button, show_button, update_button, delete_button)
        self.bot.send_message(message.chat.id, "Выберите действие:", reply_markup=keyboard)


my_bot = TodoBot(config('TOKEN'))

@my_bot.bot.message_handler(commands=['start'])
def start(message):
    my_bot.start(message)

@my_bot.bot.message_handler(func=lambda message: True)
def handle_unknown(message):
    my_bot.handle_unknown(message)

@my_bot.bot.callback_query_handler(func=lambda call: True)
def handle_button_click(call):
    if call.data == "add":
        my_bot.bot.answer_callback_query(call.id)
        my_bot.handle_add(call.message)
    elif call.data == "show":
        my_bot.bot.answer_callback_query(call.id)
        my_bot.handle_tasks(call.message)
    elif call.data == "update":
        my_bot.bot.answer_callback_query(call.id)
        my_bot.handle_update(call.message)
    elif call.data == "delete":
        my_bot.bot.answer_callback_query(call.id)
        my_bot.handle_delete(call.message)

my_bot.bot.polling()
