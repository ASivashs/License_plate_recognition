from bot_init import bot
from telebot import types
from tg_bot.bot_func.show_drivers import show_drivers
from recognition.main import graph_usage

dict_machine_data = {'num_machine': '',
                     'name': '',
                     'surname': '',
                     }

@bot.message_handler(commands=["start"])
def tag(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    but_add = types.KeyboardButton("Добавить водителя")
    but_dell = types.KeyboardButton("Удалить водителя по номеру")
    but_show = types.KeyboardButton("Просмотреть водителей")
    markup.add(but_show, but_add, but_dell)
    bot.send_message(message.chat.id, 'Выберите что вам надо', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def tags_use(message):
    match message.text:
        case "Добавить водителя":
            com_add(message)
        case "Просмотреть водителей":
            show_drivers(message)
        case "Удалить водителя по номеру":
            del_driver_start(message)

def com_add(message):
    mes = bot.send_message(message.chat.id, "Введите номер машины")
    bot.register_next_step_handler(mes, get_num)

def get_num(message):
    dict_machine_data['num_machine'] = message.text
    bot.send_message(message.chat.id, "Введите имя водителя")
    bot.register_next_step_handler(message, get_name)

def get_name(message):
    dict_machine_data['name'] = message.text
    bot.send_message(message.chat.id, "Введите фамилию водителя")
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
    if all(dict_machine_data.values()):
        match call.data:
            case "yes":
                if graph_usage.add_num_auto_for_entry(num_auto=dict_machine_data["num_machine"],
                                                      first_name_=dict_machine_data["name"],
                                                      last_name_=dict_machine_data["surname"]):
                    bot.send_message(call.message.chat.id, 'Данные были успешно добавлены!')
                else:

                    bot.send_message(call.message.chat.id,
                                     'Данные не были добавлены, так как такой номер машины уже существует')
            case "no":
                bot.send_message(call.message.chat.id, 'Повторно выберите команду')
    for key in dict_machine_data:
        dict_machine_data[key] = ''


@bot.message_handler(commands=["del"])
def del_driver_start(message):
    bot.send_message(message.from_user.id, "Введите номер машины, который вы хотите удалить")
    bot.register_next_step_handler(message, accept_del)

def accept_del(message):
    driver_num = message.text
    if graph_usage.delete_num_auto_for_entry(driver_num):
        bot.send_message(message.from_user.id, "Номер был успешно удален")
    else:
        bot.send_message(message.from_user.id, "Такого номера не существует")


bot.polling(none_stop=True, interval=0)
