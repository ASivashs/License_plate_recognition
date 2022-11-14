import ast
from recognition.main import graph_usage
from tg_bot.bot_init import bot
from telebot import types


@bot.callback_query_handler(func=lambda call: True)
def delete_driver(call):
    if call.data.startswith("['key'"):
        callback_value = ast.literal_eval(call.data)[1]
        graph_usage.delete_num_auto_for_entry(callback_value)
        bot.edit_message_text(chat_id=call.message.chat.id,
                              text="Нет доступных водителей" if len(graph_usage.get_all_add_drivers()) == 0
                              else "Список водителей",
                              message_id=call.message.message_id,
                              reply_markup=make_keyboard(graph_usage.get_all_add_drivers()),
                              parse_mode='HTML')


def show_drivers(message):
    bot.send_message(chat_id=message.chat.id,
                     text="Нет доступных водителей" if len(graph_usage.get_all_add_drivers()) == 0
                     else "Список водителей",
                     reply_markup=make_keyboard(graph_usage.get_all_add_drivers()),
                     parse_mode='HTML')


def make_keyboard(list_drivers):
    cross_icon = u"\u274C"
    markup = types.InlineKeyboardMarkup()
    for sub_list in list_drivers:
        dict_name_driver = graph_usage.find_and_choose(str(sub_list[0]))
        markup.add(types.InlineKeyboardButton(
            text=str(sub_list[0]) + " -- " + dict_name_driver["LAST_NAME"] + " " + dict_name_driver["FIRST_NAME"],
            callback_data=sub_list[0]))
    return markup
