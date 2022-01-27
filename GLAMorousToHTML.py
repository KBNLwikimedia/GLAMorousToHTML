""""
This script converts the output of the GLAMorous tool (https://glamtools.toolforge.org/glamorous.php) to a HTML page.
It creates a HTML page listing all Wikipedia articles (in all languages) in which (one or more) images/media from a
given category on Wikimedia Commons are used.
The GLAMorous input needs to be configured so that it only lists pages from Wikipedia
1) that are in the main namespace (a.k.a Wikipedia articles) (&ns0=1)
2) and not pages from Wikimedia Commons, Wikidata or other Wiki-projects (projects[wikipedia]=1)
"""
import xmltodict

def languageLookup(lang):
    """"Using Wikidata, retrieve list of Wikipedia language labels in specified lang:
        Eg. retrieving list of Dutch labels (lang='nl')
          https://ko.wikipedia.org/ -- Koreaans
          https://lez.wikipedia.org/ -- Lezgisch
          https://hu.wikipedia.org/ -- Hongaars
     """
    import sys
    from SPARQLWrapper import SPARQLWrapper, JSON

    endpoint_url = "https://query.wikidata.org/sparql"
    query = """# Get language labels for all Wikipedia sites
    SELECT ?wikiurl ?taalLabel WHERE {{ 
      ?item wdt:P856 ?wikiurl.
      ?item wdt:P407 ?taal.
      ?wikiurl wikibase:wikiGroup "wikipedia".
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "{0}". }}
    }}""".format(lang)

    def get_results(endpoint_url, query):
        user_agent = "GLAMorousToHTML Python script by User:OlafJanssen"
        sparql = SPARQLWrapper(endpoint_url, agent=user_agent)
        sparql.setQuery(query)
        sparql.setReturnFormat(JSON)
        return sparql.query().convert()

    results = get_results(endpoint_url, query)
    return(results["results"]["bindings"])

def getxml(url):
    # https://stackoverflow.com/questions/24124643/parse-xml-from-url-into-python-object
    import traceback
    import urllib3
    http = urllib3.PoolManager()
    response = http.request('GET', url)
    try: # Convert XML tot JSON - https://www.geeksforgeeks.org/python-xml-to-json/
        data = xmltodict.parse(response.data, attr_prefix='', dict_constructor=dict)
    except:
        print("Failed to parse xml from response (%s)" % traceback.format_exc())
    return data


COMMONSCAT = "Media contributed by Koninklijke Bibliotheek"
DEPTH = 0 # Depth of subcategories, 0=no subcats
XMLURL = "https://glamtools.toolforge.org/glamorous.php?doit=1&category=%s&use_globalusage=1&ns0=1&depth=%s&show_details=1&projects[wikipedia]=1&format=xml" % (COMMONSCAT.replace(" ","_"), str(DEPTH))
LOCALXMLFILE = "GLAMorous_MediaContributedByKB_Wikipedia_Mainnamespace_26012022.xml" # Saved xml response from XMLURL, readmode=local
HTMLFILE = "GLAMorous_MediaContributedByKB_Wikipedia_Mainnamespace_26012022.html" # Name of the HTML file as output

# Two readmodes: 1) read from local XML 2) read from http
#readmode = "local" # Faster readmode, but can be outdated, for live/uptodate response, choose readmode=http
readmode = "http"

if readmode == "local":
    with open(LOCALXMLFILE, 'r', encoding='utf-8') as f:
        # Convert XML to JSON
        data = xmltodict.parse(f.read(), attr_prefix='', dict_constructor=dict)
elif readmode == "http":
    data = getxml(XMLURL)
else: "ERROR: No readmode specified"

# Process json
usage = data.get('results', 'XX').get('stats', 'XX').get('usage', 'XX')
projects = [usage[index].get('project', 'XX') for index, item in enumerate(usage)]
nprojects = len(projects)
#print("%s projects: %s:" % (nprojects, projects))

# Filter projects for real languages, so omit outreach, meta, simple, incubator, defunct wikis etc.
# https://be_x_old.wikipedia.org/ is defunct now
skips = ['outreach.wikipedia', 'meta.wikipedia', 'simple.wikipedia', 'incubator.wikipedia', 'be_x_old.wikipedia']
projects_filtered = [s for s in projects if s not in skips]
nprojects_filtered = len(projects_filtered)
print("%s projects_filtered: %s:" % (nprojects_filtered, projects_filtered))

projectdict = {x: [] for x in projects_filtered}

images = data.get('results', 'XX').get('details', 'XX').get('image', 'XX')
for index, image in enumerate(images):
    names = image.get('project', 'XX') # can be a dict or a list of dicts
    if isinstance(names, dict):
        wiki = names.get('name', 'XX')
        pages = names.get('namespace', 'XX').get('page', 'XX') # can be a dict or a list of dicts
        if isinstance(pages, dict):
            title = pages.get('title', 'XX')
            wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
            if wiki in projects_filtered:
                projectdict[wiki].append(wiki_url)
            else:
                pass
                #print("%s not in projects_filtered" % wiki)
        elif isinstance(pages, list):
            for page in pages:
                title = page.get('title', 'XX')
                wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                if wiki in projects_filtered:
                    projectdict[wiki].append(wiki_url)
                else:
                    pass
                    # print("%s not in projects_filtered" % wiki)
        else:print('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX')
    elif isinstance(names, list):
        for name in names:
            wiki = name.get('name', 'XX')
            pages = name.get('namespace', 'XX').get('page', 'XX') # can be a dict or a list of dicts
            if isinstance(pages, dict):
                title = pages.get('title', 'XX')
                wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                if wiki in projects_filtered:
                    projectdict[wiki].append(wiki_url)
                else:
                    pass
                    # print("%s not in projects_filtered" % wiki)
            elif isinstance(pages, list):
                for page in pages:
                    title = page.get('title', 'XX')
                    wiki_url = 'https://%s.org/wiki/%s' % (wiki, title)
                    if wiki in projects_filtered:
                        projectdict[wiki].append(wiki_url)
                    else:
                        pass
                        # print("%s not in projects_filtered" % wiki)
            else:
                print('YYYYYYYYYYYYYYYYYYYYYY')
    else:
        print('ZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZZ')

# Do some processing/cleaning/ordering/filtering: 1,2,3,4:

# 1) Deduplicate projectdict per language, see https://datagy.io/python-remove-duplicates-from-list/
# 2) For each language: Sort deduped Wikipedia article titles alphabetically
dedupdict = {x: [] for x in projects_filtered}
for key in projectdict.keys():
    dedupdict[key] = sorted(list(set(projectdict.get(key, 'XX'))))
print('dedupdict = %s' % dedupdict)

# 3) Replace wiki-code with full language, eg. in Dutch: 'nl.wikipedia' --> 'Nederlands' , 'ru.wikipedia' --> 'Russisch'
LANG = "nl" # H4 headers in Dutch
langdict = languageLookup(LANG) #dict of Wikipedia language labels in Dutch
#print('langdict = %s' % langdict)

# 4) Sort Wiki-languages by number of Wikipedia articles: en, nl, fr, ru, de ...
# https://www.geeksforgeeks.org/python-sort-dictionary-by-value-list-length/
items = ""
articlesline = ""
sortedkeys = sorted(dedupdict, key = lambda key: len(dedupdict[key]), reverse=True)
numarticles = 0 #total number of Wikipedia articles
for key in sortedkeys:
    fulllang = [lang.get('taalLabel', 'XX').get('value', 'XX') for lang in langdict if lang.get('wikiurl', 'XX').get('value', 'XX').split("//")[1].split(".org")[0] == key.replace("_", "-")]
    numlangarticles = 0 #number of Wikipedia articles per language
    for v in dedupdict[key]:
        numlangarticles = len(dedupdict[key]) # Number of Wikipedia articles in a given language
        articlesline = ['<a href="{0}" target="_blank">{1}</a>'.format(v, v.split("/wiki/")[1].replace("_", " ")) for v in dedupdict[key]]
        articlesline = " -- ".join(articlesline)
    item = '\n    <h4>%s (%s)</h4>%s' % (fulllang[0].title(), numlangarticles, articlesline)
    print(item)
    items += item
    numarticles += numlangarticles

# Convert to HTML output
html_template = """<html>
  <body>
  <h1>{0} Wikipedia-artikelen in {1} talen waarin afbeeldingen uit de <a href="https://commons.wikimedia.org/wiki/Category:{1}" target="_blank">Category:{2}</a> worden gebruikt, uitgesplitst per taalversie</h1>
  <p>Dit overzicht is gebaseerd op <a href={3} target="_blank">deze XML-output</a> van de <a href={4} target="_blank">GLAMorous-tool</a></p>
  {5}
  </body>
</html>"""

def writeHTML(narticles,nlanguages,commonscat,xmlurl,obj):
    html = html_template.format(str(narticles), str(nlanguages), commonscat.replace("_", " "), xmlurl, xmlurl.replace("&format=xml", ""), obj)
    with open(HTMLFILE, 'w', encoding='utf-8') as f:
        f.write(html)

def main():
    """Main function of the script GLAMorousToHTML.py."""
    writeHTML(numarticles, nprojects_filtered, COMMONSCAT, XMLURL, items)

if __name__ == "__main__":
    main()