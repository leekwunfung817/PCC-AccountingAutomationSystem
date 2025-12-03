
import get_db_connection

get_db_connection = db_lib.get_db_connection




from datetime import datetime

def convert_dates_to_mmddyy(date_str):
    # Define possible date formats
    date_formats = [
        "%b %d, %Y",   # e.g., Aug 31, 2025
        "%m/%d/%y",    # e.g., 09/19/25 or 9/30/25
        "%m/%d/%Y",    # e.g., 10/31/2025 or 10/02/2025
        "%d %b %Y",    # e.g., 02 Oct 2025
    ]
    
    converted_date = None
    
    # for date_str in date_list:
    for fmt in date_formats:
        try:
            # Try parsing the date string with the current format
            parsed_date = datetime.strptime(date_str, fmt)
            # Format the date as Mm.dd.yy
            formatted_date = parsed_date.strftime("%m.%d.%y")
            converted_date = formatted_date
            break  # Exit the loop once a format matches
        except ValueError:
            continue  # Try the next format if parsing fails
    print(date_str)
    print(converted_date)
    return converted_date



from typing import List, Dict
def has_text(data: List[Dict], search_text: str) -> bool:
    """
    Check if any dictionary in the data list contains the specified text.

    Parameters:
    - data: List of dictionaries, each with a 'text' key.
    - search_text: The text to search for.

    Returns:
    - True if the text is found in any dictionary, False otherwise.
    """
    return any(item.get('text') == search_text for item in data)

def has_substring(data: List[Dict], search_text: str) -> bool:
    """
    Check if any dictionary in the data list contains the specified text.

    Parameters:
    - data: List of dictionaries, each with a 'text' key.
    - search_text: The text to search for.

    Returns:
    - True if the text is found in any dictionary, False otherwise.
    """
    return any(search_text in item.get('text') for item in data)

# Example usage:
# result = has_text(page_data, 'INVOICE')
# print(result)  # Output: True or False


# The following program is to read the pdf document and to get the text fields and all structural data to print them out
# change the following program to add the location, coordination, and related or close item next to the text.


def extract_table_rows(column_count,data: List[Dict]) -> List[List[Dict]]:
    rows = []
    used_items = set()

    for item in data:
        if item['text'].strip() == '':
            continue
        y_top = item['bbox'][1]
        y_bottom = item['bbox'][3]
        if '(' in item["text"] and ')' not in item["text"]:
            item["text"] += ' '+item["related_items"][0]['text']
        row_items = [{
            'text':item["text"],
            'bbox':item["bbox"]
        }]
        used_items.add(id(item))

        for other in data:
            if id(other) in used_items or other['text'].strip() == '':
                continue
            other_y_top = other['bbox'][1]
            other_y_bottom = other['bbox'][3]

            is_same_line = ( item["bbox"][1] < other["bbox"][1] and other["bbox"][1] < item["bbox"][3] )
            is_same_line = is_same_line or ( item["bbox"][1] < other["bbox"][3] and other["bbox"][3] < item["bbox"][3] )
            is_same_line = is_same_line or ( other["bbox"][1] < item["bbox"][1] and item["bbox"][1] < other["bbox"][3] )
            is_same_line = is_same_line or ( other["bbox"][1] < item["bbox"][3] and item["bbox"][3] < other["bbox"][3] )


            # Check if the vertical overlap is significant (same row)
            # if min(y_bottom, other_y_bottom) - max(y_top, other_y_top) > 5:
            if is_same_line:
                # row_items.append(other)
                if '(' in other["text"] and ')' not in other["text"]:
                    other["text"] += ' '+other["related_items"][0]['text']
                row_items.append({
                    'text':other["text"],
                    'bbox':other["bbox"]
                })
                used_items.add(id(other))

        # If row has exactly 3 items, consider it a valid table row
        if len(row_items) == column_count:
            rows.append(sorted(row_items, key=lambda x: x['bbox'][0]))  # sort by x-coordinate

    return rows




# pip install pymupdf
import fitz  # PyMuPDF
import fitz  # PyMuPDF
import math

import sqlite3
import json


def clean_string(original, substring_to_remove):
    cleaned = original.replace(substring_to_remove, "")
    return cleaned.strip()

def is_same_line(spans, tolerance=10):
    """Check if all spans are on the same horizontal line within a tolerance."""
    y_coords = [span["bbox"][1] for span in spans]  # y0 of each bbox
    return max(y_coords) - min(y_coords) <= tolerance

# Function to compute center of a bounding box
def get_center(bbox):
    x0, y0, x1, y1 = bbox
    return ((x0 + x1) / 2, (y0 + y1) / 2)

def is_below(bbox1, bbox2):
    """
    Returns True if bbox1 is vertically below bbox2.
    Each bbox is a tuple or list: (x0, y0, x1, y1)
    """
    _, y0_1, _, y1_1 = bbox1
    _, y0_2, _, y1_2 = bbox2

    # Check if the top of bbox1 is below the bottom of bbox2
    return y0_1 > y1_2

def is_box1_right_of_box2(box1, box2):
    """
    Checks if box1 is to the right of box2 and the vertical center of box2
    is within the vertical bounds of box1.

    Each box is defined as (x0, y0, x1, y1), where:
    - (x0, y0) is the top-left corner
    - (x1, y1) is the bottom-right corner
    """

    # Unpack coordinates
    x0_1, y0_1, x1_1, y1_1 = box1
    x0_2, y0_2, x1_2, y1_2 = box2

    # Check if box1 is to the right of box2
    box1_left_is_right_of_box2_right = x0_1 > x1_2

    # Compute vertical center of box2
    box2_center_y = (y0_2 + y1_2) / 2

    # Check if box2's center is within box1's vertical bounds
    box2_center_within_box1_vertical = y0_1 <= box2_center_y <= y1_1

    return box1_left_is_right_of_box2_right and box2_center_within_box1_vertical



from datetime import datetime

def is_valid_us_date(date_str):
    try:
        datetime.strptime(date_str, "%d %b %Y")
        return True
    except ValueError:
        return False

# Example usage
# print(is_valid_us_date("02 Oct 2025"))  # True
# print(is_valid_us_date("2025-10-02"))   # False
import re


def PCCInvoicePdfProcess(input_pdf_file_name):

    # Connect to MariaDB database
    conn = get_db_connection()
    cursor = conn.cursor()

    # Create main table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoices (
        InvoiceNo VARCHAR(100),
        Date VARCHAR(100),
        PayableTo VARCHAR(100),
        Total VARCHAR(100),
        Email VARCHAR(100),
        PaymentMethod VARCHAR(100),
        BankName VARCHAR(100),
        AccountNumber VARCHAR(100),
        RoutingNumber VARCHAR(100),
        Subtotal VARCHAR(100),
        AmountDue VARCHAR(100),
        BillTo VARCHAR(100),
        PRIMARY KEY (AccountNumber, RoutingNumber)
    )
    """)

    # Create table_row table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS invoice_items (
        AccountNumber VARCHAR(100),
        RoutingNumber VARCHAR(100),
        ItemDate VARCHAR(100),
        Description VARCHAR(100),
        Amount VARCHAR(100),
        Quantity VARCHAR(100),
        Total VARCHAR(100),
        PRIMARY KEY (AccountNumber, RoutingNumber, ItemDate, Description)
    )
    """)


    invoice_format = None
    # Load the PDF
    input_pdf = './uploads/'+input_pdf_file_name
    pdf_path = input_pdf
    doc = fitz.open(pdf_path)

    # Dictionary to store text content by page
    pdf_text_dict = {}

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")  # Extract plain text
        pdf_text_dict[f"page_{page_num + 1}"] = text.split('\n')

    # Assuming pdf_text_dict is already created
    # print(json.dumps(pdf_text_dict, indent=4, ensure_ascii=False))

    # Load the PDF
    doc = fitz.open(input_pdf)

    # Dictionary to store structured text content by page
    pdf_structured_data = {}

    # Iterate through each page
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        blocks = page.get_text("dict")["blocks"]

        page_data = []
        for block in blocks:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_item = {
                            "text": span["text"],
                            "bbox": span["bbox"],  # Bounding box coordinates (x0, y0, x1, y1)
                            "font": span["font"],
                            "size": span["size"],
                            "related_items": []
                        }

                        # Find related items based on proximity
                        for other_block in blocks:
                            if "lines" in other_block:
                                for other_line in other_block["lines"]:
                                    for other_span in other_line["spans"]:
                                        if other_span["text"] != span["text"]:
                                            ox0, oy0, ox1, oy1 = other_span["bbox"]
                                            sx0, sy0, sx1, sy1 = span["bbox"]
                                            if abs(ox0 - sx0) < 20 and abs(oy0 - sy0) < 20:
                                                text_item["related_items"].append({
                                                    "text": other_span["text"],
                                                    "bbox": other_span["bbox"]
                                                })
                        page_data.append(text_item)

        ######################################################################################################
        # closet element extract
        ######################################################################################################
        # Just Below
        # After collecting all items on the page
        for item in page_data:
            item_center = get_center(item["bbox"])
            min_distance = float("inf")
            min_distance = 100
            closest = []
            closest_item = None
            for other in page_data:
                if other["text"] != item["text"]:
                    other_center = get_center(other["bbox"])
                    distance = math.sqrt((item_center[0] - other_center[0])**2 + (item_center[1] - other_center[1])**2)
                    if distance < min_distance and is_below(other["bbox"], item["bbox"]):
                        min_distance = distance
                        closest_item = {
                            "text": other["text"],
                            "bbox": other["bbox"],
                            "is_below": is_below(other["bbox"], item["bbox"]),
                            "distance": round(distance, 2)
                        }
            if closest_item is not None:
                closest.append(closest_item)
            if closest is not None:
                item['closest'] = closest


        # Just right
        # After collecting all items on the page
        for item in page_data:
            item_center = get_center(item["bbox"])
            min_distance = float("inf")
            min_distance = 300
            closest = []
            closest_item = None
            for other in page_data:
                if other["text"] != item["text"]:
                    other_center = get_center(other["bbox"])
                    distance = math.sqrt((item_center[0] - other_center[0])**2 + (item_center[1] - other_center[1])**2)
                    if distance < min_distance and is_box1_right_of_box2(other["bbox"], item["bbox"]):
                        min_distance = distance
                        closest_item = {
                            "text": other["text"],
                            "bbox": other["bbox"],
                            "is_onright": is_box1_right_of_box2(other["bbox"], item["bbox"]),
                            "distance": round(distance, 2)
                        }
            if closest_item is not None:
                closest.append(closest_item)
            if closest is not None:
                item['on_right'] = closest
        pdf_structured_data[f"page_{page_num + 1}"] = page_data

    def reach_toright(item_bbox):
        closest = []
        closest_item = None
        for page_name in pdf_structured_data:
            page_data = pdf_structured_data[page_name]
            item_center = get_center(item_bbox)
            min_distance = float("inf")
            min_distance = 1000
            for other in page_data:
                if other["text"] != item["text"]:
                    
                    other_center = get_center(other["bbox"])
                    is_same_line = ( item_bbox[1] < other["bbox"][1] and other["bbox"][1] < item_bbox[3] )
                    is_same_line = is_same_line or ( item_bbox[1] < other["bbox"][3] and other["bbox"][3] < item_bbox[3] )
                    is_same_line = is_same_line or ( other["bbox"][1] < item_bbox[1] and item_bbox[1] < other["bbox"][3] )
                    is_same_line = is_same_line or ( other["bbox"][1] < item_bbox[3] and item_bbox[3] < other["bbox"][3] )

                    is_right = other["bbox"][2] > item_bbox[2]

                    distance = math.sqrt((item_center[0] - other_center[0])**2 + (item_center[1] - other_center[1])**2)
                    if distance < min_distance and is_same_line:
                        # print(other["text"])
                        # print(other["bbox"])
                        # x0, y0, x1, y1
                        if is_right:
                            min_distance = distance
                            closest_item = {
                                "text": other["text"],
                                "bbox": other["bbox"],
                                "is_onright": is_box1_right_of_box2(other["bbox"], item["bbox"]),
                                "distance": round(distance, 2)
                            }
            if closest_item is not None:
                closest.append(closest_item)
            if closest is not None:
                item['on_right'] = closest
        return closest_item

    def get_related_items(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if 'related_items' in text_block_dict and len(text_block_dict['related_items'])>0:
                    related_item_text = text_block_dict['related_items'][0]['text']
                    if search_key_word in text_block_dict['text']:
                        return related_item_text
        print('get_related_items got nothing from '+search_key_word)

    def get_closet_below(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if 'closest' in text_block_dict and len(text_block_dict['closest'])>0:
                    if search_key_word in text_block_dict['text']:
                        return text_block_dict['closest'][0]['text']
        print('get_closet_below got nothing from '+search_key_word)

    def get_closet_right(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if 'on_right' in text_block_dict and len(text_block_dict['on_right'])>0:
                    on_right = text_block_dict['on_right'][0]['text']
                    if search_key_word in text_block_dict['text']:
                        return on_right
        print('get_closet_right got nothing from '+search_key_word)

    def get_trim(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if search_key_word in text_block_dict['text']:
                    return clean_string(text_block_dict['text'], search_key_word)

        print('get_trim got nothing from '+search_key_word)

    def get_trim_from_desire_list(key_word):
        for page_name in pdf_text_dict:
            for list_item in pdf_text_dict[page_name]:
                if key_word in list_item:
                    return clean_string(list_item, key_word)

    def get_exact(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if search_key_word in text_block_dict['text']:
                    return clean_string(text_block_dict['text'], ' ')
        print('get_exact got nothing from '+search_key_word)

    def get_exact_same_whole_element(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if search_key_word == text_block_dict['text']:
                    return text_block_dict
        print('get_exact got nothing from '+search_key_word)

    def get_exact_whole_element(search_key_word):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if search_key_word in text_block_dict['text']:
                    return text_block_dict
        print('get_exact got nothing from '+search_key_word)

    def get_exact_by_format(format__):
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if bool(re.match(format__, text_block_dict['text'])):
                    return text_block_dict

    def get_us_date():
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if is_valid_us_date(text_block_dict['closest'][0]['text']):
                    return text_block_dict['closest'][0]['text']

    def get_desire_list(key_word, length_):
        desire_list_begin = False
        desire_list = []
        for page_name in pdf_text_dict:
            for list_item in pdf_text_dict[page_name]:
                if desire_list_begin:
                    desire_list.append(list_item)
                if key_word in list_item:
                    desire_list_begin = True
                if len(desire_list) > length_:
                    return desire_list
        return desire_list

    invoice_format_name = None
    if True and (
        has_substring(page_data, 'Date:') 
        and has_substring(page_data, 'No. Invoice :') 
        and has_substring(page_data, 'Payable to:')
        and has_substring(page_data, 'Bill To')
        and has_substring(page_data, 'Payment Method:')
        and has_substring(page_data, 'Bank Name:')
        and has_substring(page_data, 'Account Number:')
        and has_substring(page_data, 'Routing Number:')
        and has_substring(page_data, 'THANK YOU!')
        and has_substring(page_data, 'Total:')
        and has_substring(page_data, 'Subtotal:')
        and has_substring(page_data, 'Total:')
        and has_substring(page_data, 'Amount Due:')
        ):
        invoice_format_name = 'INVOICE-EX.'
    if True and (
        has_substring(page_data, 'BILLED TO:') 
        and has_substring(page_data, 'Invoice No.')
        and has_substring(page_data, 'Subject')
        and has_substring(page_data, 'Thank you!')
        and has_substring(page_data, 'PAYMENT INFORMATION')
        and has_substring(page_data, 'Account#')
        and has_substring(page_data, 'INVOICE')
        ):
        invoice_format_name = 'INVOICE'
    if True and (
        # True
        has_substring(page_data, 'Google')
        and has_substring(page_data, 'Invoice number:')
        and has_substring(page_data, 'Account:')
        and has_substring(page_data, 'Account budget:')
        # and has_substring(page_data, 'Federal Tax ID:')
        # and has_substring(page_data, 'Bill to')
        # and has_substring(page_data, 'Details')
        ):
        invoice_format_name = 'Google LLC'

    if True and (
        # True
        has_substring(page_data, 'TOTAL DUE')
        and has_substring(page_data, 'Remit To:')
        and has_substring(page_data, 'Salesperson')
        and has_substring(page_data, 'Date Shipped')
        and has_substring(page_data, '@ee3.com')
        and has_substring(page_data, 'Edward Enterprises, Inc.')
        ):
        invoice_format_name = 'Edward Enterprises'

    if True and (
        # True
        has_substring(page_data, 'Finn Partners, Inc')
        and has_substring(page_data, 'Bill To')
        and has_substring(page_data, 'Due Date:')
        and has_substring(page_data, 'Please Wire Funds To:')
        and has_substring(page_data, 'Subtotal')
        and has_substring(page_data, 'Total (')
        ):
        invoice_format_name = 'Finn Partners'

    if True and (
        # True
        has_substring(page_data, 'AIA Corporation')
        and has_substring(page_data, 'INVOICE')
        and has_substring(page_data, 'INVOICE DATE')
        and has_substring(page_data, 'PAGE')
        and has_substring(page_data, 'EAIA Order #')
        and has_substring(page_data, 'YOUR REF/PO#')
        ):
        invoice_format_name = 'AIA'

    print(' ================================================================ ')
    print(' ================================================================ ')
    print(' ================================================================ ')
    print(json.dumps(pdf_structured_data, indent=4, ensure_ascii=False))
    print(json.dumps(pdf_text_dict, indent=4, ensure_ascii=False))
    print('invoice_format_name::::::::::::::::',invoice_format_name)
    print('input_pdf::::::::::::::::',input_pdf)
    print(' ================================================================ ')
    print(' ================================================================ ')
    print(' ================================================================ ')


    # Invoice No    procesed_information['InvoiceNo'] 
    # date    procesed_information['Date']
    # total    procesed_information['Total']
    # Payable To (name of vender)    procesed_information['PayableTo']

    procesed_information = {}
    ######################################################################################################
    # assign information after extract
    ######################################################################################################

    procesed_information['PaymentMethod'] = None
    procesed_information['BankName'] = None
    procesed_information['AccountNumber'] = None
    procesed_information['RoutingNumber'] = None
    procesed_information['Subtotal'] = None
    procesed_information['ItemDescription'] = None
    procesed_information['Email'] = None
    procesed_information['BillTo'] = None
    procesed_information['AmountDue'] = None



    if invoice_format_name == 'INVOICE-EX.':
        five_column_lines = extract_table_rows(5, page_data)
        procesed_information['table_row'] = five_column_lines
        procesed_information['InvoiceNo'] = get_related_items('No. Invoice :')
        procesed_information['Date'] = get_related_items('Date:')
        procesed_information['PayableTo'] = get_related_items('Payable to:')
        procesed_information['PaymentMethod'] = get_trim('Payment Method: ')
        procesed_information['BankName'] = get_trim('Bank Name:')
        procesed_information['AccountNumber'] = get_trim('Account Number:')
        procesed_information['RoutingNumber'] = get_trim('Routing Number:')
        procesed_information['AmountDue'] = get_trim('Amount Due:')
        procesed_information['Total'] = get_trim('Total:')
        procesed_information['Subtotal'] = get_trim('Subtotal:')
        procesed_information['ItemDescription'] = get_exact('Item Description')
        procesed_information['Email'] = get_exact('@')
        procesed_information['BillTo'] = get_closet_right('Bill To')
        # Insert into invoices table
        data = procesed_information
        cursor.execute("""
        REPLACE INTO invoices (
            InvoiceNo, Date, PayableTo, Total,
            Email, PaymentMethod, BankName,
            AccountNumber, RoutingNumber,
            Subtotal, AmountDue, BillTo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["InvoiceNo"],
            data["Date"],
            data["PayableTo"],
            data["Total"],
            data["Email"],
            data["PaymentMethod"],
            data["BankName"],
            data["AccountNumber"],
            data["RoutingNumber"],
            data["Subtotal"],
            data["AmountDue"],
            data["BillTo"]
        ))

        # Insert into invoice_items table
        for row in data["table_row"]:
            cursor.execute("""
            REPLACE INTO invoice_items (
                AccountNumber,
                RoutingNumber,
                ItemDate,
                Description,
                Amount,
                Quantity,
                Total
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                data["AccountNumber"],
                data["RoutingNumber"],
                row[0]['text'],  # ItemDate
                row[1]['text'],  # Description
                row[2]['text'],  # Amount
                row[3]['text'],  # Quantity
                row[4]['text']   # Total
            ))

        
    if invoice_format_name == 'INVOICE':
        procesed_information['Email'] = ''
        procesed_information['RoutingNumber'] = ''
        procesed_information['Subtotal'] = ''
        procesed_information['AmountDue'] = ''
        procesed_information['PayableTo'] = get_related_items('PAYMENT INFORMATION')
        procesed_information['InvoiceNo'] = get_trim('Invoice No.')
        procesed_information['BillTo'] = get_closet_right('BILLED TO:')
        procesed_information['Date'] = get_us_date()
        procesed_information['BankName'] = get_exact(' Bank')
        procesed_information['AccountNumber'] = get_trim('Account#')
        for page_num in pdf_structured_data:
            for text_block_dict in pdf_structured_data[page_num]:
                if 'on_right' in text_block_dict and len(text_block_dict['on_right'])>0:
                    on_right = text_block_dict['on_right'][0]['text']
                    if 'Total' == text_block_dict['text'] and '$' in on_right:
                        procesed_information['Total'] = on_right
        three_column_lines = extract_table_rows(3, page_data)
        procesed_information['table_row'] = three_column_lines
        if has_substring(page_data, ' Bank'):
            procesed_information['PaymentMethod'] = 'Bank'
        else:
            procesed_information['PaymentMethod'] = 'Other'
        data = procesed_information
        # Insert into invoices table
        cursor.execute("""
        REPLACE INTO invoices (
            InvoiceNo, Date, PayableTo, Total,
            Email, PaymentMethod, BankName,
            AccountNumber, RoutingNumber,
            Subtotal, AmountDue, BillTo
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            data["InvoiceNo"],
            data["Date"],
            data["PayableTo"],
            data["Total"],
            data["Email"],
            data["PaymentMethod"],
            data["BankName"],
            data["AccountNumber"],
            data["RoutingNumber"],
            data["Subtotal"],
            data["AmountDue"],
            data["BillTo"]
        ))
        for row in data["table_row"]:
            if 'Total' == row[2]['text']:
                continue
            cursor.execute("""
            REPLACE INTO invoice_items (
                AccountNumber,
                RoutingNumber,
                ItemDate,
                Description,
                `Quantity`,
                Total
            ) VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                data["AccountNumber"],
                data["RoutingNumber"],
                data["Date"],      # ItemDate
                row[0]['text'],    # Description
                row[1]['text'],    # Hours
                row[2]['text']     # Total
            ))

    if invoice_format_name == 'Google LLC':
        procesed_information['Email'] = get_exact('@').replace('Forquestionsaboutthisinvoicepleaseemail','')
        procesed_information['InvoiceNo'] = get_trim('Invoice number:')
        bbox = get_exact_whole_element('Total in USD')['bbox']
        procesed_information['AmountDue'] = reach_toright(bbox)['text']
        procesed_information['Total'] = procesed_information['AmountDue']
        # print(json.dumps(bbox, indent=4, ensure_ascii=False))
        procesed_information['DateRange'] = (get_exact_by_format(r'^[A-Za-z]{3} \d{1,2}, \d{4} - [A-Za-z]{3} \d{1,2}, \d{4}$')['text'])
        desire_list = get_desire_list('Total amount due in ', 3)
        procesed_information['Subtotal'] = desire_list[0]
        procesed_information['Date'] = get_desire_list('Invoice number: ', 4)[3]
        procesed_information['BillTo'] = get_desire_list('Invoice number: ', 8)[7]
        procesed_information['AccountNumber'] = get_desire_list('Invoice number: ', 10)[9]
        procesed_information['PayableTo'] = get_trim_from_desire_list('Account holder name:')
        procesed_information['PaymentMethod'] = get_trim_from_desire_list('Bank:')
        procesed_information['BankName'] = get_trim_from_desire_list('Bank:')
        procesed_information['RoutingNumber'] = get_trim_from_desire_list('ABA/Bank Routing #:')

    if invoice_format_name == 'Edward Enterprises':
        procesed_information['Total'] = get_closet_right('Invoice Total')
        procesed_information['Date'] = get_closet_right('Invoice Date')
        procesed_information['InvoiceNo'] = get_closet_right('Invoice Number')
        procesed_information['PayableTo'] = get_exact('Edward Enterprises, Inc.')
        # print(json.dumps( get_exact_whole_element('Invoice Date') , indent=4, ensure_ascii=False))

        # Invoice No    procesed_information['InvoiceNo'] 
        # date    procesed_information['Date']
        # total    procesed_information['Total']
        # Payable To (name of vender)    procesed_information['PayableTo']

        print(json.dumps(procesed_information, indent=4, ensure_ascii=False))
        data = procesed_information
        cursor.execute("""
        REPLACE INTO invoices (InvoiceNo, Date, PayableTo, Total)
        VALUES (%s, %s, %s, %s)
        """, (
            data["InvoiceNo"],
            data["Date"],
            data["PayableTo"],
            data["Total"]
        ))

    if invoice_format_name == 'Finn Partners':
        procesed_information['Total'] = get_closet_right('TOTAL(USD):')
        procesed_information['Date'] = get_closet_right('Due Date:')
        procesed_information['InvoiceNo'] = get_trim('INVOICE ')
        procesed_information['PayableTo'] = 'Finn Partners, Inc'
        # print(json.dumps( get_exact_whole_element('Invoice Date') , indent=4, ensure_ascii=False))

        # Invoice No    procesed_information['InvoiceNo'] 
        # date    procesed_information['Date']
        # total    procesed_information['Total']
        # Payable To (name of vender)    procesed_information['PayableTo']

        print(json.dumps(procesed_information, indent=4, ensure_ascii=False))
        data = procesed_information
        cursor.execute("""
        REPLACE INTO invoices (InvoiceNo, Date, PayableTo, Total)
        VALUES (%s, %s, %s, %s)
        """, (
            data["InvoiceNo"],
            data["Date"],
            data["PayableTo"],
            data["Total"]
        ))

    if invoice_format_name == 'AIA':
        # procesed_information['Total'] = get_closet_right('TOTAL(USD):')
        # procesed_information['Date'] = get_closet_right('Due Date:')
        procesed_information['InvoiceNo'] = get_exact_same_whole_element('INVOICE')['on_right'][0]['text']
        procesed_information['Date'] = get_exact_same_whole_element('INVOICE DATE')['on_right'][0]['text']
        procesed_information['Total'] = get_exact_same_whole_element('Total Due')['on_right'][0]['text']
        procesed_information['PayableTo'] = 'AIA CORPORATION'
        # print(json.dumps( get_exact_whole_element('Invoice Date') , indent=4, ensure_ascii=False))

        # Invoice No    procesed_information['InvoiceNo'] 
        # date    procesed_information['Date']
        # total    procesed_information['Total']
        # Payable To (name of vender)    procesed_information['PayableTo']

        print(json.dumps(procesed_information, indent=4, ensure_ascii=False))
        data = procesed_information
        cursor.execute("""
        REPLACE INTO invoices (InvoiceNo, Date, PayableTo, Total)
        VALUES (%s, %s, %s, %s)
        """, (
            data["InvoiceNo"],
            data["Date"],
            data["PayableTo"],
            data["Total"]
        ))
    destination_file_name = None
    if 'InvoiceNo' in procesed_information and 'Date' in procesed_information and 'PayableTo' in procesed_information and 'Total' in procesed_information:
        destination_file_name = convert_dates_to_mmddyy(procesed_information['Date'])+'~$'+procesed_information['Total'].replace('$','')+'~'+procesed_information['PayableTo']+'~Inv#'+procesed_information['InvoiceNo']+'~.pdf'
        # doc.save('./accounting-invoice-buffer/'+)
    # Print the structured data with location and related items

    print('Format '+invoice_format_name)
    data = procesed_information
    # Commit and close
    conn.commit()
    conn.close()
    return destination_file_name

if __name__ == '__main__':
    # input_folder = './accounting-invoice/'
    PCCInvoicePdfProcess('Black And Gray Minimal Freelancer Invoice .pdf')
    PCCInvoicePdfProcess('Ivan Lee Example Invoice.pdf')
    PCCInvoicePdfProcess('8.31.25-$106,684.02-Google-Inv#5350417220-GL5100_510.pdf')
    PCCInvoicePdfProcess('9.30.25~$497.38~Edward Enterprises~Inv#D50156~GL5102_510.pdf')
    PCCInvoicePdfProcess('10.1.25~$8,376.96~Finn Partners~Inv#147813~GL5104_510.pdf')
    PCCInvoicePdfProcess('10.2.25~$492.14~320 Productions~Inv#KMO3251473~GL5101_510.pdf')
