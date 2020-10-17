# this file must be renamed to config.py!

proxy_settings = None  # may be {'https': 'socks5://127.0.0.1:9150'}
telegram_token = 'your_telegram_token'

# webhook settings
host = 'ip_address'
port = 8443       # 443, 80, 88 or 8443 (port need to be 'open')
lstn = '0.0.0.0'  # In some VPS you may need to put here the IP address

# ssl sertificate
ssl_sert = './public.pem'   # Path to the ssl certificate
ssl_priv = './private.key'  # Path to the ssl private key

# access to Mongo DataBase
mongo_path = 'mongodb://localhost:27017/'
