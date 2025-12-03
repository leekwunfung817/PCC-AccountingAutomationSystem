

import sys
import db_lib

get_db_connection = db_lib.get_db_connection


# Connect to MariaDB database
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS budget_expense (
    file_name VARCHAR(255),
    sheet_name VARCHAR(100),
    account_name_buffer VARCHAR(255),
    January DECIMAL(10,2),
    February DECIMAL(10,2),
    March DECIMAL(10,2),
    April DECIMAL(10,2),
    May DECIMAL(10,2),
    June DECIMAL(10,2),
    July DECIMAL(10,2),
    August DECIMAL(10,2),
    September DECIMAL(10,2),
    October DECIMAL(10,2),
    November DECIMAL(10,2),
    December DECIMAL(10,2),
    Total DECIMAL(10,2)
);
""")
conn.commit()
conn.close()


def get_first_dict_element(my_dict):
    # my_dict = {'a': 1, 'b': 2, 'c': 3}
    # Get first key-value pair
    first_key = next(iter(my_dict))
    first_value = my_dict[first_key]
    print('first_key::::',first_key, first_value)
    return first_value

def is_all_nan_dict(row):
    all_nan = True
    for key in row:
        ele = row[key]
        if str(ele)!='nan':
            # print('Not nan check -------- '+str(ele),key)
            all_nan = False
    return all_nan
















# Function to convert column index to Excel letters
def col_to_excel(col_idx):
    letters = ''
    while col_idx >= 0:
        letters = chr(col_idx % 26 + 65) + letters
        col_idx = col_idx // 26 - 1
    return letters




















import string


def to_excel_dict(df):
    cell_dict = {}
    for r_idx, row in enumerate(df.values, start=2):
        for c_idx, value in enumerate(row, start=1):
            col_letter = string.ascii_uppercase[c_idx - 1]
            cell_id = f"{col_letter}{r_idx}"
            cell_dict[cell_id] = value
    # print(cell_dict)
    return cell_dict




import pandas as pd
import numpy as np
import pprint

# Path to your Excel file


folder = "./budget_expense/"
file_name = "2025_Budget_Expense.xlsx"
file_path = folder+file_name

import json

def dict_to_insert_sql(data):
    table_name = "budget_expense"
    columns = ["file_name", "sheet_name", "account_name_buffer", "property"] + list(data["data"].keys())
    values = [data["file_name"], data["sheet_name"], data["account_name_buffer"], data["property"]] + list(data["data"].values())
    formatted_values = [f"'{v}'" if isinstance(v, str) else str(v) for v in values]
    insert_statement = f"REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({', '.join(formatted_values)});"
    print(insert_statement)


    # Connect to MariaDB database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(insert_statement)

    conn.commit()
    conn.close()


# from openpyxl import load_workbook
# wb = load_workbook(file_path)
# sheet = wb.active

# # Create a dictionary with cell IDs as keys
# cell_dict = {}
# for row in sheet.iter_rows():
#     for cell in row:
#         cell_dict[cell.coordinate] = cell.value

# print(cell_dict)

# sys.exit()


import time
import pandas as pd
# Path to your Excel file
# file_path = "your_excel_file.xlsx"

# Read all sheets into a dictionary of DataFrames
all_sheets = pd.read_excel(file_path, sheet_name=None, keep_default_na=True)

# # Iterate through each sheet
# for sheet_name, df in all_sheets.items():
#     print(f"\n=== Sheet: {sheet_name} ===")
    
#     # Convert DataFrame to dictionary (records format)
#     data_dict = to_excel_dict(df)
#     print(data_dict)
#     # data_dict = df.to_dict()
#     # print(data_dict)
#     # df_list = df.values.tolist()
    
#     # Print as a table
#     # print(df.to_string(index=False))
#     # print(df_list)
#     break
# sys.exit()

# Iterate through each sheet
for sheet_name, df in all_sheets.items():
    print(f"\n=== Sheet: {sheet_name} ===")
    
    # Convert DataFrame to dictionary (records format)
    data_dict = df.to_dict(orient="records")
    df_list = df.values.tolist()
    
    # Print as a table
    # print(df.to_string(index=False))
    # print(df_list)
    
    # Optional: print the dictionary representation
    # print(data_dict)
    print(' =========================================== ')
    account_name_buffer = None
    for row in data_dict:
        property_ = None
        print(' ')
        all_nan = is_all_nan_dict(row)
        if 'Unnamed: 2' in row and row['Unnamed: 2']=='January':
            continue
        if all_nan:
            print(' ')
            print(' ------------------------------------------------ ')
            print(' ')
            continue
        print('File Name: ',file_name)
        print('Sheet Name: ', sheet_name)
        
        if 'Unnamed: 0' in row:
            if ( 'Unnamed: 0' in row and str(row['Unnamed: 0'])!='nan' ):
                account_name = row['Unnamed: 0']
                account_name_buffer = account_name
        special_key = 'Note: 4th week meetings, talk about accrued expenses'
        if special_key in row and account_name_buffer is None:
            if ( special_key in row and str(row[special_key])!='nan' ):
                account_name = row[special_key]
                account_name_buffer = account_name
        print('Check ',"\""+sheet_name+"\"")
        if account_name_buffer is None and ( sheet_name in row and str(row[sheet_name])!='nan' ):
            account_name = row[sheet_name]
            account_name_buffer = account_name
        if account_name_buffer is not None:
            print("Account: ",str(account_name_buffer))
        if account_name_buffer is None or str(account_name_buffer)=='nan':
            account_name_buffer = get_first_dict_element(row)


        if account_name_buffer is not None:
            print("Account: ",str(account_name_buffer))
        if 'Unnamed: 1' in row and str(row['Unnamed: 1'])!='nan':
            property_ = row['Unnamed: 1']
            print('Property: ',property_)
        if property_ is None:
            print('property_ is None')
            print(row)
            time.sleep(2)
            continue
        else:
            property_ = str(property_)
        data_buffer = None
        try:
            data = [
                row['Unnamed: 2']
                ,row['Unnamed: 3']
                ,row['Unnamed: 4']
                ,row['Unnamed: 5']
                ,row['Unnamed: 6']
                ,row['Unnamed: 7']
                ,row['Unnamed: 8']
                ,row['Unnamed: 9']
                ,row['Unnamed: 10']
                ,row['Unnamed: 11']
                ,row['Unnamed: 12']
                ,row['Unnamed: 13']
                ,row['Unnamed: 14']
                ,row['Unnamed: 15']
            ]
            print(data)
            data_buffer = data
        except Exception as e:
            pass
        try:
            data = [
                row['January']
                ,row['February']
                ,row['March']
                ,row['April']
                ,row['May']
                ,row['June']
                ,row['July']
                ,row['August']
                ,row['September']
                ,row['October']
                ,row['November']
                ,row['December']
                ,row['Total']
            ]
            # print(data)
            data_buffer = data
        except Exception as e:
            pass
        if data_buffer is not None:
            insert_data = {
                'January': data_buffer[0]
                ,'February': data_buffer[1]
                ,'March': data_buffer[2]
                ,'April': data_buffer[3]
                ,'May': data_buffer[4]
                ,'June': data_buffer[5]
                ,'July': data_buffer[6]
                ,'August': data_buffer[7]
                ,'September': data_buffer[8]
                ,'October': data_buffer[9]
                ,'November': data_buffer[10]
                ,'December': data_buffer[11]
                ,'Total': data_buffer[12]
            }
            if is_all_nan_dict(insert_data):
                continue
            for key__ in insert_data:
                if str(insert_data[key__])=='nan':
                    insert_data[key__] = 0
                if isinstance(insert_data[key__],str):
                    # print('Detected string')
                    if '\'' in insert_data[key__]:
                        insert_data[key__] = insert_data[key__].replace('\'','\\\'')
                        # print('Replaced \'')
                # print(type(insert_data[key__]),insert_data[key__])
            insert_buffer = {
                'file_name':file_name.replace('\'','\\\''),
                'sheet_name':sheet_name.replace('\'','\\\''),
                'account_name_buffer':str(account_name_buffer).replace('\'','\\\''),
                'property':property_,
                'data': insert_data
            }
            print(insert_buffer)
            dict_to_insert_sql(insert_buffer)
            if account_name_buffer is None or isinstance(account_name_buffer, float):
                print('account_name_buffer null')
                print(row)
                time.sleep(4)
        print(row)
