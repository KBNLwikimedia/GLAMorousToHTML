"""
This script processes an Excel dataset of media files associated with Wikipedia articles,
with the goal of enriching the data using Wikidata. It performs the following key steps:

1. Loads an Excel file containing media-related records.
2. Uses a local Wikidata QID cache and the Wikidata API to:
   - Retrieve missing Wikidata QIDs for Wikipedia articles.
   - Fetch English labels for QIDs.
3. Writes the updated data with QIDs and labels to a new Excel file in a visualization-ready subfolder.
4. Optionally enriches the dataset with additional Wikidata properties based on a chosen processing step.
   Each step corresponds to a different Wikidata property, such as:
   - `P31`: instance of
   - `P279`: subclass of
   - `P625`: geographic coordinates
   - `P569`: date of birth
   - `P570`: date of death
   - `P19` / `P20`: place of birth/death
   - `P106`: occupation
   - `P21`: gender
   - `P27`: country of citizenship

The user controls which enrichment step to run via the `step_to_run` variable.

Typical usage:
- Set the correct input Excel filename and sheet name.
- Run the script with `step_to_run = 1` to begin enriching with "instance of" (P31).
- Rerun with other step numbers as needed to enrich with other properties.

The script ensures that intermediary and final results are saved to Excel for manual inspection,
label verification, and optional deduplication. Manual edits (especially label corrections) can
then be included in subsequent steps.

Note:
- Minimize the number of calls to the Wikidata API to reduce request load and speed up execution.
- Always inspect the resulting Excel files for accuracy and completeness before using them for analysis or visualization.

Dependencies:
- pandas
- pathlib
- local modules: `general.py`, `wikidata_functions.py`

Latest update: 5 July 2025
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT
"""

import sys
from pathlib import Path
# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))
from general import load_dict, save_dict, read_excel_to_df, write_df_to_excel, safe_eval, copy_file
from wikidata_functions import (cache_file, check_cache_integrity, fetch_wikidata_id_from_cache,
                                add_wikidata_property_column, convert_list_column_to_string, apply_safe_eval_to_column,
                                add_label_column_from_qids)


############################################################################################

# Define inputs
input_data_dir = Path("../data")  # Input directory containing Excel
# Define input Excel file and full path
input_excel_file = "MediafromDelpher_Wikipedia_NS0_01072025.xlsx"  # Datestamped name of the Excel input file
input_excel_path = input_data_dir / input_excel_file
# For value of input_sheet_name, see category_logo_dict.json - pick 2nd value in the list.
# For instance: "Media contributed by Koninklijke Bibliotheek": ["...", "KoninklijkeBibliotheekNL", "..", "0"]
input_sheet_name = "Delpher"

# Define outputs
output_subdir = "extras"
output_dir = input_data_dir / output_subdir
output_excel_file = "MediafromDelpher_Wikipedia_NS0_01072025.xlsx"  # (can be different if needed)
output_excel_path = output_dir / output_excel_file
sheetname_wikidata = input_sheet_name[:27] + "_wd"
print(sheetname_wikidata)

# First, make a copy of the Excel to the ../data/extras directory
#copy_file(input_excel_path, output_excel_path)

# Performs an integrity check on a JSON cache file, focusing on specific aspects of the stored data.
#check_cache_integrity(cache_file)

# Read the just copied Excel file into a pandas DataFrame
#df = read_excel_to_df(input_excel_path, input_sheet_name)

# Ensure the 'WikidataQID' column is updated correctly.
# You only want to run this once or twice, as the Wikidata API is called for each WP-article, if it is not stored in the cache file
#df['WikidataQID'] = df.apply(lambda row: fetch_wikidata_id_from_cache(row, cache_file), axis=1)

# Next, to fetch the English label for each Wikidata QID and store it in a new column:
# You only want to run this once or twice, as the Wikidata API is called for each Qid
#df = add_label_column_from_qids(df=df, source_column='WikidataQID', target_column='WikidataQIDLabelEn', language_code='en')
#write_df_to_excel(df, output_dir, output_excel_path, sheetname_wikidata)

''' After these English labels have been retrieved from WD, you might want to *manually add/correct* the missing ENlabels
and add them to WD, for instance as translated from the Dutch labels in the WD-item, or by using Google Translate.
If required, you can do  re-run of the code line above to add the manually added labels to
the 'WikidataQIDLabelEn' column in the Excel file.
But this requires a full run with many WD API calls, so it is not recommended to do this often.
'''

''' From here on, we want to treat the Excel file with the Wikidata QIDs and ENlabels
(with the manual additions/corrections, which was quite some tedious effort!) as the (new) source/cache file,
and then add more columns with extra data from Wikidata.
'''

# Set the step number to run (1, 2, 3...11)
step_to_run = 11

if step_to_run == 1: # P31 = Instance of
    #------- Step 1 - For a given WikidataQID,
    #  1- lookup corresponding P31 values (Qids), add them to a new column
    #  2- convert (Qids) from P31-list to P31-string
    #  3- lookup English labels of P31 values (Qids) and add them to a new column
    #  4- convert ENLabels from list to string representation

    # 0- Read the Excel file and convert to DataFrame
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    # 1- Add a new column 'P31_instanceOf' with the P31 values (Qids) for each WikidataQID
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P31_instanceOf', qid_column='WikidataQID', property_code='P31')
    # 2- Convert the 'P31_instanceOf' column from a list of QIDs to a string representation
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P31_instanceOf', target_column='P31_instanceOf_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )

    # 3- Lookup English labels of P31 values (Qids) and add them to a new column
    ''' The function call below (apply_safe_eval_to_column) is only needed when the value of 'P31_instanceOf' is read as a string from the Excel file 
    # and needs to be converted into a proper list again. This is the case when the Dataframe has been saved to an Excel file 
    as a intermediate step
    '''
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P31_instanceOf')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P31_instanceOf', target_column='P31_instanceOf_LEn', language_code='en')
    # 4- Convert English labels from list to string representation
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P31_instanceOf_LEn', target_column='P31_instanceOf_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    # 5- Write the updated DataFrame to an Excel file
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)


elif step_to_run == 13: # P279 = Subclass of
    ''' 
    Extra substep for the small amount of WDitems that do not have a P31 (instanceOf), but only a have a P279 (subclassOf)
    In the final Excel file, the P31 and P279 columns will be merged into the column 'P31_instanceOf' Rationale: because of the 
    very limited number of Qitems that only have a P279 and not a P31, we can 'cheat' in the Excel that P279 is 'the same' as P31.
    And sometimes the distinction between P31 and P279 is not that clear anyway....
    '''
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata) 
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P279_subclassOf', qid_column='WikidataQID', property_code='P279')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P279_subclassOf', target_column='P279_subclassOf_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P279_subclassOf', target_column='P279_subclassOf_LEn', language_code='en')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P279_subclassOf_LEn', target_column='P279_subclassOf_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)

elif step_to_run == 2: # P625 = Geo lat-longs
    #------- Step 2 - For a given WikidataQID,
    # - lookup corresponding P625 geo lat-long coordinates
    # - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P625_LatLong', qid_column='WikidataQID', property_code='P625')

    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P625_LatLong')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P625_LatLong', target_column='P625_LatLong_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)

elif step_to_run == 3:
    #Step 3 - For a given WikidataQID (for humans),
    # - lookup corresponding Date of birth (P569) - dob
    # - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P569_dob', qid_column='WikidataQID', property_code='P569')
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P569_dob')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P569_dob', target_column='P569_dob_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those Wikidata items that 
    have multiple values of the DoB . For instance, there might be a DoB value of 15-08-1973 (more precise) and 
    a value of 1973 (less precise). You want to keep the more precise value, and deprecate the less precise value.
    '''

elif step_to_run == 4:
    # Step 4 - For a given WikidataQID (for humans),
    # - lookup corresponding Date of death (P570) -
    # - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P570_dod', qid_column='WikidataQID', property_code='P570')
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P570_dod')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P570_dod', target_column='P570_dod_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those Wikidata items that 
    have multiple values of the DoD. For instance, there might be a DoD value of 11-03-1943 (more precise) and a 
    value of 1943 (less precise). You want to keep the more precise value, and deprecate the less precise value.
    '''

elif step_to_run == 5:
    # Step 5 - For a given WikidataQID (about humans),
    #  - lookup corresponding Place of birth (P19) - pob
    #  - their labels in English
    #  - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    #df_wd = add_wikidata_property_column(df=df_wd, target_column='P19_pob', qid_column='WikidataQID', property_code='P19')
    # Convert the 'P19_pob' column from a list of QIDs to a string representation
    #df_wd = convert_list_column_to_string(df=df_wd, source_column='P19_pob', target_column='P19_pob_str',
    #                                      separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )

    # Lookup English labels of P19 values (Qids) and add them to a new column
    df_wd = apply_safe_eval_to_column(df_wd, source_column='P19_pob')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P19_pob', target_column='P19_pob_LEn', language_code='en')
    # Convert from list to string representation
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P19_pob_LEn', target_column='P19_pob_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those Wikidata items that 
    have multiple values of the PoB. 
    '''

elif step_to_run == 6:
    # Step 6 - For a given WikidataQID (about humans),
    #  - lookup corresponding Place of death (P20)
    #  - their labels in English
    #  - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P20_pod', qid_column='WikidataQID', property_code='P20')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P20_pod', target_column='P20_pod_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )

    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P20_pod')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P20_pod', target_column='P20_pod_LEn', language_code='en')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P20_pod_LEn', target_column='P20_pod_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those Wikidata items that 
    have multiple values of the PoD. 
    '''

elif step_to_run == 7:
    # Step 7 - for a given Place of birth (PoB)
    # - Add P625 lat-longs
    # - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P19_pob_LatLong', qid_column='P19_pob_str', property_code='P625')
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P19_pob_LatLong')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P19_pob_LatLong', target_column='P19_pob_LatLong_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those PoB's that 
    have multiple values for their lat-longs. 
    '''

elif step_to_run == 8:
    # Step 8 - for a given Place of death (PoD)
    # - Add P625 lat-longs
    # - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P20_pod_LatLong', qid_column='P20_pod_str', property_code='P625')
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P20_pod_LatLong')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P20_pod_LatLong', target_column='P20_pod_LatLong_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those PoD's that 
    have multiple values for their lat-longs. 
    '''

elif step_to_run == 9:
    # Step 9 - For a given WikidataQID (about humans),
    #  - lookup corresponding occupation (P106)
    #  - their labels in English
    #  - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    #df_wd = add_wikidata_property_column(df=df_wd, target_column='P106_occupation', qid_column='WikidataQID', property_code='P106')
    #df_wd = convert_list_column_to_string(df=df_wd, source_column='P106_occupation', target_column='P106_occupation_str',
    #                                      separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    df_wd = apply_safe_eval_to_column(df_wd, source_column='P106_occupation')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P106_occupation', target_column='P106_occupation_LEn', language_code='en')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P106_occupation_LEn', target_column='P106_occupation_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)

elif step_to_run == 10:
    # Step 10 - For a given WikidataQID (about humans),
    #  - lookup corresponding sex/gender (P21)
    #  - their labels in English
    #  - convert from list to string representation
    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    df_wd = add_wikidata_property_column(df=df_wd, target_column='P21_gender', qid_column='WikidataQID', property_code='P21')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P21_gender', target_column='P21_gender_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    #df_wd = apply_safe_eval_to_column(df_wd, source_column='P21_gender')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P21_gender', target_column='P21_gender_LEn', language_code='en')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P21_gender_LEn', target_column='P21_gender_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' 
    After this step, in the Excel, you might want to manually add the missing male/female gender labels
    '''

elif step_to_run == 11:
    # Step 11 - For a given WikidataQID (about humans),
    #  - lookup corresponding P27 (country of citizenship - CoC)
    #  - their labels in English
    #  - convert from list to string representation

    df_wd = read_excel_to_df(output_excel_path, sheetname_wikidata)
    #df_wd = add_wikidata_property_column(df=df_wd, target_column='P27_coc', qid_column='WikidataQID', property_code='P27')
    #df_wd = convert_list_column_to_string(df=df_wd, source_column='P27_coc', target_column='P27_coc_str',
    #                                      separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    df_wd = apply_safe_eval_to_column(df_wd, source_column='P27_coc')
    df_wd = add_label_column_from_qids(df=df_wd, source_column='P27_coc', target_column='P27_coc_LEn', language_code='en')
    df_wd = convert_list_column_to_string(df=df_wd, source_column='P27_coc_LEn', target_column='P27_coc_LEn_str',
                                          separator=' -- ', handle_non_lists='keep')  # 'keep' or 'empty' or 'str' )
    write_df_to_excel(df_wd, output_dir, output_excel_path, sheetname_wikidata)
    ''' After this step, in the Excel, you might want to do a manual deduplication for those Wikidata items that 
    have multiple values of the CoC. 
    '''
else:
    print(f"Step {step_to_run} is not recognized. Please use step counter 1, 2, 3...12 to run the appropriate step.")

    ''' Finally, after having created this full Excel, you might want to remove some of the columns that have the same 
    info formatted as a list. For instance, you might want to remove the 'P19_pob' (as a list []) column: 
        P19_pob	| P19_pob_str
        ['Q1025690'] | Q1025690
        ['Q20']	| Q20
        ['Qxxx'] | Qxxx
    '''
