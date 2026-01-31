import logging
import os

from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, ConversationHandler, MessageHandler,
                          filters)

from databse import init_db
from handlers import *
from keep_alive import keep_alive
from logger_setup import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    load_dotenv()
    TOKEN = os.getenv('TOKEN')
    keep_alive()

    try:
        init_db()
        logger.error("Banco de dados iniciado com sucesso.")

    except Exception as e:
        logger.error(f"Banco de dados não foi iniciado com sucesso. {e}")

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler('help', help_command))
    app.add_handler(CommandHandler('start', start))
    app.add_handler(MessageHandler(filters.Regex(
        "^📂 Ver Histórico$"), listar_registros))
    app.add_handler(CallbackQueryHandler(
        exibir_detalhe_registro, pattern="^(ver_|voltar_lista)"))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('register', initiate_register),
                      MessageHandler(filters.Regex(
                          "^📝 Registrar Dia$"), initiate_register),
                      CallbackQueryHandler(
                          initiate_register, pattern="^iniciar_registro$"),
                      CallbackQueryHandler(editar_registro_existente, pattern="^editar_")],
        states={
            DATA: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_data)],
            CONTEUDO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_conteudo)],
            OBJETIVOS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_objetivos)],
            DESCRICAO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_descricao)],
            DIFICULDADES: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_dificuldades)],
            ASPECTOS_P: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_aspectos_positivos)],
            HORARIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_horario)],
            LOCAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_local)],
            ATIVIDADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, receber_atividade)],
            ANEXOS: [MessageHandler(filters.PHOTO | filters.Document.ALL, receber_anexos)],
            CONFIRMACAO: [MessageHandler(
                filters.TEXT & ~filters.COMMAND, confirmar_ou_editar)]

        },
        fallbacks=[CommandHandler('cancel', cancel),
                   MessageHandler(filters.Regex("^❌ Cancelar$"), cancel)],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, start))

    print('Iniciando o bot...')
    app.run_polling()
