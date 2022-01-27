# GLAMorousToHTML
 Converts the output of the [GLAMorous tool](https://glamtools.toolforge.org/glamorous.php) to a HTML page.
 
The script [GLAMorousToHTML.py](GLAMorousToHTML.py) creates a HTML page listing all Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.

The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (*&ns0=1*)
2) and not pages from Wikimedia Commons, Wikidata or other Wiki-projects (*projects[wikipedia]=1*)

## Examples
