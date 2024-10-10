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
    """Write the headers and data to a CSV file, including the PREA Incident Report title."""
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        # Write the report title (PREA INCIDENT REPORTS - YEAR) as the first row
        writer.writerow([headers[0]])  
        writer.writerow(headers[1:])  # Write the actual table headers in the second row
        writer.writerows(data)  # Write the data rows
    print(f"CSV written to {csv_filename}")

def extract_year_from_filename(filename):
    """Extract the year from the filename using regex."""
    match = re.search(r'(\d{4})', filename)
    if match:
        return int(match.group(1))  # Return the year as an integer
    return None

def process_text_for_report(text, page_num, report_year):
    """Extract and parse the relevant PREA INCIDENT REPORTS sections from the text."""
    
    # Log the extracted text for debugging
    print(f"Extracted text from page {page_num}:\n{text}\n")

    # Split the text into lines
    lines = text.splitlines()

    found_report = False
    report_title = None
    headers = None
    data = []
    
    for line in lines:
        # Look for the start of the report
        if "PREA INCIDENT REPORTS" in line:
            found_report = True
            report_title = line.strip()  # Store the "PREA INCIDENT REPORTS - YEAR" line
            # Try to extract the year from the line (e.g., "PREA INCIDENT REPORTS - 2012")
            if str(report_year - 1) in line:
                year = report_year - 1
            elif str(report_year) in line:
                year = report_year
            else:
                year = None  # If no valid year is found
            print(f"Found report for year {year} on page {page_num}")
            continue  # Move to the next line after identifying the start

        if found_report:
            # Process headers and data
            if headers is None:
                headers = [report_title] + line.split()  # Store the report title as part of the headers
                print(f"Headers found on page {page_num}: {headers}")
            else:
                # Split the line using regex to capture everything before the first numeric value as the facility name
                match = re.match(r"^(.*?)(\d.*)$", line)
                if match:
                    facility_name = match.group(1).strip()  # Get the facility name
                    numbers = match.group(2).strip().split()  # Get the numeric data
                    row = [facility_name] + numbers  # Combine the facility name and the numbers
                    data.append(row)
                    print(f"Data row added on page {page_num}: {row}")

            # Stop processing if we reach the end of the report
            if "TOTALS" in line:
                print(f"End of report found on page {page_num}")
                break

    if headers and data and year:
        # Write to CSV
        csv_filename = os.path.join(csv_directory, f"PREA_Report_{year}_page_{page_num}.csv")
        write_to_csv(headers, data, csv_filename)
    else:
        print(f"No valid data found for page {page_num}")

# Loop through each PDF in the directory
for pdf_filename in os.listdir(pdf_directory):
    if pdf_filename.endswith(".pdf"):
        pdf_path = os.path.join(pdf_directory, pdf_filename)

        # Extract the year from the filename
        report_year = extract_year_from_filename(pdf_filename)
        if report_year is None:
            print(f"No valid year found in filename: {pdf_filename}. Skipping this file.")
            continue  # Skip the file if no year is found
        
        print(f"Processing: {pdf_filename}")

        # Open the PDF file
        with pdfplumber.open(pdf_path) as pdf:
            # Loop through each page
            for page_num, page in enumerate(pdf.pages, start=1):
                # Extract the text from the page
                text = page.extract_text()

                if text:
                    # Process the text to find and parse the "PREA INCIDENT REPORTS" section
                    print(f"Processing text on page {page_num} of {pdf_filename}...")
                    process_text_for_report(text, page_num, report_year)
                else:
                    print(f"No text found on page {page_num} of {pdf_filename}")
