""" 
reads indexes from db (previously built from meta jsons
loops through the csv files, if a matching index is found, reads the csv, leaves header row and values for last columns untouched, but replaces the other values with nomitemId (if it matches* dim_label x opt_label) and writes the compacted data to a new file

**if no match is found, leaves the currerent columns untouched but writes the exception to a log file
also write a log entry for each succesful file matched and processed. if files are found in folder but are in the index, or vice-versa, write a warning tow to the log

"""

lang = "ro"
lang = "en"

# input_folder="data/2-metas/" + lang
# output_folder="data/3-datasets/" + lang

import os
import csv
import sqlite3
from pathlib import Path

import os
import csv
import sqlite3
from pathlib import Path

# Configuration
input_csvs = "data/_obsolete/csv/"
db_path = "data/_obsolete/datasets.db"
db_table = 'fields'
compacted_folder = "data/_obsolete/compact-datasets/"
log_file = "data/_obsolete/compaction_log.txt"

def log_message(message):
    with open(log_file, 'a') as log:
        log.write(message + "\n")

def compact_dataset(dataset, db_conn, cursor):
    input_file_path = os.path.join(input_csvs, f"{dataset}.csv")
    compacted_file_path = os.path.join(compacted_folder, f"{dataset}.csv")

    # Check if already compacted
    if os.path.exists(compacted_file_path):
        log_message(f"Skipped {dataset}, already compacted.")
        return

    # Check if input file exists
    if not os.path.exists(input_file_path):
        log_message(f"Skipped {dataset}, input file not found.")
        return

    try:
        with open(input_file_path, 'r', encoding='utf-8') as csv_file:
            reader = csv.reader(csv_file)
            header = next(reader)
            rows = list(reader)

        # Create a mapping of (dimCode, opt_label) to nomItemId for this dataset
        cursor.execute(f"SELECT dimCode, opt_label, nomItemId FROM {db_table} WHERE fileid = ?", (dataset,))
        mapping = {(row[0], row[1]): row[2] for row in cursor.fetchall()}

        compacted_rows = [header]
        exceptions = []

        for row in rows:
            compacted_row = row[:]
            for i in range(len(row) - 1):  # Process all columns except the last one
                key = (i + 1, row[i])  # Match dimCode (1-indexed) with opt_label
                if key in mapping:
                    compacted_row[i] = str(mapping[key])
                else:
                    exceptions.append(f"No match for {key} in dataset {dataset}")
            compacted_rows.append(compacted_row)

        # Write compacted file
        os.makedirs(compacted_folder, exist_ok=True)
        with open(compacted_file_path, 'w', encoding='utf-8', newline='') as compacted_file:
            writer = csv.writer(compacted_file)
            writer.writerows(compacted_rows)

        # Log success
        log_message(f"Successfully compacted {dataset}")

        # Log exceptions
        if exceptions:
            with open(log_file, 'a') as log:
                log.write("\n".join(exceptions) + "\n")

    except Exception as e:
        log_message(f"Error processing {dataset}: {str(e)}")

def main():
    try:
        # Connect to SQLite database
        db_conn = sqlite3.connect(db_path)
        cursor = db_conn.cursor()

        # Get list of datasets
        cursor.execute(f"SELECT DISTINCT fileid AS dataset FROM {db_table}")
        datasets = [row[0] for row in cursor.fetchall()]

        if not datasets:
            log_message("No datasets found in database.")
            return

        for dataset in datasets:
            compact_dataset(dataset, db_conn, cursor)

    except Exception as e:
        log_message(f"Error in main process: {str(e)}")

    finally:
        if db_conn:
            db_conn.close()

if __name__ == "__main__":
    main()
