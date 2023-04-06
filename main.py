import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

BOT_TOKEN = ''


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
    keyboard = [
        [
            InlineKeyboardButton("Правила игры", callback_data='rules_btn'),
            InlineKeyboardButton("Помощь", callback_data="help_btn"),

        ],
        [InlineKeyboardButton("Играть", callback_data="game_btn"),
         InlineKeyboardButton("Конец игры", callback_data="stop_btn"),
         ],
        [InlineKeyboardButton("Пропуск ведущего", callback_data="skip_btn"),
         InlineKeyboardButton("Рейтинг", callback_data="rate_btn"), ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        """
        ⫸ Игра началась. *игрок* объясняет слово.
        """, reply_markup=reply_markup)
    return 1

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query

    await query.answer()
    await query.message.reply_text(text=f"{query.data}")


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
    application.add_handler(CallbackQueryHandler(button))
    application.add_handler(CommandHandler("rules", rules))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, second_response)]
        },

        fallbacks=[CommandHandler('stop', stop), CommandHandler('skip', skip)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
