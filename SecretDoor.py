from lxml.html import fromstring
import requests
import re
from bs4 import BeautifulSoup
from googlesearch import search as go_search
import inspect

# aiogram stuff
from aiogram import types, Dispatcher, Bot
from aiogram.dispatcher import Dispatcher, FSMContext 
from aiogram.utils import executor
from aiogram.utils.helper import Helper, ListItem
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardRemove
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.utils.exceptions import BotBlocked

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

headers = {"User-Agent":"Opera/9.80 (J2ME/MIDP; Opera Mini/9.80 (S60; SymbOS; Opera Mobi/23.334; U; id) Presto/2.5.25 Version/10.54"}

dp = Dispatcher(bot = bot, storage = MemoryStorage())

def im_at() -> None:
    print(f"I'm at {inspect.currentframe().f_back.f_lineno}!")


def search_dork(query: str) -> list:
    im_at()
    urls = go_search(f"t.me/joinchat {query}", num_results=50)
    for url in urls:
        try:
            im_at()
            req = requests.get(url, headers=headers)
            res = fromstring(req.content)
            string = res.findtext(".//title")
            im_at()
            return string
        except Exception as e:
            im_at()
            print(f"Exception occured! details: {e}")
    

def extract_results(link: str) -> list:
    response = requests.get(link).text
    result_divs = BeautifulSoup(response, 'lxml').find_all('div', class_='g')
    links = []
    for div in result_divs:
        links.append(re.search(r'(?:href\=")(.+?)(?:")', BeautifulSoup(div, 'lxml').find('a')).group(1))
    return links

@dp.message_handler(text='/start')
async def start(m: types.Message):
  im_at()
  try:
    await m.answer(r"""Привет Странник, я найду для тебя приватные группы и каналы\nТы можешь использовать клавиатуру""",
                    reply_markup = bots)
  except BotBlocked:
      pass


@dp.callback_query_handler(text="help")
async def help(call: types.CallbackQuery):
    im_at()
    await call.message.answer(r"""🤖 Бот помогает с поиском частных телеграм каналов по знаменитым ресурсам облегчая вам работу""", reply_markup=bots)


@dp.callback_query_handler(text="search")
async def search(call: types.CallbackQuery):
    im_at()
    await call.message.answer(r'Окей, введи интересующую тебя тему и я постараюсь найти для тебя приватные каналы/группы\.\n'
    'Для отмены \> /cancel', reply_markup=bots)
    await google_search.key_Word.set()

@dp.message_handler(state = google_search.key_Word)
async def id(m: types.Message, state: FSMContext):
  im_at()
  text = m.text
  await state.update_data(text1 = text)

  if text == '/cancel':
    im_at()
    await m.answer(r'Отменено', reply_markup=bots)
    await state.finish()
  else:
    # await m.answer(f"""Все что удалось найти\.\.\.\n
    #                    google\.com/search\?q\=site:t\.me/joinchat\+{text}\n
    #                    yandex\.uz/search/\?text\=site\%3At\.me%2Fjoinchat\+{text}""", reply_markup=bots)
    await m.answer(r"Запускаю поиск\.\.")
    im_at()
    ##TODO Implement extraction of the results
    # result_list = []
    # for i in range(100): # arbitrary range - might changes
    #     google_link = f"google.com/search?q=site:t.me/joinchat+{text}&start={i}"
    #     result_list.append(extract_results(google_link))
    # await m.answer(f"result_list: {result_list[:20]}")
    result = search_dork(text)
    im_at()
    print(result)


    await state.finish()

if __name__ == '__main__':
    print("Starting...")
    im_at()
    executor.start_polling(dp)