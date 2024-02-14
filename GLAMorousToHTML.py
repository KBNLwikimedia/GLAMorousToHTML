"""
This script, GLAMorousToHTML.py, automates the conversion of GLAMorous tool output into an HTML page, specifically focusing on
displaying Wikipedia articles across all languages that include images or media from a specified Wikimedia Commons category.
It ensures that only main namespace articles from Wikipedia are considered, excluding pages from Wikimedia Commons, Wikidata,
or other Wiki projects. The process involves fetching XML data, filtering and transforming this data, and ultimately producing
both Excel and HTML outputs that list all unique Wikipedia articles that utilize the specified media in the selected
Wikimedia Commons category.

Features:
- Fetches and processes XML data from the GLAMorous tool based on predefined configurations.
- Transforms data from an image-centric to a Wikimedia project-centric structure for easier analysis.
- Filters out non-language-specific Wikimedia projects to focus on genuine language editions of Wikipedia.
- Deduplicates article URLs within each project and orders projects based on the count of unique articles.
- Enriches the dataset with full language names retrieved from Wikidata, facilitating a more readable output.
- Converts the processed data into a pandas DataFrame for further manipulation and output generation.
- Generates an Excel file summarizing the Wikimedia project data and associated images used across Wikipedia articles.
- Builds a detailed HTML page listing Wikipedia articles, by language, that use the images from the specified Commons category.

Usage:
The script is designed to be executed as a standalone Python program. It requires configurations to be set for the GLAMorous
input (see 'setup.py'), specifically the Wikimedia Commons category to analyze.
Users can adjust the `read_mode`, `wp_fulllanguagelabel_lang`, and other parameters in the `setup.py` module
to cater to different institutions or analysis requirements.

Dependencies:
Relies on custom project imports from `general.py` for utility functions, `setup.py` for configuration settings, `buildHTML.py`
for HTML output generation, and `buildExcel.py` for creating Excel files. External libraries such as pandas are utilized for
data manipulation, and requests are used for fetching data from web sources.

Output:
- An Excel file (`*.xlsx`) containing a summary of Wikipedia articles that use the images from the specified Commons category.
- An HTML page providing a navigable list of Wikipedia articles by language, showcasing the usage of Commons category images.

Author:
Olaf Janssen, Wikimedia coordinator at KB, the national library of the Netherlands

Latest Update:
14 February 2024

Supported by ChatGPT, this script exemplifies the integration of Wikimedia tools with Python for enhancing the visibility
and analysis of media usage across Wikipedia, aiding cultural institutions in understanding the impact of their digital
collections in the Wikimedia ecosystem.
"""


# Custom project imports
from general import *
from setup import read_mode, wp_fulllanguagelabel_lang
from buildHTML import build_html
from buildExcel import build_excel

def main():
    """ Main function of the script GLAMorousToHTML.py."""

    """
    Read remote XML over http
    data = A dictionary representation of this XML data
    """
    data = read_xml_data(read_mode)
    images = data.get('results', 'XX').get('details', 'XX').get('image', 'XX')

    """
    This step achieves two things:
    1) Retrieve a list of wikiprojects ['nl.wikipedia', 'en.wikipedia', ...] returned by the Glamorous tool, and 
    2) count the length of this list = number of wikiprojects
    """
    wikiprojects = get_wikiprojects(data)[0] # List
    #nwikiprojects = get_wikiprojects(data)[1] # Integer

    """
    This step achieves two things:
    1) Filter out non-language, test, event or defunct Wikimedia projects, such as 
    'outreach.wikipedia', 'meta.wikipedia', 'incubator.wikipedia' etc.
    2) Also count the length of this list = number of filtered wikiprojects
    """
    wikiprojects_filtered = filter_wikiprojects(wikiprojects)[0]  # List
    #nwikiprojects_filtered = filter_wikiprojects(wikiprojects)[1] # Integer

    """"
    This step transforms Glamorous data from using image names (such as 'AMH-7230-KB_Map_of_Borneo.jpg') as primary keys 
    ("image key based") to using wikiprojects (such as 'fr.wikipedia') as primary keys ("wikiproject key based")
    In other words: Transforms data from an image-centric structure to a Wikimedia project-centric structure.
    """
    projectsdict = transform_imagekeybased_to_wikiprojectkeybased(data, wikiprojects_filtered)

    # Let's process & enrich 'projectsdict' and convert into a Pandas Dataframe: Steps 1-7

    """ 1,2,3) 
    This step performs three operations on a dictionary mapping Wikimedia project names to lists of article URLs:
    1) Remove duplicate Wikipedia URLs per wikiproject/language.
    2) Sort the list of deduplicated Wikipedia article URLs alphabetically.
    3) Order the dictionary by the number of Wikipedia article URLs per wikiproject, in descending order.
    """
    deduped_sorted_ordered_projectsdict = dedup_sort_order_projectsdict(projectsdict, wikiprojects_filtered)

    """ Helper function/step to bring full language names to the table 
    Retrieve a list of dicts containing full Wikipedia language names, from Wikidata
    """
    langdictlist = get_languages_dict(wp_fulllanguagelabel_lang) #dict of full Wikipedia language labels in the language specified

    """ 4) 
    This step adds full language names as new key-value pair to 'deduped_sorted_ordered_projectsdict' (short: 'dso_pdict') 
    """
    full_language_dso_pdict = add_full_language_names_to_dict(deduped_sorted_ordered_projectsdict, langdictlist)

    """ 5) 
    This step sorts the 'full_language_dso_pdict' dict first by the descending count of URLs associated with each project 
    and then alphabetically by the project's full language name in case of equal URL counts.
    """
    sorted_fulllanguage_dso_pdict = sort_projects_by_urlcount_and_fulllanguage_name(full_language_dso_pdict)

    """ 6) 
    For every Wikipedia article in this dict, this steps adds the KB images that are included in it. 
    """
    images_projectdict = add_images_to_dict(sorted_fulllanguage_dso_pdict, images)

    """ 7) 
    This step turns 'images_projectdict' into Pandas Dataframe - as preparation for conversion into Excel and HTML
    """
    wp_df = convert_to_dataframe(images_projectdict)

    ##### So far for all data transformations and manipulations, let's now create an Excel file and a HTML page from this data

    """ 8) 
    This step writes the dataframe to Excel 
    """
    build_excel(wp_df)

    """ 9)
    This step transform dataframe to HTML components/building blocks and writes all these components to an output HTML file
    """
    build_html(wp_df)


if __name__ == "__main__":
    main()