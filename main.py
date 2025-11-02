import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from environs import Env
from database import *

env = Env()
env.read_env()
bot = Bot(token=env.str("TOKEN"))
dp = Dispatcher()

# ---- Старт ----
@dp.message(Command("start"))
async def start(msg: Message):
    create_table()
    await msg.answer(
        "📝 To-Do Bot с категориями и напоминаниями\n\n"
        "/add - добавить задачу\n"
        "/list - показать все задачи\n"
        "/list <категория> - показать задачи категории\n"
        "/clear - удалить все задачи\n"
        "/remind <номер> <минуты> - поставить напоминание"
    )

# ---- Добавление задачи ----
@dp.message(Command("add"))
async def add_cmd(msg: Message):
    await msg.answer("✏️ Введите задачу (можно указать категорию через |, например: Покупить хлеб | Личное):")

@dp.message()
async def save_task(msg: Message):
    if msg.text and not msg.text.startswith('/'):
        if "|" in msg.text:
            task_text, category = map(str.strip, msg.text.split("|", 1))
        else:
            task_text = msg.text.strip()
            category = "Без категории"

        add_task(msg.from_user.id, task_text, category)
        await msg.answer(f"✅ Задача добавлена!\nКатегория: {category}")

# ---- Список задач ----
@dp.message(Command("list"))
async def list_cmd(msg: Message):
    parts = msg.text.split(maxsplit=1)
    if len(parts) == 2:
        category = parts[1].strip()
        tasks = get_tasks_by_category(msg.from_user.id, category)
        if not tasks:
            await msg.answer(f"📭 Нет задач в категории '{category}'")
            return
    else:
        tasks = get_tasks(msg.from_user.id)
        if not tasks:
            await msg.answer("📭 Нет задач")
            return

    text = ""
    for i, task in enumerate(tasks, 1):
        status = "✅" if task[3] else "⏳"
        text += f"{i}. {status} {task[1]} (Категория: {task[2]}, добавлено: {task[4]})\n"
    await msg.answer(text)

# ---- Очистка всех задач ----
@dp.message(Command("clear"))
async def clear_cmd(msg: Message):
    clear_tasks(msg.from_user.id)
    await msg.answer("🗑️ Все задачи удалены!")

# ---- Напоминания ----
async def set_reminder(user_id, task_id, minutes):
    await asyncio.sleep(minutes * 60)
    task = get_task_by_id(task_id)
    if task and not task[3]:
        await bot.send_message(user_id, f"⏰ Напоминание: {task[1]} (Категория: {task[2]})")

@dp.message(Command("remind"))
async def remind_cmd(msg: Message):
    parts = msg.text.split()
    if len(parts) < 3:
        await msg.answer("Использование: /remind <номер задачи> <минуты>")
        return
    try:
        task_num = int(parts[1])
        minutes = int(parts[2])
        tasks = get_tasks(msg.from_user.id)
        if 0 < task_num <= len(tasks):
            task_id = tasks[task_num - 1][0]
            asyncio.create_task(set_reminder(msg.from_user.id, task_id, minutes))
            await msg.answer(f"⏰ Напоминание установлено на {minutes} минут для задачи {task_num}")
        else:
            await msg.answer("❌ Неверный номер задачи")
    except ValueError:
        await msg.answer("❌ Номер задачи и минуты должны быть числами")

# ---- Inline кнопки: выполнено / удалить ----
@dp.callback_query(F.data.startswith("done_"))
async def done_handler(call: CallbackQuery):
    task_id = int(call.data.split("_")[1])
    mark_done(task_id)
    text = call.message.text.replace("⏳", "✅")
    await call.message.edit_text(text)
    await call.answer("✅ Выполнено!")

@dp.callback_query(F.data.startswith("del_"))
async def del_handler(call: CallbackQuery):
    task_id = int(call.data.split("_")[1])
    delete_task(task_id)
    await call.message.delete()
    await call.answer("🗑️ Удалено!")

# ---- Запуск ----
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(dp.start_polling(bot))
