from pyromod import Client
import config

plugins = dict(root="plugins")

app = Client(
    "MediaDownloader",
    api_id=config.API_ID,
    api_hash=config.API_HASH,
    bot_token=config.BOT_TOKEN,
    # proxy=config.proxy,
    plugins=plugins,
)

if __name__ == "__main__":
    print("===============================run====================================")
    app.run()