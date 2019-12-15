import SpreadsheetApi
import YoutubeApi

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
      add_sheet_res = SpreadsheetApi.add_sheet(spreadsheet_resource, query)

      added_sheet_id = add_sheet_res['replies'][0]['addSheet']['properties']['sheetId']

      gen = YoutubeApi.dump_all_generator(query)
      for data in gen:
        SpreadsheetApi.batch_append(spreadsheet_resource, added_sheet_id, data)
        print('appended {0} data'.format(len(data)))

if __name__ == '__main__':
  main()