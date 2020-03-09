import SpreadsheetApi
import YoutubeApi
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from functional import seq

import TelegramBot


def get_queries(spreadsheet_resource):
  return SpreadsheetApi.read_queries(spreadsheet_resource)


def get_sheet_titles(spreadsheet_resource):
  return SpreadsheetApi.get_sheet_titles(spreadsheet_resource)


def main():
  youtube_spreadsheet = SpreadsheetApi.YoutubeSpreadsheet()

  sheets = youtube_spreadsheet.get_sheets()
  sheets_title_dict = seq(sheets).map(lambda d: (d['title'], d['sheetId'])).to_dict()

  queries = youtube_spreadsheet.read_queries()

  print('queries:,', queries)

  for query_index, query_tuple in enumerate(queries):
    query = query_tuple[0]
    print('start to crawl query: ', query)

    if query in sheets_title_dict:
      sheet_id = sheets_title_dict[query]

      if len(query_tuple) > 1:
        last_video_date = query_tuple[1]
      else:
        last_video_date = '1970-01-01T00:00:00.000Z'

      gen = YoutubeApi.video_generator(query, 3, add_second(last_video_date))

    else:
      print('add sheet. title: ', query)
      add_sheet_res = youtube_spreadsheet.add_sheet_with_video_header(query)
      sheet_id = youtube_spreadsheet.get_sheet_id_from_res(add_sheet_res)
      gen = YoutubeApi.video_generator(query)

    videos = seq(gen).flat_map(lambda v: v).to_list()

    if len(videos) > 0:
      videos.sort(key=lambda t: t[2])
      last_video_date = videos[-1][2]

      transformed = seq(videos).map(transform_video).to_list()
      youtube_spreadsheet.append_data(sheet_id, transformed)

      youtube_spreadsheet.update_query_last_crawled_date(query_index, last_video_date)
      msg = get_message(query, videos)
      TelegramBot.send_message(TelegramBot.youtube_chat_id, msg)


def get_message(query, videos):
  msg = "crawled {} new videos for query: {}\n".format(len(videos), query)
  msg += seq(videos) \
    .map(lambda v: '{}\n'.format(v[0])) \
    .reduce(lambda a, b: a + b)
  return msg


def add_second(t):
  added = parse_date(t) + relativedelta(seconds=1)
  return added.isoformat()


def change_date_format(t):
  return parse_date(t).strftime('%Y-%m-%d %H:%M:%S')


def add_youtube_url_prefix(video_id):
  return 'https://youtu.be/' + video_id


def transform_video(video):
  video[2] = change_date_format(video[2])
  video[0] = add_youtube_url_prefix(video[0])

  return video


if __name__ == '__main__':
  main()