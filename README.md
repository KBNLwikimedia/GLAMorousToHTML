<table width="100%" border="0"><tr><td align="left">
<a href="https://kbnlwikimedia.github.io/tools/index.html"><< Back to tools and scripts index</a>
</td><td align="right">
<a href="https://github.com/KBNLwikimedia/GLAMorousToHTML" target="_blank">>> To the Github repo of this page</a>
</td></tr></table>
<hr/>

# GLAMorousToHTML

*Creates a datestamped HTML report and a corresponding Excel file listing all Wikipedia articles (in all languages) in which (one or more) images from a given category tree on Wikimedia Commons are used.*

*Latest update*: 13 September 2025

--------------

## What does it do?
<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_wp.png" width="100" hspace="10" align="right"/>

This repo creates datestamped HTML reports with corresponding Excel files listing all Wikipedia articles (in all languages) in which (one or more) images/media from a given category tree on Wikimedia Commons are used. 

### Quick example
Here is quick example of such an [HTML report](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.html) and its [corresponding Excel file](https://kbnlwikimedia.github.io/GLAMorousToHTML/data/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.xlsx) 
for [images from the collection](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) of the [KB, national library of the Netherlands](https://www.kb.nl/en).
It is datestamped 04-09-2024. 

<a href="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.html" target="_blank"><image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/reports/images/screenshot_report_KB_0492024.png" hspace="0" align="left"/></a>
<br clear="all"/>

## What problem does it solve?

The KB uses the 'classical' [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to [measure the use of KB media files](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4) (as stored in Wikimedia Commons) in Wikipedia articles. This tool [reports 4 things](https://tools.wmflabs.org/glamtools/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects%5Bwikipedia%5D=1):

* 1 - The total **number of KB media files** in [Category:Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) (*Category "Media contributed by Koninklijke Bibliotheek" has XXXX files.*)
* 2 - The **number of Wikipedia language versions** in which KB media files are used (*length of the table*, omitting non-language Wikipedias, such as 'outreach.wikipedia', 'simple.wikipedia' or 'incubator.wikipedia')
* 3 - The total **number of times that these images show up** in Wikipedia articles, in all language versions. (*Total image usages*).
* 4 - The **number of unique KB media files** that are used in Wikipedia articles in all those languages. (*Distinct images used*)

Please note: 'Total image usages' does NOT equal the number of unique Wikipedia articles! A single unique image can illustrate multiple unique articles, and/or the other way around, 1 unique article can contain multiple distinct images. In other words: images-articles have many-to-many relationships.

What was still missing were functionalities to create
* 5 - The **number of unique Wikipedia articles** in which KB media files are used, 
* 6 - A **manifest overview** of those articles, grouped per Wikipedia language version,
* 7 - A **structured output format** that can be easily processed by tools, such as CSV of Excel files.

Bulk/group functionalities:
* 8 - A method to **generate these reports in bulk**, so for multiple Commons categories trees at once (with one report per category tree).
* 9 - **Aggregated data** and **key figure statistics** for sets of reports, eg. for grouped reports from a specific country.

That is why we developed the GLAMorousToHTML tool. It takes the [XML-output of the GLAMorous tool](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml) and processes that data into HTML reports and Excel files. 

## GLAM reports

The GLAMorousToHTML tool has so for produced [GLAM reports](reports/reports.md) for the following heritage institutions, countries and regions:

* [KB, national library of the Netherlands](reports/reports.md#kb-national-library-of-the-netherlands), including [Delpher](reports/reports.md#media-from-delpher) and the [KB portraits collection](reports/reports.md#portraits-from-koninklijke-bibliotheek) 
* [Kingdom of the Netherlands](reports/reports.md#kingdom-of-the-netherlands)
  * [Selected institutions](reports/reports.md#selected-institutions)
  * [Netwerk Digitaal Erfgoed (NDE)](reports/reports_nde.md), the Dutch [network for digital heritage](https://netwerkdigitaalerfgoed.nl/)
  * The [Wikipedia on Aruba - Aruba on Wikipedia](reports/reports.md#the-wikipedia-on-aruba---aruba-on-wikipedia-project) project
* [Nordic European countries](reports/reports.md#nordic-european-countries) 
  * [Norway](reports/reports.md#norway)
  * [Finland](reports/reports.md#finland)
  * [Sweden](reports/reports.md#sweden)
  * [Denmark](reports/reports.md#denmark)
* [United States of America](reports/reports.md#usa)
* [Australia and New Zealand](reports/reports.md#australia-and-new-zealand)
  * [Australia](reports/reports.md#australia) 
  * [New Zealand](reports/reports.md#new-zealand) 

When interpreting these reports, take note of 
* the [structure](reports/reports.md#reports-structure) of the reports and Excel files, 
* [who contributed](reports/reports.md#who-contributed) the images, 
* the [accuracy of category trees](reports/reports.md#accuracy-and-overshooting-of-category-trees) and 
* [image thumbnails & template contamination](reports/reports.md#image-thumbnails-in-templates-template-contamination). 

## Publications
* An article about the public outreach and reuse of [Delpher images](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher) via Wikipedia and Wikimedia Commons will be added a.s.a.p. (autumn 2025) 
* A first article about the NDE reports will be published a.s.a.p. (autumn 2025)
* [Public outreach and reuse of KB images via Wikipedia, 2014-2022](stories/Public%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.html) (December 2022). This article is also available [as a PDF](stories%2FPublic%20outreach%20and%20reuse%20of%20KB%20images%20via%20Wikipedia%2C%202014-2022.pdf).

## Products & prototypes

<a href="https://kbnlwikimedia.github.io/GLAMorousToHTML/extras/delpher_humans_q5_gallery.html" target="_blank"><image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/extras/media/wikipedia-delpher-portrait-explorer_20250912.jpg" hspace="0" align="right" width="30%"/></a>

* **[Wikipedia ❤️ Delpher - Portrait explorer](https://kbnlwikimedia.github.io/GLAMorousToHTML/extras/delpher_humans_q5_gallery.html)**, a visual exploration of notable individuals in Wikipedia, illustrated by Delpher.<br/>
It allows you to explore humans who are described in Wikipedia articles illustrated by [Delpher images](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher). You can do so by occupation, gender, country of citizenship, decades of birth and death and Wikipedia language version. For instance: [female opera singers from France born in the 1880s described by a Wikipedia article in French](https://kbnlwikimedia.github.io/GLAMorousToHTML/extras/delpher_humans_q5_gallery.html?page=1&sort=name_asc&country=Q142&gender=Q6581072&occ=Q2865819&dob=1880&pc=fr).<br/>
For this the [01-07-2025 report](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromDelpher_Wikipedia_NS0_01072025.html) for [Media from Delpher](https://commons.wikimedia.org/wiki/Category:Media_from_Delpher) has been extended with data from Wikidata (limited [humans/Q5](https://www.wikidata.org/wiki/Q5) only), and rendered into an interactive portrait gallery. 
 
* **[Map of places of birth and death]()** - To add

## Technical notes

The [technical notes](technical-notes.md) give more info about 
1. The structure of the this repo, its files and folders 
2. Short description of their functions
3. How to run this repo yourself
4. Change log
5. Features to be added

Please note that his page is still under construction and is therefore messy and incomplete.

## Licensing

<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_cc0.png" width="100" hspace="10" align="right"/>

All original materials in this repo, expect for the [flags](https://github.com/KBNLwikimedia/GLAMorousToHTML/tree/main/site/flags), [logos](https://github.com/KBNLwikimedia/GLAMorousToHTML/tree/main/site/logos) and [publications](https://github.com/KBNLwikimedia/GLAMorousToHTML/tree/main/stories)
are released under the [CC0 1.0 Universal license](https://github.com/KBNLwikimedia/GLAMorousToHTML/blob/main/LICENSE), effectively donating all original content to the public domain.

For the [publications](#publications) listed above : see each article for its exact licensing condition.

## Contact

<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_kb2.png" width="200" hspace="10" align="right"/>

This tool is developed and maintained by Olaf Janssen, Wikimedia coordinator [@KB, national library of the Netherlands](https://www.kb.nl).
You can find his contact details on his [KB expert page](https://www.kb.nl/over-ons/experts/olaf-janssen) or via his [Wikimedia user page](https://commons.wikimedia.org/wiki/User:OlafJanssen).

If you are interested in getting reports for your own GLAM institution, please send me a message.   