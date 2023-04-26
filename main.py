import logging
import sqlite3
from orm_stuff import create_chat, get_info_started, get_info_ved, change_started, \
    change_ved, change_word, get_info_word

from rating_funcs import clean_db, top_5_players, score_updates, get_user_info
from game_funcs import generate_word, help, rules

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, Chat
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

CHECK, NEW = 0, 1
DB_NAME = 'data/crocodile.db'
BOT_TOKEN = "6214547917:AAEqMsPS7rEhzuH4xzugdkHiFYGY1v_LzDs"

#chat_id = ""  # id чата
active_players = {}

# кнопки для чата
BUTTONS = [
    [
        InlineKeyboardButton("Посмотреть слово", callback_data=str(CHECK))
    ],
    [InlineKeyboardButton("Новое слово", callback_data=str(NEW))]
]
MARKUP = InlineKeyboardMarkup(BUTTONS)


async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    is_started = get_info_started(chat_id)
    if is_started:
        current_word = get_info_word(chat_id)
        ved = get_info_ved(chat_id)
        ved_info = get_user_info(DB_NAME, ved, chat_id)
        if query.from_user.id == ved_info[0]:
            if current_word == '':
                current_word = generate_word(current_word)
                change_word(chat_id, current_word)
            await query.answer("•Ваше слово: " + current_word)
        else:
            print(query.from_user.id, ved_info[4])
            await query.answer(f'•Сейчас ведущий {ved_info[2]}')
        return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    is_started = get_info_started(chat_id)

    if is_started:
        current_word = get_info_word(chat_id)
        ved = get_info_ved(chat_id)
        ved_info = get_user_info(DB_NAME, ved, chat_id)
        if query.from_user.id == ved_info[0]:
            current_word = generate_word(current_word)
            change_word(chat_id, current_word)
            await query.answer("•Ваше слово: " + current_word)
        else:
            await query.answer("•Сейчас ведущий " + ved_info[2])
        return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def current(update, context):
    chat_id = update.message.chat_id

    is_started = get_info_started(chat_id)
    ved = get_info_ved(chat_id)
    ved_info = get_user_info(DB_NAME, ved, chat_id)


    if is_started:
        await update.message.reply_text(f'💬 @{ved_info[2]} объясняет слово.',
                                        reply_markup=MARKUP)
        return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def play(update, context):
    chat_id = update.message.chat_id
    is_started = get_info_started(chat_id)

    if is_started:
        user = update.effective_user

        if user.id in active_players:
            await update.message.reply_text('•Вы уже в игре.')
        else:
            await update.message.reply_text(f'⫸ @{user.username} теперь в игре! ⫷')
            await context.bot.sendPhoto(chat_id, (open("data/croco_pic.png", "rb")))

            if chat_id not in active_players:
                score_updates(DB_NAME, user.id, 1, user.username, chat_id)
                change_ved(chat_id, user.id)
                await update.message.reply_text(f'💬 @{user.username} объясняет слово.',
                                                reply_markup=MARKUP)
                active_players[chat_id] = []
            m = active_players[chat_id]
            m.append(user.id)
            active_players[chat_id] = m

            return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def end(update, context):
    # попадает только если user уже вступал в игру по команде /play,
    # поэтому проверка нахождения в игре не требуется
    chat_id = update.message.chat_id
    user = update.effective_user

    await update.message.reply_text(f'⫸ @{user.username} вышел из игры. ⫷')
    active_players[chat_id].remove(user.id)

    return ConversationHandler.END


async def response(update, context):
    chat_id = update.message.chat_id
    current_word = get_info_word(chat_id)
    ved = get_info_ved(chat_id)

    if get_info_started(chat_id):
        text = update.message.text.lower()
        user = update.effective_user
        ved_info = get_user_info(DB_NAME, ved, chat_id)
        if current_word in text:
            if user.id == ved_info[0]:
                await update.message.reply_text(
                    f"🌟 Ведущий @{user.username} написал ответ в чат, -3 балла.")
                score_updates(DB_NAME, user.id, -3, user.username, chat_id)

            else:
                await update.message.reply_text(
                    f"🌟 Правильно! @{user.username} даёт правильный ответ - {current_word}.\n" +
                    f"@{user.username} +2 балла.\n@{ved_info[2]} +1 балл.")
                score_updates(DB_NAME, ved_info[0], 1, ved_info[2], chat_id)
                score_updates(DB_NAME, user.id, 2, user.username, chat_id)

                change_ved(chat_id, user.id)

            generated_word = generate_word(current_word)
            change_word(chat_id, generated_word)

            await update.message.reply_text(
                f'🌟 Играем дальше, @{user.username} ведущий.',
                reply_markup=MARKUP)

            return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def scoring(update, context):
    chat_id = update.message.chat_id

    if get_info_started(chat_id):
        con = sqlite3.connect(DB_NAME)
        cur = con.cursor()
        cur.execute("SELECT COUNT(*) FROM rating WHERE (userid = (?) and chat_id = (?))",
                    (update.effective_user.id, chat_id))

        if cur.fetchone()[0] > 0:
            cur.execute("SELECT score FROM rating WHERE userid = (?)",
                        (update.effective_user.id,))
            await update.message.reply_text(f'•У тебя {cur.fetchone()[0]} баллов')
        else:
            cur.execute("INSERT INTO rating (userid, score, username, chat_id) VALUES (?, ?, ?, ?)",
                        (update.effective_user.id, 0, update.effective_user.username, chat_id))
            await update.message.reply_text(f'•У тебя 0 баллов')

        top = top_5_players(DB_NAME)
        if len(top) == 0:
            a = '•Рейтинг пуст.'
        else:
            a = f'•Текущий топ игроков:\n\n'
            a += '\n'.join([f'@{i[0]}: {i[1]}' for i in top])
        await update.message.reply_text(a)

        con.commit()
        cur.close()
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def start(update, context):
    chat_type = update.message.chat.type
    if chat_type in ['group', 'supergroup']:
        chat_id = update.message.chat_id

        if get_info_started(chat_id):
            await update.message.reply_text("•Бот уже подключён. Чтобы вступить в игру отправьте /play")
        else:
            create_chat(chat_id, True, '')
            await update.message.reply_text("•Бот успешно подключён. Чтобы вступить в игру отправьте /play")
    else:
        await update.message.reply_text(
            "👽 Добавьте Крокодила в группу и начинайте игру 👽")


async def stop(update, context):
    global chat_id
    if get_info_started(chat_id):
        change_started(chat_id, False)
        # change_word(chat_id, "".join([str(randint(0, 10)) for _ in range(25)]))  # создает рандомный ключ
        await update.message.reply_text("•Бот успешно отключён. Для выхода из игры отправьте /end")
    else:
        await update.message.reply_text("•Бот уже отключён.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("current", current))
    application.add_handler(CommandHandler("rating", scoring))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('play', play)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, response),
                CallbackQueryHandler(new_word, pattern="^" + str(NEW) + "$"),
                CallbackQueryHandler(check_word, pattern="^" + str(CHECK) + "$")]
        },

        fallbacks=[CommandHandler('end', end), CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()
