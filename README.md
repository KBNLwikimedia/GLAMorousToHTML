# GLAMorousToHTML
*Converts the output of the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to a HTML page.*

## What does it do?
The script [GLAMorousToHTML.py](GLAMorousToHTML.py) creates a HTML page listing all Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.

The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)
2) and not pages from Wikimedia Commons, Wikidata or other Wikimedia projects (*projects[wikipedia]=1*)

## What problem does it solve?
De KB gebruikt de [https://glamtools.toolforge.org/glamorous.php GLAMorous tool] om het hergebruik van KB-mediabestanden in Wikipedia (hoofdnaamruimte) te meten. Deze tool [https://tools.wmflabs.org/glamtools/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects%5Bwikipedia%5D=1 rapporteert 4 grootheden]:
# Het '''totaal aantal KB-mediabestanden''' in [[:c:Category:Media contributed by Koninklijke Bibliotheek|Category:Media contributed by Koninklijke Bibliotheek]] (''Category "Media contributed by Koninklijke Bibliotheek" has XXXX files.'')
# Het '''totaal aantal keren''' dat KB-mediabestanden in WP-artikelen gebruikt worden (''Total image usages'').
# Het '''aantal taalversies''' van Wikipedia waarin KB-mediabestanden opgenomen zijn (''lengte van de tabel'')
# Het '''aantal unieke KB-mediabestanden''' dat in Wikipedia-artikelen in al die taalversies opgenomen is. (''Distinct images used'')

Wat echter nog ontbrak is
* het '''aantal unieke Wikipedia-artikelen''' waarin KB-mediabestanden zijn opgenomen 
* een '''manifest overzicht''' van die artikelen, uitgesplitst per taalversie

Daarom hebben we de '''[https://github.com/KBNLwikimedia/GLAMorousToHTML GLAMorousToHTML tool]''' gemaakt. Dit script maakt o.b.v. de [https://glamtools.toolforge.org/glamorous.php?doit=1&category=Media+contributed+by+Koninklijke+Bibliotheek&use_globalusage=1&ns0=1&show_details=1&projects[wikipedia]=1&format=xml XML-output van GLAMorous] een [https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16022022.html HTML-pagina waarin al die Wikipedia-artikelen, uitgesplitst per taalversie], worden opgesomd.


## Examples
### Category:Media contributed by Koninklijke Bibliotheek
* Input: Commons category = [Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)
* Output: [GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html) or 
 * this [output dd 16-02-2022](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_16022022.html), related to [this analysis](https://nl.wikipedia.org/wiki/Wikipedia:GLAM/Koninklijke_Bibliotheek_en_Nationaal_Archief/Resultaten/KPIs/KPI4/KPI4_KB_16-02-2022) on Dutch Wikipedia dd 16-02-2022.

### Category:Atlas de Wit 1698
* Input: Commons category = [Atlas de Wit 1698](https://commons.wikimedia.org/wiki/Category:Atlas%20de%20Wit%201698)
* Output: [GLAMorous_AtlasdeWit1698_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_AtlasdeWit1698_Wikipedia_Mainnamespace_27012022.html)

###  Category:Atlas van der Hagen
* Input: Commons category = [Atlas van der Hagen](https://commons.wikimedia.org/wiki/Category:Atlas%20van%20der%20Hagen)
* Output: [GLAMorous_AtlasvanderHagen_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_AtlasvanderHagen_Wikipedia_Mainnamespace_27012022.html)

### Category:Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek 
* Input: Commons category = [Media from Atlas of Mutual Heritage - Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Media_from_Atlas_of_Mutual_Heritage_-_Koninklijke_Bibliotheek )
* Output: [GLAMorous_MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

### Category:Nederlandsche vogelen van Nozeman en Sepp
* Input: Commons category =  [Nederlandsche vogelen van Nozeman en Sepp](https://commons.wikimedia.org/wiki/Category:Nederlandsche%20vogelen%20van%20Nozeman%20en%20Sepp)
* Output: [GLAMorous_NederlandschevogelenvanNozemanenSepp_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_NederlandschevogelenvanNozemanenSepp_Wikipedia_Mainnamespace_27012022.html)

### Category:Der naturen bloeme - KB KA 16 
* Input: Commons category = [Der naturen bloeme - KB KA 16](https://commons.wikimedia.org/wiki/Category:Der%20naturen%20bloeme%20-%20KB%20KA%2016)
* Output: [GLAMorous_Dernaturenbloeme-KBKA16_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_Dernaturenbloeme-KBKA16_Wikipedia_Mainnamespace_27012022.html) (incl. images in the subcategories, depth=2)

### Category:Catchpenny prints from Koninklijke Bibliotheek
* Input: Commons category = [Catchpenny prints from Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Catchpenny%20prints%20from%20Koninklijke%20Bibliotheek)
* Output: [GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

### Category:Bookbindings from Koninklijke Bibliotheek
* Input: Commons category = [Bookbindings from Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Bookbindings%20from%20Koninklijke%20Bibliotheek)
* Output: [GLAMorous_BookbindingsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_BookbindingsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)
