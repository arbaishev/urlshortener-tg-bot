import json
import logging
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import StatesGroup, State

from misc import dp
from config import SERVER_API_URL
from .keyboards import keyboard_basic, keyboard_shortcode


class ShortenURLStates(StatesGroup):
    waiting_for_URL = State()
    waiting_for_custom_option = State()
    waiting_for_custom_shortcode = State()
    waiting_for_shortcode = State()


@dp.message_handler(commands="short", state="*")
async def cmd_short_step_1(message: types.Message):
    await message.answer("Do you want to create short URL with custom shortcode?", reply_markup=keyboard_shortcode)
    await ShortenURLStates.waiting_for_custom_option.set()


@dp.message_handler(state=ShortenURLStates.waiting_for_custom_option, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_2(message: types.Message, state: FSMContext):
    if message.text.lower() == "yes":
        await message.answer("Send your custom shortcode", reply_markup=types.ReplyKeyboardRemove())
        await ShortenURLStates.waiting_for_custom_shortcode.set()
    else:
        await message.answer("Send your long URL", reply_markup=types.ReplyKeyboardRemove())
        await ShortenURLStates.waiting_for_URL.set()


@dp.message_handler(state=ShortenURLStates.waiting_for_custom_shortcode, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_2_2(message: types.Message, state: FSMContext):
    await state.update_data(custom_shortcode=message.text.lower())
    await message.answer("Send your long URL", reply_markup=types.ReplyKeyboardRemove())
    await ShortenURLStates.waiting_for_URL.set()


@dp.message_handler(state=ShortenURLStates.waiting_for_URL, content_types=types.ContentTypes.TEXT)
async def cmd_short_step_3(message: types.Message, state: FSMContext):
    data = {"url": message.text.lower()}
    user_data = await state.get_data()
    if user_data:
        data["custom"] = "True"
        data["custom_shortcode"] = user_data["custom_shortcode"]

    try:
        response = requests.post(f"{SERVER_API_URL}/short", data=data)
        logging.info(f"Successful request to {SERVER_API_URL}/short with data: {data}")
    except requests.exceptions.RequestException as exc:
        logging.exception(f"Request to {SERVER_API_URL}/short with data: {data} failed.")
        return await message.answer("Something has gone wrong")

    await message.answer(f"Your short URL:\n"
                         f"{json.loads(response.content.decode('utf-8'))['data']['short_url']}",
                         reply_markup=keyboard_basic)
    await state.finish()


@dp.message_handler(commands="stats", state="*")
async def cmd_stats_step_1(message: types.Message):
    await message.answer("Send your shortcode or short URL",
                         reply_markup=types.ReplyKeyboardRemove())
    await ShortenURLStates.waiting_for_shortcode.set()


@dp.message_handler(state=ShortenURLStates.waiting_for_shortcode, content_types=types.ContentTypes.TEXT)
async def cmd_stats_step_2(message: types.Message, state: FSMContext):
    if len(message.text) > 6:
        input_shortcode = message.text[-6::]
    else:
        input_shortcode = message.text
    try:
        response = requests.get(f"{SERVER_API_URL}/stats/{input_shortcode}")
        logging.info(f"Successful request to {SERVER_API_URL}/stats/{input_shortcode}")
    except requests.exceptions.RequestException as exc:
        logging.exception(f"Request to {SERVER_API_URL}/short/{input_shortcode} failed")
        return await message.answer("Something has gone wrong")

    json_obj = json.loads(response.content.decode("utf-8"))
    await message.answer(pretty_json(json_obj), reply_markup=keyboard_basic)
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
