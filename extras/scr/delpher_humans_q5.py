"""
Module for processing and summarizing data about humans (Wikidata entity Q5) from Delpher.

This script reads structured data from a source Excel file containing biographical information
about individuals referenced in Delpher-related Wikipedia articles. It performs aggregation,
analysis, and exports various summaries to a multi-sheet Excel workbook for further analysis
or visualization.

**Input:**
- Excel file: `MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx`
- Worksheet: `Delpher_Q5`
- Location of Excel: `../data/extras/`

**Processing Steps:**
1. Deduplicates rows in the `Delpher_Q5` sheet by `WikidataQID` and `ProjectCode`.
2. Aggregates rows by `WikidataQID`:
   - Groups values like language, images, and article URLs into lists.
   - Extracts the number of images per individual.
3. Outputs the aggregated data to a sheet named `'aggregated_Delpher_Q5'`.

**Additional summary Excel sheets created:**
- `occupation_summary`: Unique occupations (P106) and associated individuals, and their numbers.
- `coc_summary`: Countries of citizenship (P27).
- `pob_summary`: Places of birth (P19) with optional geocoordinates.
- `pod_summary`: Places of death (P20) with optional geocoordinates.
- `gender_summary`: Gender distribution (P21)
- `yob_summary`: Number of individuals by year of birth (P569).
- `yod_summary`: Number of individuals by year of death (P570).
- `dob_summary`: Number of individuals by decade of birth (via P569).
- `dod_summary`: Number of individuals by decade of death (via P570).
-  wp_lang_summary: Unique Wikipedia languages and associated individuals.
- `images_summary`: Unique images with associated individuals and their Wikidata QIDs.

**Notes:**
- Some geographic coordinates are retrieved from Wikidata live using property P625.
- Output may require post-processing in Excel to resolve lat/long duplicates or split columns.

Run this script (ie. delpher_humans_q5.py) after
 - You have run the script `add_wikidata.py` with input file 'MediafromDelpher_Wikipedia_NS0_01072025.xlsx', sheet 'Delpher'
   This run results into the sheet 'Delpher_wd' in the Excel file 'MediafromDelpher_Wikipedia_NS0_01072025.xlsx')
 - From this Excel sheet, you have split off all humans (Q5s) into a separate Excel file
   named 'MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx', into the sheet 'Delpher_Q5'.

After having run this script, you can
- run the script `delpher_pob_pod_map.py` to create an interactive (and embeddable) map with the places of
  birth and death of these humans.
- run the 'delpher_humans_q5_gallery.py' script to create an interactive portrait gallery of these humans

**Author:** Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
**Supported by:** ChatGPT
**Last updated:** 20 August 2025
"""


import sys
from pathlib import Path
# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from general import read_excel_to_df, write_df_to_excel, safe_eval
from wikidata_functions import (apply_safe_eval_to_column, add_label_column_from_qids,
                                add_wikidata_property_column, convert_list_column_to_string)
from delpher_humans_q5_functions import summarize_list_column, summarize_year_column

# Define inputs
data_dir = Path("../data/extras")  # Input directory containing Excel
excel_file = "MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx" # Excel with only data about Delpher-related humans (Q5)
excel_path = data_dir / excel_file
sheet_name = "Delpher_Q5"
aggr_sheet_name = "aggregated_Delpher_Q5"
excel_path = excel_path.resolve()
if not excel_path.exists():
    raise FileNotFoundError(f"Excel file not found at {excel_path}")

# Read humanQ5-data from the Excel file
df = read_excel_to_df(excel_path, sheet_name)

#Only extract data from the specified df columns we'll need
columns = ['WikidataQID',  # Q1018574
           'WikidataQIDLabelEn',  # Aného
           'Images',  # Atlas_Ortelius_KB_PPN369376781-006av-006br.jpg -- Atlas_Ortelius_KB_PPN369376781-001av-001br.jpg
           'ProjectCode',  # fi.wikipedia - use a unique key for language-based operations
           'FullLanguageName',  # Finnish - Note that 'FullLanguageName' is NOT a unique key, as 'Nynorsk' it is used for both and nn.wikipedia and no.wikipedia
           'ArticleURL',  # https://fi.wikipedia.org/wiki/Aného
           'P569_dob_str', # Date of birth , +1869-03-17T00:00:00Z^^11
           'P570_dod_str', # Date of death +1940-09-07T00:00:00Z^^11
           'P19_pob_str',  # Place of birth QID 'Q2463247'
           'P19_pob_LEn_str', # Place of birth label in English
           'P19_pob_LatLong_str', # Place of birth coordinates in (lat,long) format
           'P20_pod_str',  # Place of death QID - 'Q36600'
           'P20_pod_LEn_str', # Place of death label in English
           'P20_pod_LatLong_str', # Place of death coordinates in (lat,long) format
           'P106_occupation',  # List of occupations QIDs ['Q739437', 'Q15296811', 'Q42973']
           'P106_occupation_LEn', # List of occupations LabelsEN, ['poster artist','draftsperson','architect']
           'P21_gender_str',  # Gender QID - mostly 'Q6581097' (male) or 'Q6581072' (female)
           'P21_gender_LEn_str', # Gender label in English - Male of Female
           'P27_coc', # List of country of citizenship QIDs  ['Q29999', 'Q43287']
           'P27_coc_LEn' # List of country of citizenship, LabelsEN ['Germany','France','Switzerland']
           ]

missing_cols = [col for col in columns if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing columns in DataFrame: {missing_cols}")

original_count = len(df)
# Limit df to selected columns and remove any duplicate rows
df = df[columns].drop_duplicates(subset=['WikidataQID','ProjectCode'])
print(f"Reduced from {original_count} to {len(df)} rows after deduplication.")

"""
Next, we want to group and aggregate the df 
1) We want to group by the following columns: 
  -  'WikidataQID', 
2) We want to aggregate the following columns into lists:
 - 'ProjectCode'
 - 'FullLanguageName',
 - 'ArticleURL'
 - 'Images' 

!! Be aware that no.wikipedia (Nynorsk) and nn.wikipedia (Norwegian) are both represented by 'Nynorsk' in the 
FullLanguageName column.
We must take this into account when aggregating the 'FullLanguageName' column!
"""

# Proceed with your aggregation
aggr_df = df.groupby('WikidataQID').agg({
    'WikidataQIDLabelEn': 'first',
    'ProjectCode':  lambda x: list(x),
    'FullLanguageName' : lambda x: list(x),  # Keeps duplicate languages, as 'Nynorsk' is used for both nn.wikipedia and no.wikipedia
    'ArticleURL': lambda x: list(x),
    'Images': lambda x: list(set(
        image.strip()
        for sublist in x.dropna()
        for image in sublist.split(' -- ')
        if image.strip()
    )),
    'P569_dob_str': 'first',
    'P570_dod_str': 'first',
    'P19_pob_str': 'first',
    'P19_pob_LEn_str': 'first',
    'P19_pob_LatLong_str': 'first',
    'P20_pod_str': 'first',
    'P20_pod_LEn_str': 'first',
    'P20_pod_LatLong_str': 'first',
    'P106_occupation': 'first',
    'P106_occupation_LEn':  'first',
    'P21_gender_str': 'first',
    'P21_gender_LEn_str': 'first',
    'P27_coc': 'first',
    'P27_coc_LEn':  'first',
}).reset_index()

# To add a new column that contains the number of images per row, you can simply apply len() to that column after you've already processed it into a list.
aggr_df['NumImages'] = aggr_df['Images'].apply(lambda x: len(x) if isinstance(x, list) else 0)
# Reorder columns: insert NumImages after Images
cols = aggr_df.columns.tolist()
if 'Images' in cols and 'NumImages' in cols:
    idx = cols.index('Images')
    # Move NumImages to right after Images
    cols.insert(idx + 1, cols.pop(cols.index('NumImages')))
    aggr_df = aggr_df[cols]
#write_df_to_excel(aggr_df, data_dir, excel_path, aggr_sheet_name)
print(f"Reduced from {len(df)} to {len(aggr_df)} rows after aggregation.")

'''
In this aggregated sheet, in the column 'P106_occupation_LEn', you need to *manually* modify occupations that have an 
inner apostrofe. Otherwise, the function 'format_list_with_separator' in general.py will not be able to 
handle these strings correctly. So for example, you need to replace:
* 'women's rights activist' --> 'women\'s rights activist'
* 'children's writer' --> 'children\'s writer'
'''

'''
=============================================
 Next, we want to run a number of stats on this aggregated DataFrame:
- 1 - List of unique occupations, and their counts, and a list of the WikidataQIDs of the people with that occupation
- 2 - List of unique countries of citizenship
- 3 - List of unique places of birth, and their geo coordinates (if available in WD)
- 4 - List of unique places of death, and their geo coordinates (if available in WD)
- 5 - List of unique genders, and their counts, and a list of the WikidataQIDs of the people with the gender
- 6 - List of(number of) people + their QIDs born in a certain year
- 7 - List of (number of) people + their QIDs who died in a certain year
- 8 - List of (number of) people + their QIDs born in a certain decade
- 9 - List of (number of) people + their QIDs who died in a certain decade
- 10 - List of unique Wikipedia languages, and a list of the WikidataQIDs of the people described in that language
- 11- List of unique images, and a list of the WikidataQIDs of the people portrayed by that image

Each needs to be outputted to a separate Excel sheet.

For these next steps, we want to read from the Excel sheet 'aggregated_Delpher_Q5', so that any 
manual modifications made in that sheet (such as 'women's rights activist' --> 'women\'s rights activist') 
are taken into account.
'''

# Read humanQ5-data from the aggregated sheet, which can have been manually modified
aggr_df = read_excel_to_df(excel_path, aggr_sheet_name)

''' 
1 - List of unique occupations, and their counts, and a list of the WikidataQIDs of the people with that occupation
'''
# Convert string-represented lists ("['Q739437', 'Q15296811', 'Q42973']") to actual Python lists (['Q739437', 'Q15296811', 'Q42973'])
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='P106_occupation')
# Create dataframe with occupation summary
#P106_occupation_df = summarize_list_column(aggr_df, list_col='P106_occupation', label_prefix='Occupation')
# Add English labels to the occupation QIDs
#P106_occupation_df = add_label_column_from_qids(df=P106_occupation_df, source_column='OccupationQID',
#                                                        target_column='OccupationQID_LEn', language_code='en')
# Write to Excel
#write_df_to_excel(P106_occupation_df, data_dir, excel_path, 'occupation_summary')

''' 
2 - List of unique countries of citizenship
'''
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='P27_coc')
#P27_coc_df = summarize_list_column(aggr_df, list_col='P27_coc', label_prefix='CountryOfCitizenship')
#P27_coc_df = add_label_column_from_qids(df=P27_coc_df, source_column='CountryOfCitizenshipQID',
#                                                        target_column='CountryOfCitizenshipQID_LEn', language_code='en')
#write_df_to_excel(P27_coc_df, data_dir, excel_path, 'coc_summary')

''' 
3 - List of unique places of birth, and their geo coordinates (if available in WD)
'''
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='P19_pob_str')
#P19_pob_df = summarize_list_column(aggr_df, list_col='P19_pob_str', label_prefix='PoB')
#P19_pob_df = add_label_column_from_qids(df=P19_pob_df, source_column='PoBQID',
#                                                        target_column='PoBQID_LEn', language_code='en')
# Add PoB lat-long coordinates to the DataFrame - retrieved live from WD (so not from the Excel file)
#P19_pob_df = add_wikidata_property_column(df=P19_pob_df, target_column='PoB_LatLong', qid_column='PoBQID',
#                                     property_code='P625')
#P19_pob_df = convert_list_column_to_string(df=P19_pob_df, source_column='PoB_LatLong', target_column='PoB_LatLong_str',
#                                      separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
#write_df_to_excel(P19_pob_df, data_dir, excel_path, 'pob_summary')
''' After this step, in the Excel, you might want to 
    - do a manual deduplication for those PoB's that have multiple values for their lat-longs. 
         Tip: Do a lookup in the 'aggregated_Delpher_Q5' sheet, in the 'P19_pob_LatLong_str' column
    - remove the 'PoB_LatLong' (list) column
    - rename the 'PoB_LatLong_str' column to 'PoB_LatLong'
    - split into two separate columns: 'PoB_Lat' and 'PoB_Long'
'''

''' 
4 - List of unique places of death, and their geo coordinates (if available in WD)
'''
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='P20_pod_str')
#P20_pod_df = summarize_list_column(aggr_df, list_col='P20_pod_str', label_prefix='PoD')
#P20_pod_df = add_label_column_from_qids(df=P20_pod_df, source_column='PoDQID',
#                                                        target_column='PoDQID_LEn', language_code='en')
#P20_pod_df = add_wikidata_property_column(df=P20_pod_df, target_column='PoD_LatLong', qid_column='PoDQID',
#                                     property_code='P625')
#P20_pod_df = convert_list_column_to_string(df=P20_pod_df, source_column='PoD_LatLong', target_column='PoD_LatLong_str',
#                                      separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
#write_df_to_excel(P20_pod_df, data_dir, excel_path, 'pod_summary')
''' After this step, in the Excel, you might want to 
    - do a manual deduplication for those PoD's that have multiple values for their lat-longs. 
         Tip: Do a lookup in the 'aggregated_Delpher_Q5' sheet, in the 'P20_pod_LatLong_str' column
    - remove the 'PoD_LatLong' (list) column
    - rename the 'PoD_LatLong_str' column to 'PoD_LatLong'
    - split into two separate columns: 'PoD_Lat' and 'PoD_Long'
'''

''' 
5 - List of unique genders, and their counts, and a list of the WikidataQIDs of the people with the gender
'''
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='P21_gender_str')
#P21_gender_df = summarize_list_column(aggr_df, list_col='P21_gender_str', label_prefix='Gender')
#P21_gender_df = add_label_column_from_qids(df=P21_gender_df, source_column='GenderQID',
#                                                        target_column='GenderQID_LEn', language_code='en')
#write_df_to_excel(P21_gender_df, data_dir, excel_path, 'gender_summary')

''' 
6 - List of (number of) people + their QIDs born in a certain year
'''
#yob_df = summarize_year_column(df=aggr_df, timestamp_col='P569_dob_str', qid_col='WikidataQID',
#                               label='YoB', bin_by_decade=False)
#write_df_to_excel(yob_df, data_dir, excel_path, 'yob_summary')

''' 
7 - List of (number of) people + their QIDs who died in a certain year
'''
#yod_df = summarize_year_column(df=aggr_df, timestamp_col='P570_dod_str', qid_col='WikidataQID',
#                               label='YoD', bin_by_decade=False)
#write_df_to_excel(yod_df, data_dir, excel_path, 'yod_summary')

'''
8 - List of (number of) people + their QIDs born in a certain decade

'''
#dob_df = summarize_year_column(df=aggr_df, timestamp_col='P569_dob_str', qid_col='WikidataQID',
#                               label='DoB', bin_by_decade=True)
#write_df_to_excel(dob_df, data_dir, excel_path, 'dob_summary')


'''
9 - List of (number of) people + their QIDs who died in a certain decade
'''
#dod_df = summarize_year_column(df=aggr_df, timestamp_col='P570_dod_str', qid_col='WikidataQID',
#                               label='DoD', bin_by_decade=True)
#write_df_to_excel(dod_df, data_dir, excel_path, 'dod_summary')

'''
10 - List of unique Wikipedia languages, and a list of the WikidataQIDs of the people described in that language
Sheet = 'wp_lang_summary':
ProjectCode: ['nl.wikipedia', 'fy.wikipedia', 'cs.wikipedia']	
FullLanguageName: ['Dutch', 'West Frisian', 'Czech']
'''
aggr_df = apply_safe_eval_to_column(aggr_df, source_column='ProjectCode')
ProjectCode_df = summarize_list_column(aggr_df, list_col='ProjectCode', label_prefix='ProjectCode')
ProjectCode_df = add_label_column_from_qids(df=ProjectCode_df, source_column='ProjectCodeQID',
                                                        target_column='FullLanguageName', language_code='en')
'''
This will return an empty column 'FullLanguageName', because the ProjectCode values like 'nl.wikipedia' 
are not Wikidata QIDs, so English labels cannot be retrieved from the Wikidata API.
So next, do this seperate step : Map from ProjectCode (like 'nl.wikipedia') to FullLanguageName (like 'Dutch') using a helper function.
'''
# Get the list of dicts from the helper
from GLAMorousToHTML_functions import get_languages_dict
langs_list = get_languages_dict(lang="en")
# Convert into a { "nl.wikipedia": "Dutch", "en.wikipedia": "English", ... } dict
lang_dict = {d["wikiurl"]["value"].replace("https://", "").strip("/").replace(".org", ""):  # <- drop .org
        d["languageLabel"]["value"] for d in langs_list if "wikiurl" in d and "languageLabel" in d}
# Apply mapping to your dataframe column
ProjectCode_df["FullLanguageName"] = ProjectCode_df["ProjectCodeQID"].map(lang_dict)
# Optional fallback if some codes are missing
ProjectCode_df["FullLanguageName"] = ProjectCode_df["FullLanguageName"].fillna("Unknown")
#write_df_to_excel(ProjectCode_df, data_dir, excel_path, 'projectcode_summary')

''' After running this step, you might want to do some manual adjustments in the Excel sheet 'projectcode_summary', 
such as:
- nn.wikipedia --> Nynorsk
- no.wikipedia --> Bokmål
- nds-nl.wikipedia --> Dutch Low Saxon
'''

''' 
11 - List of unique images, and a list of the WikidataQIDs of the people portrayed by that image
'''
#aggr_df = apply_safe_eval_to_column(aggr_df, source_column='Images')
#images_df = summarize_list_column(aggr_df, list_col='Images', label_prefix='Images')
#write_df_to_excel(images_df, data_dir, excel_path, 'images_summary')


''' 
Next steps: 
- use the **delpher_pob_pod_map.py** script to create an interactive map with the places of birth and death of these humans.
- use the **delpher_humans_q5_gallery.py** script to create an interactive portrait gallery of these humans.
'''