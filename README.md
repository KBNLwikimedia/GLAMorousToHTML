# GLAMorousToHTML
 Converts the output of the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to a HTML page.
 
The script [GLAMorousToHTML.py](GLAMorousToHTML.py) creates a HTML page listing all Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.

The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)
2) and not pages from Wikimedia Commons, Wikidata or other Wikimedia projects (*projects[wikipedia]=1*)

## Examples
### Category:Media contributed by Koninklijke Bibliotheek
* Input: Commons category = [Media contributed by Koninklijke Bibliotheek](https://commons.wikimedia.org/wiki/Category:Media_contributed_by_Koninklijke_Bibliotheek)
* Output: [GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_MediacontributedbyKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

### GLAMorous_AtlasdeWit1698_Wikipedia_Mainnamespace_27012022.html

### GLAMorous_AtlasvanderHagen_Wikipedia_Mainnamespace_27012022.html

### GLAMorous_MediafromAtlasofMutualHeritage-KoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html

### GLAMorous_NederlandschevogelenvanNozemanenSepp_Wikipedia_Mainnamespace_27012022.html

### GLAMorous_Dernaturenbloeme-KBKA16_Wikipedia_Mainnamespace_27012022.html

### Category:Catchpenny prints from Koninklijke Bibliotheek 
* Input: Commons category = [Catchpenny prints from Koninklijke Bibliotheek ](https://commons.wikimedia.org/wiki/Category:Catchpenny%20prints%20from%20Koninklijke%20Bibliotheek)
* Output: [GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html](https://kbnlwikimedia.github.io/GLAMorousToHTML/GLAMorous_CatchpennyprintsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html)

### GLAMorous_BookbindingsfromKoninklijkeBibliotheek_Wikipedia_Mainnamespace_27012022.html

