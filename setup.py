"""
Global configurations
"""

# Custom project imports
import general

#===== BEGIN USER INPUT ===================================
# Change these two variables if you want to generate output files for other institutions and/or in other countries
# Do not forget to also check or add the relevant institution data to "category_logo_dict.json"
country_key = "Netherlands"
institute_index = 0 # Numerical order in the category_logo_dict; eg: 0 = "Media contributed by Koninklijke Bibliotheek"
#=============== END USER INPUT ============================

READMODE = "http" # Choose "local" or "http".

DICTFILE = "category_logo_dict_beta.json"
category_logo_dict = general.load_dict(DICTFILE)

COMMONSCAT = general.get_institution_details(category_logo_dict, country_key, institute_index)[0]
LOGO = general.get_institution_details(category_logo_dict, country_key, institute_index)[2]

DEPTH = 0 # Depth of subcategories in Glamorous tool, 0=no subcats
XMLURL = "https://glamtools.toolforge.org/glamorous.php?doit=1&category=%s&use_globalusage=1&ns0=1&depth=%s&show_details=1&projects[wikipedia]=1&format=xml" % (COMMONSCAT.replace(" ","_"), str(DEPTH))

LOCALXMLFILE = "GLAMorous_MediaContributedByKB_Wikipedia_Mainnamespace_26012022.xml" # Saved xml response from XMLURL, readmode=local

HTML_TEMPLATE = 'pagetemplate.html'
HTMLFILE = "%s_Wikipedia_NS0_%s.html" % (COMMONSCAT.replace(" ", ""), str(general.today))  # datestamped name of the HTML output file
