"""
This module is dedicated to generating Excel output files for Wikimedia Commons categories associated with specific
institutions. It encompasses the functionality to convert pandas DataFrames into Excel files, systematically organizing
and preserving data related to Wikimedia Commons contributions for archival and analysis purposes.

Latest update: 6 March 2024
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

from general import today, write_df_to_excel
from setup import commons_cat, sheet_name
import os

data_dir = "data" #Output directory containing Excel and other (structured) data outputs
excel_file = "%s_Wikipedia_NS0_%s.xlsx" % (commons_cat.replace(" ", ""), str(today)) # datestamped name of the Excel output file
excel_path = os.path.join(data_dir, excel_file)

def build_excel(dataframe):
    write_df_to_excel(dataframe, data_dir, excel_path, sheet_name)