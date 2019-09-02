# -*- coding: utf-8 -*-
"""
Created on Tue Aug 27 14:47:15 2019

@author: Babak Hosseini
"""

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pprint
import pandas as pd


# use creds to create a client to interact with the Google Drive API
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('C:/Keys/mongoDB_secret.json', scope)
client = gspread.authorize(creds)

# Find a workbook by name and open the first sheet
# Make sure you use the right name here.
sheet = client.open("test").sheet1

# Extract and print all of the values
#list_of_hashes = sheet.get_all_records()

#to get all the values inside the file
list_of_hashes=sheet.get_all_values()
#to get exact row values in a second row (Since 1st row is the header)
sheet.row_values(2)
#to get all the column values in the column 'place'
sheet.col_values(16)
#to extract a particular cell value
sheet.cell(1, 1).value


pp = pprint.PrettyPrinter()
pp.pprint(list_of_hashes)



temp_SQL=pd.DataFrame(list_of_hashes)
                      
temp_SQL=pd.DataFrame(list_of_hashes, columns = ['servertime','description',
                                                         'checkstatus','consecutiveFails','dsc247',
                                                         'extra','checkid','deviceid']).sort_values(by = 
#                                                        'servertime')#, ascending = False)
                                                        ['checkid','servertime'])#, ascending = False)     




row = ["I'm","inserting","a","new","row","into","a,","Spreadsheet","using","Python"]
index = 3
sheet.insert_row(row, index)
sheet.update_cell(2, 1, "telemedicine_id")
