from bot import bot
import game_handler


try:
    bot.polling()
except Exception as e:
    print(f"Polling failed! {str(e)}")
