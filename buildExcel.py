"""
This module is dedicated to generating Excel output files for Wikimedia Commons categories associated with specific
institutions. It encompasses the functionality to convert pandas DataFrames into Excel files, systematically organizing
and preserving data related to Wikimedia Commons contributions for archival and analysis purposes.

Latest update: 14 February 2024
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT

Features:
- Automated creation of Excel files from pandas DataFrames, facilitating the management and sharing of data on
  Wikimedia Commons contributions.
- Comprehensive error handling to ensure robust file writing operations and provide clear feedback on any issues encountered.
- Dynamic file naming and path selection, allowing for customizable output locations ('data_dir') and
  file names ('excel_path ') based on the Wikimedia Commons category and date of file generation.
- Integration with global configurations from the 'setup' module, aligning output file generation with overarching
  project settings and preferences.

Functions:
- write_df_to_excel(df, datadir, excelpath, sheetname): Writes a DataFrame to an Excel file, handling directory
  creation, file writing, and error reporting.
- build_excel(dataframe): Facilitates the conversion of a given DataFrame to an Excel file using predefined
  configurations, streamlining the process for end users.

Usage:
To generate an Excel output file for a Wikimedia Commons category, prepare a DataFrame containing the data to
be exported, and call `build_excel(dataframe)` with the DataFrame as the argument. The module will automatically
handle the file creation process, including directory setup and naming conventions, based on configurations
specified in the 'setup' module.

Dependencies:
- general module for accessing the current date.
- setup module for retrieving Wikimedia Commons category and Excel sheet name.
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