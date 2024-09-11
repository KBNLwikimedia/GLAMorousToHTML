# GLAMorousToHTML

*Creates a datestamped HTML report and a corresponding Excel file listing all Wikipedia articles (in all languages) in which (one or more) images from a given category tree on Wikimedia Commons are used.*

*Latest update*: 16 September 2024

--------------

## What does it do?
<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_wp.png" width="100" hspace="10" align="right"/>

This repo creates datestamped HTML reports with corresponding Excel files listing all Wikipedia articles (in all languages) in which (one or more) images/media from a given category tree on Wikimedia Commons are used. 

### Quick example
Here is quick example of such an [HTML report](https://kbnlwikimedia.github.io/GLAMorousToHTML/site/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.html) and its [corresponding Excel file](https://kbnlwikimedia.github.io/GLAMorousToHTML/data/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.xlsx) 
for [images from the collection](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) of the [KB, national library of the Netherlands](https://www.kb.nl/en).
It is datestamped 04-09-2024. 

<a href="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/nde/MediacontributedbyKoninklijkeBibliotheek_Wikipedia_NS0_04092024.html" target="_blank"><image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/reports/screenshot_report_KB_0492024.png" hspace="0" align="left"/></a>
<br clear="all"/>

--------------

## What problem does it solve?
The KB uses the 'classical' [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to [measure the use of KB media files](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4) (as stored in Wikimedia Commons) in Wikipedia articles. This tool [rapports 4 things](https://tools.wmflabs.org/glamtools/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects%5Bwikipedia%5D=1) :

* 1 - The total **number of KB media files** in [Category:Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek) (*Category "Media contributed by Koninklijke Bibliotheek" has XXXX files.*)
* 2 - The **number of Wikipedia language versions** in which KB media files are used (*length of the table*, omitting non-language Wikipedias, such as 'outreach.wikipedia', 'simple.wikipedia' or 'incubator.wikipedia')
* 3 - The total **number of times that distinct images show up** in Wikipedia articles, in all language versions. (*Total image usages*).
* 4 - The **number of unique KB media files** that are used in Wikipedia articles in all those languages. (*Distinct images used*)

Please note: 'Total image usages' does NOT equal the number of unique Wikipedia articles! A single unique image can illustrate multiple unique articles, and/or the other way around, 1 unique article can contain multiple distinct images. In other words: images-articles have many-to-many relationships.

What was still missing were functionalities to measure
* 5 - The **number of unique Wikipedia articles** in which KB media files are used, 
* 6 - A **manifest overview** of those articles, grouped per Wikipedia language version,
* 7 - A **structured output format** that can be easily processed by tools, such as CSV of Excel files.
* 8 - A method to **generate these reports in bulk**, so for multiple Commons categories trees at once (with one report per category tree). 

That is why we developed the GLAMorousToHTML tool. It takes the [XML-output of the GLAMorous tool](https://glamtools.toolforge.org/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml) and processes that data into HTML reports and Excel files. 

--------------

## Reports
The GLAMorousToHTML tool has so for produced [reports](./reports/reports.md) for the following institutions, countries and regions:

* [KB, national library of the Netherlands](https://kbnlwikimedia.github.io/GLAMorousToHTML/reports/reports.html#kb-national-library-of-the-netherlands)
* The Netherlands
  * Selected institutions
  * Netwerk Digitaal Erfgoed (NDE), the Dutch [network for digital heritage](https://netwerkdigitaalerfgoed.nl/)
* Nordic European countries
  * Norway
  * Finland
  * Sweden
  * Denmark
* United States of America
* Australia and New Zealand
  * Australia
  * New Zealand

--------------

## Technical notes

The [technical notes](technical-notes.md) give more info about 
1. The structure of the this repo, its files and folders 
2. Short description of their functions
3. How to run this repo yourself
4. Change log
5. Features to be added

Please note that his page is still under construction and is therefore messy and incomplete.

--------------

## CC0 licensing
<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_cc0.png" width="100" hspace="10" align="right"/>

All original materials in this repo, expect for the [flags](https://github.com/KBNLwikimedia/GLAMorousToHTML/tree/main/site/flags) and [logos](https://github.com/KBNLwikimedia/GLAMorousToHTML/tree/main/site/logos), are released under the [CC0 1.0 Universal license](LICENSE)

--------------

## Contact
<image src="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/logos/icon_kb2.png" width="200" hspace="10" align="right"/>

This tool is developed and maintained by Olaf Janssen, Wikimedia coordinator [@KB, national library of the Netherlands](https://www.kb.nl).
You can find his contact details on his [KB expert page](https://www.kb.nl/over-ons/experts/olaf-janssen) or via his [Wikimedia user page](https://commons.wikimedia.org/wiki/User:OlafJanssen).