import asyncio
import datetime
import json
from aiogram import Bot, Dispatcher, executor, types
# методы для форматирования от айограм
from aiogram.utils.markdown import hbold, hunderline, hcode, hlink
# привязка текста и кнопок
from aiogram.dispatcher.filters import Text
from config import token, user_id
from main import check_news_update

# объект бота, + форматирование
bot = Bot(token=token, parse_mode=types.ParseMode.HTML)
# объект диспетчера для управления хендлерами, срабатывающие на текст сообщения от _бот
dp = Dispatcher(bot)

# keyboard
@dp.message_handler(commands="start")
async def start(message: types.Message):
    start_buttons = ["Все новости", "Последние 5 новостей", "Свежие новости"]
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(*start_buttons)

    await message.answer("Лента новостей", reply_markup=keyboard)

# получаем все новости
@dp.message_handler(Text(equals="Все новости"))
async def get_all_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items()):
                 # форматирование времени из юникс форм 
        # news = f"<b>{datetime.datetime.fromtimestamp(v['article_date_timestamp'])}</b>\n" \
        #        f"<u>{v['article_title']}</u>\n" \
        #        f"<code>{v['article_desc']}</code>\n" \
        #        f"{v['article_url']}"

        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"
            #    вшиваем ссылку в текст

        await message.answer(news)


@dp.message_handler(Text(equals="Последние 5 новостей"))
async def get_last_five_news(message: types.Message):
    with open("news_dict.json") as file:
        news_dict = json.load(file)

    for k, v in sorted(news_dict.items())[-5:]:
        news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
               f"{hlink(v['article_title'], v['article_url'])}"

        await message.answer(news)


@dp.message_handler(Text(equals="Свежие новости"))
async def get_fresh_news(message: types.Message):
    fresh_news = check_news_update()
    # проверка на наличие свежих новостей
    if len(fresh_news) >= 1:
        for k, v in sorted(fresh_news.items()):
            news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                   f"{hlink(v['article_title'], v['article_url'])}"

            await message.answer(news)

    else:
        await message.answer("Пока нет свежих новостей...")

# asynsio ассинхронное выполнение цикла, проверка на наличие новых новостей и отображение их в беззвучном режиме
async def news_every_minute():
    while True:
        fresh_news = check_news_update()

        if len(fresh_news) >= 1:
            for k, v in sorted(fresh_news.items()):
                news = f"{hbold(datetime.datetime.fromtimestamp(v['article_date_timestamp']))}\n" \
                       f"{hlink(v['article_title'], v['article_url'])}"

                # get your id @userinfobot
                await bot.send_message(user_id, news, disable_notification=True)

        else:
            await bot.send_message(user_id, "Пока нет свежих новостей...", disable_notification=True)

        # 40 sec
        await asyncio.sleep(40)


if __name__ == '__main__':
    # петля текущего цикла событий
    loop = asyncio.get_event_loop()
    # новая задача
    loop.create_task(news_every_minute())
    executor.start_polling(dp)