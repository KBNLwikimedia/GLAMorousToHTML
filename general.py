"""
This module serves as a foundational utility for various scripts and modules related to Wikimedia projects,
providing a collection of generic functions, configurations, and utilities. It facilitates interactions
with Wikimedia APIs, Wikidata, and other web resources, offering functionalities like loading JSON configurations,
fetching and parsing XML data, validating URLs, and more. This versatility makes it a crucial component
for scripts aimed at analyzing, reporting, or enhancing data related to Wikimedia Commons and Wikipedia.

Latest update: 6 March 2024
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT

Key Features:
- JSON data management: Functions for loading JSON files into Python dictionaries, enabling the script to dynamically
  access configurations and metadata stored in external files.
- URL validation and XML data fetching: Utilities for validating URLs and fetching XML data from remote sources,
  parsing it into Python dictionaries for further processing.
- Wikimedia and Wikidata interaction: Functions to query Wikimedia and Wikidata for specific information, including
  extracting Wikimedia project usage and Wikidata item IDs based on Wikipedia article titles.
- Language label retrieval: A method for fetching Wikipedia language labels from Wikidata, facilitating the
  internationalization and localization of output files.
- Data transformation: Utilities to transform and reorganize data structures, making it easier to work with
  data collected from the Glamorous tool and other sources.
- Excel and HTML preparation: Functions to prepare data for output in Excel or HTML formats, including sorting,
  deduplication, and adding full language names to Wikimedia project data.

Usage:
The functions within this module are designed to be reused across various scripts and modules
(GLAMorousToHTML.py, buildHTML.py, buildExcel.py, setup.py) that require interaction with Wikimedia projects, parsing and
transforming data, or generating reports. By centralizing these utilities, the module promotes code reuse
and simplifies maintenance.

Dependencies:
- External libraries such as requests, SPARQLWrapper, urllib3, xmltodict, and pandas, facilitating web requests,
  SPARQL queries, XML parsing, and data manipulation.
- Local configurations from 'setup.py', ensuring that the module operates within the context of predefined
  project settings and preferences.

Example Use Case:
To fetch and parse XML data from a Wikimedia Commons category, validate URLs, and load project configurations
from a JSON file, thereby enabling the analysis or reporting scripts to efficiently access and organize
the data needed for their operations.

Note:
While this module provides a wide range of utilities, its functions are tailored to specific use cases related
to Wikimedia projects. Users may need to adapt these utilities or extend them based on the requirements
of their specific projects or scripts.
"""

from SPARQLWrapper import SPARQLWrapper, JSON
import traceback
import urllib3
import xmltodict
import json
import os
from urllib.parse import urlparse
from datetime import date
import pandas as pd
from typing import Optional
from pandas import DataFrame
import logging
import requests

today = date.today().strftime("%d%m%Y") #20122022
today2 = date.today().strftime("%d-%m-%Y")  #20-12-2022

def load_dict(file_path: str):
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
        with open(file_path, 'r', encoding='utf-8') as file:
            dictfile = file.read()
            loaded_dict = json.loads(dictfile)
    except json.JSONDecodeError:
        print(f"Error decoding JSON from the file: {file_path}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    return loaded_dict

def save_dict(file_path: str, data_dict: dict):
    """
    Writes a dictionary to a JSON file at the specified file path.
    If any exception occurs during writing, it prints an appropriate error message.
    If writing is successful, it confirms the operation to the user.
    Parameters:
    - file_path (str): The path where the JSON file should be written.
    - data_dict (dict): The dictionary that should be saved to the JSON file.
    Returns:
    - bool: True if the file is successfully written, False otherwise.
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data_dict, file, ensure_ascii=False, indent=4)
        print(f"File successfully written to: {file_path}")
        return True
    except Exception as e:
        print(f"An error occurred while writing to the file: {file_path}. Error: {e}")
        return False


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
from setup import local_xml_file, xml_url
def read_xml_data(readmode, local_xml_file_path=local_xml_file, remote_xml_url=xml_url):

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


def get_wikiprojects(glamorous_dict):
    """
    Extracts all Wikimedia projects reported by the Glamorous tool and calculates the total number of these projects.
    The function navigates through a nested dictionary structure typically returned by the Glamorous tool,
    looking for usage statistics of Wikimedia projects (e.g., 'nl.wikipedia', 'en.wikipedia'). It extracts
    the project names and counts the total number of distinct projects reported.
    Parameters:
    - glamorous_dict (dict): A dictionary containing the Glamorous tool's output, expected to have a nested
                             structure where project usage statistics are stored under keys ['results']['stats']['usage'].
    Returns:
    - tuple: A tuple containing two elements:
        - A list of project names (str), each representing a Wikimedia project reported by Glamorous.
        - An integer representing the total number of projects found.
    """
    # Navigate through the dictionary safely with `.get()` to avoid KeyError if a key is missing
    usage = glamorous_dict.get('results', {}).get('stats', {}).get('usage', [])
    # Extract project names, default to 'Unknown' if 'project' key is not found or if the item is not a dictionary
    projects = [item.get('project', 'Unknown') for item in usage if isinstance(item, dict)]
    # Count the total number of projects extracted
    nprojects = len(projects)
    # Optional: print the number of projects and their names for debugging or informational purposes
    #print(f"{nprojects} projects: {projects}")
    return projects, nprojects

def filter_wikiprojects(projects, skips=None):
    """
    Filters out specified non-language Wikimedia projects from a list of projects.
    This function removes projects related to Wikimedia's meta activities, tests, and special events
    (like Wikimania), which are not considered 'real' language editions of Wikipedia. It is based on
    a predefined list of projects to skip but can be customized by passing a different list.
    Parameters:
    - projects (list): A list of Wikimedia project strings to be filtered.
    - skips (list, optional): A list of project strings to be excluded from the `projects` list. If not provided,
      a default list of known non-language projects will be used.
    Returns:
    - tuple: A tuple containing two elements:
        - A list of filtered project names (str), excluding specified non-language projects.
        - An integer representing the total number of projects after filtering.
    """
    if skips is None:
        skips = ['outreach.wikipedia', 'meta.wikipedia', 'simple.wikipedia', 'incubator.wikipedia',
                 'be_x_old.wikipedia', 'test.wikipedia', 'test2.wikipedia', 'species.wikipedia',
                 'sources.wikipedia', 'mediawiki.wikipedia', 'wikimania2012.wikipedia', 'wikimania2013.wikipedia',
                 'wikimania2014.wikipedia', 'wikimania2015.wikipedia', 'wikimania2016.wikipedia',
                 'wikimania2017.wikipedia', 'wikimania2018.wikipedia', 'wikimania2019.wikipedia',
                 'wikimania2020.wikipedia', 'wikimania2021.wikipedia', 'wikimania2022.wikipedia',
                 'wikimania2023.wikipedia', 'wikimania2024.wikipedia', 'ten.wikipedia']

    list_filtered = [project for project in projects if project not in skips]
    nlist_filtered = len(list_filtered)  # Number of 'real' Wikipedia language versions
    #print(f"{nlist_filtered} filtered projects: {list_filtered}")
    return list_filtered, nlist_filtered

def transform_imagekeybased_to_wikiprojectkeybased(data, projects):
    """
    Transforms Glamorous data from using image names (such as 'AMH-7230-KB_Map_of_Borneo.jpg') as primary keys
    ("image key based") to using wikiprojects (such as 'fr.wikipedia') as primary keys ("wikiproject key based")

    Transforms data from an image-centric structure to a Wikimedia project-centric structure.

    This function takes a nested dictionary that initially organizes images by their names
    and reorganizes this information so that the primary keys are Wikimedia project names (e.g., 'fr.wikipedia').
    Each wikiproject key in the resulting dictionary maps to a list of Wikipedia article URLs within that project.
    This reorganization facilitates access to image data based on the wikiproject rather than the image name.
    Parameters:
    - data (dict): The original dataset containing details about images, structured such that image names
                   are the primary keys. The expected structure is a nested dictionary where the path to
                   the image details is ['results']['details']['image'].
    - projects (list): A list of Wikimedia project names (e.g., 'fr.wikipedia') that are considered in the
                       transformation process. Only projects listed here will be included in the output.
    Returns:
    - dict: A dictionary where each key is a Wikimedia project name from the provided `projects` list, and
            each value is a list of Wikipedia article URLs in the language of the wikiproject (eg. French).
            If a project does not have any associated images in the input data, it maps to an empty list.
    Note:
    - The function gracefully handles various data inconsistencies, such as missing fields or unexpected data types,
      by using default values ('XX') and checking the type of each item (e.g., dict or list) before processing.
    - Projects not listed in the `projects` parameter are ignored, and any unexpected structure in `data` results
      in printing error messages (e.g., 'XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX' for unexpected page structure).
    """
    pdict = {x: [] for x in projects}

    # Fill pdict with data
    images = data.get('results', 'XX').get('details', 'XX').get('image', 'XX')
    for index, image in enumerate(images):
        names = image.get('project', 'XX') # can be a dict or a list of dicts
        image_key = image.get('name', 'XX') # "Album_amicorum_Jacoba_Bolten_-_79_L_40_-_57r.jpg"
        #print(f"** {image_key} -- {image}")
        if isinstance(names, dict):
            names = [names]  # Normalize names to always be a list for consistent processing
        for name in names:
            wiki = name.get('name', 'XX') # 'fr.wikipedia'
            pages = name.get('namespace', 'XX').get('page', 'XX') # can be a dict or a list of dicts
            if isinstance(pages, dict):
                pages = [pages] # Normalize pages to always be a list for consistent processing
            for page in pages:
                wikipagetitle = page.get('title', 'XX')
                wiki_url = f"https://{wiki}.org/wiki/{wikipagetitle.replace(' ', '_')}"
                if wiki in projects:
                    pdict[wiki].append(wiki_url)
                else:
                    pass
        else: pass
    #for p in pdict.items():
    #    print(f"project = {p}")
    return pdict


def dedup_sort_order_projectsdict(pdict, projects):
    """
    Performs three operations on a dictionary mapping Wikimedia project names to lists of article URLs:
    1) Removes duplicate Wikipedia URLs per wikiproject/language.
    2) Sorts the list of deduplicated Wikipedia article URLs alphabetically.
    3) Orders the dictionary by the number of Wikipedia article URLs per wikiproject, in descending order.
    Parameters:
    - pdict (dict): A dictionary where each key is a Wikimedia project name (e.g., 'en.wikipedia'), and each value
                    is a list of URLs pointing to Wikipedia articles. These URLs may contain duplicates.
    - projects (list): A list of wikiproject names (str) indicating which projects in `pdict` should be processed.
                       Only projects listed here will be included in the output.
    Returns:
    - dict: A new dictionary where
            1) each key is a Wikimedia project name,
            2) each list of URLs is deduplicated and sorted alphabetically, and
            3) the keys are ordered by the descending count of URLs in their lists.
    Example:
    >>> pdict = {
    ...     'en.wikipedia': ['url3', 'url1', 'url2', 'url1'],
    ...     'fr.wikipedia': ['url2', 'url1', 'url2', 'url3', 'url3', 'url4'],
    ... }
    >>> projects = ['en.wikipedia', 'fr.wikipedia']
    >>> sorted_dict = dedup_sort_order_projectsdict(pdict, projects)
    >>> for key in sorted_dict:
    ...     print(f"{key}: {sorted_dict[key]}")
    'fr.wikipedia': ['url1', 'url2', 'url3', 'url4']
    'en.wikipedia': ['url1', 'url2', 'url3']
    """
    # Deduplicate and sort URLs within each project
    dedupdict = {project: sorted(set(pdict[project])) for project in projects if project in pdict}
    # Order projects by the descending length of URL lists
    ordered_projects = sorted(dedupdict, key=lambda key: len(dedupdict[key]), reverse=True)
    # Build a new dictionary in the sorted order
    deduped_sorted_ordered_dict = {project: dedupdict[project] for project in ordered_projects}

    #print(f"deduped_sorted_ordered_dict:")
    #for key in deduped_sorted_ordered_dict:
    #    print(f"{key}: {len(deduped_sorted_ordered_dict[key])} - {deduped_sorted_ordered_dict[key]} ")
    return deduped_sorted_ordered_dict

def get_languages_dict(lang="en"):
    # TODO: Adapt this query because language of a Wikipedia is not always uniquely defined, see for instance
    #   Norwegian Wikipedia, https://www.wikidata.org/wiki/Q191769#P407
    #   --> https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromNationaalArchief_Wikipedia_Mainnamespace_16012024.html
    #   has two h4-headers labeled "Nynorsk (1,531)" (associated with no.wiki) and "Nynorsk (409" (associated with nn.wiki)
    #   TODO : query below gives back 351 results, but why is https://w.wiki/8thB only returning 339 items?
    """
    Retrieves a list of Wikipedia language labels in a specified language using Wikidata.
    This function queries the Wikidata SPARQL endpoint to obtain the URLs of various Wikipedia sites
    and their corresponding language labels in the specified language.
    It does not yet addresses the complexity of language representation in Wikipedia, such as the Norwegian Wikipedia, which has multiple
    language labels for the same language variant (e.g., Nynorsk).
    Parameters:
     - lang (str): A language code (e.g., 'nl' for Dutch) to retrieve the language labels. Defaults to 'en' if not specified.
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

def get_full_language_name(ldictlist, key):
    """
    Extracts the full language name corresponding to a given language code/key from a dictionary containing language data.
    The function searches through a dictionary where each entry represents a language, containing both a Wikipedia
    project URL ('wikiurl') and a language label ('languageLabel'). It matches the given language code (key) against
    the domain part of each 'wikiurl' to find the corresponding full language name.
    Parameters:
    - ldictlist (list): A list of dictionaries, where each dictionary contains 'wikiurl' and 'languageLabel' keys.
                       The 'wikiurl' should contain the URL of a Wikipedia project, and 'languageLabel' should contain
                       the full language name.
    - key (str): The language code to search for, which may use underscores ('_') instead of dashes ('-') as found in the URLs.
    Returns:
    - str: The full language name associated with the given language code if found, or 'Full language name not found' if not found.

    Example:
    >>> ldictlist = [
    ...     {'wikiurl': {'value': 'https://en.wikipedia.org/'}, 'languageLabel': {'value': 'English'}},
    ...     {'wikiurl': {'value': 'https://nds-nl.wikipedia.org/'}, 'languageLabel': {'value': 'Low Saxon'}},
    ... ]
    >>> print(extract_full_language_name(ldictlist, 'nds_nl.wikipedia'))
    'Low Saxon'
    """
    normalized_key = key.replace("_", "-")
    for lang in ldictlist:
        wiki_url = lang.get('wikiurl', {}).get('value', '')
        domain = wiki_url.split("//")[-1].split(".org")[0]
        if domain == normalized_key:
            full_language = lang.get('languageLabel', {}).get('value', 'XX')
            return full_language
    return 'get_full_language_name: Full language name not found'

def add_full_language_names_to_dict(dso_pdict, ldictlist):
    """
    Adds the full language name to each project entry in the provided dictionary.
    Parameters:
    - dso_pdict (shorthand for 'deduped_sorted_ordered_projectsdict') (dict): A dictionary with Wikimedia project
      codes as keys (e.g., 'en.wikipedia') and lists of URLs as values.
    - ldictlist (list): A list of dictionaries, where each dictionary contains 'wikiurl' and 'languageLabel' keys
      with the URL of a Wikimedia project and the full language name, respectively.
    This function updates dso_pdict by adding a new key-value pair ('fullLanguageName': <name>)
    to each project entry, containing the full language name associated with the project's language code.
    Note: If the full language name cannot be found, the entry for that project is skipped with a warning.
    """
    for key in list(dso_pdict.keys()):
        fulllang = get_full_language_name(ldictlist, key)  # Assuming this function returns 'XX' if not found
        if fulllang == 'get_full_language_name: Full language name not found':
            print(f"Warning: Full language name not found for key '{key}'. Skipping...")
            continue
        dso_pdict[key] = {
            'fullLanguageName': fulllang,  # Add the full language name
            'urls': dso_pdict[key]  # Keep existing URLs
        }
    # Check outputs:
    # for key, value in dso_pdict.items():
    #    print(f"** {key} - {value} ")
    return dso_pdict

def sort_projects_by_urlcount_and_fulllanguage_name(fl_dso_pdict):
    """
    Sorts a dictionary of Wikimedia projects : first by the descending count of URLs associated with each project and then
    alphabetically by the project's full language name in case of equal URL counts.
    Parameters:
    - fl_dso_pdict (short for 'full_language_dso_pdict') (dict): A dictionary where each key is a project code
            (e.g. 'en.wikipedia'), and the value is a dictionary containing 'fullLanguageName' ('English') and
            a list of 'urls'. The 'urls' list contains URLs pointing to Wikipedia articles.
    Returns:
    - dict: A new dictionary sorted according to the specified criteria. The structure is maintained, with each project code
            mapping to a dictionary with keys 'fullLanguageName' and 'urls', but the order of the keys reflects the sorting criteria.
    Note: Since dictionaries in Python 3.7+ maintain insertion order, the returned dictionary will respect the sorted order.
    """
    # Convert the dictionary to a list of tuples for sorting
    projects_list = [(key, val['fullLanguageName'], val['urls']) for key, val in fl_dso_pdict.items()]
    # Sort the list by descending length of 'urls', then alphabetically by 'fullLanguageName'
    sorted_projects_list = sorted(projects_list, key=lambda x: (-len(x[2]), x[1]))
    # Convert the sorted list back to a dictionary, preserving the new order
    sorted_projects_dict = {item[0]: {'fullLanguageName': item[1], 'urls': item[2]} for item in sorted_projects_list}
    # Check outputs:
    # for key, value in sorted_projects_dict.items():
    #    print(f"** {key} - {len(value.get('urls', 'AAAAAAA'))} - {value} ")
    return sorted_projects_dict


def initialize_articles_pictures_dict(sorted_projects_dict):
    """
    Initializes a dictionary to store articles and associated pictures for each project.
    This function creates a structured dictionary where each project code from 'sorted_projects_dict' is a key.
    The value for each key (e.g. 'en.wikipedia') is another dictionary with two keys: 'fullLanguageName'
    (e.g., 'English'), holding the full language name of the project, and 'articles', a list of dictionaries.
    Each dictionary in the 'articles' list represents a WP article, containing the article's URL ('wikiURL') and an
    initially empty list of images used in that article ('imagesInArticle').
    Parameters:
    - sorted_projects_dict (dict): A dictionary containing project codes as keys. Each key maps to a dictionary
      that should include a 'fullLanguageName' and a list of 'urls' representing articles within that project.
    Returns:
    - dict: A dictionary structured to hold article information and associated images for each project. Each
      project's 'articles' list contains dictionaries for articles, initially with empty 'imagesInArticle' lists.
    Example:
        Input:
        {'en.wikipedia': {'fullLanguageName': 'English',
                'urls': ['https://en.wikipedia.org/wiki/Python_(programming_language)']}}

        Output:
        {'en.wikipedia': {'fullLanguageName': 'English',
                'articles': [
                    {'wikiURL': 'https://en.wikipedia.org/wiki/Python_(programming_language)', 'imagesInArticle': []}]}}
    """
    init_articles_pictures_dict = {
        project_code: {
            'fullLanguageName': sorted_projects_dict[project_code].get('fullLanguageName', 'XX'),
            'articles': [
                {'wikiURL': url, 'imagesInArticle': []}  # Initialize empty list for images
                for url in sorted_projects_dict[project_code].get('urls', [])  # Extract URLs from the input dict
            ]
        }
        for project_code in sorted_projects_dict  # Iterate through each project code in the input dictionary
    }
    return init_articles_pictures_dict


def add_image_to_article(articles_pictures_dict, project, wptitle, picture_name):
    """
    Helper function that adds an image to an article within a specific project in the articles and pictures dictionary.
    If the article already exists, the image name is appended to the 'imagesInArticle' list of that article,
    ensuring no duplicate image names are added. If the article does not exist under the given project,
    a new article entry is created with the image name included.
    This function directly modifies the 'articles_pictures_dict' by either adding a new image to an existing
    article or creating a new article entry if necessary.
    Parameters:
    - articles_pictures_dict (dict): The main dictionary being modified. It organizes articles by project
      codes, each containing a list of articles. Each article is represented as a dictionary with keys for
      the article URL ('wikiURL') and a list of associated images ('imagesInArticle').
    - project (str): The code of the project (e.g., 'en.wikipedia') to which the article belongs.
    - wptitle (str): The title of the Wikipedia article. This title is used to generate the article's URL
      and identify the correct article entry within the project.
    - picture_name (str): The name of the image to be added to the article's entry. This is the file name
      of the image as it appears in the Wikimedia project.
    Returns:
    - None: This function modifies 'articles_pictures_dict' in place and does not return a value.

    Example:
    Given an 'articles_pictures_dict' with project 'en.wikipedia' and an existing article entry,
    calling `add_image_to_article(articles_pictures_dict,'en.wikipedia', 'Python_(programming_language)', 'logo.png')`
    would append 'logo.png' to the 'imagesInArticle' list for the specified article.
    If the article does not exist, it creates a new entry with 'logo.png' as the first image.
    """
    wiki_url = f"https://{project}.org/wiki/{wptitle.replace(' ', '_')}"
    project_articles = articles_pictures_dict.get(project, {}).get('articles', [])
    article_entry = next((article for article in project_articles if article['wikiURL'] == wiki_url), None)

    if not article_entry:
        article_entry = {'wikiURL': wiki_url, 'imagesInArticle': [picture_name]}
        articles_pictures_dict[project]['articles'].append(article_entry)
    elif picture_name not in article_entry['imagesInArticle']:
        article_entry['imagesInArticle'].append(picture_name)


def add_images_to_dict(sorted_projects_dict, pictures):
    """
    Incorporates image data into a structured dictionary based on provided picture information and project details.
    This function iterates over a list of pictures, each containing image names and associated project information.
    It uses 'add_image_to_article' to append each image to its corresponding Wikipedia article within the specified project,
    creating new article entries in 'articles_pictures_dict' if necessary. The function ensures that all images are
    accurately associated with their respective articles and projects, updating the 'articles_pictures_dict' accordingly.
    Parameters:
    - sorted_projects_dict (dict): A dictionary containing project codes as keys. Each key maps to another dictionary
      with details about the project, including a 'fullLanguageName' and a list of 'urls' for articles within that project.
      This dictionary serves as the basis for initializing the structure into which image data will be incorporated.
    - pictures (list): A list of dictionaries, where each dictionary represents an image and contains keys for the image's
      name ('name') and project usage ('project'). The 'project' key maps to a list (or a single dictionary) detailing the
      projects and articles where the image is used.
    Returns:
    - dict: The updated 'articles_pictures_dict' with articles now containing lists of associated images. This dictionary
      is structured with project codes as keys, under which are lists of article dictionaries. Each article dictionary
      includes a 'wikiURL' and an 'imagesInArticle' list with the names of associated images.
    Example:
    Assuming 'sorted_projects_dict' is initialized with project and article URLs, and 'pictures' contains data about images
    and their use across articles:

        sorted_projects_dict = {
            'en.wikipedia': {
                'fullLanguageName': 'English',
                'urls': ['https://en.wikipedia.org/wiki/Python_(programming_language)']
            }
        }

        pictures = [
            {'name': 'PythonLogo.png', 'project': [{'name': 'en.wikipedia', 'namespace': {'page': [{'title': 'Python_(programming_language)'}]}}]}
        ]

    Calling `add_images_to_dict(sorted_projects_dict, pictures)` would add 'PythonLogo.png' to the 'imagesInArticle' list
    for the 'Python_(programming_language)' article within the 'en.wikipedia' project.
    """
    articles_pictures_dict = initialize_articles_pictures_dict(sorted_projects_dict)

    for entry in pictures:
        picture_name = entry.get('name', 'Unknown Image Name')
        project_info = entry.get('project', [])
        if isinstance(project_info, dict):
            project_info = [project_info]  # Normalize project_info to always be a list for consistent processing
        for project in project_info:
            project_code = project.get('name', 'Unknown Project')
            if project_code in articles_pictures_dict:  # Ensure the project exists in the initialized dictionary
                titles = project.get('namespace', {}).get('page', [])
                titles = [titles] if isinstance(titles, dict) else titles  # Normalize titles to list for consistent processing
                for title in titles:
                    wptitle = title.get('title', 'Unknown Title')
                    add_image_to_article(articles_pictures_dict,project_code, wptitle, picture_name)

    # Example print to check the outcome
    # for project, info in articles_pictures_dict.items():
    #     print(f"Project: {project}, Full Language Name: {info['fullLanguageName']}")
    #     for article in info['articles']:
    #         print(f"  Article URL: {article['wikiURL']}, Images in Article: {article['imagesInArticle']}")

    return articles_pictures_dict


def convert_to_dataframe(articles_pictures_dict):
    """
    Converts the articles and pictures dictionary into a pandas DataFrame.
    This function iterates over each project in the articles_pictures_dict, creating a list of dictionaries
    where each dictionary corresponds to a row in the intended DataFrame. Each row includes the project code,
    the full language name, the article's URL, and a list of images in that article. This approach ensures
    each article URL appears in a separate row alongside its project code, full language name, and associated images.
    Parameters:
    - articles_pictures_dict (dict): A dictionary containing project codes as keys, where each key maps to a dictionary
      with 'fullLanguageName', and 'articles', a list containing article dictionaries with 'wikiURL' and 'imagesInArticle'.
    Returns:
    - DataFrame: A pandas DataFrame with columns for 'Project Code', 'Full Language Name', 'Article URL', 'ArticleTitle,
     'NumberOfImages' and 'Images'. Each row represents an article, including its associated project and images.
    """
    data = []  # Initialize an empty list to hold row data for the DataFrame

    for project_code, project_info in articles_pictures_dict.items():
        full_language_name = project_info.get('fullLanguageName', 'Unknown')
        for article in project_info.get('articles', []):
            wiki_url = article.get('wikiURL', 'Unknown URL')
            images = article.get('imagesInArticle', [])
            # Assuming you want to keep the images list as a string of comma-separated values
            images_str = ' -- '.join(images)
            data.append({
                'ProjectCode': project_code,
                'FullLanguageName': full_language_name,
                'ArticleURL': wiki_url,
                'ArticleTitle': wiki_url.split('/wiki/')[1],
                'Images': images_str,  # Or just 'images' if you prefer to keep it as a list
                'NumberOfImages': len(images)
            })

    # Convert the list of dictionaries to a DataFrame
    df = pd.DataFrame(data, columns=['ProjectCode', 'FullLanguageName', 'ArticleURL', 'ArticleTitle', 'Images', 'NumberOfImages'])
    return df


#============================================================

def read_excel_to_df(excel_file: str, sheet_name: Optional[str] = None) -> DataFrame:
    """
    Reads data from a specified sheet of an Excel file into a pandas DataFrame.
    Parameters:
    - excel_file (str): The path to the Excel file to read.
    - sheet_name (Optional[str]): The name of the sheet to read. If None, the first sheet is read by default.
    Returns:
    - DataFrame: A pandas DataFrame containing the data from the specified Excel sheet.
    Raises:
    - FileNotFoundError: If the Excel file cannot be found at the specified path.
    - ValueError: If the specified sheet name does not exist in the Excel file.
    - Exception: For any other issues that arise when attempting to read the Excel file.

    New (for me): Type Annotations: These are used for excel_file and sheet_name parameters and the return type.
    They indicate that 'excel_file' should be a string, 'sheet_name' is an optional string (which could be None),
    and the function returns a pandas DataFrame.
    """
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        return df
    except FileNotFoundError:
        raise FileNotFoundError(f"The file {excel_file} cannot be found.")
    except ValueError as ve:
        raise ValueError(f"The sheet '{sheet_name}' does not exist in the file: {excel_file}.") from ve
    except Exception as e:
        raise Exception(f"An error occurred while reading the Excel file: {excel_file}.") from e


def write_df_to_excel(df: pd.DataFrame, datadir: str, excelpath: str, sheetname: str) -> None:
    """
    Writes the given pandas DataFrame to an Excel file in the specified directory with comprehensive error handling.
    This function ensures the specified 'data' directory exists, creating it if necessary. It then writes the DataFrame
    to an Excel file at the specified path, using a specified sheet name. Errors during the writing process are caught
    and reported.
    Parameters:
    - df (pd.DataFrame): The DataFrame to be written to the Excel file.
    - datadir (str): The directory path where the Excel file will be saved. This function will attempt to create
                     the directory if it does not already exist.
    - excelpath (str): The complete path, including the file name, where the Excel file will be saved. This path
                       should reflect the intended location within the 'datadir'.
    - sheetname (str): The name of the Excel sheet where the DataFrame will be written. If the sheet already exists,
                       it will be overwritten.
    Returns:
    - None: The function's primary purpose is to write data to an Excel file and does not return a value.
    Raises:
    - Various exceptions can be raised by the underlying pandas and openpyxl libraries, depending on the nature of
      the failure (e.g., IOError for issues accessing the file, ValueError for invalid input data). These exceptions
      are caught and reported as error messages.
    """
    # Initialize logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    # Validate DataFrame is not empty
    if df.empty:
        logging.error("The DataFrame is empty. No data to write.")
        return
    # Ensure the data directory exists
    try:
        os.makedirs(datadir, exist_ok=True)
    except Exception as e:
        logging.error(f"Failed to create directory {datadir}: {e}")
        return
    try:
        # Write (in append mode) the DataFrame to an Excel file with the specified sheet name
        with pd.ExcelWriter(excelpath, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
            df.to_excel(writer, index=False, sheet_name=sheetname)
        logging.info(f"Successfully wrote sheet '{sheetname}' to '{excelpath}'.")
    except Exception as e:
        logging.error(f"An error occurred while writing to Excel: {e}")

def get_label_from_qid(qid: str, language_code: str = 'en') -> Optional[str]:
    """
    Retrieves the label for a specified Wikidata item ID in a given language.
    Parameters:
    - qid (str): The Wikidata item ID for which the label is requested (e.g., 'Q42').
    - language_code (str, optional): The language code of the label to retrieve. Defaults to 'en' (English).
    Returns:
    - Optional[str]: The label of the specified Wikidata item in the specified language, if found.
                     Returns None if the label cannot be retrieved.
    Raises:
    - requests.exceptions.RequestException: If a request to the Wikidata API fails.
    - ValueError: If there is an issue decoding the JSON response from the API.
    """
    api_url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qid}&props=labels&languages={language_code}&format=json'
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'GLAMorousToHTML Python script by User:OlafJanssen'
    }
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the response is an HTTP error status.
        data = response.json()
        # Navigate through the JSON response to extract the label.
        label_data = data.get('entities', {}).get(qid, {}).get('labels', {}).get(language_code, {})
        label = label_data.get('value', None)

        if label:
            print(f'The {language_code} label for {qid} is: {label}')
            return label
        else:
            print(f"No label found for {qid} in {language_code}.")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None
    except ValueError as e:
        print(f"JSON decoding error: {e}")
        return None
