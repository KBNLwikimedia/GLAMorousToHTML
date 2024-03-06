"""
This module automates the process of adding Wikidata Qnumbers to a pandas DataFrame based on Wikipedia URLs contained
within the DataFrame. It then writes the enhanced DataFrame to an Excel file.

The module leverages local caching to minimize redundant API calls to Wikipedia by storing previously retrieved
Wikidata Qnumbers in a JSON file. If a Wikipedia URL's corresponding Wikidata Qnumber is already in the cache,
it's used directly; otherwise, the Qnumber is fetched via the Wikipedia API and added to the cache.

The module provides functionalities to:
- Retrieve Wikidata Q-ids for given Wikipedia article URLs.
- Update and maintain a local cache of Wikipedia URL to Wikidata Q-id mappings.
- Perform integrity checks on the cache file to ensure data accuracy and consistency.
- Write the DataFrame with added Wikidata IDs to an Excel file, supporting data sharing and further analysis.

Key components include:
- `get_wikidata_item_from_api`: Fetches Wikidata IDs from the API for given Wikipedia URLs.
- `update_wikidata_cache`: Updates the local cache with new Wikidata IDs as needed.
- `check_cache_integrity`: Ensures the cache's integrity, checking for duplicates and proper ID formatting.
- `fetch_wikidata_id_from_cache`: Retrieves Wikidata IDs from the cache for DataFrame processing.
- External utility functions for file handling and DataFrame processing.

Requirements:
- pandas for DataFrame manipulation.
- requests for API requests.
- openpyxl and ExcelWriter for Excel file writing.

Latest update: 6 March 2024
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT
"""

from general import load_dict, save_dict, read_excel_to_df, write_df_to_excel, get_label_from_qid
from setup import sheet_name
import json
import os
import pandas as pd
import requests
from typing import Tuple, Set, Dict, List, Optional

cache_file = 'wikidata_cache.json'

def get_wikidata_item_from_api(wp_article_url: str) -> Optional[str]:
    """
    Retrieves the Wikidata item ID associated with a given Wikipedia article URL.
    Parameters:
    - wp_article_url (str): The URL of the Wikipedia article, eg 'https://en.wikipedia.org/wiki/1624'
    Returns:
    - Optional[str]: The Wikidata item ID associated with the Wikipedia article, or None if not found or an error occurs.
    Raises:
    - ValueError: If the provided URL does not conform to the expected Wikipedia article URL format.
    - requests.exceptions.RequestException: For issues making the HTTP request to the Wikipedia API.
    """
    try:
        # Validate and parse the article URL
        if '.org/wiki/' not in wp_article_url:
            raise ValueError("Invalid Wikipedia article URL format.")
        wp_project_code = wp_article_url.split('://')[1].split('.org')[0] # 'en.wikipedia'
        wp_article_title = wp_article_url.split('/wiki/')[1] # '1624'
        wikipedia_api_url = f'https://{wp_project_code}.org/w/api.php'
        params = {
            'action': 'query',
            'format': 'json',
            'prop': 'pageprops',
            'titles': wp_article_title
        }
        user_agent = "GLAMorousToHTML Python script by User:OlafJanssen - https://github.com/KBNLwikimedia/GLAMorousToHTML"
        headers = {'User-Agent': user_agent}
        response = requests.get(wikipedia_api_url, params=params, headers=headers)
        response.raise_for_status()  # Raises HTTPError, if one occurred

        data = response.json()
        # Extract page ID
        page_id = next(iter(data['query']['pages']), None)
        if page_id is None:
            return None
        # Extract Wikidata item ID from the page properties
        wikidata_item_id = data['query']['pages'][page_id].get('pageprops', {}).get('wikibase_item', None)
        return wikidata_item_id
    except ValueError:
        # Re-raise ValueError with a more specific message if URL format is incorrect
        raise ValueError("Provided URL is not a valid Wikipedia article URL.")
    except requests.exceptions.RequestException as e:
        # Handle potential request issues
        print(f"An error occurred while fetching data: {e}")
        return None

def update_wikidata_cache(wp_article_url: str, cache_file_path: str = cache_file) -> Dict[str, str]:
    """
    Updates a local cache file with Wikidata QIDs for Wikipedia article URLs.
    If the article URL's QID is already in the cache, it returns immediately from the cache.
    Otherwise, it retrieves the QID via an API call and updates the cache.
    Parameters:
    - wp_article_url (str): The URL of the Wikipedia article.
    - cache_file_path (str): The file path for the JSON cache.
    Returns:
    - Dict[str, str]: The updated cache as a dictionary.
    """
    try:
        # Attempt to load the existing cache
        try:
            cache = load_dict(cache_file_path)
        except FileNotFoundError:
            cache = {}

        # Check if URL is already in cache; if so, return the cache
        if wp_article_url in cache:
            return cache

        # If not, retrieve Wikidata QID from API and update cache
        wikidata_qid = get_wikidata_item_from_api(wp_article_url)
        cache[wp_article_url] = wikidata_qid
        # Save the updated cache
        save_dict(cache_file_path, cache)
        return cache
    except Exception as e:
        raise Exception(f"An error occurred while updating the Wikidata cache: {e}")


def check_cache_integrity(cache_file_path: str = cache_file) -> Tuple[int, int, List[str], bool, bool, Dict[str, Set[str]]]:
    """
    Performs an integrity check on a JSON cache file, focusing on specific aspects of the stored data.
    Parameters:
    - cache_file_path (str): Path to the JSON cache file.
    Returns:
    - A tuple containing:
        1. An integer representing the number of unique key-value pairs.
        2. An integer indicating how many "null" or None values were found.
        3. A list of keys associated with "null" or None values.
        4. A boolean indicating if all non-None/"null" values are strings that start with 'Q'.
        5. A boolean indicating if there are any duplicate values.
        6. A dictionary with duplicate values as keys and sets of their corresponding Article URLs (keys) as values.
    """
    try:
        with open(cache_file_path, 'r', encoding='utf-8') as file:
            cache = json.load(file)

        null_or_none_count = 0
        keys_with_null_or_none = []
        all_values_start_with_q = True
        value_to_keys = {}
        duplicates = {}

        for key, value in cache.items():
            if value is None or value == "null":
                null_or_none_count += 1
                keys_with_null_or_none.append(key)
                continue

            if not isinstance(value, str) or not value.startswith('Q'):
                all_values_start_with_q = False

            if value in value_to_keys:
                if value not in duplicates:
                    duplicates[value] = {value_to_keys[value]}
                duplicates[value].add(key)
            else:
                value_to_keys[value] = key

        has_duplicate_values = len(duplicates) > 0

        # Convert sets to lists for JSON serializability, if needed
        duplicate_details = {k: list(v) for k, v in duplicates.items()}

        # Print the results
        print(f"Check Results for Cache File: {cache_file_path}")
        print("------------------------------------------------")
        print(f"* Number of unique key-value pairs: {len(cache)}")
        print(f"* Number of 'null' or None values found: {null_or_none_count}")
        if null_or_none_count > 0:
            print(f"  - Keys with 'null' or None values: {keys_with_null_or_none}")

        print(f"* Are all values that are not 'None/'null' starting with 'Q': {'Yes' if all_values_start_with_q else 'No'}")
        print(f"* Duplicate Q-values found: {'Yes, ' + str(len(duplicate_details)) if has_duplicate_values else 'No'}")
        if has_duplicate_values:
            print("* Duplicate values and their corresponding Article URLs:")
            for value, keys in duplicate_details.items():
                print(f"  - Value: {value}, Article URLs: {keys}")

    except FileNotFoundError:
        raise FileNotFoundError(f"The cache file at {cache_file_path} was not found.")
    except json.JSONDecodeError:
        raise ValueError(f"The cache file at {cache_file_path} is not a valid JSON file.")
    except Exception as e:
        raise Exception(f"An unexpected error occurred: {e}")

def fetch_wikidata_id_from_cache(row: pd.Series, cache_file_path: str = cache_file) -> Optional[str]:
    """
    Fetches the Wikidata Qitem ID for a given Wikipedia article URL present in the DataFrame row.
    Parameters:
    - row (pd.Series): A row from a pandas DataFrame, expected to contain an 'ArticleURL' field.
    - cache_file (str): The path to the JSON file used for caching Wikidata Qitem IDs.
    Returns:
    - Optional[str]: The Wikidata Qitem ID if available; otherwise, None.
    """
    cache = update_wikidata_cache(row['ArticleURL'], cache_file_path)
    return cache.get(row['ArticleURL'], None)


#==========================================================================
# TODO:  Retrieve list of P31 values (in Dutch) from Wikidata items

def get_wikidata_property_qids(qid: str, property_id: str) -> List[str]:
    """
    Retrieves a list of QIDs associated with a specific property of a given Wikidata item.

    Parameters:
    - qid (str): The Wikidata ID of the item (e.g., 'Q1234').
    - property_id (str): The property ID to retrieve QIDs for (e.g., 'P31'). The property must have data-type = 'wikibase-item'.

    Returns:
    - List[str]: A list of QIDs associated with the specified property of the given item. If the property is not found or
                 there's an error in fetching data, an empty list is returned.
    """
    api_url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&props=claims&ids={qid}&format=json'
    headers = {
        'Accept': 'application/json',
        'User-Agent': 'GLAMorousToHTML Python script by User:OlafJanssen'
    }
    q_list = []
    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError if the response is an error
        data = response.json()
        claims = data.get('entities', {}).get(qid, {}).get('claims', {}).get(property_id, [])
        for claim in claims:
            mainsnak = claim.get('mainsnak', {})
            if mainsnak.get('snaktype') == 'value':
                datavalue = mainsnak.get('datavalue', {})
                datatype = datavalue.get('type')
                if datatype == 'wikibase-entityid':
                    entity_type = datavalue.get('value', {}).get('entity-type')
                    if entity_type == 'item':
                        qid_value = datavalue.get('value', {}).get('id', '')
                        if qid_value:
                            q_list.append(qid_value)

    except requests.RequestException as e:
        print(f"Request error: {e}")
    except ValueError as e:
        print(f"JSON decoding error: {e}")

    return q_list

#====================================================

data_dir = "data" #Output directory containing Excel and other (structured) data outputs
excel_file="MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024.xlsx" # datestamped name of the Excel output file
excel_path = os.path.join(data_dir, excel_file)
sheetname_wikidata = sheet_name[:27] + "_wd"

df = read_excel_to_df(excel_path, sheet_name)

# Performs an integrity check on a JSON cache file, focusing on specific aspects of the stored data.
#check_cache_integrity(cache_file)

# First, ensure the 'WikidataQID' column is updated correctly.
#df['WikidataQID'] = df.apply(lambda row: fetch_wikidata_id_from_cache(row, cache_file), axis=1)
# Next, to fetch the English label for each Wikidata QID and store it in a new column:

#TODO: add ''WikidataQIDLabelEn' to the wikidata cache json file (now it is stored in the Excel)
#df['WikidataQIDLabelEn'] = df['WikidataQID'].apply(lambda qid: get_label_from_qid(qid, language_code='en') if pd.notna(qid) else None)
#print(df.head(10))
#write_df_to_excel(df, data_dir, excel_path, sheetname_wikidata)

# Open
#f_wd = read_excel_to_df(excel_path, sheetname_wikidata)



#=================================================================


def fetch_P31_qids(row: pd.Series, property_id: str = 'P31') -> Optional[List[str]]:
    """
    Fetches the 'instance of' (P31) QIDs for the given Wikidata item.
    Parameters:
    - row (pd.Series): A row from a pandas DataFrame, which is expected to have a 'WikidataQID' field.
    - property_id (str): The property ID for which QIDs are fetched, default is 'P31'.
    Returns:
    - Optional[List[str]]: A list of QIDs for the 'instance of' P31 property if available; otherwise, None.
    """
    wikidata_qid = row['WikidataQID']
    if pd.notna(wikidata_qid):
        return get_wikidata_property_qids(wikidata_qid, property_id)
    return None


# Apply the function to each row in the DataFrame
# Make sure 'WikidataQID' column exists and contains valid Wikidata item IDs (e.g., 'Q1234')
#df_wd['InstanceOfQIDs'] = df_wd.head(10).apply(fetch_P31_qids, axis=1)
#print(df_wd.head(10))

