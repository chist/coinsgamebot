from bot import bot
import telebot
import game_handler
import ssl
from aiohttp import web
import config

url_path = f"https://{config.host}:{config.port}/{config.telegram_token}/"

telebot.apihelper.proxy = config.proxy_settings

# Remove previous webhook
bot.remove_webhook()
# Set webhook
bot.set_webhook(url=url_path, certificate=open(config.ssl_sert, "r"))

# Build ssl context
context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(config.ssl_sert, config.ssl_priv)

app = web.Application()

# Process webhook calls
async def handle(request):
    if request.match_info.get("token") == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post("/{token}/", handle)

# Start aiohttp server
web.run_app(app, host=config.lstn, port=config.port, ssl_context=context)
