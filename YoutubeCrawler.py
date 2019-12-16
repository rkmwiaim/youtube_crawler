import SpreadsheetApi
import YoutubeApi
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta
from functional import seq

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

  for query in queries:
    print('start to crawl query: ', query)

    if query in sheets_title_dict:
      sheet_id = sheets_title_dict[query]
      last_video_date = youtube_spreadsheet.get_last_video_date(query)
      videos = []

      try:
        gen = YoutubeApi.video_generator(query, 3, add_second(last_video_date))
        for vs in gen:
          for v in vs:
            videos.append(v)
      except:
        pass

      youtube_spreadsheet.insert_data_at_head(sheet_id, videos)

    else:
      print('add sheet. title: ', query)
      add_sheet_res = youtube_spreadsheet.add_sheet_with_video_header(query)
      added_sheet_id = youtube_spreadsheet.get_sheet_id_from_res(add_sheet_res)

      gen = YoutubeApi.video_generator(query)
      for data in gen:
        youtube_spreadsheet.batch_append(added_sheet_id, data)
        print('appended {0} data'.format(len(data)))


def add_second(t):
  added = parse_date(t) + relativedelta(seconds=1)
  return added.isoformat()

def test():
  youtube_spreadsheet = SpreadsheetApi.YoutubeSpreadsheet()
  last_video_date = youtube_spreadsheet.get_last_video_date('워크맨')

  gen = YoutubeApi.video_generator('워크맨', 3, add_second(last_video_date))
  videos = []
  for vs in gen:
    for v in vs:
      videos.append(v)

  for i in videos:
    print(i)


if __name__ == '__main__':
  try:
    raise ValueError()
  except:
    pass

  print(1)