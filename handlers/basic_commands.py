from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text

from misc import dp
from .keyboards import keyboard_basic


@dp.message_handler(commands="cancel", state="*")
@dp.message_handler(Text(equals=["отмена", "стоп", "cancel"], ignore_case=True), state="*")
async def cmd_cancel(message: types.Message, state: FSMContext):
    await state.finish()
    await message.answer("The command has been cancelled", reply_markup=keyboard_basic)


@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    await message.reply("Hey, I can shorten your long links. Choose what you want to do",
                        reply_markup=keyboard_basic)


@dp.message_handler(commands=["help"])
async def cmd_help(message: types.Message):
    await message.reply("Available commands:\n"
                        "/short - shorten URL\n"
                        "/stats - get info of URL by shortcode\n"
                        "/cancel - cancel the current operation",
                        reply_markup=types.ReplyKeyboardRemove())





