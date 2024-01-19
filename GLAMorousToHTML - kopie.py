""""
This script converts the output of the GLAMorous tool (https://glamtools.toolforge.org/glamorous.php) to a HTML page.
It creates a HTML page listing all unique Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.
The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (&ns0=1)
2) and not pages from Wikimedia Commons, Wikidata or other Wiki-projects (projects[wikipedia]=1)

Latest update: 19 January 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
Supported by ChatGPT

"""
import xmltodict
from datetime import date
import traceback
import urllib3
from SPARQLWrapper import SPARQLWrapper, JSON
import json
import os


def language_lookup(lang):
    # TODO: Adapt this query because language of a Wikipedia is not always uniquely defined, see for instance
    #   Norwegian Wikipedia, https://www.wikidata.org/wiki/Q191769#P407
    #   --> https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromNationaalArchief_Wikipedia_Mainnamespace_16012024.html
    #   has two h4-headers labeled "Nynorsk (1,531)" (associated with no.wiki) and "Nynorsk (409" (associated with nn.wiki)
    #   TODO : query below gives back 351 results, but why is https://w.wiki/8thB only returning 339 items?
    """
    Retrieve a list of Wikipedia language labels in a specified language using Wikidata.
    This function queries the Wikidata SPARQL endpoint to obtain the URLs of various Wikipedia sites
    and their corresponding language labels in the specified language.
    It does not yet addresses the complexity of language representation in Wikipedia, such as the Norwegian Wikipedia, which has multiple
    language labels for the same language variant (e.g., Nynorsk).
    Parameters:
     - lang (str): A language code (e.g., 'nl' for Dutch) to retrieve the language labels.
    Returns:
    - list: A list of dictionaries, each containing the 'wikiurl' and its corresponding 'taalLabel' (language label).
    Example:
     - [{'wikiurl': 'https://ko.wikipedia.org/', 'taalLabel': 'Korean'}, ...]
    """

    endpoint_url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?wikiurl ?taalLabel WHERE {{
      ?item wdt:P856 ?wikiurl.
      ?item wdt:P407 ?taal.
      ?wikiurl wikibase:wikiGroup "wikipedia".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{0}". }}
    }}""".format(lang)

    def get_results(endpoint_url, query):
        user_agent = "GLAMorousToHTML Python script by User:OlafJanssen"
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    results = get_results(endpoint_url, query)
    return results["results"]["bindings"]

def get_remote_xml(url):
    """
    Fetches and parses XML data from a given URL and converts it into a Python dictionary.
    This function retrieves XML data from a specified URL using HTTP GET request and then
    converts the XML data into a Python dictionary for easier manipulation and access. It
    handles exceptions during the XML parsing process and prints an error message if the
    parsing fails.
    Parameters:
     - url (str): The URL from which to fetch the XML data.
    Returns:
    - dict: A dictionary representation of the XML data. Returns None if parsing fails.
    References:
    - StackOverflow discussion on parsing XML from URL: https://stackoverflow.com/questions/24124643/parse-xml-from-url-into-python-object
    - XML to JSON conversion method: https://www.geeksforgeeks.org/python-xml-to-json/
    """
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    data = None
    try:
        # Convert XML to JSON (Python dictionary)
        data = xmltodict.parse(response.data, attr_prefix='', dict_constructor=dict)
    except Exception as e:
        print(f"Failed to parse XML from response: {traceback.format_exc()}")
    return data

def load_category_logo_dict(file_path, country):
    """
    Retrieve the Commons cats and logos of the GLAM institutions in a specified country from a .json file, and output it as a dict.
    Parameters:
    - file_path (str): The path to the JSON file with the Commons cats and logos
    - country (str): The country for which to retrieve the information.
    Returns:
    - dict or None: A dictionary containing the Commons categories and logos for the GLAM institutions in the specified country.
                  Returns None if the country is not found or if an error occurs.
    Note:
    - The function checks if the file exists before attempting to open it.
    - It handles JSON parsing errors and file not found errors gracefully.
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r') as file:
            dictfile = file.read()
            category_logo_dic = json.loads(dictfile)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return category_logo_dic.get(country)


today = date.today().strftime("%d%m%Y") #20122022
today2 = date.today().strftime("%d-%m-%Y")  #20-12-2022


dictfile = "category_logo_dict.json"
category_logo_dict = load_category_logo_dict(dictfile, 'Netherlands')
#print(category_logo_dict)
COMMONSCAT = list(category_logo_dict)[0] # First key of dict = index [0]= "Media contributed by Koninklijke Bibliotheek"
#COMMONSCAT = "Der naturen bloeme - KB KA 16"
print(COMMONSCAT)

# Retrieve the logo of the institute
institute_logo = category_logo_dict[COMMONSCAT]
#print(institute_logo)

DEPTH = 0 # Depth of subcategories, 0=no subcats
XMLURL = "https://glamtools.toolforge.org/glamorous.php?doit=1&category=%s&use_globalusage=1&ns0=1&depth=%s&show_details=1&projects[wikipedia]=1&format=xml" % (COMMONSCAT.replace(" ","_"), str(DEPTH))
print(XMLURL)
#LOCALXMLFILE = "GLAMorous_MediaContributedByKB_Wikipedia_Mainnamespace_26012022.xml" # Saved xml response from XMLURL, readmode=local
HTMLFILE = "GLAMorous_%s_Wikipedia_Mainnamespace_%s.html" % (COMMONSCAT.replace(" ",""), str(today)) # datestamped name of the HTML file

# Two readmodes: 1) read from local XML 2) read from http
#readmode = "local" # Faster readmode, but can be outdated, for live/uptodate response, choose readmode=http
readmode = "http"
if readmode == "local":
    with open(LOCALXMLFILE, 'r', encoding='utf-8') as f:
        # Convert XML to JSON
        data = xmltodict.parse(f.read(), attr_prefix='', dict_constructor=dict)
elif readmode == "http":
    data = get_remote_xml(XMLURL)
else: "ERROR: No readmode specified"
#print(data)

# Extracts project information from a nested data structure.
# This coden navigates through a nested dictionary structure to find usage statistics.
# It then extracts a list of projects from these statistics.
usage = data.get('results', {}).get('stats', {}).get('usage', [])
projects = [item.get('project', 'XX') for item in usage if isinstance(item, dict)]
nprojects = len(projects)
#print("%s projects: %s:" % (nprojects, projects))

# Filter projects for real languages, so omit outreach, meta, simple, incubator, test, defunct wikis etc.
# https://be_x_old.wikipedia.org/ is defunct now
# This list might not yet be complete (dd18 Jan 2024)
skips = ['outreach.wikipedia', 'meta.wikipedia', 'simple.wikipedia', 'incubator.wikipedia', 'be_x_old.wikipedia',
         'test.wikipedia','test2.wikipedia','species.wikipedia','sources.wikipedia','mediawiki.wikipedia',
         'wikimania2012.wikipedia', 'wikimania2013.wikipedia','wikimania2014.wikipedia','wikimania2015.wikipedia',
         'wikimania2016.wikipedia', 'wikimania2017.wikipedia', 'wikimania2018.wikipedia', 'wikimania2019.wikipedia',
         'wikimania2020.wikipedia', 'wikimania2021.wikipedia', 'wikimania2022.wikipedia', 'wikimania2023.wikipedia',
         'wikimania2024.wikipedia','ten.wikipedia']
projects_filtered = [s for s in projects if s not in skips]
nprojects_filtered = len(projects_filtered) # Number of 'real' Wikipedia language versions
#print("%s projects_filtered: %s:" % (nprojects_filtered, projects_filtered))

projectdict = {x: [] for x in projects_filtered}

images = data.get('results', 'XX').get('details', 'XX').get('image', 'XX')
for index, image in enumerate(images):
    names = image.get('project', 'XX') # can be a dict or a list of dicts
    if isinstance(names, dict):
        wiki = names.get('name', 'XX')
        pages = names.get('namespace', 'XX').get('page', 'XX') # can be a dict or a list of dicts
        if isinstance(pages, dict):
            title = pages.get('title', 'XX')
            wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
            if wiki in projects_filtered:
                projectdict[wiki].append(wiki_url)
            else:
                pass
                #print("%s not in projects_filtered" % wiki)
        elif isinstance(pages, list):
            for page in pages:
                title = page.get('title', 'XX')
                wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                if wiki in projects_filtered:
                    projectdict[wiki].append(wiki_url)
                else:
                    pass
                    # print("%s not in projects_filtered" % wiki)
        else:print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    elif isinstance(names, list):
        for name in names:
            wiki = name.get('name', 'XX')
            pages = name.get('namespace', 'XX').get('page', 'XX') # can be a dict or a list of dicts
            if isinstance(pages, dict):
                title = pages.get('title', 'XX')
                wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                if wiki in projects_filtered:
                    projectdict[wiki].append(wiki_url)
                else:
                    pass
                    # print("%s not in projects_filtered" % wiki)
            elif isinstance(pages, list):
                for page in pages:
                    title = page.get('title', 'XX')
                    wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                    if wiki in projects_filtered:
                        projectdict[wiki].append(wiki_url)
                    else:
                        pass
                        # print("%s not in projects_filtered" % wiki)
            else:
                print('YYYYYYYYYYYYYYYYYYYYYY')
    else:
        print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')

# Do some processing/cleaning/ordering/filtering: 1,2,3,4:

# 1) Deduplicate projectdict per language, see https://datagy.io/python-remove-duplicates-from-list/
# 2) For each language: Sort deduped Wikipedia article titles alphabetically
dedupdict = {x: [] for x in projects_filtered}
for key in projectdict.keys():
    dedupdict[key] = sorted(list(set(projectdict.get(key, 'XX'))))
#print('dedupdict = %s' % dedupdict)

# 3) Replace wiki-code with full language, eg. in Dutch: 'nl.wikipedia' --> 'Nederlands' , 'ru.wikipedia' --> 'Russisch'
#LANG = "nl" # H4 headers in Dutch
LANG = "en" # H4 headers in English
langdict = language_lookup(LANG) #dict of Wikipedia language labels in the language specified
# TODO: Note the duplicate Norwegian "no.wikipedia" and "nn.wikipedia" in this dict
print(" "*100)
print("-"*100)
print('langdict = %s' % langdict)
print("-"*100)
print(" "*100)
# 4) Sort Wiki-languages by number of Wikipedia articles: en, nl, fr, ru, de ...
# https://www.geeksforgeeks.org/python-sort-dictionary-by-value-list-length/
items = ""
articlesline = ""
sortedkeys = sorted(dedupdict, key=lambda key: len(dedupdict[key]), reverse=True)
print(" "*100)
print("-"*100)
print('sortedkeys = %s' % sortedkeys)
print("-"*100)
print(" "*100)
numarticles = 0  # Total number of Wikipedia articles

for key in sortedkeys:
    print(f"aaaaaaaaaaaaaaaaa {key}")
    # Extract full language names matching the key
    fulllang = [lang.get('taalLabel', 'XX').get('value', 'XX') for lang in langdict if lang.get('wikiurl', 'XX').get('value', 'XX').split("//")[1].split(".org")[0] == key.replace("_", "-")]

    # Check if fulllang has any elements
    if not fulllang:
        print(f"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaassssssssssssssssssssssssssssssssssssssssssssss"
              f"aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaavvvvvvvvvvvvvvvvvvvvvvvvvv"
              f"vvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvvaaaa {key}")
        # You can skip the iteration or set a default value for fulllang
        break

    numlangarticles = len(dedupdict[key])  # Number of Wikipedia articles in a given language
    formatted_numlangarticles = "{:,}".format(numlangarticles)
    articlesline = ['<a href="{0}" target="_blank">{1}</a>'.format(v, v.split("/wiki/")[1].replace("_", " ")) for v in dedupdict[key]]
    articlesline = " -- ".join(articlesline)
    item = '\n    <h4>%s (%s)</h4>%s' % (fulllang[0].title(), formatted_numlangarticles, articlesline)
    #print(item)
    items += item
    numarticles += numlangarticles

formatted_numarticles = "{:,}".format(numarticles)

# Convert to HTML output
html_template = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" type="text/css" href="style.css">
</head>
<body>
    <div class="content">
    <div class="image-container">
        <img src="logos/icon_wp.png" alt="Wikipedia logo">
        <img src="logos/{6}" alt="Logo of institute">
    </div>
        <h1>{0} Wikipedia articles in {1} languages in which images from <a href="https://commons.wikimedia.org/wiki/Category:{2}" target="_blank">Category:{2}</a> are used, grouped by language</h1>
        <p>This overview is based on <a href="{3}" target="_blank">this XML output</a> of the <a href="{4}" target="_blank">GLAMorous tool</a> d.d. {5}. 
        It was generated using the <a href="https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/main/GLAMorousToHTML.py" target="_blank">GLAMorousToHTML</a> Python script.
        Also see the <a href="https://kbnlwikimedia.github.io/GLAMorousToHTML/" target="_blank">documentation of this tool</a>.</p>
        {7}
    </div>
</body>
</html>
"""

def writeHTML(narticles,nlanguages,commonscat,xmlurl,date, logo, obj):
    html = html_template.format(str(narticles), str(nlanguages), commonscat.replace("_", " "), xmlurl, xmlurl.replace("&format=xml", ""), str(date), logo, obj)
    with open(HTMLFILE, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function of the script GLAMorousToHTML.py."""
    writeHTML(formatted_numarticles, nprojects_filtered, COMMONSCAT, XMLURL, today2, institute_logo, items)

if __name__ == "__main__":
    main()