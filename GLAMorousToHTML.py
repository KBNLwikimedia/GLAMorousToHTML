""""
This script converts the output of the GLAMorous tool (https://glamtools.toolforge.org/glamorous.php) to a HTML page.
It creates a HTML page listing all unique Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.
The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (&ns0=1)
2) and not pages from Wikimedia Commons, Wikidata or other Wiki-projects (projects[wikipedia]=1)

Latest update: 12 February 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
Supported by ChatGPT

"""
#System imports

# Custom project imports
from general import *
from setup import read_mode, wp_fulllanguagelabel_lang
from buildHTML import build_html
from buildExcel import build_excel

"""
Read remote XML over http
data = A dictionary representation of this XML data
"""
data = read_xml_data(read_mode)

"""
1) Retrieve a list of wikiprojects ['nl.wikipedia', 'en.wikipedia', ...] returned by the Glamorous tool, and 
2) count the length of this list = number of wikiprojects
"""
wikiprojects = get_wikiprojects(data)[0] # List
nwikiprojects = get_wikiprojects(data)[1] # Integer

"""
1) Filter out non-language, test, event or defunct Wikimedia projects, such as 
'outreach.wikipedia', 'meta.wikipedia', 'incubator.wikipedia' etc.
2) Also count the length of this list = number of filtered wikiprojects
"""
wikiprojects_filtered = filter_wikiprojects(wikiprojects)[0]  # List
nwikiprojects_filtered = filter_wikiprojects(wikiprojects)[1] # Integer

""""
Transform Glamorous data from using image names (such as 'AMH-7230-KB_Map_of_Borneo.jpg') as primary keys 
("image key based") to using wikiprojects (such as 'fr.wikipedia') as primary keys ("wikiproject key based")
In other words: Transforms data from an image-centric structure to a Wikimedia project-centric structure.
"""
projectsdict = transform_imagekeybased_to_wikiprojectkeybased(data, wikiprojects_filtered)

# Let's process & enrich 'projectsdict' and convert into a Pandas Dataframe: Steps 1-7

""" 1,2,3) Perform three operations on a dictionary mapping Wikimedia project names to lists of article URLs:
1) Remove duplicate Wikipedia URLs per wikiproject/language.
2) Sort the list of deduplicated Wikipedia article URLs alphabetically.
3) Order the dictionary by the number of Wikipedia article URLs per wikiproject, in descending order.
"""
deduped_sorted_ordered_projectsdict = dedup_sort_order_projectsdict(projectsdict, wikiprojects_filtered)

""" Helper function/step to bring full language names to the table 
Retrieve a list of dicts containing full Wikipedia language names, from Wikidata
"""
langdictlist = get_languages_dict(wp_fulllanguagelabel_lang) #dict of full Wikipedia language labels in the language specified

""" 4) Add full language names as new key-value pair to 'deduped_sorted_ordered_projectsdict' (short: 'dso_pdict') 
"""
full_language_dso_pdict = add_full_language_names_to_dict(deduped_sorted_ordered_projectsdict, langdictlist)

""" 5) Sort the 'full_language_dso_pdict' dict first by the descending count of URLs associated with each project 
and then alphabetically by the project's full language name in case of equal URL counts.
"""
sorted_fulllanguage_dso_pdict = sort_projects_by_urlcount_and_fulllanguage_name(full_language_dso_pdict)

"""6) For every Wikipedia article in this dict, add the KB images that are included in it. 
"""
images = data.get('results', 'XX').get('details', 'XX').get('image', 'XX')
images_projectdict = add_images_to_dict(sorted_fulllanguage_dso_pdict, images)

"""7) Turn 'images_projectdict' into Pandas Dataframe - as preparation for conversion into Excel and HTML
"""
wp_df = convert_to_dataframe(images_projectdict)

##### So far for all data transformations and manipulations, let's now create an Excel file and a HTML page from this data

"""8) Write dataframe to Excel 
"""
build_excel(wp_df)

"""9) Transform dataframe to HTML components/building blocks
"""
build_html(wp_df)

#==================================================

def main():
    """Main function of the script GLAMorousToHTML.py."""
    #TODO: move this call to builHTML.py
    #buildHTML()
    #write_html(formatted_numarticles, nwikiprojects_filtered, commons_cat, xml_url, today2, logo, languagesmenu, items)
    #TODO: buildExcel.write_excel()

if __name__ == "__main__":
    main()