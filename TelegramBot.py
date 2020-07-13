import requests
import yaml
import os
import definitions

with open(os.path.join(definitions.RESOURCE_DIR, 'telegram_conf.yaml')) as f:
  TELEGRAM_CONF = yaml.load(f, Loader=yaml.FullLoader)
  BOT_KEY = TELEGRAM_CONF['bot_key']
  telegram_ids = TELEGRAM_CONF['ids']


def get_updates():
  return requests.get('https://api.telegram.org/bot{}/getUpdates'.format(BOT_KEY)).text


def send_message(chat_id, msg):
  data = {
    'chat_id': chat_id,
    'text': msg
  }
  return requests.post('https://api.telegram.org/bot{}/sendMessage'.format(BOT_KEY), data=data)


if __name__ == '__main__':
  res = send_message(telegram_ids['alarm'], 'this message is from bot')
  print(res)
  print(res.text)
