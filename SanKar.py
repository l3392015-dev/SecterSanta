from aiogram import Bot, Dispatcher
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
        [InlineKeyboardButton(text="📋 Участники", callback_data="list")],
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

@dp.callback_query()
async def callback_handler(call: CallbackQuery):
    chat_id = call.message.chat.id
    user = call.from_user
    game = games.get(chat_id)

    if call.data == "join":
        if game is None:
            await call.answer("Игра не запущена", show_alert=True)
            return
        game['players'][user.id] = user.username
        await call.answer(f"{user.username} присоединился 🎁", show_alert=True)

    elif call.data == "list":
        if game is None or not game['players']:
            await call.answer("Нет участников", show_alert=True)
            return
        text = "🎁 Участники:\n" + "\n".join(game['players'].values())
        text += f"\n💰 Бюджет подарка: {BUDGET} ₽"
        await call.message.answer(text)

    elif call.data == "draw":
        if game is None or len(game['players']) < 3:
            await call.answer("Минимум 3 участника", show_alert=True)
            return
        ids = list(game['players'].keys())
        shuffled = ids[:]
        random.shuffle(shuffled)
        for i, giver in enumerate(ids):
            receiver = shuffled[i-1]
            await bot.send_message(giver, f"🎅 Ты даришь подарок @{game['players'][receiver]} на {BUDGET} ₽")
        await call.message.answer("Жеребьёвка проведена!")
        del games[chat_id]

# ---------- RUN BOT ----------
if __name__ == "__main__":
    asyncio.run(dp.start_polling(bot))
