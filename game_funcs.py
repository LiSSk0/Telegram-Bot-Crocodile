from random import randint


# база слов для игры
with open('data/crocodile_words.txt', 'r', encoding='utf-8') as f:
    LIST_OF_WORDS = f.read().split('\n')


def generate_word(cur_word):
    word_id = randint(0, len(LIST_OF_WORDS) - 1)

    while LIST_OF_WORDS[word_id].lower() == cur_word:
        word_id = randint(0, len(LIST_OF_WORDS) - 1)
    cur_word = LIST_OF_WORDS[word_id].lower()

    return cur_word


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