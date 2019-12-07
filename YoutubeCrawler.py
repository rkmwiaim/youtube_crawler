import SpreadsheetApi


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
      SpreadsheetApi.add_sheet(spreadsheet_resource, query)



if __name__ == '__main__':
  main()