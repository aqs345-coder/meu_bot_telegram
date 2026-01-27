# flake8: noqa: E501

import logging
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

logging.basicConfig(level=logging.INFO)

TOKEN = 'YOUR_TOKEN_HERE'


def start(update, context):
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Olá, eu sou o seu bot de tarefas!')


def add_task(update, context):
    task = ' '.join(context.args)
    with open('tasks.txt', 'a') as file:
        file.write(task + '\n')
    context.bot.send_message(
        chat_id=update.effective_chat.id, text='Tarefa adicionada com sucesso!')


def list_tasks(update, context):
    with open('tasks.txt', 'r') as file:
        tasks = file.readlines()
    context.bot.send_message(chat_id=update.effective_chat.id, text='\n'.join(
        [task.strip() for task in tasks]))


def main():
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start))
    dp.add_handler(CommandHandler('add', add_task))
    dp.add_handler(CommandHandler('list', list_tasks))

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
