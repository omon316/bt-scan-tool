from cli import start_cli
from telegram_report import load_config, save_config, prompt_for_telegram_credentials

if __name__ == "__main__":
    config = load_config()
    if not config:
        print("No configuration found. Type in your Telegram credentials.")
        config = prompt_for_telegram_credentials()
        save_config(config)
    start_cli()
