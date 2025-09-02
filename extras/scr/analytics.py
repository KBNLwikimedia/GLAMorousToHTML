"""
This module runs a number of analytics/ stratistics on the data -
- uniuq calues, and their counts


Latest update: 6 April 2024
Author: Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands
Supported by ChatGPT

"""

from general import read_excel_to_df, write_df_to_excel
from setup import sheet_name
import numpy as np
import os

def count_items_per_unique_value(data_column):
    # Count the number of items in for each of the unique values of P31
    return


####### Prepare the data: dataframes and Excel ########################################################################

data_dir = "data" #Output directory containing Excel and other (structured) data outputs
excel_file="MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024.xlsx"
excel_path = os.path.join(data_dir, excel_file)
sheetname_wikidata = sheet_name + "_wd"

map_excel_file = 'MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024_for_analytics.xlsx'
map_excel_path = os.path.join(data_dir, map_excel_file)
analytics_sheetname = "analytics_data"

df = read_excel_to_df(excel_path, sheetname_wikidata)

#Only extract data from the specified df columns we'll need to making geo maps about PoB and PoD
columns = ['WikidataQID',  # Q1018574
           'WikidataQIDLabelEn',  # Aného
           'Images',  # Atlas_Ortelius_KB_PPN369376781-006av-006br.jpg -- Atlas_Ortelius_KB_PPN369376781-001av-001br.jpg
           'ProjectCode',  # fi.wikipedia - use a unique key for language-based operations
           'FullLanguageName',  # Finnish - Note that 'FullLanguageName' is NOT a unique key, as 'Nynorsk' it is used for both and nn.wikipedia and no.wikipedia
           'ArticleURL',  # https://fi.wikipedia.org/wiki/Aného
           'P31_instanceOf',  # ['Q707813', 'Q2039348']
           'P31_instanceOfLabelEn',  #['Hanseatic city', 'municipality of the Netherlands']
           'Metagroep',  #Humans --> #TODO dit moet uit een aparte key-value store gaan komen --> zie https://chat.openai.com/c/b425cae3-9334-496b-98a7-8ad38d3a9cea
           #TODO and at the bottom of this file
           'P21_genderLabelEN',  # male, female, NaN
           'P106_occupationLabelEn'  #'['publisher', 'writer', 'poet']
           ]

df = df[columns].drop_duplicates(subset=['WikidataQID', 'ProjectCode'])

# delete rows without a WikidataQID
df_analytics = df[df['WikidataQID'].notna()]
df_analytics.reset_index(drop=True, inplace=True)
#print(df_analytics)
write_df_to_excel(df_analytics, data_dir, map_excel_path, analytics_sheetname)

#Fill missing values with a placeholder to ensure they can be grouped
df_analytics['P31_instanceOf'].fillna('No_P31_instanceOf', inplace=True)
df_analytics['P31_instanceOfLabelEn'].fillna('No_P31_instanceOfLabelEn', inplace=True)
df_analytics['Metagroep'].fillna('No_Metagroep', inplace=True)
df_analytics['P21_genderLabelEN'].fillna('No_P21_genderLabelEN', inplace=True)
df_analytics['P106_occupationLabelEn'].fillna('No_P106_occupationLabelEn', inplace=True)

# Proceed with your aggregation
aggr_df_analytics = df_analytics.groupby(['WikidataQID', 'WikidataQIDLabelEn']).agg({
    'ArticleURL': lambda x: list(x),
    'Images': lambda x: list(set(image.strip() for sublist in x for image in sublist.split(' -- '))),
    'ProjectCode': lambda x: list(x),
    'FullLanguageName': lambda x: list(x),
    'P21_genderLabelEN': 'first',
    'P106_occupationLabelEn': 'first'
}).reset_index()

# Optionally, you can replace the placeholders back to NaN if needed for further processing
aggr_df_analytics.replace({'No_P31_instanceOf': np.nan,
                           'No_P31_instanceOfLabelEn': np.nan,
                           'No_Metagroep': np.nan,
                           'No_P21_genderLabelEN': np.nan,
                           'No_P106_occupationLabelEn': np.nan}, inplace=True)

#print(aggr_df_analytics.tail(100))

write_df_to_excel(aggr_df_analytics, data_dir, map_excel_path, 'aggr_analytics_data')


"""
# Do several things: 
1) Deduplicate the 'WikidataQID' column 
2) lookup the 'WikidataQIDLabelEn' values, 
3) lookup the corresponding Wikipedia article (put them in a list [])
4) lookup the corresponding full languages names (in English) (put them in a list [])
5) lookup the corresponding KB images (put them in a list [])
6) write this to a separate sheet
"""




# Use the function on the dataframe
#deduplicated_df = deduplicate_wikidata(df_wd)
#print(deduplicated_df.head(20))
#write_df_to_excel(deduplicated_df, data_dir, excel_path, f'Unique_WDQids2')

# column_name = 'WikidataQID'
# df_wd[column_name] = df_wd[column_name].apply(safe_eval)
# unique_df = extract_unique_values(df_wd[column_name], column_name)
# unique_df['WikidataQIDLabelEn'] = unique_df[column_name].apply(lambda x: local_lookup_ENlabel(df_wd, x))
# write_df_to_excel(unique_df, data_dir, excel_path, f'Unique_{column_name}s')

"""
# # Step 1a: deduplicate values of P31 for entire dataframe column 'P31_instanceOfLabelEn', and write to separate sheet
"""

# column_name = 'P31_instanceOfLabelEn'
# df_wd[column_name] = df_wd[column_name].apply(safe_eval)
# unique_df = extract_unique_values(df_wd[column_name], column_name)
# write_df_to_excel(unique_df, data_dir, excel_path, f'Unique_{column_name}s')

"""
# Step 6a: deduplicate values of P31 for entire dataframe column 'P106_occupationLabelEn', and write to separate sheet
"""

# column_name = 'P106_occupationLabelEn'
# df_wd[column_name] = df_wd[column_name].apply(safe_eval)
# unique_df = extract_unique_values(df_wd[column_name], column_name)
# write_df_to_excel(unique_df, data_dir, excel_path, f'Unique_{column_name}s')


#if __name__ == "__main__":
#    main()

"""
To derive metagroups from the data you've provided, we can look for common themes or categories that can encompass several of the specific items you listed. Here are some proposed metagroups based on the information:

1. **Geographical and Administrative Entities**: 
   - Hanseatic city, 
   - Municipalities (in various countries and types)
   - Cities (in various countries and types)
   - Villages 
   - Cadastral populated places
   - Urban-type settlement (Ukraine and other types)
   - Fortress
   - Historic sites
   - Feudal states, 
   - historical countries, regions, provinces, places, cities, villages
   - Regional districts
   - territories 
   - states 
   - countries 
   - provinces 
   - regions
   - republics
   - present countries

2. **Religious and Spiritual**:
   - Buddhism of an area
   - Aspects of history related to religion
   - Theonyms 
   - names of God in Judaism
   - Public religiuos holidays 
   - Christian holy days
   - Religions, deities, religious orders, churches, temples, religious buildings etc.

3. **Heraldry and Symbols**:
   - Coat of arms of a Dutch village

4. **Human Aspects**:
   - Human, family, tribe
   - Noble family, dynasty

5. **Arts and Literature**:
   - Literary work
   - Musical work/composition
4. **Cultural and Artistic**:
   - Art movements, genres, museums, literature, music, etc.

6. **Political and Social Structures**:
Historical periods
   - Bilateral relations, hostage crises
   - National days
   6. **Political and Legal Systems**:
   - Governments, political movements, laws, decrees, constitutions, etc.

2. **Historical and Archaeological**:
   - Historical periods, events, archaeological sites, empires, kingdoms, etc.

7. **Events and Timeframes**:
   - Events in a specific year or time period
   - Historical periods
   - Timelines
   . **Events and Celebrations**:
    - Festivals, holidays, annual events, traditions, etc.


8. **Military, Wars and Conflict**:
   - Naval battles
   - Civil wars
   - Wars of independence
   - crusades, Battles, 
   - wars, 
   - military units, 
   - alliances, 
   - occupations, etc.

8. **Architecture and Infrastructure**:
   - Buildings 
   - architectural styles 
   - fortifications 
   - roads 
   - bridges
   - abbeys, church buildings

9. **Miscellaneous**:
   - Ship type, naval aspects
   - Wikimedia disambiguation pages and list articles

9. **Natural World**:
   - Natural regions, 
   - bodies of water 
   - landscapes 
   - flora 
   - fauna.
   
   
XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX

7. **Science and Academia**:
   - Academic disciplines, theories, educational institutions, etc.

11. **Society and Demography**:
    - Ethnic groups, demographic profiles, migrations, social classes, etc.

12. **Economics and Industry**:
    - Economic concepts, industries, enterprises, markets, etc.



XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX














"""