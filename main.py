import logging
from random import randint

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

ved = 0  # id ведущего
current_word = ""  # текущее загаданное слово

# база слов для игры
with open('crocodile_words.txt', 'r', encoding='utf-8') as f:
    LIST_OF_WORDS = f.read().split('\n')

KEYBOARD_BUTTONS = [
    [
        InlineKeyboardButton("Посмотреть слово", callback_data=str(CHECK))
    ],
    [InlineKeyboardButton("Новое слово", callback_data=str(NEW))]
]
MARKUP = InlineKeyboardMarkup(KEYBOARD_BUTTONS)


def generate_word():
    global current_word
    word_id = randint(0, len(LIST_OF_WORDS) - 1)
    while LIST_OF_WORDS[word_id].lower() == current_word:
        word_id = randint(0, len(LIST_OF_WORDS) - 1)
    current_word = LIST_OF_WORDS[word_id].lower()


async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query.from_user.id == ved.id:
        if current_word == '':
            generate_word()
        await query.answer("•Ваше слово: " + current_word)
    else:
        await query.answer(f'Сейчас ведущий @{ved.username}')
    return 1


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    if query.from_user.id == ved.id:
        generate_word()
        await query.answer("•Ваше слово: " + current_word)
    else:
        await query.answer(f'Сейчас ведущий @{ved.username}')
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


async def current(update, context):
    await update.message.reply_text(
        f"""
            💬 @{ved.username} объясняет слово.
            """, reply_markup=MARKUP)
    return 1


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
    global ved

    keyboard_panel = [["/start", "/stop"],
                      ["/rules", "/help"],
                      ["/rating", "/current"]]

    markup_kb = ReplyKeyboardMarkup(keyboard_panel, one_time_keyboard=False)
    ved = update.effective_user

    await update.message.reply_text(
        """
        ⫸ Игра началась ⫷
        """, reply_markup=markup_kb)
    await update.message.reply_text(
        f"""
        💬 @{ved.username} объясняет слово.
        """, reply_markup=MARKUP)
    return 1


async def stop(update, context):
    global current_word
    current_word = ""

    await update.message.reply_text("⫸ Игра завершена")
    return ConversationHandler.END


async def first_response(update, context):
    global current_word, ved
    text = update.message.text
    if current_word in text:
        await update.message.reply_text(
            f"Правиьно! @{update.effective_user.username} угадал!")
        ved = update.effective_user
        await update.message.reply_text(
            f'Играем дальше! @{update.effective_user.username} ведущий.',
            reply_markup=MARKUP)
        return 2


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("current", current))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, first_response),
                CallbackQueryHandler(new_word, pattern="^" + str(NEW) + "$"),
                CallbackQueryHandler(check_word, pattern="^" + str(CHECK) + "$")],
            2: [MessageHandler(filters.TEXT & ~filters.COMMAND, current)]
        },

        fallbacks=[CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)

    application.run_polling()


if __name__ == '__main__':
    main()
