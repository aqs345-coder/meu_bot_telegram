
import asyncio
import csv
import io
import logging
import os
import tempfile
import time
import zipfile
from datetime import datetime

import cloudinary
import cloudinary.uploader
import requests
from docx.shared import Mm
from docxtpl import DocxTemplate, InlineImage
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from constants import (
    ANEXOS,
    ASPECTOS_P,
    ATIVIDADE,
    ATIVIDADE_PADRAO,
    CONFIRMACAO,
    CONTEUDO,
    DATA,
    DESCRICAO,
    DIFICULDADES,
    HORARIO,
    HORARIO_PADRAO,
    LOCAL,
    LOCAL_PADRAO,
    MSG_BOAS_VINDAS,
    MSG_HELP,
    MSG_START,
    OBJETIVOS,
    ROTAS,
    SQL,
    SQL_UPDATE,
    TECLADO_CANCELAR,
    TECLADO_CONFIRMACAO,
    TECLADO_INICIAL,
)
from database import get_connection

logger = logging.getLogger(__name__)

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


def get_botao_cancelar():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("❌ Cancelar", callback_data="cancelar_registro")]
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=MSG_BOAS_VINDAS,
        parse_mode='Markdown',
        reply_markup=TECLADO_INICIAL
    )


def calcular_minutos_trabalhados(horario_str):
    """Lê uma string no formato '08:00 às 12:00' e retorna o total de minutos."""
    try:
        # Separa a string em duas partes usando o " às " como divisor
        inicio_str, fim_str = horario_str.split(' às ')

        formato = "%H:%M"
        inicio = datetime.strptime(inicio_str.strip(), formato)
        fim = datetime.strptime(fim_str.strip(), formato)

        diferenca = fim - inicio

        # Retorna o valor em minutos
        return diferenca.total_seconds() / 60
    except Exception as e:
        # Se o formato estiver errado (ex: usuário digitou errado no registro), ignora e soma 0
        logger.error(f"Erro ao calcular minutos trabalhados: {horario_str}. Erro: {e}")  # noqa: E501 f"Erro na função calcular_minutos {e}"
        return 0


async def listar_registros(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT id, data_estagio, horario FROM registros WHERE user_id = %s ORDER BY id DESC",
            (user_id,)
        )

        registros = cursor.fetchall()
        conn.close()

        if not registros:
            await update.message.reply_text(
                "📭 **Nenhum registro encontrado.**\n"
                "Comece registrando o seu primeiro dia!",
                parse_mode='Markdown'
            )
            return

        teclado = []
        minutos_totais = 0
        for reg in registros:
            id_reg = reg[0]
            data_reg = reg[1]
            horario_reg = reg[2]
            if horario_reg:
                minutos_totais += calcular_minutos_trabalhados(horario_reg)
            teclado.append([InlineKeyboardButton(
                f"📅 {data_reg}", callback_data=f"ver_{id_reg}")])

        # 4. Transformamos o total de minutos de volta para o formato de Horas:Minutos
        horas_finais = int(minutos_totais // 60)
        minutos_finais = int(minutos_totais % 60)

        # Formata para sempre ter dois dígitos (ex: 08:05 em vez de 8:5)
        horas_totais_str = f"{horas_finais:02d}:{minutos_finais:02d}"
        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"📂 **Seus Registros:**\n"
                f"⏱️ Horas totais: {horas_totais_str}\n"
                f"Clique em uma data para ver os detalhes:\n"),
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup(teclado)
        )

    except Exception as e:
        logger.error(
            f"Erro ao listar os registros: {e}"
            "Função: listar_registros, Arquivo: handlers.py"
        )
        await context.bot.send_message(chat_id=chat_id, text="❌ Erro ao buscar registros.")


async def exibir_detalhe_registro(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    dados = query.data

    if dados == "voltar_lista":
        await query.delete_message()
        await listar_registros(update, context)
        return

    if dados.startswith("ver_"):
        registro_id = dados.split("_")[1]

        try:
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM registros WHERE id = %s", (registro_id,))
            registro = cursor.fetchone()
            cursor.close()
            conn.close()

            if not registro:
                await query.edit_message_text("❌ Registro não encontrado.")
                return

            texto_detalhe = (
                f"📅 **DATA:** {registro[3]}\n"
                f"⌚ **Horário:** {registro[4]}\n"
                f"📍 **Local:** {registro[5]}\n"
                f"🏋️‍♂️ **Atividade:** {registro[6]}\n"
                f"──────────────────\n"
                f"📝 **Conteúdo:**\n{registro[7]}\n\n"
                f"🎯 **Objetivos:**\n{registro[8]}\n\n"
                f"📖 **Descrição:**\n{registro[9]}\n\n"
                f"⚠️ **Dificuldades:**\n{registro[10]}\n\n"
                f"✨ **Pontos Positivos:**\n{registro[11]}"
            )

            botoes_detalhe = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    "✏️ Editar", callback_data=f"editar_{registro_id}")],
                [InlineKeyboardButton(
                    "🗑️ Excluir Registro", callback_data=f"confexclusao_{registro_id}")],
                [InlineKeyboardButton(
                    "🔙 Voltar para Lista", callback_data="voltar_lista")]
            ])

            if registro[12]:
                await query.delete_message()
                caminho_url = registro[12]

                try:
                    await context.bot.send_photo(
                        chat_id=update.effective_chat.id,
                        photo=caminho_url,
                        caption=texto_detalhe[:1024],
                        parse_mode='Markdown',
                        reply_markup=botoes_detalhe
                    )
                except Exception as e:
                    logger.error(
                        f"Erro ao exibir detalhes do registro {registro_id}: {e}"
                    )
                    await context.bot.send_message(
                        chat_id=update.effective_chat.id,
                        text=f"⚠️ Não foi possível carregar a imagem.\n\n{texto_detalhe[:4000]}",
                        reply_markup=botoes_detalhe
                    )
            else:
                await query.edit_message_text(
                    text=texto_detalhe,
                    parse_mode='Markdown',
                    reply_markup=botoes_detalhe
                )

        except Exception as e:
            logger.error(
                f"Erro ao exibir detalhes do registro {registro_id}: {e}")
            await query.edit_message_text("Erro ao carregar detalhes.")


async def exibir_resumo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    status_anexo = "✅ Recebido" if dados.get('caminho_anexo') else "❌ Pendente"

    msg = (
        f"📋 **REVISÃO DO REGISTRO**\n\n"
        f"📅 **Data:** {dados.get('data_estagio')}\n"
        f"⌚ **Horário:** {dados.get('horario')}\n"
        f"📍 **Local:** {dados.get('local')}\n"
        f"🏋️‍♂️ **Atividade:** {dados.get('atividade')}\n"
        f"📝 **Conteúdo:** {dados.get('conteudo')}\n"
        f"🎯 **Objetivos:** {dados.get('objetivos')}\n"
        f"📖 **Descrição:** {dados.get('descricao')}\n"
        f"⚠️ **Dificuldades:** {dados.get('dificuldades')}\n"
        f"✨ **Aspectos:** {dados.get('aspectos_positivos')}\n"
        f"📎 **Anexo:** {status_anexo}\n\n"
        f"O que deseja fazer?\n\n"
        f"Para alterar alguma informação, clique na opção correspondente."
    )

    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=msg,
        parse_mode='Markdown',
        reply_markup=TECLADO_CONFIRMACAO
    )


async def menu_exportacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.callback_query:
        await update.callback_query.answer()
        msg_func = update.callback_query.message.reply_text
    else:
        msg_func = update.message.reply_text

    teclado = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 Apenas Planilha (CSV)",
                              callback_data="export_csv")],
        [InlineKeyboardButton("📦 Completo (Planilha + Fotos)",
                              callback_data="export_zip")],
        [InlineKeyboardButton("📄 Relatório Padrão",
                              callback_data="export_doc")],
        [InlineKeyboardButton("❌ Cancelar",
                              callback_data="cancelar_registro")],
    ])

    await msg_func(
        "💾 **BACKUP DE DADOS**\n\n"
        "Escolha como deseja baixar seus registros:\n\n"
        "• **Planilha:** Gera um arquivo `.csv` compatível com Excel.\n"
        "• **Completo:** Gera um `.zip` com a planilha e todas as fotos organizadas.\n"
        "• **Relatório:** Gera um documento padrão preenchido com os seus registros.\n",
        reply_markup=teclado,
        parse_mode='Markdown'
    )


# Coloque esta função auxiliar fora da sua função principal (pode ser logo acima dela)
# 1. Adicionamos o semáforo na função de download
async def baixar_imagem_async(url, semaforo):
    """Baixa a imagem limitando a concorrência para poupar a RAM do Render."""
    if not url or not str(url).startswith("http"):
        return url, None

    # O semáforo segura a execução se já tiverem 5 fotos baixando ao mesmo tempo
    async with semaforo:
        try:
            resposta = await asyncio.to_thread(requests.get, url, timeout=15)
            if resposta.status_code == 200:
                return url, resposta.content
        except Exception as e:
            logger.error(f"Erro ao baixar {url}: {e}")
        return url, None

# Sua função principal otimizada


async def executar_exportacao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    tipo = query.data
    user_id = update.effective_user.id

    # Imports específicos do Docx (o ideal é estarem no topo do arquivo)
    if tipo == 'export_doc':
        from docx.shared import Mm
        from docxtpl import DocxTemplate, InlineImage

    await query.answer("Gerando arquivos...")
    await query.edit_message_text("⏳ **Processando seus dados...**\nIsso pode levar alguns segundos.")

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, data_estagio, horario, local, tipo_atividade, conteudo, "
            "objetivos, descricao, dificuldades, aspectos_positivos, caminho_anexo "
            "FROM registros WHERE user_id = %s ORDER BY data_estagio DESC",
            (user_id,)
        )
        registros = cursor.fetchall()
        cursor.close()
        conn.close()

        if not registros:
            await query.edit_message_text("❌ Você ainda não possui registros para exportar.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d")

        # =========================================================
        # OTIMIZAÇÃO 1: DOWNLOAD CONCORRENTE DAS IMAGENS
        # =========================================================
        urls_para_baixar = {reg[10] for reg in registros if reg[10] and str(
            reg[10]).startswith("http")}

        # Cria as tarefas para baixar tudo ao mesmo tempo
        tarefas = [baixar_imagem_async(url) for url in urls_para_baixar]

        # Espera todas terminarem e guarda em um dicionário {url: bytes_da_foto}
        # Se você tiver 10 fotos, isso levará o tempo de baixar 1 foto (a mais pesada), e não a soma das 10.
        imagens_baixadas = dict(await asyncio.gather(*tarefas))

        # =========================================================
        # GERAÇÃO DO CSV BASE (Sempre necessário para ZIP e CSV)
        # =========================================================
        output_csv = io.StringIO()
        writer = csv.writer(output_csv, delimiter=';')
        writer.writerow(['ID', 'Data', 'Horário', 'Local', 'Atividade', 'Conteúdo',
                         'Objetivos', 'Descrição', 'Dificuldades', 'Positivos', 'Nome do Arquivo'])

        lista_arquivos_para_zip = []

        for reg in registros:
            data_estagio = reg[1]
            caminho_original = reg[10]
            novo_nome_anexo = ""

            if caminho_original:
                str_data = str(data_estagio).replace(
                    "/", "-")  # Evita erro de pastas no zip
                extensao = ".jpg"
                if str(caminho_original).lower().endswith(".png"):
                    extensao = ".png"
                elif str(caminho_original).lower().endswith(".pdf"):
                    extensao = ".pdf"

                novo_nome_anexo = f"anexo_{str_data}{extensao}"

                lista_arquivos_para_zip.append({
                    'caminho_original': caminho_original,
                    'nome_final': novo_nome_anexo
                })

            writer.writerow(list(reg[:-1]) + [novo_nome_anexo])

        csv_bytes = output_csv.getvalue().encode('utf-8-sig')
        output_csv.close()

        # =========================================================
        # ROTEAMENTO E EXPORTAÇÃO
        # =========================================================
        if tipo == 'export_doc':
            doc = DocxTemplate("template_estagio.docx")
            dados_relatorio = []

            for reg in registros:
                caminho_original = reg[10]
                imagem_injetada = "📎 Sem anexo"

                if caminho_original and str(caminho_original).startswith("http"):
                    bytes_foto = imagens_baixadas.get(caminho_original)
                    if bytes_foto:
                        stream_imagem = io.BytesIO(bytes_foto)
                        imagem_injetada = InlineImage(
                            doc, image_descriptor=stream_imagem, width=Mm(150))
                    else:
                        imagem_injetada = "❌ Imagem indisponível ou erro no download."

                dados_relatorio.append({
                    'data_estagio': reg[1], 'horario': reg[2], 'local': reg[3],
                    'tipo_atividade': reg[4], 'conteudo': reg[5], 'objetivos': reg[6],
                    'descricao': reg[7], 'dificuldades': reg[8], 'aspectos_positivos': reg[9],
                    'caminho_anexo': imagem_injetada
                })

            doc.render({'registros': dados_relatorio})

            arquivo_final_docx = io.BytesIO()
            doc.save(arquivo_final_docx)
            arquivo_final_docx.name = f"Diario_Bordo_{timestamp}.docx"
            arquivo_final_docx.seek(0)

            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=arquivo_final_docx,
                caption="📄 **Aqui está o seu relatório formatado com sucesso!**", parse_mode='Markdown'
            )

        elif tipo == "export_csv":
            arquivo_final = io.BytesIO(csv_bytes)
            arquivo_final.name = f"Diario_Bordo_{timestamp}.csv"
            arquivo_final.seek(0)

            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=arquivo_final,
                caption="📊 **Aqui está sua planilha.**", parse_mode='Markdown'
            )

        elif tipo == "export_zip":
            # OTIMIZAÇÃO 2: ZipFile em memória RAM ao invés de tempfile
            zip_buffer = io.BytesIO()

            with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
                # Adiciona o CSV
                zip_file.writestr(f"Diario_Bordo_{timestamp}.csv", csv_bytes)

                # Adiciona as imagens que já estão na RAM
                for item in lista_arquivos_para_zip:
                    bytes_foto = imagens_baixadas.get(item['caminho_original'])
                    if bytes_foto:
                        zip_file.writestr(item['nome_final'], bytes_foto)

            zip_buffer.seek(0)
            zip_buffer.name = f"Backup_Completo_{timestamp}.zip"

            await context.bot.send_document(
                chat_id=update.effective_chat.id, document=zip_buffer,
                caption="📦 Aqui está seu backup completo."
            )

        await query.delete_message()

    except Exception as e:
        logger.error(f"Erro ao gerar backup: {e}", exc_info=True)
        try:
            await query.edit_message_text("❌ Ocorreu um erro ao processar os arquivos.")
        except:
            pass


async def initiate_register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['editando'] = False
    context.user_data['horario'] = HORARIO_PADRAO
    context.user_data['local'] = LOCAL_PADRAO
    context.user_data['atividade'] = ATIVIDADE_PADRAO

    await update.message.reply_text(
        MSG_START,
        parse_mode='Markdown',
        reply_markup=get_botao_cancelar()
    )
    return DATA


async def cancelar_registro_inline(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    try:
        await query.edit_message_text("❌ Operação cancelada pelo usuário.")

    except:
        pass

    context.user_data.clear()
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Você voltou ao menu principal.",
        reply_markup=TECLADO_INICIAL
    )
    return ConversationHandler.END


async def receber_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text.strip().lower()
    user_id = update.effective_user.id
    data_final = ""

    if texto_usuario in ["hoje", "hj", "today"]:
        data_final = datetime.now().strftime("%d/%m/%Y")

    else:
        formatos = ["%d/%m/%Y", "%d/%m/%y", "%d-%m-%Y", "%d%m%Y", "%d.%m.%Y"]

        for formato in formatos:
            try:
                data_obj = datetime.strptime(texto_usuario, formato)
                data_final = data_obj.strftime("%d/%m/%Y")
                break
            except ValueError:
                continue

    if not data_final:
        await update.message.reply_text(
            "Não entendi a data. 🤔\n"
            "Por favor, digite 'hoje' ou uma data válida (ex: 27/01/2026)."
        )
        return DATA

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            """SELECT id FROM registros WHERE user_id = %s AND data_estagio = %s""",
            (user_id, data_final)
        )
        registro_existente = cursor.fetchone()
        cursor.close()
        conn.close()

        if registro_existente:
            id_conflito = registro_existente[0]
            botoes = InlineKeyboardMarkup([
                [InlineKeyboardButton(
                    f"🔍 Ver Registro de {data_final}", callback_data=f"ver_{id_conflito}")],
                [InlineKeyboardButton(
                    "❌ Cancelar", callback_data="cancelar_registro")]
            ])

            await update.message.reply_text(
                f"🚫 **Registro Duplicado!**\n\n"
                f"Você já possui um registro para a data **{data_final}**.\n"
                f"O sistema não permite dois registros no mesmo dia.\n\n"
                f"👇 **O que você deseja fazer?**\n"
                f"• Clique no botão abaixo para ver/editar o registro antigo.\n"
                f"• Ou digite uma **nova data** para continuar este cadastro.",
                parse_mode='Markdown',
                reply_markup=botoes
            )
            return DATA

    except Exception as e:
        logger.error(f"Erro segundo try da funcao receber_data: {e}")

    context.user_data['data_estagio'] = data_final

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Data atualizada!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{data_final}'\n\n"
        "Agora, fale sobre os conteúdos trabalhados.\n",
        reply_markup=get_botao_cancelar()
    )
    return CONTEUDO


async def receber_conteudo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor o conteúdo trabalhado?\n"
        )
        return CONTEUDO

    context.user_data['conteudo'] = texto_usuario

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Conteúdo atualizado!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre os objetivos da aula/atividade.\n",
        reply_markup=get_botao_cancelar()
    )
    return OBJETIVOS


async def receber_objetivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor os objetivos da aula?\n"
        )
        return OBJETIVOS

    context.user_data['objetivos'] = texto_usuario

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Objetivos atualizados!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, descreva as experiências.\n",
        reply_markup=get_botao_cancelar()
    )
    return DESCRICAO


async def receber_descricao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor as experiências (observações, práticas, etc.)?\n"
        )
        return DESCRICAO

    context.user_data['descricao'] = texto_usuario

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Descrição atualizada!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre as dificuldades enfrentadas.\n",
        reply_markup=get_botao_cancelar()
    )
    return DIFICULDADES


async def receber_dificuldades(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor as dificuldades enfrentadas?\n"
        )
        return DIFICULDADES

    context.user_data['dificuldades'] = texto_usuario

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Dificuldades atualizadas!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        "Agora, fale sobre os aspectos positivos.\n",
        reply_markup=get_botao_cancelar()
    )
    return ASPECTOS_P


async def receber_aspectos_positivos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    texto_usuario = update.message.text

    if len(texto_usuario) < 5:
        await update.message.reply_text(
            "Que pouquinho. Vamos detalhar melhor os aspectos positivos?\n"
        )
        return ASPECTOS_P

    context.user_data['aspectos_positivos'] = texto_usuario

    if context.user_data.get('editando'):
        await update.message.reply_text("✅ Aspectos positivos atualizados!")
        await exibir_resumo(update, context)
        return CONFIRMACAO

    context.user_data['editando'] = True

    if context.user_data.get('caminho_anexo'):
        await exibir_resumo(update, context)
        return CONFIRMACAO

    await update.message.reply_text(
        f"📝 Anotei: '{texto_usuario}'\n\n"
        f"Agora, me envie os anexos para {context.user_data['data_estagio']}.\n",
        reply_markup=get_botao_cancelar()
    )
    return ANEXOS


async def receber_anexos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    arquivo = None

    if update.message.photo:
        arquivo = await update.message.photo[-1].get_file()

    elif update.message.document:
        arquivo = await update.message.document.get_file()
    else:
        await update.message.reply_text("Por favor, envie uma imagem ou um documento válido.")
        return ANEXOS

    try:
        await update.message.reply_chat_action("upload_photo")

        f_memoria = io.BytesIO()
        await arquivo.download_to_memory(f_memoria)
        f_memoria.seek(0)

        upload_result = cloudinary.uploader.upload(
            f_memoria,
            folder="diario_bordo_bot",
            resource_type="auto"
        )

        url_imagem = upload_result['secure_url']
        context.user_data['caminho_anexo'] = url_imagem

        await update.message.reply_text(
            "✅ **Foto salva na nuvem!**\n\nAgora, confira o resumo e confirme o registro.",
            parse_mode='Markdown'
        )
        await exibir_resumo(update, context)
        return CONFIRMACAO
    except Exception as e:
        await update.message.reply_text(f"Erro ao enviar o anexo: {e}")
        return ANEXOS


async def receber_horario(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['horario'] = update.message.text
    await update.message.reply_text("✅ Horário atualizado!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def receber_local(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['local'] = update.message.text
    await update.message.reply_text("✅ Local atualizado!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def receber_atividade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['atividade'] = update.message.text
    await update.message.reply_text("✅ Atividade atualizada!")
    await exibir_resumo(update, context)
    return CONFIRMACAO


async def confirmar_ou_editar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    opcao = update.message.text
    dados = context.user_data

    if "✅ SALVAR" in opcao:
        return await salvar_no_banco_final(update, context)
    if "Cancelar" in opcao:
        return await cancel(update, context)

    for palavra_chave, (estado, mensagem, campo_valor) in ROTAS.items():
        if palavra_chave in opcao:
            texto = mensagem.format(
                dados.get(campo_valor, '')) if campo_valor else mensagem
            await update.message.reply_text(texto, reply_markup=get_botao_cancelar())
            return estado

    await update.message.reply_text("Opção inválida. Use o teclado abaixo.")
    return CONFIRMACAO


async def editar_registro_existente(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    id_registro = query.data.split("_")[1]

    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM registros WHERE id = %s", (id_registro,))
        registro = cursor.fetchone()
        cursor.close()
        conn.close()

        if not registro:
            await query.edit_message_text("❌ Erro: Registro não encontrado.")
            return ConversationHandler.END

        # SALVAMOS O ID PARA O UPDATE DEPOIS
        context.user_data['id_edicao'] = registro[0]
        context.user_data['data_estagio'] = registro[3]
        context.user_data['horario'] = registro[4]
        context.user_data['local'] = registro[5]
        context.user_data['atividade'] = registro[6]
        context.user_data['conteudo'] = registro[7]
        context.user_data['objetivos'] = registro[8]
        context.user_data['descricao'] = registro[9]
        context.user_data['dificuldades'] = registro[10]
        context.user_data['aspectos_positivos'] = registro[11]
        context.user_data['caminho_anexo'] = registro[12]

        context.user_data['editando'] = True

        await query.delete_message()
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f"✏️ **Editando Registro #{id_registro}**\nOs dados foram carregados. O que deseja alterar?",
            parse_mode='Markdown'
        )

        await exibir_resumo(update, context)
        return CONFIRMACAO

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ocorreu um erro ao tentar editar o registro."
        )
        logger.error(e)
        return ConversationHandler.END


async def salvar_no_banco_final(update: Update, context: ContextTypes.DEFAULT_TYPE):
    dados = context.user_data
    user = update.effective_user

    try:
        conn = get_connection()
        cursor = conn.cursor()

        if 'id_edicao' in dados:
            sql = SQL_UPDATE

            valores = (
                dados.get('data_estagio'), dados.get('horario'), dados.get(
                    'local'), dados.get('atividade'),
                dados.get('conteudo'), dados.get('objetivos'),
                dados.get('descricao'), dados.get('dificuldades'), dados.get(
                    'aspectos_positivos'), dados.get('caminho_anexo'),
                # ID e User ID no final para o WHERE
                dados.get('id_edicao'), user.id
            )

        else:
            sql = SQL

            valores = (
                user.id, dados.get('data_estagio'), dados.get('horario'),
                dados.get('local'), dados.get('atividade'),
                dados.get('conteudo'), dados.get('objetivos'),
                dados.get('descricao'), dados.get('dificuldades'), dados.get(
                    'aspectos_positivos'), dados.get('caminho_anexo')
            )

        cursor.execute(sql, valores)
        conn.commit()
        cursor.close()
        conn.close()

        await update.message.reply_text("✅ Registro salvo com sucesso!", reply_markup=TECLADO_INICIAL)
        context.user_data.clear()
        return ConversationHandler.END

    except Exception as e:
        await update.message.reply_text("Erro ao salvar o registro.")
        logger.error(e)
        return ConversationHandler.END


async def solicitar_exclusao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    id_registro = query.data.split("_")[1]

    botoes = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Sim, excluir", callback_data=f"deletefinal_{id_registro}"),
         InlineKeyboardButton("❌ Não", callback_data=f"ver_{id_registro}")]
    ])

    await query.edit_message_caption(
        caption=f"⚠️ **TEM CERTEZA?**\n\nVocê está prestes a apagar o registro **#{id_registro}**.\nEssa ação não pode ser desfeita e a foto será perdida.",
        parse_mode='Markdown',
        reply_markup=botoes
    ) if query.message.photo else await query.edit_message_text(
        text=f"⚠️ **TEM CERTEZA?**\n\nVocê está prestes a apagar o registro **#{id_registro}**.\nEssa ação não pode ser desfeita.",
        parse_mode='Markdown',
        reply_markup=botoes
    )


async def executar_exclusao(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    id_registro = query.data.split("_")[1]
    user_id = update.effective_user.id

    try:
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "SELECT caminho_anexo FROM registros WHERE id = %s AND user_id = %s", (id_registro, user_id))
        resultado = cursor.fetchone()

        if resultado:
            caminho_anexo = resultado[0]
            if caminho_anexo and os.path.exists(caminho_anexo):
                try:
                    os.remove(caminho_anexo)
                    logger.info(f"Arquivo excluido: {caminho_anexo}")
                except Exception as e:
                    logger.error(
                        f"Erro ao excluir o arquivo: {caminho_anexo}. Erro: {e}")

            cursor.execute(
                "DELETE FROM registros WHERE id = %s AND user_id = %s", (id_registro, user_id))
            conn.commit()

            await query.delete_message()
            await context.bot.send_message(
                chat_id=update.effective_chat.id,
                text=f"🗑️ **Registro #{id_registro} excluído com sucesso!**",
                parse_mode='Markdown'
            )
            await listar_registros(update, context)

        else:
            await query.edit_message_teste("❌ Registro não encontrado ou sem permissão.")

        cursor.close()
        conn.close()

    except Exception as e:
        await context.bot.send_message(
            chat_id=update.effective_chat.id,
            text="❌ Ocorreu um erro ao tentar excluir o registro."
        )
        logger.error(e)
        return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text("Registro cancelado.", reply_markup=TECLADO_INICIAL)
    return ConversationHandler.END


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = (MSG_HELP)

    await update.message.reply_text(help_text, parse_mode='Markdown')
