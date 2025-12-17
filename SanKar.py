from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command
import asyncio
import random

TOKEN = "8419759472:AAEABsBJJVxqoLXYi1kOnXqkdnnCKag3iPs"
bot = Bot(TOKEN)
dp = Dispatcher()

BUDGET = 500  # фиксированный бюджет подарка
games = {}

# ---------- BUTTONS ----------
def main_menu():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🎁 Присоединиться", callback_data="join")],
        [InlineKeyboardButton(text="📋 Участники", callback_data="list_players")],
        [InlineKeyboardButton(text="🎲 Жеребьёвка", callback_data="draw")]
    ])

# ---------- BOT LOGIC ----------
@dp.message(Command("start_santa"))
async def start_santa_command(message: Message):
    games[message.chat.id] = {"players": {}}
    await message.answer(
        f"🎄 Тайный Санта начался!\n💰 Бюджет подарка: {BUDGET} ₽",
        reply_markup=main_menu()
    )

# ----- JOIN -----
@dp.callback_query(F.data == "join")
async def join_handler(call: CallbackQuery):
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
    chat_id = call.message.chat.id
    game = games.get(chat_id)

    if not game or not game["players"]:
        await call.answer("Участников пока нет", show_alert=True)
        return

    text = "🎁 Участники:\n"
    for name in game["players"].values():
        text += f"• {name}\n"
    text += f"\n💰 Бюджет подарка: {BUDGET} ₽"

    await call.message.answer(text)
    await call.answer()

# ----- DRAW -----
@dp.callback_query(F.data == "draw")
async def draw_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user = call.from_user
    game = games.get(chat_id)

    if not game or len(game["players"]) < 3:
        await call.answer("Нужно минимум 3 участника", show_alert=True)
        return

    players = list(game["players"].items())
    ids = [p[0] for p in players]
    random.shuffle(ids)

    for i, giver in enumerate(ids):
        receiver = ids[i - 1]
        await bot.send_message(
            giver,
            f"🎅 Ты даришь подарок @{game['players'][receiver]}\n💰 Бюджет: {BUDGET} ₽"
        )

    await call.message.answer("🎉 Жеребьёвка проведена! Проверьте ЛС 🎁")
    await call.answer()
    del games[chat_id]

# ---------- RUN BOT ----------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot, allowed_updates=["message", "callback_query"]))
