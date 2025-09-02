"""
docstring

**Author:**
Olaf Janssen – Wikimedia coordinator at KB, the national library of the Netherlands
**Supported by:** ChatGPT
**Last updated:** 20 August 2025
"""

import sys
from pathlib import Path
import pandas as pd
import ast
from folium.plugins import HeatMap
from folium.plugins import MarkerCluster

# Add the project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from general import read_excel_to_df, safe_eval, format_list_with_separator
from delpher_humans_q5_pob_pod_map_functions import *

# ====================== Config ======================
BASE_URL="http://127.0.0.1:8080/"
DEFAULT_OCCUPATION = "person"
MAX_OCCUPATIONS = 5
MAX_CITIZENSHIPS = 2
PLACEHOLDER_IMAGE = "media/portrait_placeholder.png"
CSS_FILE = 'css/delpher_humans_q5_pob_pod_map.css'
OUTPUT_FILE = Path("delpher_humans_q5_pob_pod_map_embed.html")

####### Prepare the data: dataframes and Excel ########################################################################

data_dir = Path("../data/extras")   # Input directory containing Excel
excel_file = "MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx" # Excel with only data about Delpher-related humans (Q5)
sheet_name = "aggregated_Delpher_Q5"
excel_path = (data_dir / excel_file).resolve()
if not excel_path.exists():
    raise FileNotFoundError(f"Excel file not found at {excel_path}")

# Read humanQ5-data from the Excel file
df = read_excel_to_df(excel_path, sheet_name)

required_columns = [
    "WikidataQID", "WikidataQIDLabelEn", "Images", "FullLanguageName", "ArticleURL",
    "P569_dob_str", "P570_dod_str", "P27_coc_LEn", "P21_gender_LEn_str","P106_occupation_LEn",
    "P19_pob_LatLong_str", "P19_pob_LEn_str", "P20_pod_LatLong_str", "P20_pod_LEn_str"
]

missing_cols = [col for col in required_columns if col not in df.columns]
if missing_cols:
    raise ValueError(f"Missing required columns: {missing_cols}")

df = df[required_columns].drop_duplicates(subset=["WikidataQID"])
df = df.sort_values("WikidataQIDLabelEn")

# Convert string-represented lists ("['Q739437', 'Q15296811', 'Q42973']") to actual Python lists (['Q739437', 'Q15296811', 'Q42973'])
for col in ["Images", "FullLanguageName", "ArticleURL", "P106_occupation_LEn", "P27_coc_LEn"]:
    df[col] = df[col].apply(lambda x: safe_eval(x) if not isinstance(x, list) else x)

#################################

print(f"Data read from {excel_path} on sheet '{sheet_name}'")
print(f"Dataframe shape: {df.shape}")
print(f"Columns in df: {df.columns.tolist()}")
print(df.head(20))

######### Data has been prepared - Now build the PoB-PoD map ##############

# Create a Map instance
m = folium.Map([52 ,4], zoom_start=7,width="100%",height="100%")
folium.TileLayer('cartodb positron').add_to(m)

# Initialize MarkerClusters
pob_marker_cluster = MarkerCluster(name='Markers - Places of Birth').add_to(m)
pod_marker_cluster = MarkerCluster(name='Markers - Places of Death').add_to(m)

locations=[] # Make list of [(lat,long)] for Heatmap display, holding both pob's and pod's

for i, row in enumerate(df.itertuples(index=False)):

    person_qid = row.WikidataQID
    name = row.WikidataQIDLabelEn

    gender = row.P21_gender_LEn_str
    # Pronoun choice
    pronoun = (
        "He was a" if gender == "male"
        else "She was a" if gender == "female"
        else f"{name} was a"
    )

    dob = row.P569_dob_str[1:11] if isinstance(row.P569_dob_str, str) else ""
    dod = row.P570_dod_str[1:11] if isinstance(row.P570_dod_str, str) else ""
    yob_yod = f"({dob[:4]} – {dod[:4]})" if dob and dod else f"({dob[:4]} – )" if dob else f"( – {dod[:4]})" if dod else ""

    person_pob = row.P19_pob_LEn_str if isinstance(row.P19_pob_LEn_str, str) else ""
    person_pob_html = f'{name} was born in {person_pob}'
    person_pod = row.P20_pod_LEn_str if isinstance(row.P20_pod_LEn_str, str) else ""
    person_pod_html = f'{name} died in {person_pod}'

    cocs = row.P27_coc_LEn if isinstance(row.P27_coc_LEn, list) else []
    occupations = row.P106_occupation_LEn if isinstance(row.P106_occupation_LEn, list) else [DEFAULT_OCCUPATION]
    formatted_cocs = format_list_with_separator(cocs[:MAX_CITIZENSHIPS], ", ")
    formatted_occs = f'{pronoun} {format_list_with_separator(occupations[:MAX_OCCUPATIONS], ", ")}'

    person_subtitle = f"{formatted_occs} from {formatted_cocs}" if formatted_cocs else formatted_occs
    person_subtitle_block = f"<h4>{person_subtitle} <i>{yob_yod}</i></h4>" if person_subtitle or yob_yod else ""

    # Carousel + links
    images = row.Images if isinstance(row.Images, list) else []
    langs = row.FullLanguageName if isinstance(row.FullLanguageName, list) else []
    urls = row.ArticleURL if isinstance(row.ArticleURL, list) else []
    swiper_class = f"swiper-{i}"
    img_carousel_html = build_carousel_html(images, name, swiper_class, PLACEHOLDER_IMAGE)

    # Build list of article link tags
    if langs and urls and len(langs) == len(urls):
        article_links_list = [
            f'<a href="{u}" target="_blank" title="View Wikipedia article in {l}">{l}</a>'
            for l, u in zip(langs, urls)
        ]
        formatted_article_links = format_list_with_separator(article_links_list, ", ")
    elif langs and urls:
        formatted_article_links = "<i>Incomplete article links</i>"
    else:
        formatted_article_links = "<i>No article links found</i>"

    credit_text = "Image provided by" if len(images) == 1 else "Images provided by"
    credit_html = f'<div class="credit-line">{credit_text} <img src="media/delpher_logo.svg" alt="Delpher logo" /></div>'

    """
    Transform the string tuple "(-27.55, -48.8)" from the DataFrame into the desired input for CircleMarker, 
    which should be of the (list) format [-27.55, -48.8]. 
    To convert a string representation of a tuple, like "(a, b)", into a list [a, b], you can use
    the ast.literal_eval function from the ast module to safely evaluate the string as a Python literal (tuple),
    and then convert that tuple to a list. 
    """
    #Handle Place of Birth
    if pd.notna(row.P19_pob_LatLong_str):
        pob_location = list(ast.literal_eval(row.P19_pob_LatLong_str))
        locations.append(pob_location)

        pob_popup_html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
      <meta charset="UTF-8">
      <meta name="viewport" content="width=device-width, initial-scale=1.0">
      <base href="{BASE_URL}">
      <link rel="stylesheet" href="{CSS_FILE}">
      <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css">
    </head>
    <body>
        <div class="person-block" data-qid="{person_qid}">
            <h3>{person_pob_html}</h3> 
            {person_subtitle_block}
            <div class="article-links-flex">
                <div class="wikipedia-logo"><img src="media/icon_wp.svg" alt="Wikipedia logo" /></div>
                <div class="article-text"><p>Read more on Wikipedia in {formatted_article_links}</p></div>
            </div>
            {img_carousel_html}
            {credit_html}
        </div>
    
      <!-- Swiper JS -->
      <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
      <script>
        // Init Swiper(s) inside this popup iframe
        document.addEventListener('DOMContentLoaded', () => {{
          document.querySelectorAll('.swiper').forEach(el => {{
            if (!el.__inited) {{
              new Swiper(el, {{
                slidesPerView: 1,
                spaceBetween: 10,
                pagination: {{
                  el: el.querySelector('.swiper-pagination'),
                  clickable: true
                }}
              }});
              el.__inited = true;
            }}
          }});
        }});
      </script>
    </body>
    </html>
    """

    pob_tooltip_html = f"""
    <div style="font-size: 14px; font-weight: normal; text-align: center; line-height: 1.4">
      <div style="margin: 0; font-size: 1.6em; color: #ef6079">
        <b>{name}</b> was born in {row.P19_pob_LEn_str}
      </div>
      <div style="margin: 4px 0 0;  font-size: 0.9em; color: #333; font-weight: normal">
        Click to see more info about {name}
      </div>
    </div>
    """

    add_marker_to_cluster(
        location=pob_location,
        popup_html=pob_popup_html,
        icon_color="pink",
        icon="baby-carriage",
        tooltip_html=pob_tooltip_html,
        cluster=pob_marker_cluster
    )

    # # Handle Place of Death
    # if pd.notna(row.P20_pod_LatLong_str):
    #     pod_location = list(ast.literal_eval(row.P20_pod_LatLong_str))
    #     locations.append(pod_location)
    #
    #     pod_popup_html = build_popup_content(
    #         event='died in',
    #         location_label=P20_PoDLabelEn_string,
    #         WikidataQID=WikidataQID,
    #         WikidataQIDLabelEn=WikidataQIDLabelEn,
    #         images_list=images_list,
    #         gender=gender,
    #         occupations_list=occupations_list,
    #         FullLanguageName_list=FullLanguageName_list,
    #         ArticleURL_list=ArticleURL_list,
    #         placeholder_image = "media/portrait_placeholder.png",
    #         swiper_width = 450,
    #         base_url=BASE_URL
    #     )
    #
    #     pod_tooltip_html = f"""
    #     <div style="font-size:14px; color:#01415b; font-weight:bold; text-align:center; line-height:1.4;">
    #       <h2 style="margin:0; font-size:1.6em; color:#ef6079;">
    #         <b>{WikidataQIDLabelEn}</b> died in {P20_PoDLabelEn_string}
    #       </h2>
    #       <p style="margin:4px 0 0; font-size:0.9em; color:#333;">
    #         Click to see more info about {WikidataQIDLabelEn}
    #       </p>
    #     </div>
    #     """
    #     # add_marker_to_cluster(
    #     #     pod_location,
    #     #     pod_popup_html,
    #     #     'black',
    #     #     'cross',
    #     #     pod_tooltip_html,
    #     #     pod_marker_cluster)

# Add the heatmap to the map
heatmap = HeatMap(locations,  # list of coordinates, see above,
                             # format is [(51.9617013, 5.8618218), (52.0039373, 5.9423836), (lat,long)....]
     max= 10,
     min_opacity= 0.5,
     max_zoom =10, #If max_zoom value is small (6 o so..) the heatmap layer becomes untoggleable (can't be switched on/off)
     radius = 10,
     blur = 2.0,
     gradient = {0.4: "blue", 0.6: "cyan", 0.7: "lime", 0.8: "yellow", 1.0: "red"},
     name = 'Heatmap of places of birth and death - humans in Wikipedia and portrayed in Delpher',
 )
heatmap.add_to(m)

# Add layers control to toggle between marker clusters and heatmap
folium.LayerControl().add_to(m)

# Save the map to an HTML file
m.save(OUTPUT_FILE)

