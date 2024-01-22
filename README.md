# GLAMorousToHTML
*Converts the output of the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to a HTML page.*

*Latest update*: 23 Jan 2024

## What does it do?
<image src="logos/icon_wp.png" width="100" hspace="10" align="right"/>

The script [GLAMorousToHTML.py](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/master/GLAMorousToHTML.py) creates a HTML page listing all Wikipedia articles (in all languages) in which (one or more) images/media from a given category on Wikimedia Commons are used.

## What problem does it solve?
The KB uses the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to [measure the use of KB media files](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4) (as stored in Wikimedia Commons) in Wikipedia articles. This tool [rapports 4 things](https://tools.wmflabs.org/glamtools/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects%5Bwikipedia%5D=1) :

* 1 The **total number of KB media files** in [Category:Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) (*Category "Media contributed by Koninklijke Bibliotheek" has XXXX files.*)
* 2 The **total number of times** that KB media files are used in WP articles (*Total image usages*).
* 3 The **number of Wikipedia language versions** in which KB media files are used (*length of the table*)
* 4 The **number of unique KB media files** that are used in Wikipedia articles in all those languages. (*Distinct images used*)

Please note: 'Total image usages' does NOT equal the number of unique WP articles! A single unique KB image can illustrate multiple unique WP articles, and/or the other way around, 1 unique WP article can contain multiple unique KB images. In other words: images-articles have many-to-many relationships.

What was still missing was the functionality to measure
* 5 The **number of unique WP articles** in which KB media files are used, and to make 
* 6 A **manifest overview** of those articles, grouped per WP language version

That is why we made the GLAMorousToHTML tool. This script uses the [XML-output of GLAMorous](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml) to make an [HTML page listing unique WP articles](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html) (in which one or more KB media files are used), grouped by language.

## Configuration of GLAMorous
The script relies on the XML output of GLAMorous, which needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)
2) and not pages from Wikimedia Commons, Wikidata or other Wikimedia projects (*projects[wikipedia]=1*)

The base URL looks like *[https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=](https://glamtools.toolforge.org/glamorous.php?doit=1&use_globalusage=1&ns0=1&projects[wikipedia]=1&format=xml&category=)*. The Commons category of interest needs to be added to the end, omitting the *Category:* prefix.

## Examples
### KB, national library of the Netherlands 
<image src="logos/icon_kb.png" width="100" hspace="10" align="right"/>

#### Media contributed by Koninklijke Bibliotheek
* Input: Commons category = [Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)
* Output: 
  * [this output dd 16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16012024.html) or [this output dd 10-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_10012024.html), 
  * [this result dd 20-12-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_20122022.html), related to the article *[Public outreach and reuse of KB images via Wikipedia, 2014-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/stories/Public%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.html)*, or
  * [this output dd 16-02-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16022022.html), related to [this analysis](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4/KPI4_KB_16-02-2022) on Dutch Wikipedia dd 16-02-2022, or 
  * [this output dd 27-01-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html) 

#### Atlas de Wit 1698
* Input: Commons category = [Atlas de Wit 1698](https://commons.wikimedia.org/wiki/Category:Atlas%20de%20Wit%201698)
* Output: [GLAMorous_AtlasdeWit1698_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_AtlasdeWit1698_Wikipedia_Mainnamespace_27012022.html)

#### Atlas van der Hagen
* Input: Commons category = [Atlas van der Hagen](https://commons.wikimedia.org/wiki/Category:Atlas%20van%20der%20Hagen)
* Output: [GLAMorous_AtlasvanderHagen_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_AtlasvanderHagen_Wikipedia_Mainnamespace_27012022.html)

#### Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek 
* Input: Commons category = [Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Media_from_Atlas_of_Mutual_Heritage_-_Koninklijke_Bibliotheek )
* Output: [GLAMorous_MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

#### Nederlandsche vogelen van Nozeman en Sepp
* Input: Commons category =  [Nederlandsche vogelen van Nozeman en Sepp](https://commons.wikimedia.org/wiki/Category:Nederlandsche%20vogelen%20van%20Nozeman%20en%20Sepp)
* Output: [GLAMorous_NederlandschevogelenvanNozemanenSepp_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_NederlandschevogelenvanNozemanenSepp_Wikipedia_Mainnamespace_27012022.html)

#### Der naturen bloeme - KB KA 16 
* Input: Commons category = [Der naturen bloeme - KB KA 16](https://commons.wikimedia.org/wiki/Category:Der%20naturen%20bloeme%20-%20KB%20KA%2016)
* Output: [GLAMorous_Dernaturenbloeme-KBKA16_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_Dernaturenbloeme-KBKA16_Wikipedia_Mainnamespace_27012022.html) (incl. images in the subcategories, depth=2)

#### Catchpenny prints from Koninklijke Bibliotheek
* Input: Commons category = [Catchpenny prints from Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Catchpenny%20prints%20from%20Koninklijke%20Bibliotheek)
* Output: [GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

#### Bookbindings from Koninklijke Bibliotheek
* Input: Commons category = [Bookbindings from Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Bookbindings%20from%20Koninklijke%20Bibliotheek)
* Output: [GLAMorous_BookbindingsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_BookbindingsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

### Other institutions
#### Netherlands
<image src="logos/icon_na.jpg" width="100" hspace="10" align="right"/>

* [Nationaal Archief](https://commons.wikimedia.org/wiki/Category:Images%20from%20Nationaal%20Archief) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromNationaalArchief_Wikipedia_Mainnamespace_16012024.html)
* [Rijksmuseum Amsterdam](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Rijksmuseum) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheRijksmuseum_Wikipedia_Mainnamespace_16012024.html)
* [Beeld en Geluid](https://commons.wikimedia.org/wiki/Category:Media%20from%20Beeld%20en%20Geluid%20Wiki) : Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediafromBeeldenGeluidWiki_Wikipedia_Mainnamespace_16012024.html)
* [Tropenmuseum (former)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Tropenmuseum) :  Output on [16-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheTropenmuseum_Wikipedia_Mainnamespace_16012024.html)
* [Afrika Studiecentrum (Universiteit Leiden)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20African%20Studies%20Centre%20(Leiden)) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheAfricanStudiesCentre(Leiden)_Wikipedia_Mainnamespace_17012024.html)
* [Universiteitsbibliotheek Maastricht](https://commons.wikimedia.org/wiki/Category:Images%20from%20Universiteitsbibliotheek%20Maastricht) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromUniversiteitsbibliotheekMaastricht_Wikipedia_Mainnamespace_17012024.html)
* [Het Utrechts Archief](https://commons.wikimedia.org/wiki/Category:Images%20from%20Het%20Utrechts%20Archief) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromHetUtrechtsArchief_Wikipedia_Mainnamespace_17012024.html)
* [Rijksdienst voor het Cultureel Erfgoed](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Rijksdienst%20voor%20het%20Cultureel%20Erfgoed) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheRijksdienstvoorhetCultureelErfgoed_Wikipedia_Mainnamespace_17012024.html)
* [University of Amsterdam (Special Collections)](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20Special%20Collections%20of%20the%20University%20of%20Amsterdam) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheSpecialCollectionsoftheUniversityofAmsterdam_Wikipedia_Mainnamespace_17012024.html)
* [Naturalis Biodiversity Center](https://commons.wikimedia.org/wiki/Category:Media%20donated%20by%20Naturalis%20Biodiversity%20Center) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediadonatedbyNaturalisBiodiversityCenter_Wikipedia_Mainnamespace_17012024.html)
* [Stadsarchief Amsterdam](https://commons.wikimedia.org/wiki/Category:Photographs%20in%20the%20Stadsarchief%20Amsterdam) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_PhotographsintheStadsarchiefAmsterdam_Wikipedia_Mainnamespace_17012024.html)
* [Museum Catharijneconvent](https://commons.wikimedia.org/wiki/Category:Media%20contributed%20by%20Museum%20Catharijneconvent) :  Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyMuseumCatharijneconvent_Wikipedia_Mainnamespace_17012024.html)
* [Nationaal Museum van Wereldculturen](https://commons.wikimedia.org/wiki/Category:Files%20from%20the%20Nationaal%20Museum%20van%20Wereldculturen) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_FilesfromtheNationaalMuseumvanWereldculturen_Wikipedia_Mainnamespace_17012024.html)

#### USA
<image src="logos/icon_loc.png" width="200" hspace="10" align="right"/>

* [U.S. Navy Museum](https://commons.wikimedia.org/wiki/Category:Photographs_from_the_U.S._Navy_Museum) : Output on [22-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/PhotographsfromtheU.S.NavyMuseum_Wikipedia_NS0_22012024.html)
* [Walters Art Museum](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_the_Walters_Art_Museum) : Output on [22-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/MediacontributedbytheWaltersArtMuseum_Wikipedia_NS0_22012024.html)
* [Smithsonian Institution](https://commons.wikimedia.org/wiki/Category:Images_from_the_Smithsonian_Institution) : Output on [22-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/ImagesfromtheSmithsonianInstitution_Wikipedia_NS0_22012024.html)
* [Library of Congress](https://commons.wikimedia.org/wiki/Category:Images_from_the_Library_of_Congress) : Output on [19-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheLibraryofCongress_Wikipedia_Mainnamespace_19012024.html)
* [National Archives and Records Administration](https://commons.wikimedia.org/wiki/Category:Images%20from%20the%20National%20Archives%20and%20Records%20Administration) (NARA) : Output on [19-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheNationalArchivesandRecordsAdministration_Wikipedia_Mainnamespace_19012024.html)
* [Metropolitan Museum of Art](https://commons.wikimedia.org/wiki/Category:Images_from_Metropolitan_Museum_of_Art) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromMetropolitanMuseumofArt_Wikipedia_Mainnamespace_17012024.html)
* [New York Public Library](https://commons.wikimedia.org/wiki/Category:Images_from_the_New_York_Public_Library) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheNewYorkPublicLibrary_Wikipedia_Mainnamespace_17012024.html)
* [National Gallery of Art](https://commons.wikimedia.org/wiki/Category:Images_from_the_National_Gallery_of_Art) (Washington, D.C.) : Output on [17-01-2024](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_ImagesfromtheNationalGalleryofArt_Wikipedia_Mainnamespace_17012024.html)

## See also
* [https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML](https://commons.wikimedia.org/wiki/Commons:GLAMorousToHTML)
* *[Public outreach and reuse of KB images via Wikipedia, 2014-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/stories/Public%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.html)* (20-12-2022)

## Features to add
* ....
