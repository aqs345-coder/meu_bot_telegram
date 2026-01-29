# flake8: noqa: E501
# type: ignore
import logging
import os
from datetime import datetime

from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          ConversationHandler, MessageHandler, filters)

from handlers import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO)

load_dotenv()

TOKEN = os.getenv('TOKEN')


if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('start', start))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', initiate_register)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
            CONTEUDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_conteudo)],
            OBJETIVOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_objetivos)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
            DIFICULDADES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_dificuldades)],
            ASPECTOS_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_aspectos_positivos)],
            ANEXOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_anexos)],

        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, start))

    print('Iniciando o bot...')
    app.run_polling()
