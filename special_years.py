import os
import pdfplumber
import csv
import re

# Directories
pdf_directory = "pdf_files"  # Directory containing PDFs
csv_directory = "csv_files"  # Directory to save CSV files

# Ensure the CSV directory exists
os.makedirs(csv_directory, exist_ok=True)

def write_to_csv(headers, data, csv_filename):
    """Write the headers and data to a CSV file."""
    if not headers or not data:
        print(f"Skipping CSV write for {csv_filename} as no valid headers or data found.")
        return
    
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(headers)  # Write the headers
        writer.writerows(data)  # Write the data rows
    print(f"CSV written to {csv_filename}")

def extract_year_from_filename(filename):
    """Extract the year from the filename using regex."""
    match = re.search(r'(\d{4})', filename)
    if match:
        return int(match.group(1))  # Return the year as an integer
    return None

def process_tables_for_report(pdf, page_start, page_end, report_year):
    """Extract and process tables from specified pages."""
    
    for page_num in range(page_start, page_end + 1):
        page = pdf.pages[page_num - 1]
        tables = page.extract_tables()

        if not tables:
            print(f"No tables found on page {page_num} of the {report_year} report")
            continue

        for table in tables:
            # Assuming the first row contains headers and the remaining rows are data
            headers = table[0]
            data = table[1:]

            # Debug: Check extracted table content
            print(f"Headers on page {page_num} of the {report_year} report: {headers}")
            print(f"Data on page {page_num} of the {report_year} report: {data}")

            if headers and data:
                csv_filename = os.path.join(csv_directory, f"PREA_Report_{report_year}_page_{page_num}.csv")
                write_to_csv(headers, data, csv_filename)

# Loop through each PDF in the directory
for pdf_filename in os.listdir(pdf_directory):
    if pdf_filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, pdf_filename)

        # Extract the year from the filename
        report_year = extract_year_from_filename(pdf_filename)
        if report_year not in [2013, 2021, 2023]:
            print(f"Skipping file {pdf_filename} as it's not for 2013, 2021, or 2023.")
            continue  # Skip files that are not for 2013, 2021, or 2023
        
        print(f"Processing: {pdf_filename}")

        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Process the tables based on the year
            if report_year == 2013:
                process_tables_for_report(pdf, page_start=2, page_end=5, report_year=2013)
            elif report_year == 2021:
                process_tables_for_report(pdf, page_start=10, page_end=len(pdf.pages), report_year=2021)
            elif report_year == 2023:
                process_tables_for_report(pdf, page_start=9, page_end=len(pdf.pages), report_year=2023)
