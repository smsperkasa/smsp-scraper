from datetime import datetime

import gspread
from google.oauth2.service_account import Credentials


class SheetUploader:
    def __init__(self):
        self.sheet = None
        self.scopes = ["https://www.googleapis.com/auth/spreadsheets"]
        self.creds = Credentials.from_service_account_file(
            "credentials.json", scopes=self.scopes
        )
        self.client = gspread.authorize(self.creds)
        self.sheet_id = "15TermcNQYeUueb1L4HT7Lfa7_IjdjHTZv4-H1ijNC2M"
        self.workbook = self.client.open_by_key(self.sheet_id)

    def upload_data(self, sheet_name, data):
        """
        NOTE: omit the first element of the data list if it is a date
        """
        sheet = self.workbook.worksheet(sheet_name)
        new_row_index = len(sheet.get_all_values()) + 1
        current_date = datetime.now().date()
        res_date = [current_date.strftime("%Y-%m-%d")]
        res = res_date + data
        sheet.insert_row(res, new_row_index)

    def upload_data_raw(self, sheet_name, data):
        sheet = self.workbook.worksheet(sheet_name)
        new_row_index = len(sheet.get_all_values()) + 1
        sheet.insert_row(data, new_row_index)
