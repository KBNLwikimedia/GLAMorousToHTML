"""

Latest update: 29 June 2025
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT
"""

from general import load_dict, save_dict, safe_eval
import json
import pandas as pd
import requests
from typing import Tuple, Set, Dict, List, Optional, Union, Any

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
    - Optional[str]: The Wikidata Qitem ID if available in the cache; otherwise, None.
    """
    cache = update_wikidata_cache(row['ArticleURL'], cache_file_path)
    return cache.get(row['ArticleURL'], None)

def get_wditem_property_values(qid: str, property_id: str) -> List[str]:
    """
    Retrieves a list of values associated with a specific property of a given Wikidata item.
    The values can be either:
      1) QIDs for 'wikibase-item' type properties (such as P31, P21),
      2) latitude-longitude pairs for 'globe-coordinate' type properties (such as P625), or
      3) points in time for 'time' type properties (such as P569 - date of birth).
    (see https://www.wikidata.org/wiki/Special:ListDatatypes for all data types in Wikidata)

    Examples:
    - For Q72752496 (Album amicorum of Jacobus Heyblocq) and P31 ('instance of'),
      this function retrieves 'Q457843' (album amicorum).
    - For Q513 (Mt Everest) and P625 ('coordinate location'),
      this function retrieves the latitude-longitude pair '(27.9882361, 86.9250181)'.
    - For Q42 (Douglas Adams) and P569 ('date of birth'),
      this function retrieves '+1952-03-11T00:00:00Z'.

    Parameters:
    - qid (str): The Wikidata ID of the item (e.g., 'Q1234').
    - property_id (str): The property ID for which to retrieve values.
       Supported types are 'wikibase-item', 'globe-coordinate', and 'time'.

    Returns:
    - List[str]: A list of strings representing the QIDs, latitude-longitude pairs, or points in time,
      associated with the specified property of the given item.
      Returns an empty list if the property is not found or if there's an error in fetching data.
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
                    qid_value = datavalue.get('value', {}).get('id', '')
                    if qid_value:
                        q_list.append(qid_value)

                elif datatype == "globecoordinate":
                    latitude = datavalue.get('value', {}).get('latitude', '')
                    longitude = datavalue.get('value', {}).get('longitude', '')
                    latlong = f'({latitude},{longitude})'
                    q_list.append(latlong)

                elif datatype == "time":
                    pit = datavalue.get('value', {}).get('time', '')
                    precision = datavalue.get('value', {}).get('precision', '')
                    """
                    precision – explicit value encoded in a shortint. The numbers have the following meaning: 
                    0 - billion years, 1 - hundred million years, ..., 6 - millennium, 7 - century, 8 - decade, 
                    9 - year, 10 - month, 11 - day, 12 - hour, 13 - minute, 14 - second.
                    """
                    if pit:
                        pit_precision = f'{pit}^^{precision}'
                        q_list.append(pit_precision)

    except requests.RequestException as e:
        print(f"HTTP request error: {e}")
    except ValueError as e:
        print(f"Error decoding JSON: {e}")
    return q_list

def fetch_Pxx_values(row: pd.Series, column_name: str = 'WikidataQID', property_id: str = 'P31') -> Optional[List[str]]:
    """
    Fetches the values for a specified property (e.g., P31, P625, P569) of a Wikidata item identified in a pandas DataFrame row.
    The values can be either:
      1) QIDs for 'wikibase-item' type properties (such as P31, P21),
      2) latitude-longitude pairs for 'globe-coordinate' type properties (such as P625), or
      3) points in time for 'time' type properties (such as P569 - date of birth).

    This function is designed to handle the diversity of Wikidata property types by converting their values into a
    uniform list of strings, facilitating further processing or analysis.
    (see https://www.wikidata.org/wiki/Special:ListDatatypes for all data types in Wikidata)

    Parameters:
    - row (pd.Series): A row from a pandas DataFrame, expected to have a column (default column_name = 'WikidataQID')
      containing the Wikidata ID of the item.
    - property_id (str): The property ID for which the values are fetched. Defaults to 'P31'.
       Supported types are 'wikibase-item', 'globe-coordinate', and 'time'.

    Returns:
    - Optional[List[str]]: A list of strings representing the
      - QIDs,
      - latitude-longitude pairs, or
      - points in time,
      associated with the specified property if available; otherwise, None.
    """

    wikidata_qid = row[column_name]
    if pd.notna(wikidata_qid):
        values = get_wditem_property_values(wikidata_qid, property_id)
        print(f'Fetched values {values} for {property_id} in item {wikidata_qid}')
        return values
    return None


def fetch_labels_for_qids(qids: Union[str, List[str]], language_code: str = 'en') -> Optional[Union[str, List[str]]]:
    """
    Fetches labels for given Wikidata QID(s) in the specified language code using a single API call.
    This function supports fetching labels for both a single QID and multiple QIDs by utilizing the Wikidata API's
    capability to process multiple QIDs separated by '|'. The function returns the label(s) in the specified language.
    Parameters:
    - qids (Union[str, List[str]]): A single Wikidata item ID (QID) as a string, or a list of QIDs for which to fetch labels.
    - language_code (str, optional): The language code for the labels to fetch. Defaults to 'en' (English).
    Returns:
    - Optional[Union[str, List[str]]]: If a single QID is provided, returns a single label as a string. If multiple QIDs
      are provided, returns a list of labels corresponding to each QID. Returns None for any QID whose label cannot be retrieved.
    Raises:
    - requests.exceptions.RequestException: If the request to the Wikidata API fails.
    - ValueError: If there's an issue decoding the JSON response from the API.
    Notes:
    - For local label lookups for a given Qid (in a dataframe) --> see local_lookup_ENlabel()

    """
    # Convert qids to a single string separated by '|' if it's a list
    qids_param = '|'.join(qids) if isinstance(qids, list) else qids

    api_url = f'https://www.wikidata.org/w/api.php?action=wbgetentities&ids={qids_param}&props=labels&languages={language_code}&format=json'
    headers = {'Accept': 'application/json', 'User-Agent': 'Wikidata Label Fetcher - by User:OlafJanssen'}

    try:
        response = requests.get(api_url, headers=headers)
        response.raise_for_status()  # Raises a HTTPError for bad responses
        data = response.json()

        if isinstance(qids, list):
            labels = []
            for qid in qids:
                label = data.get('entities', {}).get(qid, {}).get('labels', {}).get(language_code, {}).get('value', None)
                labels.append(label if label is not None else '')
            # Filter out None values or replace them with an empty string (or a placeholder)
            labels_str = " -- ".join(filter(None, labels))
            print(f'Labels for {" -- ".join(qids)} : {labels_str}')
            return labels
        else:
            label = data.get('entities', {}).get(qids, {}).get('labels', {}).get(language_code, {}).get('value', None)
            print(f'Label for {qids} : {label}')
            return label

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return None if isinstance(qids, list) else [None] * len(qids)
    except ValueError as e:
        print(f"JSON decoding error: {e}")
        return None if isinstance(qids, list) else [None] * len(qids)

def local_lookup_ENlabel(df: pd.DataFrame, wikidata_qid: str) -> str:
    """
    Looks up the English label for a given Wikidata QID in a DataFrame.
    The DataFrame is expected to have at least two columns: 'WikidataQID' for the QIDs and
    'WikidataQIDLabelEn' for the English labels of these QIDs.
    Parameters:
    - df (pd.DataFrame): The DataFrame containing the Wikidata QIDs and their English labels.
    - wikidata_qid (str): The Wikidata QID for which to find the corresponding English label.
    Returns:
    - str: The English label for the given Wikidata QID. Returns an empty string if not found.
    Notes:
    - For looking up labels for a given QID using the Wikidata API, see fetch_labels_for_qids()
    """
    # Attempt to find the row with the matching QID
    match = df.loc[df['WikidataQID'] == wikidata_qid, 'WikidataQIDLabelEn']

    # Return the label if found, else return an empty string
    return match.iloc[0] if not match.empty else ''


def add_wikidata_property_column(
    df: pd.DataFrame,
    target_column: str,
    qid_column: str,
    property_code: str
) -> pd.DataFrame:
    """
    Adds a new column to the DataFrame by applying the fetch_Pxx_values function to each row.

    Parameters:
    - df: pd.DataFrame
        The input DataFrame containing Wikidata QIDs.
    - target_column: str
        The name of the new column to create (e.g., 'P31_instanceOf').
    - qid_column: str
        The column name in df containing the Wikidata QIDs (e.g., 'WikidataQID').
    - property_code: str
        The Wikidata property to fetch (e.g., 'P31').

    Returns:
    - pd.DataFrame: The DataFrame with the new column added.

    Raises:
    - ValueError: If qid_column does not exist in the DataFrame.
    - Exception: For any row-level fetch error (logged but not raised).
    """

    if qid_column not in df.columns:
        raise ValueError(f"Column '{qid_column}' not found in DataFrame.")

    def safe_fetch(row: pd.Series) -> Any:
        try:
            return fetch_Pxx_values(row, qid_column, property_code)
        except Exception as e:
            print(f"Error fetching value for row {row.name} (QID: {row.get(qid_column)}): {e}")
            return None

    df[target_column] = df.apply(safe_fetch, axis=1)
    return df


def convert_list_column_to_string(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
    separator: str = " -- ",
    handle_non_lists: str = "keep"  # options: 'keep', 'empty', 'str'
) -> pd.DataFrame:
    """
    Converts list values in a column to a single string with a separator.

    Transform specific columns in the 'df_wd' DataFrame that may contain lists into string representations.
    It specifically targets columns associated with Wikidata QIDs ('P31_instanceOf') and their corresponding
    English labels ('P31_instanceOfLabelEn'), ensuring that any lists present in these columns are joined into
    a single string, with elements separated by ' -- '. This transformation is useful for preparing the data
    for export or display, where a unified string format is preferred over list format.

    Parameters:
    - df: pd.DataFrame
        The input DataFrame.
    - source_column: str
        Name of the column with list values.
    - target_column: str
        Name of the new or overwritten column to hold the stringified values.
    - separator: str
        String used to join list elements. Default is ' -- '.
    - handle_non_lists: str
        How to handle non-list values:
        - 'keep': Keep as-is
        - 'empty': Convert to empty string
        - 'str': Convert to string using str(x)

    Returns:
    - pd.DataFrame: Updated DataFrame with the new column.
    """

    if source_column not in df.columns:
        raise ValueError(f"Source column '{source_column}' not found in DataFrame.")

    def to_string(x: Union[list, any]) -> str:
        try:
            if isinstance(x, list):
                return separator.join(map(str, x))
            elif handle_non_lists == "empty":
                return ""
            elif handle_non_lists == "str":
                return str(x)
            else:  # 'keep'
                return x
        except Exception as e:
            print(f"Error converting value in column '{source_column}': {e}")
            return ""

    df[target_column] = df[source_column].apply(to_string)
    return df



def apply_safe_eval_to_column(
    df: pd.DataFrame,
    source_column: str,
    target_column: Optional[str] = None
) -> pd.DataFrame:
    """
    Applies safe_eval to a DataFrame column, optionally saving to a new column.

    Parameters:
    - df: pd.DataFrame
        The input DataFrame.
    - source_column: str
        Column to apply safe_eval to.
    - target_column: Optional[str]
        Column to write output to. If None, overwrites source_column.

    Returns:
    - pd.DataFrame: Updated DataFrame with evaluated content.
    """
    if source_column not in df.columns:
        raise ValueError(f"Column '{source_column}' not found in DataFrame.")

    def safe_apply(x):
        try:
            return safe_eval(x)
        except Exception as e:
            print(f"safe_eval failed on value '{x}': {e}")
            return x  # Optionally: return None

    col_to_update = target_column if target_column else source_column
    df[col_to_update] = df[source_column].apply(safe_apply)
    return df


def add_label_column_from_qids(
    df: pd.DataFrame,
    source_column: str,
    target_column: str,
    language_code: str = 'en'
) -> pd.DataFrame:
    """
    Fetch the English label for each Wikidata QID and store it in a new column.
    Applies fetch_labels_for_qids to each cell in a column of QID lists or strings,
    storing the result in a new column.

    Parameters:
    - df: pd.DataFrame
        The input DataFrame.
    - source_column: str
        Name of the column with QID values or lists of QIDs.
    - target_column: str
        Name of the new column to store labels in.
    - language_code: str
        Language for labels (default is 'en').

    Returns:
    - pd.DataFrame: Updated DataFrame with the label column added.
    """

    if source_column not in df.columns:
        raise ValueError(f"Source column '{source_column}' not found in DataFrame.")

    def safe_fetch_labels(qids: Union[str, list]) -> Optional[Union[str, list]]:
        try:
            return fetch_labels_for_qids(qids, language_code=language_code)
        except Exception as e:
            print(f"Error fetching labels for value '{qids}': {e}")
            return None

    df[target_column] = df[source_column].apply(safe_fetch_labels)
    return df
