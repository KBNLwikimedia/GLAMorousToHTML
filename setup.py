"""
Global configurations

Latest update: 14 February 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
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
country_key = "Netherlands"
institute_index = 0 # Numerical order in the category_logo_dict; eg: 0 = "Media contributed by Koninklijke Bibliotheek"
#=============== END USER INPUT ============================

read_mode = "http" # Choose "local" or "http".

category_logo_dict = load_dict(dict_file)

commons_cat = get_institution_details(category_logo_dict, country_key, institute_index)[0]

depth= 0 # Depth of subcategories in Glamorous tool, 0=no subcats
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
