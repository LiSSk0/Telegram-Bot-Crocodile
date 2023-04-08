import logging
from random import random

from telegram import ReplyKeyboardMarkup
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

CHECK, NEW = range(2)
BOT_TOKEN = "6214547917:AAEqMsPS7rEhzuH4xzugdkHiFYGY1v_LzDs"

v = 0


async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query.from_user.id == v.id:
        await query.answer('слово')
    else:
        await query.answer(f'сейчас ведущий @{v.username}')
    return 1


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query.from_user.id == v.id:
        # word_id = random.randint(0, 100)
        await query.answer('новое слово')
    else:
        await query.answer(f'сейчас ведущий @{v.username}')
    return 1


async def help(update, context):
    await update.message.reply_text("""
    ⫸ Команды бота:
    /help - Помощь по боту
    /rules - Правила игры
    /start - Запуск игры
    /stop - Остановка игры
    /skip - Смена ведущего
    /rating - Рейтинг по чату
    """)


async def rules(update, context):
    await update.message.reply_text("""
    ⫸ Правила игры в крокодила:
    • Есть ведущий и игроки, которые отгадывают слова.
    • После ввода команды /start задача ведущего — нажать кнопку "Посмотреть слово" и объяснить его игрокам, 
    не используя однокоренные слова. Если ведущий не в силах объяснить загаданное слово, его можно сменить, нажав
    кнопку "Следующее слово".
    • Задача игроков — отгадать загаданное слово, для этого нужно написать догадку в чат,
    по одному слову в сообщении.
    • За каждое отгаданное слово игрок получает 2 балла, а тот, кто объяснял - 1 балл.
    • В случае, если нечестный ведущий пишет слово-ответ в чат - с него снимаются 3 балла рейтинга.
    """)


async def start(update, context):
    global v
    keyboard1 = [["/start", "/stop"],
                 ["/rules", "/help"],
                 ["/rating"]]
    keyboard2 = [
        [
            InlineKeyboardButton("Посмотреть слово", callback_data=str(CHECK))
        ],
        [InlineKeyboardButton("Новое слово", callback_data=str(NEW))]
    ]

    markup = ReplyKeyboardMarkup(keyboard1, one_time_keyboard=False)
    reply_markup = InlineKeyboardMarkup(keyboard2)
    v = update.effective_user

    await update.message.reply_text(
        """
        ⫸ Игра началась ⫷
        """, reply_markup=markup)
    await update.message.reply_text(
        f"""
        @{v.username} объясняет слово.
        """, reply_markup=reply_markup)
    return 1


async def first_response(update, context):
    locality = update.message.text
    await update.message.reply_text(f"first response")
    return 2


async def second_response(update, context):
    weather = update.message.text
    logger.info(weather)
    await update.message.reply_text("second response")
    return ConversationHandler.END


async def skip(update, context):
    await update.message.reply_text(
        f"*смена ведущего*")
    return 2


async def stop(update, context):
    await update.message.reply_text("⫸ Игра завершена")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response),
                CallbackQueryHandler(new_word, pattern="^" + str(NEW) + "$"),
                CallbackQueryHandler(check_word, pattern="^" + str(CHECK) + "$")],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)],

        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
