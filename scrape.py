import os
import csv
import pdfplumber
import re

# Directories
pdf_directory = "pdf_files"  # Directory containing PDFs
csv_directory = "csv_files"  # Directory to save CSV files

# Ensure the output directory exists
os.makedirs(csv_directory, exist_ok=True)

# List of years to process
valid_years = [2013, 2020, 2021, 2022, 2023]

def table_matches_criteria(table, report_year):
    """Check if the table matches the desired pattern for the given year or previous year."""
    if not table or not table[0]:  # Ensure the table and first row exist
        return False

    # Check the first cell of the table safely
    first_cell = table[0][0] if table[0] else None  # Get the first cell or None

    if first_cell is None:  # If first_cell is None, return False
        return False

    # Check for PREA INCIDENT REPORTS - for the report year and previous year
    previous_year = report_year - 1
    return (f"PREA INCIDENT REPORTS - {previous_year}" in first_cell or
            f"PREA INCIDENT REPORTS - {report_year}" in first_cell)

def extract_year_from_filename(filename):
    """Extract the year from the given filename using regular expressions."""
    match = re.search(r'(\d{4})', filename)  # Look for a 4-digit year
    if match:
        return int(match.group(1))
    return None  # Return None if no year is found

# Loop over each PDF in the directory
for pdf_filename in os.listdir(pdf_directory):
    if pdf_filename.endswith(".pdf"):  # Process only PDF files
        print(f"Processing: {pdf_filename}")  # Print the filename being processed

        pdf_path = os.path.join(pdf_directory, pdf_filename)

        # Extract the year from the filename
        report_year = extract_year_from_filename(pdf_filename)
        if report_year is None:
            print(f"No valid year found in filename: {pdf_filename}. Skipping this file.")
            continue  # Skip this file if no year found

        # Only process the file if the year is in the valid years list
        if report_year not in valid_years:
            print(f"Skipping file for year {report_year} as it's not in the valid years list.")
            continue  # Skip files not in the valid_years list

        # Open the PDF
        with pdfplumber.open(pdf_path) as pdf:
            # Loop over each page
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract tables
                tables = page.extract_tables()

                # Loop over the extracted tables
                for i, table in enumerate(tables):
                    # Check if the table matches the criteria for the current or previous year
                    if table_matches_criteria(table, report_year):
                        # Define CSV file name based on PDF name, page number, and table index
                        csv_filename = f"{pdf_filename[:-4]}_page_{page_num}_table_{i+1}.csv"
                        csv_path = os.path.join(csv_directory, csv_filename)

                        # Save the table to a CSV file
                        with open(csv_path, mode="w", newline="") as f:
                            writer = csv.writer(f)
                            writer.writerows(table)  # Write the table rows to the CSV

                        print(f"Matching table {i+1} from page {page_num} saved to {csv_path}")
