"""
Global configurations for generating output files for Wikimedia Commons categories associated with specific institutions.

This module centralizes the configuration for selecting an institution based on country and index within the predefined
dictionary (from 'category_logo_dict.json') of institutions. It also specifies the read mode for fetching GLAMorous tool
data, defines base URLs for XML data retrieval, and sets up variables for Excel and HTML output customization.

Latest update: 14 February 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
Supported by ChatGPT

Global Variables:
- dict_file (str): Path to the JSON file containing a dictionary of country names and institutions.
- country_key (str): Key representing the country of interest within the 'dict_file'.
- institute_index (int): Index specifying the institution of interest within the country's list in 'dict_file'.
- read_mode (str): Mode for fetching XML data ('local' for local files, 'http' for remote files).
- commons_cat (str): Wikimedia Commons category name associated with the selected institution.
- depth (int): Depth parameter for the GLAMorous tool, determining the subcategory depth to consider.
- xml_base_url (str): Base URL for constructing the request to the GLAMorous tool.
- xml_url (str): Complete URL for fetching XML data about Wikimedia Commons category usage.
- local_xml_file (str): Filename for storing a local copy of the XML data fetched using 'xml_url'.
- wp_full_language_label_lang (str): Language code for displaying Wikipedia language labels.
- sheet_name (str): Name for the Excel sheet where data will be written, derived from the selected institution.
- logo (str): Filename of the logo image associated with the selected institution, for use in HTML outputs.

The module's user input section allows for easy configuration to generate outputs for different institutions
by changing 'category_logo_dict.json', 'country_key' and 'institute_index'  as needed.
It leverages custom project imports for loading dictionaries and fetching institution details, ensuring that
outputs are tailored to specific institutional contributions to Wikimedia Commons.

Usage:
1. Update 'category_logo_dict.json', 'country_key' and 'institute_index' to select a different institution.
2. Choose 'read_mode' based on the source of XML data (local file or remote URL).
3. Run associated script 'GLAMorousToHTML.py' for generating HTML and also Excel

Dependencies:
- general module for functions like 'load_dict' and 'get_institution_details'.
"""

# Custom project imports
from general import load_dict, get_institution_details

#===== BEGIN USER INPUT ===================================
"""
A dictionary (json) keyed by country names, each containing a dictionary of institutions and their details.
Details are: 
1) Wikimedia Commons category name, 
2) the shortname of the institution, and 
3) its icon filename
Add new data to this file if you want to run the script for new institutions not yet present in the dict.
Do not change the name of this json file itself
"""
dict_file = "category_logo_dict.json"

"""
Change these two variables if you want to generate output files for other institutions and/or in other countries
Do not forget to also check and/or add the relevant institution data to "dict_file"
"""
country_key = "New Zealand"
institute_index = 3 # Numerical order in the category_logo_dict; eg: 0 = "Media contributed by Koninklijke Bibliotheek"
#=============== END USER INPUT ============================

read_mode = "http" # Choose "local" or "http".

category_logo_dict = load_dict(dict_file)

commons_cat = get_institution_details(category_logo_dict, country_key, institute_index)[0]

depth = 0 # Depth of subcategories in Glamorous tool, 0=no subcats
xml_base_url = "https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml&"
xml_url = f"{xml_base_url}category={commons_cat}&depth={depth}"
local_xml_file = "MediaContributedByKB_Wikipedia_NS0_ddmmyyyy.xml" # Saved xml response from xml_url, readmode='local'

"""
wp_full_language_label_lang indicates the language used for translating or displaying full language labels
of Wikipedia language versions. 
- If wp_full_language_label_lang = "en", use English to display the full Wikipedia language labels. 
   Therefore, Wikipedia language versions like 'nl.wikipedia' and 'ru.wikipedia' would be labeled as 'Dutch' and 'Russian' respectively. 
- If wp_full_language_label_lang = "nl", the labels would be displayed in Dutch, e.g., 'Nederlands' for Dutch and 'Russisch' for Russian.
"""
wp_fulllanguagelabel_lang = "en"

### For Excel / data outputs ###
# See buildExcel.py for other Excel/data output related variables
# Define the Excel sheet name (limited to 31 characters)
sheet_name = get_institution_details(category_logo_dict, country_key, institute_index)[1]
sheet_name = sheet_name[:30]

### For HTML outputs ###
# See buildHTML.py for other html output related variables
# Logo for HTML report pages
logo = get_institution_details(category_logo_dict, country_key, institute_index)[2]
