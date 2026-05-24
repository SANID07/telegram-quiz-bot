import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    InlineQueryResultArticle,
    InputTextMessageContent
)
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

TOKEN = "8621282238:AAEvYBVj1c4j0KedZqe1gU_d8NvT2n1Y_yM"
ADMIN_ID = 1249170269

bot = Bot(
    token=TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()

ready_users = set()

QUIZ_QUESTION = "Wrestling Bot"

QUIZ_OPTIONS = [
    "0",
    "1",
    "2",
    "3"
    "4",
    "5",
    "6"
]

CORRECT_OPTION = 0

answer_times = {}


# START COMMAND
@dp.message(Command("start"))
async def start(message: types.Message):

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="I am ready!",
                    callback_data="ready"
                )
            ]
        ]
    )

    text = f"""
🎲 Get ready for the quiz '{QUIZ_QUESTION}'

🖊 1 question
⏱ 10 seconds per question
🗳 Votes are visible to quiz owner only

🏁 The quiz will begin when at least 2 people are ready.
"""

    await message.answer(
        text,
        reply_markup=keyboard
    )


# INLINE MODE
@dp.inline_query()
async def inline_quiz(inline_query: types.InlineQuery):

    results = [
        InlineQueryResultArticle(
            id="quiz1",
            title="Start this Quiz",
            description="Start Quiz in the Group",
            input_message_content=InputTextMessageContent(
                message_text="/start"
            )
        )
    ]

    await inline_query.answer(
        results=results,
        cache_time=1,
        is_personal=True
    )


# READY BUTTON
@dp.callback_query()
async def ready_button(callback: types.CallbackQuery):

    global answer_times

    user = callback.from_user

    ready_users.add(user.id)

    await callback.answer("You are ready!")

    await bot.send_message(
        callback.message.chat.id,
        f"✅ {user.full_name} is ready! ({len(ready_users)}/2)"
    )

    if len(ready_users) >= 2:

        await bot.send_message(
            callback.message.chat.id,
            "⏳ Quiz starting in 5 seconds..."
        )

        await asyncio.sleep(5)

        answer_times = {}

        poll_msg = await bot.send_poll(
            chat_id=callback.message.chat.id,
            question=QUIZ_QUESTION,
            options=QUIZ_OPTIONS,
            type="quiz",
            correct_option_id=CORRECT_OPTION,
            is_anonymous=False,
            open_period=10
        )

        ready_users.clear()

        poll_id = poll_msg.poll.id

        start_time = asyncio.get_event_loop().time()

        await asyncio.sleep(11)

        correct_answer = QUIZ_OPTIONS[CORRECT_OPTION]

        winners = []

        for username, data in answer_times.items():

            answer, response_time = data

            if answer == correct_answer:
                winners.append((username, response_time))

        winners.sort(key=lambda x: x[1])

        result_text = f"""
🏁 The quiz '{QUIZ_QUESTION}' has finished!

1 question answered
"""

        medals = ["🥇", "🥈", "🥉"]

        for i, winner in enumerate(winners[:3]):

            username, response_time = winner

            medal = medals[i] if i < 3 else "🏅"

            result_text += (
                f"\n{medal} @{username} – "
                f"{correct_answer} ({response_time} sec)"
            )

        result_text += "\n\n🏆 Congratulations to the winners!"

        await bot.send_message(
            callback.message.chat.id,
            result_text
        )


# POLL ANSWERS
@dp.poll_answer()
async def poll_answer_handler(poll_answer: types.PollAnswer):

    global answer_times

    user = poll_answer.user

    option_ids = poll_answer.option_ids

    if not option_ids:
        return

    selected = option_ids[0]

    answer = QUIZ_OPTIONS[selected]

    response_time = round(
        asyncio.get_event_loop().time(),
        1
    )

    username = user.username or user.full_name

    answer_times[username] = (
        answer,
        response_time
    )

    # ONLY ADMIN SEES LIVE ANSWERS
    await bot.send_message(
        ADMIN_ID,
        f"👤 {user.full_name} selected: {answer}"
    )


# MAIN
async def main():
    print("Bot running...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
