from recognition.main import graph_usage
from tg_bot.bot_init import bot
from telebot import types

def show_drivers(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Нет доступных водителей" if len(graph_usage.get_all_add_drivers()) == 0
                     else "Список водителей",
                     reply_markup=make_keyboard(graph_usage.get_all_add_drivers()),
                     parse_mode='HTML')


def make_keyboard(list_drivers):
    markup = types.InlineKeyboardMarkup()
    for sub_list in list_drivers:
        dict_name_driver = graph_usage.find_and_choose(str(sub_list[0]))
        markup.add(types.InlineKeyboardButton(
            text=str(sub_list[0]) + " -- " + dict_name_driver["LAST_NAME"] + " " + dict_name_driver["FIRST_NAME"],
            callback_data=sub_list[0]))
    return markup
