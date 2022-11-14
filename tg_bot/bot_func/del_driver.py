from tg_bot.bot_init import bot
from recognition.main import graph_usage

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