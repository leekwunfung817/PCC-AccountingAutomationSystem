#!/usr/bin/env python3
import os
import json
import shutil
from datetime import datetime

import pymysql
from PyPDF2 import PdfReader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_DIR = os.path.join(BASE_DIR, "uploads")
PROCESSED_DIR = os.path.join(BASE_DIR, "processed")

DB_HOST = "localhost"
DB_NAME = "pcc_accounting"
DB_USER = "root"
DB_PASS = ""  # no password

os.makedirs(PROCESSED_DIR, exist_ok=True)


def get_db_connection():
    return pymysql.connect(
        host=DB_HOST,
        user=DB_USER,
        password=DB_PASS,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
    )


# def make_processed_name(stored_name: str) -> str:
#     """
#     Given the stored upload filename (e.g. 'a1b2c3.pdf'),
#     return a new processed filename (e.g. 'a1b2c3_processed.pdf').
#     """
#     base, ext = os.path.splitext(stored_name)
#     if not ext:
#         ext = ".pdf"
#     return f"{base}_processed{ext}"


def process_pdf_file(src_path: str, dest_path: str) -> dict:
    """
    Process a single PDF file.

    - Copies the file from src_path to dest_path.
    - Reads the PDF to count pages.
    - Computes file size in KB.
    - Returns an info dict with pages and size_kb.

    Raises FileNotFoundError if src_path does not exist.
    Propagates other exceptions from shutil / PyPDF2 as needed.
    """
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source file not found: {src_path}")

    # Copy file to processed folder using new name
    shutil.copy2(src_path, dest_path)

    # Extract info from original PDF
    pages = 0
    try:
        with open(src_path, "rb") as f:
            reader = PdfReader(f)
            pages = len(reader.pages)
    except Exception as e:
        # Logable warning; we still continue with pages=0
        print(f"Warning: could not read PDF pages for {src_path}: {e}")

    size_bytes = os.path.getsize(src_path)
    size_kb = size_bytes / 1024.0

    info = {
        "pages": pages,
        "size_kb": round(size_kb, 1),
    }

    return info


import pcc_invoice_pdf_process

def process_pending():
    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            # Fetch pending PDFs
            cur.execute("SELECT * FROM pdf_files WHERE status = 'pending'")
            rows = cur.fetchall()

            for row in rows:
                pdf_id = row["id"]
                stored_name = row["filename"]  # name in uploads/
                processed_name = pcc_invoice_pdf_process.PCCInvoicePdfProcess(stored_name)
                if processed_name is None:
                    print('Processed failed')
                    continue
                src_path = os.path.join(UPLOAD_DIR, stored_name)
                # processed_name = make_processed_name(stored_name)
                dest_path = os.path.join(PROCESSED_DIR, processed_name)

                print(f"Processing ID={pdf_id}, upload_file={stored_name}, processed_file={processed_name}")

                # Mark as processing
                cur.execute(
                    "UPDATE pdf_files SET status='processing' WHERE id=%s",
                    (pdf_id,),
                )
                conn.commit()

                try:
                    # Use the new function here
                    info = process_pdf_file(src_path, dest_path)
                    processed_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

                    # Update main table
                    cur.execute(
                        """
                        UPDATE pdf_files
                        SET status=%s,
                            info=%s,
                            processed_at=%s
                        WHERE id=%s
                        """,
                        (
                            "done",
                            json.dumps(info),
                            processed_at,
                            pdf_id,
                        ),
                    )

                    # Insert or update processed filename in the separate table
                    cur.execute(
                        """
                        INSERT INTO pdf_processed_files (pdf_id, processed_name)
                        VALUES (%s, %s)
                        ON DUPLICATE KEY UPDATE
                            processed_name = VALUES(processed_name)
                        """,
                        (pdf_id, processed_name),
                    )

                    conn.commit()

                except Exception as e:
                    print(f"Error processing {stored_name}: {e}")
                    cur.execute(
                        "UPDATE pdf_files SET status='error' WHERE id=%s",
                        (pdf_id,),
                    )
                    conn.commit()
    finally:
        conn.close()
        print("Done.")

import time

if __name__ == "__main__":
    while True:
        process_pending()
        time.sleep(10)
