import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

load_dotenv()

TOKEN = os.getenv('TOKEN')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Olá! Sou seu novo assistente. O que vamos programar hoje?")

if __name__ == '__main__':
    # Substitua 'SEU_TOKEN_AQUI' pelo token do BotFather
    app = ApplicationBuilder().token(TOKEN).build()

    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)

    print("Bot em execução...")
    app.run_polling()
