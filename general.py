"""
General functions that can be used generically
"""

import requests
from SPARQLWrapper import SPARQLWrapper, JSON
import traceback
import urllib3
import xmltodict
import json
import os
from urllib.parse import urlparse
from datetime import date

today = date.today().strftime("%d%m%Y") #20122022
today2 = date.today().strftime("%d-%m-%Y")  #20-12-2022

def load_dict(file_path):
    """
    Loads and returns a dictionary from a JSON file specified by the given file path.
    This function checks if the specified JSON file exists at the given path. If the file does not exist,
    it prints an error message indicating the file was not found and returns None. If the file exists,
    it attempts to read and parse the JSON content into a Python dictionary. If the JSON content is
    malformed or if any other exception occurs during reading or parsing, it prints an appropriate
    error message and again returns None. In case of successful parsing, the loaded dictionary is returned.
    Parameters:
    - file_path (str): The path to the JSON file that should be loaded.
    Returns:
    - dict or None: Returns the loaded dictionary if the file is successfully read and parsed.
                    Returns None if the file does not exist, the content cannot be decoded as JSON,
                    or if an unexpected error occurs.
    Example of JSON file content:
    ```json
    {
        "key1": "value1",
        "key2": "value2"
    }
    ```
    """
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    try:
        with open(file_path, 'r') as file:
            dictfile = file.read()
            loaded_dict = json.loads(dictfile)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return loaded_dict

def get_institution_details(countries_dict, country_key, institute_index):
    """
    Retrieves details for a specified institution within a given country from the provided dictionary.
    Parameters:
    - countries_dict (dict): A dictionary keyed by country names, each containing a dictionary of institutions and their details.
    - country_key (str): The name of the country whose institutions are to be queried.
    - institute_index (int): The index of the institution within the specified country's list of institutions.
    Returns:
    - list: A list containing 0) the Wikimedia Commons category name, 1) the shortname of the institution, and 2) its icon filename,
      or None if the specified index is out of range or the country is not found.
    Example Return:
    ["Media contributed by Koninklijke Bibliotheek", "KoninklijkeBibliotheekNL", "icon_kb.png"]
    """
    try:
        # Directly return the constructed list if the country and index are valid
        institution_name, details = list(countries_dict[country_key].items())[institute_index]
        return [institution_name] + details
    except (IndexError, KeyError):
        # Handles cases where the country_key is not found or the index is out of range
        return None

def is_valid_url(url):
    """
    Checks if the provided URL is valid.
    Parameters:
    - url (str): The URL to be validated.
    Returns:
    - bool: True if the URL is valid, False otherwise.
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def get_remote_xml(url):
    """
    Fetches and parses XML data from a given URL and converts it into a Python dictionary.
    Parameters:
    - url (str): The URL from which to fetch the XML data.
    Returns:
    - dict: A dictionary representation of the XML data. Returns None if parsing fails.
    """
    http = urllib3.PoolManager()
    try:
        response = http.request('GET', url)
        if response.status != 200:
            print(f"Failed to fetch XML: HTTP {response.status}")
            return None
        data = xmltodict.parse(response.data, attr_prefix='', dict_constructor=dict)
        return data
    except urllib3.exceptions.HTTPError as e:
        print(f"HTTP error encountered: {e}")
    except Exception as e:
        print(f"Failed to parse XML from response: {traceback.format_exc()}")
    return None

# Custom project import
 # DO NOT place this import on top of this page (otherwise you might get a circular import)
from setup import LOCALXMLFILE, XMLURL
def read_xml_data(readmode, local_xml_file_path=LOCALXMLFILE, remote_xml_url=XMLURL):

    """
    Reads XML data based on the specified mode ('local' or 'http'), converts it to a Python dictionary,
    and returns the dictionary.
    Parameters:
    - readmode (str): The mode to read XML data ('local' for local files, 'http' for remote files).
    - local_xml_file_path (str, optional): The file path to the local XML file. Required if readmode is 'local'.
    - remote_xml_url (str, optional): The URL to the remote XML file. Required if readmode is 'http'.
    Returns:
    - dict: A dictionary representation of the XML data. Returns None if an error occurs or the mode is invalid.
    """
    if readmode == "local":
        if local_xml_file_path is None or not os.path.exists(local_xml_file_path):
            print(f"Local XML file path is not specified or does not exist: {local_xml_file_path}")
            return None
        try:
            with open(local_xml_file_path, 'r', encoding='utf-8') as f:
                data = xmltodict.parse(f.read(), attr_prefix='', dict_constructor=dict)
            return data
        except Exception as e:
            print(f"Failed to read or parse local XML file: {e}")
            return None
    elif readmode == "http":
        if remote_xml_url is None or not is_valid_url(remote_xml_url):
            print(f"Remote XML URL is not specified or is invalid: {remote_xml_url}")
            return None
        return get_remote_xml(remote_xml_url)
    else:
        print("ERROR: Invalid readmode specified. Choose 'local' or 'http'.")
        return None


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
    - list: A list of dictionaries, each containing the 'wikiurl' and its corresponding 'languageLabel' .
    Example:
     - [{'wikiurl': 'https://ko.wikipedia.org/', 'languageLabel': 'Korean'}, ...]
    """

    endpoint_url = "https://query.wikidata.org/sparql"
    query = """
    SELECT ?wikiurl ?languageLabel WHERE {{
      ?item wdt:P856 ?wikiurl.
      ?item wdt:P407 ?language.
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







def extract_full_language_name(langdict, key):
    """
    Extracts the full language name matching the given key from the language dictionary.
    Parameters:
    - langdict (dict): A dictionary containing language data.
    - key (str): The language code.
    Returns:
    str: The full language name, or 'XX' if not found.
    """
    for lang in langdict:
        wiki_url = lang.get('wikiurl', {}).get('value', '')
        if wiki_url.split("//")[1].split(".org")[0] == key.replace("_", "-"):
            return lang.get('languageLabel', {}).get('value', 'XX')
    return 'XX'

def get_wikidata_item(wp_title, language):
    """
    Retrieves the Wikidata item ID associated with a given Wikipedia article title.
    Parameters:
    - wp_title (str): The title of the Wikipedia article.
    - language (str): The language edition of Wikipedia to query
    Returns:
    - str: The Wikidata item ID associated with the Wikipedia article.
    """
    # URL to query Wikipedia for the article's associated Wikidata item
    wikipedia_url = f'https://{language}.wikipedia.org/w/api.php'
    params = {
        'action': 'query',
        'format': 'json',
        'prop': 'pageprops',
        'titles': wp_title
    }
    response = requests.get(wikipedia_url, params=params)
    data = response.json()
    # Extract page ID
    page_id = next(iter(data['query']['pages']))
    # Extract Wikidata item ID from the page properties
    wikidata_item_id = data['query']['pages'][page_id]['pageprops'].get('wikibase_item', 'No Wikidata item found')
    return wikidata_item_id

# Example usage
#title = "Python (programming language)"
#wikidata_item_id = get_wikidata_item(title)
#print(f"Wikidata item ID for '{title}': {wikidata_item_id}")