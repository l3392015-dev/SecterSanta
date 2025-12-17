from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, ChatType
from aiogram.filters import Command
import asyncio
import random
import logging

logging.basicConfig(level=logging.INFO)

TOKEN = "8419759472:AAEABsBJJVxqoLXYi1kOnXqkdnnCKag3iPs"
bot = Bot(TOKEN)
dp = Dispatcher()

BUDGET = 500  # фиксированный бюджет подарка
games = {}
ready_users = set()  # пользователи, написавшие боту в ЛС

# ---------- BUTTONS ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Присоединиться", callback_data="join")],
        [InlineKeyboardButton(text="📋 Участники", callback_data="list_players")],
        [InlineKeyboardButton(text="🎲 Жеребьёвка", callback_data="draw")]
    ])

# ---------- PRIVATE START ----------
@dp.message(Command(commands=["start"]))
async def private_start(message: Message):
    if message.chat.type == ChatType.PRIVATE:
        ready_users.add(message.from_user.id)
        await message.answer("✅ Отлично! Теперь ты можешь участвовать в Тайном Санте 🎄")

# ---------- BOT LOGIC ----------
@dp.message(Command(commands=["start_santa"]))
async def start_santa_command(message: Message):
    logging.info(f"Received /start_santa from {message.from_user.id} in chat {message.chat.id}")
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.answer("❌ Команду /start_santa можно использовать только в группе")
        return

    games[message.chat.id] = {"players": {}, "admin_id": message.from_user.id}
    await message.answer(
        f"🎄 Тайный Санта начался!\n💰 Бюджет подарка: {BUDGET} ₽",
        reply_markup=main_menu()
    )

# ----- JOIN -----
@dp.callback_query(F.data == "join")
async def join_handler(call: CallbackQuery):
    logging.info(f"{call.from_user.id} clicked join in chat {call.message.chat.id}")
    chat_id = call.message.chat.id
    user = call.from_user
    game = games.get(chat_id)

    if not game:
        await call.answer("Игра не запущена", show_alert=True)
        return

    name = user.username or user.full_name
    game["players"][user.id] = name

    await call.answer("Ты участвуешь 🎁", show_alert=True)

# ----- LIST -----
@dp.callback_query(F.data == "list_players")
async def list_handler(call: CallbackQuery):
    logging.info(f"{call.from_user.id} clicked list_players in chat {call.message.chat.id}")
    chat_id = call.message.chat.id
    game = games.get(chat_id)

    if not game or not game["players"]:
        await call.answer("Участников пока нет", show_alert=True)
        return

    text = "🎁 Участники:\n"
    for uid, name in game["players"].items():
        status = "✅" if uid in ready_users else "❌"
        text += f"• {name} {status}\n"
    text += f"\n💰 Бюджет подарка: {BUDGET} ₽"

    await call.message.answer(text)
    await call.answer()

# ----- DRAW (только админ) -----
@dp.callback_query(F.data == "draw")
async def draw_handler(call: CallbackQuery):
    logging.info(f"{call.from_user.id} clicked draw in chat {call.message.chat.id}")
    chat_id = call.message.chat.id
    user = call.from_user
    game = games.get(chat_id)

    if not game:
        await call.answer("Игра не запущена", show_alert=True)
        return

    if user.id != game.get("admin_id"):
        await call.answer("⚠️ Только админ может провести жеребьёвку", show_alert=True)
        return

    if len(game["players"]) < 3:
        await call.answer("Нужно минимум 3 участника", show_alert=True)
        return

    not_ready = [name for uid, name in game["players"].items() if uid not in ready_users]
    if not_ready:
        await call.answer("Не все участники готовы", show_alert=True)
        await call.message.answer(
            "❗ Следующие участники не написали боту в ЛС:\n"
            + "\n".join(f"• {n}" for n in not_ready)
            + "\n\n➡️ Пусть они откроют бота и напишут /start"
        )
        return

    ids = list(game["players"].keys())
    random.shuffle(ids)

    for i, giver in enumerate(ids):
        receiver = ids[i - 1]
        name = game['players'][receiver]
        await bot.send_message(
            giver,
            f"🎅 Ты даришь подарок {name}\n💰 Бюджет: {BUDGET} ₽"
        )

    await call.message.answer("🎉 Жеребьёвка проведена! Проверьте ЛС 🎁")
    await call.answer()
    del games[chat_id]

# ---------- RUN BOT ----------
if __name__ == "__main__":
    logging.info("Starting bot...")
    asyncio.run(dp.start_polling(bot, allowed_updates=["message", "callback_query"]))
