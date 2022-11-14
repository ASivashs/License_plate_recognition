from tg_bot.bot_init import bot
from telebot import types
from recognition.main import graph_usage

dict_machine_data = {'num_machine': '',
                     'name': '',
                     'surname': '',
                     }


@bot.message_handler(commands=["add"])
def com_add(message):
    bot.send_message(message.from_user.id, "Введите номер машины")
    bot.register_next_step_handler(message, get_num)

def get_num(message):
    dict_machine_data['num_machine'] = message.text
    bot.send_message(message.from_user.id, "Введите имя водителя")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    dict_machine_data['name'] = message.text
    bot.send_message(message.from_user.id, "Введите фамилию водителя")
    bot.register_next_step_handler(message, get_surname_and_check)

def get_surname_and_check(message):
    dict_machine_data['surname'] = message.text
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    keyboard.add(key_yes)
    key_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(key_no)
    question = f'Вы хотите добавить следующие данные: \n' \
               f'Номер машины: {dict_machine_data["num_machine"]} \n' \
               f'Имя водителя: {dict_machine_data["name"]} \n' \
               f'Фамилия водителя: {dict_machine_data["surname"]}'
    bot.send_message(message.chat.id, text=question, reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "yes":
        if graph_usage.add_num_auto_for_entry(num_auto=dict_machine_data["num_machine"],
                                              first_name_=dict_machine_data["name"],
                                              last_name_=dict_machine_data["surname"]):
            bot.send_message(call.message.chat.id, 'Данные были успешно добавлены!')
        else:
            bot.send_message(call.message.chat.id,
                             'Данные не были добавлены, так как такой номер машины уже существует')
    if call.data == "no":
        bot.send_message(call.message.chat.id, 'Повторно введите комманду /add')
