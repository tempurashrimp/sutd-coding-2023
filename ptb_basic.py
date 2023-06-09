
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, CallbackQueryHandler
from tictactoe import TicTacToe
from random import randint
from typing import Union, List
import signal

TOKEN = None

# function for the bot to reply "Hello" when a user sends "/start" to it
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # update.effective_chat.id is the id of the chat that the user has sent the message in
    # this is so that the bot knows where to send the message to
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This spoon has 37 calories")
    print("sent message")

# samstailor
async def eat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    samstailor = open('thing.jpg', 'rb')
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=samstailor)
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I will eat this")
    samstailor.close()
    print("sent picture")


# ----------
def handler(signum, frame):
    res = input("\nCtrl-c was pressed. Do you really want to exit? y/n ")
    if res == 'y':
        exit(1)

# table thing
def build_menu(
    buttons: List[InlineKeyboardButton],
    n_cols: int,
    header_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None,
    footer_buttons: Union[InlineKeyboardButton, List[InlineKeyboardButton]]=None
) -> List[List[InlineKeyboardButton]]:
    menu = [buttons[i:i + n_cols] for i in range(0, len(buttons), n_cols)]
    if header_buttons:
        menu.insert(0, header_buttons if isinstance(header_buttons, list) else [header_buttons])
    if footer_buttons:
        menu.append(footer_buttons if isinstance(footer_buttons, list) else [footer_buttons])
    return menu

game = TicTacToe()
chat_id = -1
message_id = -1

async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("new game budy")
    global game, chat_id, message_id
    game = TicTacToe()
    chat_id = update.effective_chat.id

    button_list = []
    for i in range(3):
        for j in range(3):
            button_list.append(InlineKeyboardButton(game.board[i][j], 
                                        callback_data = str(i * 3 + j)))
            
    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
    await context.bot.send_message(chat_id=chat_id, text="new game budy", reply_markup=reply_markup)
    message_id = update.effective_message.message_id + 1

async def callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global game, chat_id, message_id

    message = update.callback_query.message
    data = update.callback_query.data
    query_id = update.callback_query.id

    def game_message(cmsg):
        return context.bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id, text=msg)

    print(data)

    if message.chat_id == chat_id and message.message_id == message_id:
        available = game.getempty()
        if data is available:
            game.move("X", int(data))

            if game.checkwin():
                await game_message("W liao")
            elif not game.checkwin() and len(game.getempty()) == 0:
                await game_message("bruh")
            else:
                available = game.getempty()
                bot_move = randint(0, len(available) - 1)
                game.move("O", int(available(bot_move)))
                if game.checkwin():
                    await game_message("L Bozo")
                elif (not game.checkwin()) and len(game.getempty()) == 0:
                    await game_message("bruh")
                else:
                    button_list = []
                    for i in range(3):
                        for j in range(3):
                            button_list.append(InlineKeyboardButton(game.board[i][j], 
                                                            callback_data = str(i * 3 + j)))
                    reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
            await context.bot.answer_callback_query(query_id)
        else:
            print("skill issue, pick another cell bozo")
            button_list = []
            for i in range(3):
                for j in range(3):
                    button_list.append(InlineKeyboardButton(game.board[i][j], 
                                                    callback_data = str(i * 3 + j)))
            reply_markup = InlineKeyboardMarkup(build_menu(button_list, n_cols=3))
            await context.bot.answer_callback_query(query_id, text="pick another cell bozo")
    else:
        if message.text == "new game budy" or message.text == "ur turn budy":
            await game_message("invalid game budy")
            await game_message("pick another cell bozo")

signal.signal(signal.SIGINT, handler)

if __name__ == '__main__':
    # creates an entry point for the bot using your bot's token
    app = ApplicationBuilder().token(TOKEN).build()
    
    # this creates a CommandHandler object
    # the first parameter is the command aka what the user writes after / to activate the command
    # the second parameter is the function written earlier
    start_handler = CommandHandler('start', start)
    app.add_handler(start_handler)
    eat_handler = CommandHandler('eat', eat)
    app.add_handler(eat_handler)
    newgame_handler = CommandHandler('newgame', newgame)
    app.add_handler(newgame_handler)
    callback_handler = CallbackQueryHandler(callback)
    app.add_handler(callback_handler)

    # this starts the bot
    app.run_polling()

    