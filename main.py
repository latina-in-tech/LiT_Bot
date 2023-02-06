import logging
import telegram.constants
import re
from datetime import datetime
from telegram import Update
from telegram.ext import (filters, 
                         ApplicationBuilder, 
                         ContextTypes, 
                         CommandHandler, 
                         MessageHandler, 
                         ConversationHandler)


BOT_TOKEN: str = '<TOKEN>'
WELCOME_MESSAGE: str = '<b>Benvenuto nel bot del gruppo Latina In Tech!</b>'

# Tipologia di contratto, posizione ricercata, descrizione, link, RAL
JOB_TYPE, JOB_POSITION, JOB_DESCRIPTION, JOB_LINK, JOB_RAL = range(5)

user_data: dict = {}

# Impostazione del formato di log dell'applicazione
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Funzione asincrona associata al comando di start,
# la quale e' in attesa del comando per eseguire le istruzioni contenute in essa
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(text=WELCOME_MESSAGE, 
                                   parse_mode=telegram.constants.ParseMode.HTML)


async def new_job_offer(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    await update.message.reply_text(text='\U0001F516 Stai creando una nuova offerta di lavoro.\n' + \
                                         'Premi /cancel per annullare la creazione della nuova offerta.\n' + \
                                         'Per prima cosa, inserisci la tipologia di contratto:')

    return JOB_TYPE


async def job_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_data['job_type'] = update.message.text
    
    await update.message.reply_text(text='\U0001F477 Inserisci la posizione dell\'offerta:')
    
    return JOB_POSITION


async def job_position(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:

    user_data['job_position'] = update.message.text

    await update.message.reply_text(text='\U0001F4C3 Inserisci una breve descrizione dell\'offerta:')

    return JOB_DESCRIPTION


async def job_description(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_data['job_description'] = update.message.text
    
    await update.message.reply_text(text='\U0001F310 Inserisci il link del lavoro (scrivi "na" se non presente):')
    
    return JOB_LINK


async def job_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    
    user_data['job_link'] = update.message.text
    
    await update.message.reply_text(text='\U0001F4B0 Inserisci il RAL del lavoro (scrivi "na" se non presente):')
    
    return JOB_RAL


async def job_ral(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    

    user_data['job_ral'] = update.message.text

    user = update.message.from_user

    user_job_link = "Non disponibile" if user_data.get("job_link") == "na" else user_data.get("job_link")
    user_job_ral = "Non disponibile" if user_data.get("job_ral") == "na" else user_data.get("job_ral")

    message = f'<b>Tipologia di contratto:</b> {user_data.get("job_type")}\n' + \
              f'<b>Posizione ricercata:</b> {user_data.get("job_position")}\n' + \
              f'<b>Descrizione:</b> {user_data.get("job_description")}\n' + \
              f'<b>Link:</b> {user_job_link}\n' + \
              f'<b>RAL:</b> {user_job_ral}\n' + \
              f'<i>Creata da {user.name} il {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}</i>'
        
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='\U00002705 La nuova offerta di lavoro e\' stata creata.\n' + \
                                        'Inoltrala nel gruppo e nel rispettivo topic.')
    
    await context.bot.send_message(chat_id=update.effective_chat.id, text=message, parse_mode=telegram.constants.ParseMode.HTML)

    # await context.bot.forward_message(chat_id='LiT - Latina In Tech', 
    #                                   from_chat_id=update.effective_chat.id, 
    #                                   message_id=update.message.message_id)
    
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:    
    
    await context.bot.send_message(chat_id=update.effective_chat.id,
                                   text='\U000026A0 Operazione annullata dall\'utente.')    
    
    return ConversationHandler.END


# Funzione asincrona associata per ogni messaggio,
# la quale e' in attesa di un messaggio che NON SIA un comando per eseguire le istruzioni contenute in essa
async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, 
                                   text='Comando non valido.\n' \
                                        'Digita il comando /commands per vedere la lista dei comandi disponibili.',
                                   parse_mode=telegram.constants.ParseMode.HTML)

if __name__ == '__main__':
    
    # Creazione dell'applicazione (bot)
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Creazione dell'handler per il comando 'start'
    start_handler = CommandHandler('start', callback=start)

    new_job_offer_handler = CommandHandler('newjoboffer', callback=new_job_offer)

    job_type_handler = MessageHandler(filters=filters.Regex(re.compile(pattern='^Indeterminato$|^Determinato$', 
                                                                       flags=re.IGNORECASE)), 
                                      callback=job_type)

    job_position_handler = MessageHandler(filters=filters.TEXT, callback=job_position)

    job_description_handler = MessageHandler(filters=filters.TEXT, callback=job_description)

    job_link_handler = MessageHandler(filters=filters.TEXT, callback=job_link)

    job_ral_handler = MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=job_ral)

    fallback_handler = CommandHandler('cancel', cancel)

    new_job_offer_conv_handler = ConversationHandler(
                                 entry_points=[new_job_offer_handler],
                                 states={
                                    JOB_TYPE: [job_type_handler],                               
                                    JOB_POSITION: [job_position_handler],
                                    JOB_DESCRIPTION: [job_description_handler],
                                    JOB_LINK: [job_link_handler],
                                    JOB_RAL: [job_ral_handler]
                                 },
                                 fallbacks=[fallback_handler]

    )

    # Handler per i comandi sconosciuti digitati dall'utente
    # Questo handler va inserito dopo tutti gli altri command handlers
    unkown_command_handler = MessageHandler(filters.COMMAND, unknown_command)
    
    
    # Avvio dell'handler per il comando 'start'
    application.add_handler(start_handler)
    application.add_handler(new_job_offer_conv_handler)
    application.add_handler(unkown_command_handler)
    
    # Avvio del bot, e messa in ascolto dello stesso
    application.run_polling()