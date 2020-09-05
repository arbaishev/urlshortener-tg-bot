import json

import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from misc import dp
from handlers.basic_commands import keyboard

SERVER_API_URL = "https://django-urlshortener.herokuapp.com/api/"
headers = {
    "Content-Type": "application/json",
}


class ShortenURL(StatesGroup):
    waiting_for_URL = State()
    waiting_for_custom_option = State()
    waiting_for_custom_shortcode = State()
    waiting_for_shortcode = State()


available_options = ["yes", "no"]
keyboard_custom_code = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard_custom_code.row(available_options[0], available_options[1])


@dp.message_handler(commands="short", state="*")
async def cmd_short_step_1(message: types.Message):
    await message.answer("Do you want to create short URL with custom shortcode?", reply_markup=keyboard_custom_code)
    await ShortenURL.waiting_for_custom_option.set()


@dp.message_handler(state=ShortenURL.waiting_for_custom_option, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_2(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        await message.answer("Send your custom shortcode", reply_markup=types.ReplyKeyboardRemove())
        await ShortenURL.waiting_for_custom_shortcode.set()
    else:
        await message.answer("Send your long URL", reply_markup=types.ReplyKeyboardRemove())
        await ShortenURL.waiting_for_URL.set()


@dp.message_handler(state=ShortenURL.waiting_for_custom_shortcode, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_2_2(message: types.Message, state: FSMContext):
    await state.update_data(custom_shortcode=message.text.lower())
    await message.answer("Send your long URL", reply_markup=types.ReplyKeyboardRemove())
    await ShortenURL.waiting_for_URL.set()


@dp.message_handler(state=ShortenURL.waiting_for_URL, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_3(message: types.Message, state: FSMContext):
    data = {"url": message.text.lower()}
    user_data = await state.get_data()
    if user_data:
        data["custom"] = "True"
        data["custom_shortcode"] = user_data["custom_shortcode"]

    try:
        response = requests.post(f"{SERVER_API_URL}short", data=data)
    except requests.exceptions.RequestException:
        return await message.answer("Something has gone wrong")

    await message.answer(f"Your short URL:\n"
                         f"{json.loads(response.content.decode('utf-8'))['data']['short_url']}")
    await message.answer("You can create a new one or get stats of existing short URL", reply_markup=keyboard)
    await state.finish()


@dp.message_handler(commands="stats", state="*")
async def cmd_stats_step_1(message: types.Message):
    await message.answer("Send your shortcode or short URL",
                         reply_markup=types.ReplyKeyboardRemove())
    await ShortenURL.waiting_for_shortcode.set()


@dp.message_handler(state=ShortenURL.waiting_for_shortcode, content_types=types.ContentTypes.TEXT)
async def cmd_stats_step_2(message: types.Message, state: FSMContext):
    if len(message.text) > 6:
        input_text = message.text[-6::]
    else:
        input_text = message.text
    try:
        response = requests.get(f"{SERVER_API_URL}stats/{input_text}")
    except requests.exceptions.RequestException:
        return await message.answer("Something has gone wrong")

    json_obj = json.loads(response.content.decode("utf-8"))
    await message.answer(pretty_json(json_obj), reply_markup=keyboard)
    await state.finish()


def pretty_json(json_string):
    json_data = json_string["data"]
    json_error = json_string["error"]
    if json_data:
        output = f"Full URL: {json_data['url']}\n" \
                 f"Shortcode: {json_data['shortcode']}\n" \
                 f"Created: {json_data['created']}\n" \
                 f"Last used: {json_data['recently_used']}\n" \
                 f"Number of uses: {json_data['clicks']}"
        return output
    else:
        return json_error
