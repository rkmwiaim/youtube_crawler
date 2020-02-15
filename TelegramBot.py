import requests
import os

with open('telegram_bot_key', 'r') as f:
  current_path = os.getcwd()
  bot_key = f.read()

with open('chat_id', 'r') as f:
  youtube_chat_id = f.read()


def get_updates():
  return requests.get('https://api.telegram.org/bot{}/getUpdates'.format(bot_key)).text


def send_message(chat_id, msg):
  requests.get('https://api.telegram.org/bot{}/sendMessage?chat_id={}&text={}'.format(bot_key, chat_id, msg))


if __name__ == '__main__':
  send_message(youtube_chat_id, 'this message is from program')
