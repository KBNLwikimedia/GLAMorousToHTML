"""
All the code to build and publish the Excel output files

Latest update: 12 February 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
Supported by ChatGPT
"""

from general import today
from setup import commons_cat, sheet_name
import os
import pandas as pd

data_dir = "data" #Output directory containing Excel and other (structured) data outputs
excel_file = "%s_Wikipedia_NS0_%s.xlsx" % (commons_cat.replace(" ", ""), str(today))
excel_path = os.path.join(data_dir, excel_file)  # datestamped name of the Excel output file

def write_df_to_excel(df, datadir=data_dir, excelpath=excel_path, sheetname=sheet_name):
    """
    Writes the given pandas DataFrame to an Excel file in the specified directory with comprehensive error handling.
    This function ensures the specified 'data' directory exists, creating it if necessary. It then writes the DataFrame
    to an Excel file at the specified path, using a specified sheet name. Errors during the writing process are caught
    and reported.
    Parameters:
    - df (pandas.DataFrame): The DataFrame to be written to the Excel file.
    - datadir (str): The directory path where the Excel file will be saved. This function will attempt to create
                     the directory if it does not already exist.
    - excelpath (str): The complete path, including the file name, where the Excel file will be saved. This path
                       should reflect the intended location within the 'datadir'.
    - sheetname (str): The name of the Excel sheet where the DataFrame will be written. If the sheet already exists,
                       it will be overwritten.
    Returns:
    - None: The function's primary purpose is to write data to an Excel file and does not return a value. It prints
            a success message upon successful writing or an error message if an exception occurs.
    Raises:
    - Various exceptions can be raised by the underlying pandas and openpyxl libraries, depending on the nature of
      the failure (e.g., IOError for issues accessing the file, ValueError for invalid input data). These exceptions
      are caught and reported as error messages.
    """
    # Ensure the data directory exists
    os.makedirs(datadir, exist_ok=True)

    try:
        # Write the DataFrame to an Excel file with the specified sheet name
        with pd.ExcelWriter(excelpath, engine='openpyxl', mode='w') as writer:
            df.to_excel(writer, index=False, sheet_name=sheetname)
        print(f"Successfully wrote sheet '{sheetname}' to '{excelpath}'.")
    except Exception as e:
        print(f"An error occurred while writing to Excel: {e}")

def build_excel(dataframe):
    write_df_to_excel(df=dataframe)