import logging
import sys

from orm_stuff import create_chat, change_started, \
    change_ved, change_word, get_info, score_updates, get_user_info, top_5_players, \
    get_user_score, active_chat_players_get, \
    active_chat_players_add, active_chat_players_remove, create_rating, \
    active_chat_players_clean
from game_funcs import generate_word, help, rules
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, \
    ConversationHandler, ContextTypes, CallbackQueryHandler

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG
)
logger = logging.getLogger(__name__)

CHECK, NEW, CHANGE = 0, 1, 2
try:
    with open('data/bot_token.txt', 'r', encoding='utf-8') as f:
        BOT_TOKEN = f.readline().strip()
except Exception:
    print("Не найден токен бота по адресу data/bot_token.txt")
    sys.exit()


# кнопки для чата
BUTTONS = [
    [
        InlineKeyboardButton("Посмотреть слово", callback_data=str(CHECK))
    ],
    [InlineKeyboardButton("Новое слово", callback_data=str(NEW))]
]
MARKUP = InlineKeyboardMarkup(BUTTONS)
BUTTON_SKIP = [
    [
        InlineKeyboardButton("Я ВЕДУЩИЙ!", callback_data=str(CHANGE))
    ]]
MARKUP_SKIP = InlineKeyboardMarkup(BUTTON_SKIP)


async def check_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    is_started, ved, current_word = get_info(chat_id)

    if is_started:
        if ved != '':
            if query.from_user.id == ved:
                if current_word == '':
                    current_word = generate_word(current_word)
                    change_word(chat_id, current_word)
                await query.answer("•Ваше слово: " + current_word)
            else:
                ved_info = get_user_info(ved, chat_id)
                await query.answer(f'•Сейчас ведущий {ved_info[2]}')
            return 1
        else:
            await update.message.reply_text(
                f'⚠ Для игры нужен ведущий.')
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def new_word(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    is_started, ved, current_word = get_info(chat_id)
    if is_started:
        if ved != '':
            ved_info = get_user_info(ved, chat_id)
            if query.from_user.id == ved_info[0]:
                current_word = generate_word(current_word)
                change_word(chat_id, current_word)
                await query.answer("•Ваше слово: " + current_word)
            else:
                await query.answer("•Сейчас ведущий " + ved_info[2])
            return 1
        else:
            await query.message.reply_text(
                f'⚠ Для игры нужен ведущий.')
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def current(update, context):
    chat_id = update.message.chat_id

    is_started, ved, current_word = get_info(chat_id)
    if is_started:
        if ved != '':
            ved_info = get_user_info(ved, chat_id)
            await update.message.reply_text(f'💬 @{ved_info[2]} объясняет слово.',
                                            reply_markup=MARKUP)
            return 1
        else:
            await update.message.reply_text(
                f'⚠ Для игры нужен ведущий.')
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def play(update, context):
    chat_id = update.message.chat_id
    is_started, ved, current_word = get_info(chat_id)
    if is_started:
        user = update.effective_user
        players = active_chat_players_get(chat_id)
        if user.id in players:
            await update.message.reply_text('•Вы уже в игре.')
        else:
            score_updates(user.id, 0, user.username, chat_id)
            await update.message.reply_text(f'⫸ @{user.username} теперь в игре! ⫷')

            if len(players) == 0:
                change_ved(chat_id, user.id)
                current_word = generate_word(current_word)
                change_word(chat_id, current_word)
                await update.message.reply_text(f'💬 @{user.username} объясняет слово.',
                                                reply_markup=MARKUP)
            active_chat_players_add(chat_id, user.id)
            return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def end(update, context):
    # попадает только если user уже вступал в игру по команде /play,
    # поэтому проверка нахождения в игре не требуется
    chat_id = update.message.chat_id
    user = update.effective_user
    if user.id == get_info(chat_id)[1]:
        change_ved(chat_id, '')
        await update.message.reply_text(f'⫸ Ведущий @{user.username} вышел из игры. ⫷')
        active_chat_players_remove(chat_id, user.id)
    else:
        await update.message.reply_text(f'⫸ @{user.username} вышел из игры. ⫷')
        active_chat_players_remove(chat_id, user.id)
    return ConversationHandler.END


async def response(update, context):
    chat_id = update.message.chat_id
    is_started, ved, current_word = get_info(chat_id)

    if is_started:
        if ved == '':
            await update.message.reply_text(
                f'⚠ Для игры нужен ведущий.')
        else:
            text = update.message.text.lower()
            user = update.effective_user
            ved_info = get_user_info(ved, chat_id)
            if user.id == ved_info[0]:
                if current_word in text:
                    await update.message.reply_text(
                        f"🌟 Ведущий @{user.username} написал ответ в чат, -3 балла.")
                    score_updates(ved_info[0], -3, ved_info[2], chat_id)

                    generated_word = generate_word(current_word)
                    change_word(chat_id, generated_word)

                    await update.message.reply_text(
                        f'🌟 Играем дальше, @{user.username} ведущий.',
                        reply_markup=MARKUP)

                    return 1
            else:
                if current_word == text:
                    await update.message.reply_text(
                        f"🌟 Правильно! @{user.username} даёт правильный ответ - {current_word}.\n" +
                        f"@{user.username} +2 балла.\n@{ved_info[2]} +1 балл.")
                    score_updates(ved_info[0], 1, ved_info[2], chat_id)
                    score_updates(user.id, 2, user.username, chat_id)

                    change_ved(chat_id, user.id)

                    generated_word = generate_word(current_word)
                    change_word(chat_id, generated_word)

                    await update.message.reply_text(
                        f'🌟 Играем дальше, @{user.username} ведущий.',
                        reply_markup=MARKUP)

                    return 1
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def new_ved(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    chat_id = query.message.chat_id
    is_started, ved, current_word = get_info(chat_id)
    if is_started and ved == '':
        change_ved(chat_id, query.from_user.id)
        current_word = generate_word(current_word)
        change_word(chat_id, current_word)
        await query.answer(f"Новый ведущий - {query.from_user.username}")
        await query.message.reply_text(f'💬 @{query.from_user.username} объясняет слово.',
                                       reply_markup=MARKUP)
        return 1
    else:
        ved_info = get_user_info(ved, chat_id)
        await query.answer(f"Ведущий - {ved_info[2]}")


async def skip(update, context):
    chat_id = update.message.chat_id
    is_started, ved, current_word = get_info(chat_id)
    if is_started:
        change_ved(chat_id, '')
        await update.message.reply_text(
            f'🚨 Смена ведущего:',
            reply_markup=MARKUP_SKIP)
    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def scoring(update, context):
    chat_id = update.message.chat_id
    is_started, ved, current_word = get_info(chat_id)

    if is_started:
        score = get_user_score(update.effective_user.id, chat_id, update.effective_user.username, 0)
        if score != 0:
            await update.message.reply_text(f'•Твои баллы: {score}')
        else:
            await update.message.reply_text(f'•У тебя 0 баллов')
        top = top_5_players(chat_id)
        if len(top) == 0:
            a = '•Рейтинг пуст.'
        else:
            a = f'•Текущий топ игроков:\n\n'
            a += '\n'.join([f'@{i[0]}: {i[1]}' for i in top])
        await update.message.reply_text(a)

    else:
        await update.message.reply_text("•Для подключения бота к чату введите /start")


async def start(update, context):
    chat_type = update.message.chat.type
    if chat_type in ['group', 'supergroup']:
        chat_id = update.message.chat_id
        is_started, ved, current_word = get_info(chat_id)
        if is_started:
            await update.message.reply_text("•Бот уже подключён. Чтобы вступить в игру отправьте /play")
        else:
            create_chat(chat_id, True, '')
            await update.message.reply_text("•Бот успешно подключён. Чтобы вступить в игру отправьте /play")
            await context.bot.sendPhoto(chat_id, (open("data/croco_pic_start.jpg", "rb")))

    else:
        await update.message.reply_text(
            "👽 Добавьте Крокодила в группу и начинайте игру 👽")


async def stop(update, context):
    chat_id = update.message.chat_id
    is_started, ved, current_word = get_info(chat_id)

    if is_started:
        change_started(chat_id, False)
        change_ved(chat_id, '')
        active_chat_players_clean(chat_id)
        await update.message.reply_text("•Бот успешно отключён.")
    else:
        await update.message.reply_text("•Бот уже отключён.")


def main():
    application = Application.builder().token(BOT_TOKEN).build()

    application.add_handler(CommandHandler("help", help))
    application.add_handler(CommandHandler("rules", rules))
    application.add_handler(CommandHandler("current", current))
    application.add_handler(CommandHandler("rating", scoring))
    application.add_handler(CommandHandler("skip", skip))

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stop", stop))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('play', play)],

        states={
            1: [MessageHandler(filters.TEXT & ~filters.COMMAND, response),
                CallbackQueryHandler(new_word, pattern="^" + str(NEW) + "$"),
                CallbackQueryHandler(check_word, pattern="^" + str(CHECK) + "$"),
                CallbackQueryHandler(new_ved, pattern="^" + str(CHANGE) + "$")
                ]
        },

        fallbacks=[CommandHandler('end', end), CommandHandler('stop', stop)]
    )

    application.add_handler(conv_handler)
    application.run_polling()


if __name__ == '__main__':
    main()

