# Technical notes (under construction)

*Latest update*: 16 September 2024

This page gives more info about 
1. The structure of the [GLAMorousToHTML repository](https://github.com/KBNLwikimedia/GLAMorousToHTML), its files and folders 
2. Short description of their functions (see the docstrings for more detailed functional descriptions)
3. How to run this repo yourself
4. Change log
5. Features to be added

-------------------- 

## Repository structure and functional descriptions

What are the main files and folders in this repo, and what do they do?

### Main folder

* [GLAMorousToHTML.py](GLAMorousToHTML.py) : The main script  
* [GLAMorousToHTML_functions.py](GLAMorousToHTML_functions.py): 

[category_logo_dict.json](category_logo_dict.json)
[category_logo_dict_nde.json](category_logo_dict_nde.json)

[build_html.py](build_html.py)

[build_excel.py](build_excel.py)

[analytics.py](analytics.py)

* [add_wikidata.py](add_wikidata.py)
* [wikidata_functions.py](wikidata_functions.py): 
* 
* [general.py](general.py)
* [generate_report_markup.py](generate_report_markup.py)

* [geolocations.py](geolocations.py)
* [geolocations_functions.py](geolocations_functions.py)
* [geo_map.html](geo_map.html)

* [pob_pod_map.py](pob_pod_map.py)
* [pob_pod_map_functions.py](pob_pod_map_functions.py)
* [pod_pob_map.html](pod_pob_map.html)

[wikidata_cache.json](wikidata_cache.json)


[README.md](README.md) - this file

[pagetemplate.html](pagetemplate.html)

[GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html)

### Subfolders
* [site](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/site) : 
  * site/nde : 
  * site/logos : 
  * site/flags : 

* [data](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/data) : 
  * data/nde : 
  * data/nde/aggregated : 
* [reports](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/reports) : 
* [stories](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/stories) : 

------------------------------

## Running the scripts yourself 
To follow..
<!--If you want to run this script for your own Commons category and create HTML and Excel overviews for your own institution, you can clone/download the repo and run it on your own machine.
You will need to make some simple adaptations to the existing code to make it work for the Commons category of your choice. These are: 

3) In [setup.py](setup.py), change 
   * the *country_key* variable to the new country key you added to the json file  (default = "Netherlands")
   * the *institute_index* to the index of the line corresponding to your institution in the json file (default = 0; first line under a country key)
 
That's  all, you should now be able to run the main [GLAMorousToHTML script](GLAMorousToHTML.py). The generated HTML page will be added to the [site/](site/) folder and the Excel to the [data/](data/) folder. 

In case you can't get the script up and running, please open an issue in this repo.  

### Configuration of GLAMorous
The script relies on the XML output of the GLAMorous tool, which needs to be configured so that it only lists pages from Wikipedia

1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)

2) and *not* pages from Wikimedia Commons, Wikidata or other Wikimedia projects (*projects[wikipedia]=1*)

The base URL thus looks like *[https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=](https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=)*. The Commons category of interest needs to be added to the end, omitting the *Category:* prefix.
This base URL is defined (and can be adapted if necessary) in the *xml_base_url* variable in [GLAMorousToHTML_functions.process_category](GLAMorousToHTML_functions.py). 

The depth of the GLAMorous output (where '0' means no subcategories are read) is specified in the *depth* (=fourth) variable in [category_logo_dict.json](category_logo_dict.json). 
See the section on Repo structure below for more info. 

### category_logo_dict.json
1) Adapt the [category_logo_dict.json](category_logo_dict.json) for your own needs, making sure the existing syntax is maintained. 
   * If not yet available, make a new top level country key (similar to "Netherlands", "USA", "Norway" etc.) to include your country.
   * Under this country key, add a line with a syntax identical to the one starting with "Media contributed by Koninklijke Bibliotheek", but with modifications for four things: 
     
      1) The exact name (without underscores '_') of the Wikimedia Commons category you want run the script for ("[Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)")
      
      2) A shortname of the institution ("KoninklijkeBibliotheekNL"). This is used for the name of the sheet in the Excel file, so keep it shorter than 32 characters. 
       
      3) Name of an institutional logo file, starting with "icon_", followed by a unique and descriptive letter code for the institution, and appended with a .png or .jpg extension at the end. This logo/icon is displayed at the top of the HTML page. Don't forget the next step!

      4) The GLAMororous 'Search depth' parameter. Default = '0', for no subcategories. For [Category:Collections of Leiden University Library](https://commons.wikimedia.org/wiki/Category:Collections_of_Leiden_University_Library) depth = 5, so [all files up to 5 subcategories deep](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Collections_of_Leiden_University_Library&use_globalusage=1&depth=5&show_details=1&projects[wikipedia]=1) are also taken into account.  

2) Add a small logo of the institution (256x256 px or so) as a .png of .jpg to the [site/logos](site/logos) folder, and add the filename "icon_xxxxx.png/jpg" to the json file.



-->



--------------

## Change log (needs updating)

### xx April 2024
* Reports
 - Added [reports](reports_nde.md) for [partners of NDE](https://netwerkdigitaalerfgoed.nl/activiteiten/manifest-netwerk-digitaal-erfgoed/), the Dutch Network for Digital Heritage.
 - Moved all [GLAM reports to separate folder and page](reports/reports.md).
 - Added [report](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/CollectionsofLeidenUniversityLibrary_Wikipedia_NS0_22032024.html) for [Leiden University Library](https://commons.wikimedia.org/wiki/Category:Collections_of_Leiden_University_Library) 
 - In those reports, removed underscores from article URLs.
* Code 
  - Refactoring:  
    - Reduced [general.py](general.py) to only contain very general functions that can be used everywhere in this project.
    - Grouped all functions specific for [GLAMorousToHTML.py](GLAMorousToHTML.py) module into dedicated module [GLAMorousToHTML_functions.py](GLAMorousToHTML_functions.py).
    - Added [type annotations]() for many functions.
  - Made the GLAMororous 'Search depth' parameter configurable via [category_logo_dict.json](category_logo_dict.json). Default = '0', for no subcategories. For [Category:Collections of Leiden University Library](https://commons.wikimedia.org/wiki/Category:Collections_of_Leiden_University_Library) depth = 5, so [all files up to 5 subcategories deep](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Collections_of_Leiden_University_Library&use_globalusage=1&depth=5&show_details=1&projects[wikipedia]=1) are also taken into account.  

### 14 March 2024
* Included reports for 14 institutions from Australia and New Zealand.

### 29 February 2024
* Included reports for institutions from Norway, Sweden, Finland and Sweden.
* [README.md](README.md): Added explanations how you can run the script yourself. 

### 14 February 2024
* Refactored all code into multiple separated modules: [setup.py](setup.py), [general.py](general.py), [buildHTML.py](buildHTML.py) and [buildExcel.py](buildExcel.py). This has reduced the complexity of the main script [GLAMorousToHTML.py](GLAMorousToHTML.py) significantly and made the total suite of code much more modular and easier to understand, maintain and expand.
* Moved all HTML report pages into a separate [site/ folder](site/). This has made the repo much cleaner, clearer and more maintainable.
* Created five HTML files that redirect the old KB HTML pages (from [27-01-2022](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html) to [16-01-2024](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16012024.html)) to the new equivalent ones in "/site" folder. Did not implement redirection for other institutions.
* Per 14-02-2024 added Excel outputs in [data/ folder](data/), to be used as structured input for data applications, such as OpenRefine
* In the proces of updating the data structure in [category_logo_dict.json](category_logo_dict.json), where the new structure can be seen under the 'Netherlands' key.
* Improved [pagetemplate.html](pagetemplate.html) to be key based (*{numarticles} Wikipedia articles*) rather than index based (*{0} Wikipedia articles*)

-------------------- 

## Features to add
* Export reports to Wiki format and put on Commons: (work in progress)
  * [Index page](https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML/Reports) for all institutions 
    * [Index page for KB](https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML/Reports/Media_contributed_by_Koninklijke_Bibliotheek), related to  [Category:Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek).
      * [KB report dd 14 Feb 2024](https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML/Reports/Media_contributed_by_Koninklijke_Bibliotheek/14022024), for this category.

