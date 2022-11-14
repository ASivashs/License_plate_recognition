from bot_init import bot
from telebot import types
from tg_bot.bot_func.add_driver import com_add
from tg_bot.bot_func.del_driver import del_driver_start
from tg_bot.bot_func.show_drivers import show_drivers

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


bot.polling(none_stop=True, interval=0)
