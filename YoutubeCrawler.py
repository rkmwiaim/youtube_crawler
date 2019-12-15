import SpreadsheetApi
import YoutubeApi
from dateutil.parser import parse as parse_date
from dateutil.relativedelta import relativedelta

def get_queries(spreadsheet_resource):
  return SpreadsheetApi.read_queries(spreadsheet_resource)


def get_sheet_titles(spreadsheet_resource):
  return SpreadsheetApi.get_sheet_titles(spreadsheet_resource)


def main():
  spreadsheet_resource = SpreadsheetApi.get_spreadsheet_resource()
  sheet_titles = set(get_sheet_titles(spreadsheet_resource))

  queries = get_queries(spreadsheet_resource)
  print('queries:,', queries)

  for query in queries:
    print('start to crawl query: ', query)

    if query not in sheet_titles:
      print('add sheet. title: ', query)
      add_sheet_res = SpreadsheetApi.add_sheet_with_video_header(spreadsheet_resource, query)

      added_sheet_id = SpreadsheetApi.get_sheet_id_from_res(add_sheet_res)

      gen = YoutubeApi.video_generator(query)
      for data in gen:
        SpreadsheetApi.batch_append(spreadsheet_resource, added_sheet_id, data)
        print('appended {0} data'.format(len(data)))


def add_second(t):
  added = parse_date(t) + relativedelta(seconds=1)
  return added.isoformat()

def test():
  start_time = '2019-12-14T07:21:46.000Z'

  gen = YoutubeApi.video_generator('워크맨', 3, add_second(start_time))
  videos = []
  for vs in gen:
    for v in vs:
      videos.append(v)

  spreadsheet_resource = SpreadsheetApi.get_spreadsheet_resource()
  SpreadsheetApi.insert_data_at_head(spreadsheet_resource, 168470890, videos)

if __name__ == '__main__':
  test()