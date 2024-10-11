import os
import pandas as pd

# Define the folder where your Excel files are located
excel_folder = 'excel_files'
csv_folder = 'clean_csvs'

# Create the CSV folder if it doesn't exist
if not os.path.exists(csv_folder):
    os.makedirs(csv_folder)

# Loop through all Excel files in the folder
for filename in os.listdir(excel_folder):
    if filename.endswith(".xlsx") or filename.endswith(".xls"):  # Check if it's an Excel file
        # Define the full path to the Excel file
        excel_file = os.path.join(excel_folder, filename)
        
        # Load the Excel file
        df = pd.read_excel(excel_file)
        
        # Define the CSV file path (with the same name as the Excel file)
        csv_file = os.path.join(csv_folder, filename.rsplit('.', 1)[0] + '.csv')
        
        # Save the dataframe to a CSV file
        df.to_csv(csv_file, index=False)

        print(f"Converted {filename} to CSV.")
