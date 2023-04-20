import logging
import sqlite3

from rating_funcs import clean_db, top_5_players, score_updates
from game_funcs import generate_word, help, rules

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Chat
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

CHAT_ID = "" # id чата
CHECK, NEW = range(2)
DB_NAME = 'data/crocodile.db'
BOT_TOKEN = ""

ved = 0  # id ведущего
current_word = ""  # текущее загаданное слово
is_started = False
active_players = []

# кнопки для чата
BUTTONS = [
    [
        InlineKeyboardButton("Посмотреть слово", callback_data=str(CHECK))
    ],
    [InlineKeyboardButton("Новое слово", callback_data=str(NEW))]
]
MARKUP = InlineKeyboardMarkup(BUTTONS)


async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global current_word

    if is_started:
        query = update.callback_query
        if query.from_user.id == ved.id:
            if current_word == '':
                generated_word = generate_word(current_word)
                current_word = generated_word
            await query.answer("•Ваше слово: " + current_word)
        else:
            await query.answer(f'•Сейчас ведущий @{ved.username}')
    return 1


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    global current_word

    if is_started:
        query = update.callback_query
        if query.from_user.id == ved.id:
            generated_word = generate_word(current_word)
            current_word = generated_word
            await query.answer("•Ваше слово: " + current_word)
        else:
            await query.answer("•Сейчас ведущий @" + ved.username)
        return 1


async def current(update, context):
    if is_started:
        await update.message.reply_text(f'💬 @{ved.username} объясняет слово.',
                                        reply_markup=MARKUP)
        return 1


async def play(update, context):
    global ved, is_started

    user = update.effective_user

    if user.id in active_players:
        await update.message.reply_text('•Вы уже в игре.')
    else:
        await update.message.reply_text(f'⫸ @{user.username} теперь в игре! ⫷')

        if len(active_players) == 0:
            is_started = True  # ???
            ved = update.effective_user
            await update.message.reply_text(f'💬 @{ved.username} объясняет слово.',
                                            reply_markup=MARKUP)
        active_players.append(user.id)

        return 1


async def start(update, context):
    global CHAT_ID
    CHAT_ID = update.message.chat_id


async def end(update, context):
    # попадает только если user уже вступал в игру по команде /play,
    # поэтому проверка нахождения в игре не требуется

    user = update.effective_user

    # if user.id in active_players:
    await update.message.reply_text(f'⫸ @{user.username} вышел из игры. ⫷')
    active_players.remove(user.id)
    # else:
    #    await update.message.reply_text('•Вы не в игре.')

    return ConversationHandler.END


async def response(update, context):
    global current_word, ved, CHAT_ID

    text = update.message.text.lower()
    user = update.effective_user
    if current_word in text:
        if user == ved:
            await update.message.reply_text(
                f"🌟 Ведущий @{user.username} написал ответ в чат, -3 балла.")
            score_updates(DB_NAME, user.id, -3, user.username, CHAT_ID)
        else:
            await update.message.reply_text(
                f"🌟 Правильно! @{user.username} даёт правильный ответ - {current_word}.\n" +
                f"@{user.username} +2 балла.\n@{ved.username} +1 балл.")
            score_updates(DB_NAME, ved.id, 1, ved.username, CHAT_ID)
            score_updates(DB_NAME, user.id, 2, user.username, CHAT_ID)
            ved = user

        generated_word = generate_word(current_word)
        current_word = generated_word

        await update.message.reply_text(
            f'🌟 Играем дальше, @{user.username} ведущий.',
            reply_markup=MARKUP)

        return 1


async def scoring(update, context):
    con = sqlite3.connect(DB_NAME)
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM rating WHERE (userid = (?) and chat_id = (?))",
                (update.effective_user.id, CHAT_ID))

    if cur.fetchone()[0] > 0:
        cur.execute("SELECT score FROM rating WHERE userid = (?)",
                    (update.effective_user.id,))
        await update.message.reply_text(f'•У тебя {cur.fetchone()[0]} баллов')
    else:
        cur.execute("INSERT INTO rating (userid, score, username, chat_id) VALUES (?, ?, ?, ?)",
                    (update.effective_user.id, 0, update.effective_user.username, CHAT_ID))
        await update.message.reply_text(f'•У тебя 0 баллов')

    top = top_5_players(DB_NAME)
    if len(top) == 0:
        a = 'Рейтинг пуст.'
    else:
        a = f'Текущий топ игроков:\n\n'
        a += '\n'.join([f'@{i[0]}: {i[1]}' for i in top])
    await update.message.reply_text(a)

    con.commit()
    cur.close()


#
# def start(update):
#     db_create()
#     if is_started:
#         "бб игра уже есть"


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("current", current))
    application.add_handler(CommandHandler("rating", scoring))
    application.add_handler(CommandHandler("start", start))


    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('play', play)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, response),
                CallbackQueryHandler(new_word, pattern="^" + str(NEW) + "$"),
                CallbackQueryHandler(check_word, pattern="^" + str(CHECK) + "$")]
        },

        fallbacks=[CommandHandler('end', end)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
