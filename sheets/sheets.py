import gspread

def fetch_from_google_sheet():
    raise NotImplementedError("not implemented yet")

def upload_to_google_sheet(spreadsheet_id, strings_map):
    gc = gspread.oauth(credentials_filename='credentials.json')
    wks = gc.open_by_key(spreadsheet_id).sheet1
    wks.clear()
    rows = []
    for index in strings_map.index.values():
        row = [index.value]
        for translation in index.translations.values():
            row.append(translation)
        rows.append(row)
    wks.insert_rows(rows)