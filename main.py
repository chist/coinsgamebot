from bot import bot
import game_handler
import time


if __name__ == "__main__":
    while True:
        try:
            bot.infinity_polling()
        except Exception as e:
            print(f"Polling failed! {str(e)}")
            time.sleep(1.0)
