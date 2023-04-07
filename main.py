import logging

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)

logger = logging.getLogger(__name__)

RULES, HELP, START_GAME, STOP, SKIP, RATE = range(6)
BOT_TOKEN = "6214547917:AAEqMsPS7rEhzuH4xzugdkHiFYGY1v_LzDs"


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text("""
    ⫸ Команды бота:
    /help - Помощь по боту
    /rules - Правила игры
    /start - Запуск игры
    /stop - Остановка игры
    /skip - Смена ведущего
    /rating - Рейтинг по чату
    """)


async def rules(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text("""
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
    return 1


async def start(update, context):
    keyboard = [
        [
            InlineKeyboardButton("Правила игры", callback_data=str(RULES)),
            InlineKeyboardButton("Помощь", callback_data=str(HELP)),

        ],
        [InlineKeyboardButton("Играть", callback_data=str(START_GAME)),
         InlineKeyboardButton("Конец игры", callback_data=str(STOP)),
         ],
        [InlineKeyboardButton("Пропуск ведущего", callback_data=str(SKIP)),
         InlineKeyboardButton("Рейтинг", callback_data=str(RATE))]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        """
        ⫸ Игра началась. *игрок* объясняет слово.
        """, reply_markup=reply_markup, )
    return 1


async def game(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text("""
    ⫸ game started""")
    return 1


async def rate(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text(
        f"*вывод рейтинга*")
    return 2


async def skip(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text(
        f"*смена ведущего*")
    return 2


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.message.reply_text("⫸ Игра завершена")
    return ConversationHandler.END


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [
                CallbackQueryHandler(rules, pattern="^" + str(RULES) + "$"),
                CallbackQueryHandler(help, pattern="^" + str(HELP) + "$"),
                CallbackQueryHandler(game, pattern="^" + str(START_GAME) + "$"),
                # CallbackQueryHandler(skip, pattern="^" + str(SKIP) + "$"),
                CallbackQueryHandler(stop, pattern="^" + str(STOP) + "$"),
                # CallbackQueryHandler(rate, pattern="^" + str(RATE) + "$"),

                # CallbackQueryHandler(three, pattern="^" + str(THREE) + "$"),
                # CallbackQueryHandler(four, pattern="^" + str(FOUR) + "$"),
            ],
            # 1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response)],
            # 2: []
        },

        fallbacks=[CommandHandler('stop', stop), CommandHandler('skip', skip)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
