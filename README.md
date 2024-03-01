# GLAMorousToHTML

*Creates a HTML page and a corresponding Excel file listing all Wikipedia articles (in all languages) in which (one or more) images from a given category on Wikimedia Commons are used.*

*Latest update*: 1 March 2024

## What does it do?
<image src="site/logos/icon_wp.png" width="100" hspace="10" align="right"/>

The script [GLAMorousToHTML.py](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/GLAMorousToHTML.py) creates a HTML page and a corresponding Excel file listing all Wikipedia articles (in all languages) in which (one or more) images/media from a given category on Wikimedia Commons are used. It does so by converting the XML output of the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php). 

## What problem does it solve?
The KB uses the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to [measure the use of KB media files](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4) (as stored in Wikimedia Commons) in Wikipedia articles. This tool [rapports 4 things](https://tools.wmflabs.org/glamtools/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects%5Bwikipedia%5D=1) :

* 1 The **total number of KB media files** in [Category:Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) (*Category "Media contributed by Koninklijke Bibliotheek" has XXXX files.*)
* 2 The **total number of times** that KB media files are used in WP articles (*Total image usages*).
* 3 The **number of Wikipedia language versions** in which KB media files are used (*length of the table*)
* 4 The **number of unique KB media files** that are used in Wikipedia articles in all those languages. (*Distinct images used*)

Please note: 'Total image usages' does NOT equal the number of unique WP articles! A single unique KB image can illustrate multiple unique WP articles, and/or the other way around, 1 unique WP article can contain multiple unique KB images. In other words: images-articles have many-to-many relationships.

What was still missing was the functionality to measure
* 5 The **number of unique WP articles** in which KB media files are used, 
* 6 A **manifest overview** of those articles, grouped per WP language version,
* 7 A structured output format that can be **easily processed** by tools, such as Excel.

That is why we made the GLAMorousToHTML tool. This script uses the [XML-output of GLAMorous](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml) to make an [HTML page listing unique WP articles](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024.html) (in which one or more KB media files are used), grouped by language. 

Per 14-02-2024 it also delivers an Excel file with equivalent data.

## Configuration of GLAMorous
The script relies on the XML output of GLAMorous, which needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)
2) and *not* pages from Wikimedia Commons, Wikidata or other Wikimedia projects (*projects[wikipedia]=1*)

The base URL looks like *[https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=](https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=)*. The Commons category of interest needs to be added to the end, omitting the *Category:* prefix.
It is defined (and can be adapted) in the *xml_base_url* variable in [setup.py](setup.py). 

By default the depth of the GLAMorous output is set to 0, meaning no subcategories are read. If you want to include images from subcategories in your outputs, you can change the *depth* variable in setup.py. 

## Running the script yourself
If you want to run this script for your own Commons category and create HTML and Excel overviews for your own institution, you can clone/download the repo and run it on your own machine.
You will need to make some simple adaptations to the existing code to make it work for the Commons category of your choice. These are: 
1) Adapt the [category_logo_dict.json](category_logo_dict.json) for your own needs, making sure the existing syntax is maintained. 
    * If not yet available, make a new top level country key (similar to "Netherlands", "USA", "Norway" etc.) to include your country.
    * Under this country key, add a line with a syntax identical to the one starting with "Media contributed by Koninklijke Bibliotheek", but with modifications for three things: 
        1) The exact name (without underscores '_') of the Wikimedia Commons category you want run the script for ("[Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)")
        2) A shortname of the institution ("KoninklijkeBibliotheekNL"). This is used for the name of the sheet in the Excel file, so keep it shorter than 32 characters. 
        3) Name of an institutional logo file, starting with "icon_", followed by a unique and descriptive letter code for the institution, and appended with a .png or .jpg extension at the end. This logo/icon is displayed at the top of the HTML page. Don't forget the next step!
2) Add a small logo of the institution (256x256 px or so) as a .png of .jpg to the [site/logos](site/logos) folder, and add the filename "icon_xxxxx.png/jpg" to the json file.
4) In [setup.py](setup.py), change 
    - the *country_key* variable to the new country key you added to the json file  (default = "Netherlands")
    - the *institute_index* to the index of the line corresponding to your institution in the json file (default = 0; first line under a country key)
 
That's  all, you should now be able to run the main [GLAMorousToHTML script](GLAMorousToHTML.py). The generated HTML page will be added to the [site/](site/) folder and the Excel to the [data/](data/) folder. 

In case you can't get the script up and running, please open an issue in this repo.  

## Examples
### KB, national library of the Netherlands 
<image src="site/logos/icon_kb.png" width="100" hspace="10" align="right"/>

#### Media contributed by Koninklijke Bibliotheek
* Input: Commons category = [Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)
* Output: 
  * [this output dd 14-02-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024.html), together with this [Excel file](https://kbnlwikimedia.github.io/GLAMorousToHTML/data/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_14022024.xlsx). 
  * [this output dd 16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16012024.html) or [this output dd 10-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html), 
  * [this result dd 20-12-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_20122022.html), related to the article *[Public outreach and reuse of KB images via Wikipedia, 2014-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/stories/Public%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.html)*, or
  * [this output dd 16-02-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16022022.html), related to [this analysis](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4/KPI4_KB_16-02-2022) on Dutch Wikipedia dd 16-02-2022, or 
  * [this output dd 27-01-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html) 

#### Atlas de Wit 1698
* Input: Commons category = [Atlas de Wit 1698](https://commons.wikimedia.org/wiki/Category:Atlas%20de%20Wit%201698)
* Output: [AtlasdeWit1698_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/AtlasdeWit1698_Wikipedia_NS0_27012022.html)

#### Atlas van der Hagen
* Input: Commons category = [Atlas van der Hagen](https://commons.wikimedia.org/wiki/Category:Atlas%20van%20der%20Hagen)
* Output: [AtlasvanderHagen_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/AtlasvanderHagen_Wikipedia_NS0_27012022.html)

#### Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek 
* Input: Commons category = [Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Media_from_Atlas_of_Mutual_Heritage_-_Koninklijke_Bibliotheek )
* Output: [MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_NS0_27012022.html)

#### Nederlandsche vogelen van Nozeman en Sepp
* Input: Commons category =  [Nederlandsche vogelen van Nozeman en Sepp](https://commons.wikimedia.org/wiki/Category:Nederlandsche%20vogelen%20van%20Nozeman%20en%20Sepp)
* Output: [NederlandschevogelenvanNozemanenSepp_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/NederlandschevogelenvanNozemanenSepp_Wikipedia_NS0_27012022.html)

#### Der naturen bloeme - KB KA 16 
* Input: Commons category = [Der naturen bloeme - KB KA 16](https://commons.wikimedia.org/wiki/Category:Der%20naturen%20bloeme%20-%20KB%20KA%2016)
* Output: [Dernaturenbloeme-KBKA16_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/Dernaturenbloeme-KBKA16_Wikipedia_NS0_27012022.html) (incl. images in the subcategories, depth=2)

#### Catchpenny prints from Koninklijke Bibliotheek
* Input: Commons category = [Catchpenny prints from Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Catchpenny%20prints%20from%20Koninklijke%20Bibliotheek)
* Output: [CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_NS0_27012022.html)

#### Bookbindings from Koninklijke Bibliotheek
* Input: Commons category = [Bookbindings from Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Bookbindings%20from%20Koninklijke%20Bibliotheek)
* Output: [BookbindingsfromKoninklijkeBibliotheek_Wikipedia_NS0_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/BookbindingsfromKoninklijkeBibliotheek_Wikipedia_NS0_27012022.html)

### Other institutions
#### Netherlands
<image src="site/logos/icon_na.jpg" width="100" hspace="10" align="right"/>

* [Nationaal Archief](https://commons.wikimedia.org/wiki/Category:Images%20from%20Nationaal%20Archief) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromNationaalArchief_Wikipedia_NS0_16012024.html)
* [Rijksmuseum Amsterdam](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Rijksmuseum) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheRijksmuseum_Wikipedia_NS0_16012024.html)
* [Beeld en Geluid](https://commons.wikimedia.org/wiki/Category:Media%20from%20Beeld%20en%20Geluid%20Wiki) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromBeeldenGeluidWiki_Wikipedia_NS0_16012024.html)
* [Tropenmuseum (former)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Tropenmuseum) :  Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheTropenmuseum_Wikipedia_NS0_16012024.html)
* [Afrika Studiecentrum (Universiteit Leiden)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20African%20Studies%20Centre%20(Leiden)) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheAfricanStudiesCentre(Leiden)_Wikipedia_NS0_17012024.html)
* [Universiteitsbibliotheek Maastricht](https://commons.wikimedia.org/wiki/Category:Images%20from%20Universiteitsbibliotheek%20Maastricht) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromUniversiteitsbibliotheekMaastricht_Wikipedia_NS0_17012024.html) and [15-02-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromUniversiteitsbibliotheekMaastricht_Wikipedia_NS0_15022024.html)
* [Het Utrechts Archief](https://commons.wikimedia.org/wiki/Category:Images%20from%20Het%20Utrechts%20Archief) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromHetUtrechtsArchief_Wikipedia_NS0_17012024.html)
* [Rijksdienst voor het Cultureel Erfgoed](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Rijksdienst%20voor%20het%20Cultureel%20Erfgoed) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheRijksdienstvoorhetCultureelErfgoed_Wikipedia_NS0_17012024.html)
* [University of Amsterdam (Special Collections)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Special%20Collections%20of%20the%20University%20of%20Amsterdam) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheSpecialCollectionsoftheUniversityofAmsterdam_Wikipedia_NS0_17012024.html)
* [Naturalis Biodiversity Center](https://commons.wikimedia.org/wiki/Category:Media%20donated%20by%20Naturalis%20Biodiversity%20Center) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediadonatedbyNaturalisBiodiversityCenter_Wikipedia_NS0_17012024.html)
* [Stadsarchief Amsterdam](https://commons.wikimedia.org/wiki/Category:Photographs%20in%20the%20Stadsarchief%20Amsterdam) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/PhotographsintheStadsarchiefAmsterdam_Wikipedia_NS0_17012024.html)
* [Museum Catharijneconvent](https://commons.wikimedia.org/wiki/Category:Media%20contributed%20by%20Museum%20Catharijneconvent) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediacontributedbyMuseumCatharijneconvent_Wikipedia_NS0_17012024.html)
* [Nationaal Museum van Wereldculturen](https://commons.wikimedia.org/wiki/Category:Files%20from%20the%20Nationaal%20Museum%20van%20Wereldculturen) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/FilesfromtheNationaalMuseumvanWereldculturen_Wikipedia_NS0_17012024.html)

#### USA
<image src="site/logos/icon_loc.png" width="200" hspace="10" align="right"/>

* [National Park Service Gallery](https://commons.wikimedia.org/wiki/Category:Images_from_NPGallery) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromNPGallery_Wikipedia_NS0_24012024.html)
* [Boston Public Library](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Boston_Public_Library) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediacontributedbyBostonPublicLibrary_Wikipedia_NS0_24012024.html)
* [Los Angeles County Museum of Art](https://commons.wikimedia.org/wiki/Category:Public_domain_images_from_the_Los_Angeles_County_Museum_of_Art) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/PublicdomainimagesfromtheLosAngelesCountyMuseumofArt_Wikipedia_NS0_24012024.html)
* [U.S. Navy Museum](https://commons.wikimedia.org/wiki/Category:Photographs_from_the_U.S._Navy_Museum) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/PhotographsfromtheU.S.NavyMuseum_Wikipedia_NS0_24012024.html)
* [Walters Art Museum](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_the_Walters_Art_Museum) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediacontributedbytheWaltersArtMuseum_Wikipedia_NS0_24012024.html)
* [Smithsonian Institution](https://commons.wikimedia.org/wiki/Category:Images_from_the_Smithsonian_Institution) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheSmithsonianInstitution_Wikipedia_NS0_24012024.html)
* [Library of Congress](https://commons.wikimedia.org/wiki/Category:Images_from_the_Library_of_Congress) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheLibraryofCongress_Wikipedia_NS0_24012024.html)
* [National Archives and Records Administration](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20National%20Archives%20and%20Records%20Administration) (NARA) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNationalArchivesandRecordsAdministration_Wikipedia_NS0_24012024.html)
* [Metropolitan Museum of Art](https://commons.wikimedia.org/wiki/Category:Images_from_Metropolitan_Museum_of_Art) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromMetropolitanMuseumofArt_Wikipedia_NS0_24012024.html)
* [New York Public Library](https://commons.wikimedia.org/wiki/Category:Images_from_the_New_York_Public_Library) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNewYorkPublicLibrary_Wikipedia_NS0_24012024.html)
* [National Gallery of Art](https://commons.wikimedia.org/wiki/Category:Images_from_the_National_Gallery_of_Art) (Washington, D.C.) : Output on [24-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNationalGalleryofArt_Wikipedia_NS0_24012024.html)


#### Scandinavia
<image src="site/logos/icon_nbn.png" width="200" hspace="10" align="right"/>

##### *Norway*  
* [Nasjonalbiblioteket](https://commons.wikimedia.org/wiki/Category:Images_from_Nasjonalbiblioteket) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromNasjonalbiblioteket_Wikipedia_NS0_01032024.html)
* [Norwegian Directorate for Cultural Heritage](https://commons.wikimedia.org/wiki/Category:Images_from_The_Norwegian_Directorate_for_Cultural_Heritage) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromTheNorwegianDirectorateforCulturalHeritage_Wikipedia_NS0_01032024.html)
* [Digitalt Museum, Norway](https://commons.wikimedia.org/wiki/Category:Images_from_Digitalt_Museum,_Norway) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromDigitaltMuseum,Norway_Wikipedia_NS0_01032024.html)
* [National Archives of Norway](https://commons.wikimedia.org/wiki/Category:Media_from_the_National_Archives_of_Norway) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromtheNationalArchivesofNorway_Wikipedia_NS0_01032024.html)
* [Kartverket](https://commons.wikimedia.org/wiki/Category:Media_from_Kartverket) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromKartverket_Wikipedia_NS0_01032024.html)
* [Oslo Museum](https://commons.wikimedia.org/wiki/Category:Media_from_the_collection_of_Oslo_Museum) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromthecollectionofOsloMuseum_Wikipedia_NS0_01032024.html)
* [Municipal Archives of Trondheim](https://commons.wikimedia.org/wiki/Category:Images_from_The_Municipal_Archives_of_Trondheim) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromTheMunicipalArchivesofTrondheim_Wikipedia_NS0_01032024.html)

##### *Sweden*
* [Nationalmuseum Stockholm](https://commons.wikimedia.org/wiki/Category:Images_from_the_Nationalmuseum_Stockholm) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNationalmuseumStockholm_Wikipedia_NS0_01032024.html)
* [National Archives of Sweden](https://commons.wikimedia.org/wiki/Category:Images_from_the_National_Archives_of_Sweden) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNationalArchivesofSweden_Wikipedia_NS0_01032024.html)
* [National Library of Sweden](https://commons.wikimedia.org/wiki/Category:Images_from_the_National_Library_of_Sweden) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromtheNationalLibraryofSweden_Wikipedia_NS0_01032024.html)
* [National Museums of World Culture](https://commons.wikimedia.org/wiki/Category:Media_from_the_National_Museums_of_World_Culture) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromtheNationalMuseumsofWorldCulture_Wikipedia_NS0_01032024.html)
* [National Museum of Science and Technology](https://commons.wikimedia.org/wiki/Category:Images_from_Tekniska_museet) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromTekniskamuseet_Wikipedia_NS0_01032024.html)
* [Livrustkammaren](https://commons.wikimedia.org/wiki/Category:Images_from_Livrustkammaren) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesfromLivrustkammaren_Wikipedia_NS0_01032024.html)

##### *Finland*
* [Helsinki City Museum](https://commons.wikimedia.org/wiki/Category:Files_from_the_Helsinki_City_Museum) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/FilesfromtheHelsinkiCityMuseum_Wikipedia_NS0_01032024.html)
* [National Archives of Finland](https://commons.wikimedia.org/wiki/Category:Files_from_the_National_Archives_of_Finland) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/FilesfromtheNationalArchivesofFinland_Wikipedia_NS0_01032024.html)
* [Finnish Society of Swedish Literature](https://commons.wikimedia.org/wiki/Category:Files_from_the_Society_of_Swedish_Literature_in_Finland) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/FilesfromtheSocietyofSwedishLiteratureinFinland_Wikipedia_NS0_01032024.html)

##### *Denmark*
 * [Statens Museum for Kunst](https://commons.wikimedia.org/wiki/Category:Images_released_under_the_CC0_1.0_Universal_license_by_Statens_Museum_for_Kunst) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/ImagesreleasedundertheCC01.0UniversallicensebyStatensMuseumforKunst_Wikipedia_NS0_01032024.html)
 * [Royal Danish Library, Portraits](https://commons.wikimedia.org/wiki/Category:Files_from_The_Portrait_Collection_of_Royal_Danish_Library) : Output on [01-03-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/FilesfromThePortraitCollectionofRoyalDanishLibrary_Wikipedia_NS0_01032024.html)

## See also
* [https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML](https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML)
* *[Public outreach and reuse of KB images via Wikipedia, 2014-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/stories/Public%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.html)* (20-12-2022)

## Change log
### 29 February 2024
* Included institutions from Norway, Sweden, Finland and .
* [README.md](README.md): Added explanations how you can run the script yourself. 

### 14 February 2024
* Refactored all code into multiple separated modules: [setup.py](setup.py), [general.py](general.py), [buildHTML.py](buildHTML.py) and [buildExcel.py](buildExcel.py). This has reduced the complexity of the main script [GLAMorousToHTML.py](GLAMorousToHTML.py) significantly and made the total suite of code much more modular and easier to understand, maintain and expand.
* Moved all HTML report pages into a separate [site/ folder](site/). This has made the repo much cleaner, clearer and more maintainable.
* Created five HTML files that redirect the old KB HTML pages (from [27-01-2022](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html) to [16-01-2024](GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16012024.html)) to the new equivalent ones in "/site" folder. Did not implement redirection for other institutions.
* Per 14-02-2024 added Excel outputs in [data/ folder](data/), to be used as structured input for data applications, such as OpenRefine
* In the proces of updating the data structure in [category_logo_dict.json](category_logo_dict.json), where the new structure can be seen under the 'Netherlands' key.
* Improved [pagetemplate.html](pagetemplate.html) to be key based (*{numarticles} Wikipedia articles*) rather than index based (*{0} Wikipedia articles*)

## Features to add
* TODO: Add Wikidata column to KB Excel sheets
