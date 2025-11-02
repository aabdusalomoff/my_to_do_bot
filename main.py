import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from environs import Env
from database import *

# Настройка
env = Env()
env.read_env()
bot = Bot(token=env.str("TOKEN"))
dp = Dispatcher()

# Старт
@dp.message(Command("start"))
async def start(msg: Message):
    create_table()
    await msg.answer("📝 To-Do Bot\n/add - добавить\n/list - показать список")

# Добавление задачи
@dp.message(Command("add"))
async def add_cmd(msg: Message):
    await msg.answer("✏️ Введите задачу:")

@dp.message()
async def save_task(msg: Message):
    if msg.text and not msg.text.startswith('/'):
        add_task(msg.from_user.id, msg.text)
        await msg.answer("✅ Задача добавлена!")

# Список задач
@dp.message(Command("list"))
async def list_cmd(msg: Message):
    tasks = get_tasks(msg.from_user.id)
    if not tasks:
        await msg.answer("📭 Нет задач")
        return
    
    for task in tasks:
        kb = InlineKeyboardMarkup(inline_keyboard=[[
            InlineKeyboardButton("✅ Готово", callback_data=f"done_{task[0]}"),
            InlineKeyboardButton("❌ Удалить", callback_data=f"del_{task[0]}")
        ]])
        status = "✅" if task[2] else "⏳"
        await msg.answer(f"{status} {task[1]}", reply_markup=kb)

# Отметка выполнено
@dp.callback_query(F.data.startswith("done_"))
async def done_handler(call: CallbackQuery):
    task_id = int(call.data.split("_")[1])
    mark_done(task_id)
    text = call.message.text.replace("⏳", "✅")
    await call.message.edit_text(text)
    await call.answer("✅ Выполнено!")

# Удаление задачи
@dp.callback_query(F.data.startswith("del_"))
async def del_handler(call: CallbackQuery):
    task_id = int(call.data.split("_")[1])
    delete_task(task_id)
    await call.message.delete()
    await call.answer("🗑️ Удалено!")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
