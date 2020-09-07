from aiogram import types

available_commands = {"basic_short": "/short", "basic_stats": "/stats",
                      "custom_shortcode_positive": "yes", "custom_shortcode_negative": "no"}

keyboard_basic = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard_basic.row(available_commands["basic_short"], available_commands["basic_stats"])

keyboard_shortcode = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
keyboard_shortcode.row(available_commands["custom_shortcode_positive"],
                       available_commands["custom_shortcode_negative"])
