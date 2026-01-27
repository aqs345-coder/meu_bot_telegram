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

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, mensagem_informativa))

    print('Iniciando o bot...')
    app.run_polling()
