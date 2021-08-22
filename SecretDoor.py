import requests
import re
from bs4 import BeautifulSoup

# aiogram stuff
from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import Dispatcher, FSMContext 
from aiogram.utils import executor
from aiogram.utils.helper import Helper, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup

try:
    from _config import token
    bot = Bot(token = token, parse_mode='MarkdownV2')
except ModuleNotFoundError:
    token = input("_config.py is absent, enter your token here: ")
    try:
        bot = Bot(token = token, parse_mode='MarkdownV2')
    except Exception as e:
        print(f"Invalid token! Error: {e}")

class google_search(StatesGroup):
  key_Word = State()

bots = InlineKeyboardMarkup()
btn1 = InlineKeyboardButton(text = '❔ Помощь', callback_data='help')
btn2 = InlineKeyboardButton(text = '🔎 Начать поиск', callback_data='search')
bots.add(btn1)
bots.add(btn2)

dp = Dispatcher(bot = bot, storage = MemoryStorage())

def extract_results(link: str) -> list:
    response = requests.get(link).text
    result_divs = BeautifulSoup(response, 'lxml').find_all('div', class_='g')
    links = []
    for div in result_divs:
        links.append(re.search(r'(?:href\=")(.+?)(?:")', BeautifulSoup(div, 'lxml').find('a')).group(1))
    return links

@dp.message_handler(text='/start')
async def start(m: types.Message):
  await m.answer('Привет Странник, я найду для тебя приватные группы и каналы\n'
'Ты можешь использовать клавиатуру',
reply_markup = bots)

@dp.callback_query_handler(text="help")
async def help(call: types.CallbackQuery):
    await call.message.answer('🤖 Бот помогает с поиском частных телеграм каналов по знаменитым ресурсам облегчая вам работу\n\n'
'**Мелкая справка:**\n'
'Если вам нужно найти канал с названием больше одного слова, вместо пробела ставьте "\+"\.', reply_markup=bots)


@dp.callback_query_handler(text="search")
async def search(call: types.CallbackQuery):
    await call.message.answer('Окей, введи интересующую тебя тему и я постараюсь найти для тебя приватные каналы/группы\.\n'
    'Для отмены \> /cancel', reply_markup=bots)
    await google_search.key_Word.set()

@dp.message_handler(state = google_search.key_Word)
async def id(m: types.Message, state: FSMContext):
  text = m.text
  await state.update_data(text1 = text)

  if text == '/cancel':
    await m.answer('Отмененно', reply_markup=bots)
    await state.finish()
  else:
    # await m.answer(f"""Все что удалось найти\.\.\.\n
    #                    google\.com/search\?q\=site:t\.me/joinchat\+{text}\n
    #                    yandex\.uz/search/\?text\=site\%3At\.me%2Fjoinchat\+{text}""", reply_markup=bots)
    await m.answer("Запускаю поиск..")
    ##TODO Implement extraction of the results
    result_list = []
    for i in range(100): # arbitrary range - might changes
        google_link = f"google.com/search?q=site:t.me/joinchat+{text}&start={i}"
        result_list.append(extract_results(google_link))
    await m.answer(f"result_list: {result_list[:20]}")
    await state.finish()

if __name__ == '__main__':
    print("Starting...")
    executor.start_polling(dp)