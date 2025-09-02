"""
Delpher × Wikipedia — Portrait Explorer (Static HTML Generator)
===============================================================

This script builds a **single, static HTML gallery** of people (Wikidata class Q5) who
are described in Wikipedia and visually represented in **Delpher**, the Dutch
digital library of historical documents. The gallery is fully client-side: once
the HTML is written, filtering, searching, sorting, pagination, and image
carousels all run in the browser.

# What it generates
- `delpher_humans_q5_gallery.html` — a complete, responsive gallery page.
- Each “person card” includes:
  - Name (Wikidata label)
  - Subtitle with occupation(s) and country/ies of citizenship
  - Years of birth/death (if known)
  - **Swiper** image carousel (Commons thumbnails) with lazy loading
  - Multilingual Wikipedia links
  - Delpher image attribution line
- Client-side **facets** exposed as `<select>` filters:
  - Occupation, Gender, Country of citizenship
  - **Decade of birth** and **Decade of death**
  - Wikipedia language (by project code)
- Client-side **search** (free text) and **sorting**:
  - Sort by **Name (A–Z / Z–A)**, **Year of birth** (↑/↓) and **Year of death** (↑/↓)
- Client-side **pagination** with a results summary (“Showing … | Page … | Sort …”)
- Defensive fallbacks so the page still renders if some pieces fail to build

# Data inputs (Excel workbook)
By default the script reads:
- File: `../../data/extras/MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx`
- Sheets and required columns:
  - `aggregated_Delpher_Q5`:
    - `WikidataQID`, `WikidataQIDLabelEn`, `Images`, `FullLanguageName`,
      `ArticleURL`, `P569_dob_str`, `P570_dod_str`, `P106_occupation_LEn`, `P27_coc_LEn`
  - `occupation_summary`:
    - `OccupationQID`, `OccupationQID_LEn`, `PeopleWithThisOccupationQIDs`
  - `gender_summary`:
    - `GenderQID`, `GenderQID_LEn`, `PeopleWithThisGenderQIDs`
  - `coc_summary`:
    - `CountryOfCitizenshipQID`, `CountryOfCitizenshipQID_LEn`,
      `PeopleWithThisCountryOfCitizenshipQIDs`
  - `dob_summary`:
    - `DoB`, `PeopleWithThisDoBQIDs`
  - `dod_summary`:
    - `DoD`, `PeopleWithThisDoDQIDs`
  - `projectcode_summary`:
    - `ProjectCodeQID`, `FullLanguageName`, `PeopleWithThisProjectCodeQIDs`

The script validates file existence and the presence of required columns/sheets,
and will exit with an error message if critical inputs are missing.

# Output & expected assets
- Writes: `../delpher_humans_q5_gallery.html`
- References external assets you should provide/deploy:
  - CSS: `css/delpher_humans_q5_gallery.css`
  - JS:  `js/delpher_humans_q5_gallery.js`
  - Media (logos/placeholders): e.g. `media/icon_wp.svg`, `media/delpher_logo.svg`,
    `media/portrait_placeholder.png`
  - Swiper from CDN (CSS/JS) is linked in the HTML

# Implementation notes
- Cards carry `data-*` attributes (e.g., `data-occs`, `data-gender`, `data-countries`,
  `data-yob`, `data-yod`, `data-dob`, `data-dod`, `data-pcs`) so the browser can
  filter/sort without reloading.
- Commons thumbnails are requested via `Special:FilePath?width=…` for fast loads.
- The script uses helper functions from:
  - `general.py` — `read_excel_to_df`, `safe_eval`, `format_list_with_separator`
  - `delpher_humans_q5_gallery_functions.py` — HTML builders & utilities
- **Error handling & fallbacks**
  - Fatal issues (missing Excel or columns, write failures) abort with a clear message.
  - Non-fatal issues (a facet block failing to build, a single card failing to render)
    are **logged** and replaced with minimal, safe HTML so the page still loads.
  - A summary of non-fatal warnings is printed at the end of each stage.

# Usage
Run the script directly (ensure working directory resolves the relative paths above):
    python path/to/this_script.py

Adjust constants near the top (TITLE, SUBTITLE, paths, BLOCKS_PER_PAGE, etc.) as needed.

# Attribution
- Data: Wikipedia, Wikidata, Wikimedia Commons, and **Delpher** (KB – National Library of the Netherlands).
- Author: **Olaf Janssen**, Wikimedia coordinator of the KB (National Library of the Netherlands)
- Supported by: ChatGPT
- Last updated: **1 September 2025**
"""

from pathlib import Path
from collections import defaultdict
import sys
import html
# Extend sys.path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from general import read_excel_to_df, safe_eval, format_list_with_separator
from delpher_humans_q5_gallery_functions import *


# ====================== Config ======================
TITLE = "Delpher ❤️ Wikipedia - Portrait explorer"
SUBTITLE = "A visual exploration of notable individuals in Wikipedia, illustrated by Delpher"
DEFAULT_OCCUPATION = "Person"
MAX_OCCUPATIONS = 5
MAX_CITIZENSHIPS = 2
BLOCKS_PER_PAGE = 50
PLACEHOLDER_IMAGE = "media/portrait_placeholder.png"
CSS_FILE = "css/delpher_humans_q5_gallery.css"
JS_FILE = "js/delpher_humans_q5_gallery.js"
OUTPUT_FILE = Path("../delpher_humans_q5_gallery.html")
LATEST_UPDATE = "1 September 2025"

# ====================== Data loading ======================
try:
    data_dir = Path("../../data/extras")
    excel_file = "MediafromDelpher_Wikipedia_NS0_01072025 - humansQ5.xlsx"
    sheet_name = "aggregated_Delpher_Q5"
    excel_path = (data_dir / excel_file).resolve()

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found at {excel_path}")

    df = read_excel_to_df(excel_path, sheet_name)

    required_columns = [
        "WikidataQID", "WikidataQIDLabelEn", "Images", "FullLanguageName",
        "ArticleURL", "P569_dob_str", "P570_dod_str", "P106_occupation_LEn", "P27_coc_LEn"
    ]
    missing_cols = [col for col in required_columns if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns: {missing_cols}")

    df = df[required_columns].drop_duplicates(subset=["WikidataQID"])
    df = df.sort_values("WikidataQIDLabelEn") # Sort dataframe alphabetically by full name of person

    # Parse list-like columns
    for col in ["Images", "FullLanguageName", "ArticleURL", "P106_occupation_LEn", "P27_coc_LEn"]:
        df[col] = df[col].apply(lambda x: safe_eval(x) if not isinstance(x, list) else x)

except Exception as e:
    sys.exit(f"❌ Error loading data: {e}")


# ====================== Facet summaries ======================
try:
    occ_sheet = "occupation_summary"
    gender_sheet = "gender_summary"
    country_sheet = "coc_summary"

    dob_sheet = "dob_summary"
    dod_sheet = "dod_summary"
    pc_sheet = "projectcode_summary"

    occ_df = read_excel_to_df(excel_path, occ_sheet)[
        ["OccupationQID", "OccupationQID_LEn", "PeopleWithThisOccupationQIDs"]
    ]
    gdf = read_excel_to_df(excel_path, gender_sheet)[
        ["GenderQID", "GenderQID_LEn", "PeopleWithThisGenderQIDs"]
    ]
    country_df = read_excel_to_df(excel_path, country_sheet)[
        ["CountryOfCitizenshipQID", "CountryOfCitizenshipQID_LEn", "PeopleWithThisCountryOfCitizenshipQIDs"]
    ]
    dob_df = read_excel_to_df(excel_path, dob_sheet)[
        ["DoB","PeopleWithThisDoBQIDs"]
    ]
    dob_df["DoB"] = dob_df["DoB"].astype(str) # Convert from int64 to string for consistent processing
    dod_df = read_excel_to_df(excel_path, dod_sheet)[
        ["DoD","PeopleWithThisDoDQIDs"]
    ]
    dod_df["DoD"] = dod_df["DoD"].astype(str)

    pc_df = read_excel_to_df(excel_path, pc_sheet)[
        ["ProjectCodeQID", "FullLanguageName", "PeopleWithThisProjectCodeQIDs"]
    ]

    # Drop nulls
    occ_df = occ_df[occ_df["OccupationQID_LEn"].notna() & (occ_df["OccupationQID_LEn"].str.strip() != "")]
    gdf = gdf[gdf["GenderQID_LEn"].notna() & (gdf["GenderQID_LEn"].str.strip() != "")]
    country_df = country_df[country_df["CountryOfCitizenshipQID_LEn"].notna() & (country_df["CountryOfCitizenshipQID_LEn"].str.strip() != "")]
    dob_df = dob_df[dob_df["DoB"].notna() & (dob_df["DoB"].str.strip() != "")]
    dod_df = dod_df[dod_df["DoD"].notna() & (dod_df["DoD"].str.strip() != "")]
    pc_df = pc_df[pc_df["FullLanguageName"].notna() & (pc_df["FullLanguageName"].str.strip() != "")]

    # Parse lists - Safely parse a stringified list of strings into a Python list of strings.
    occ_df["PeopleQIDs"] = occ_df["PeopleWithThisOccupationQIDs"].apply(parse_qids)
    gdf["PeopleQIDs"] = gdf["PeopleWithThisGenderQIDs"].apply(parse_qids)

    country_df["PeopleQIDs"] = country_df["PeopleWithThisCountryOfCitizenshipQIDs"].apply(parse_qids)
    dob_df["PeopleQIDs"] = dob_df["PeopleWithThisDoBQIDs"].apply(parse_qids)
    dod_df["PeopleQIDs"] = dod_df["PeopleWithThisDoDQIDs"].apply(parse_qids)


    pc_df["PeopleQIDs"] = pc_df["PeopleWithThisProjectCodeQIDs"].apply(parse_qids)

    # Restrict to gallery people
    people_in_gallery = set(df["WikidataQID"])
    occ_df["PeopleQIDs"] = occ_df["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])
    gdf["PeopleQIDs"] = gdf["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])
    country_df["PeopleQIDs"] = country_df["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])
    dob_df["PeopleQIDs"] = dob_df["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])
    dod_df["PeopleQIDs"] = dod_df["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])
    pc_df["PeopleQIDs"] = pc_df["PeopleQIDs"].apply(lambda L: [q for q in L if q in people_in_gallery])

    # Compute counts + sort
    # Occupations
    occ_df["Count"] = occ_df["PeopleQIDs"].apply(len)
    occ_df = occ_df[occ_df["Count"] > 0].sort_values(
        by=["Count", "OccupationQID_LEn"], ascending=[False, True],
        key=lambda col: col.str.lower() if col.name == "OccupationQID_LEn" else col
    )

    # Genders
    gdf["Count"] = gdf["PeopleQIDs"].apply(len)
    gdf = gdf[gdf["Count"] > 0].sort_values(
        by=["Count", "GenderQID_LEn"], ascending=[False, True],
        key=lambda col: col.str.lower() if col.name == "GenderQID_LEn" else col
    )

    # Countries of citizenship
    country_df["Count"] = country_df["PeopleQIDs"].apply(len)
    country_df = country_df[country_df["Count"] > 0].sort_values(
        by=["Count", "CountryOfCitizenshipQID_LEn"], ascending=[False, True],
        key=lambda col: col.str.lower() if col.name == "CountryOfCitizenshipQID_LEn" else col
    )

    # Decade of birth
    dob_df["Count"] = dob_df["PeopleQIDs"].apply(len)
    dob_df = dob_df[dob_df["Count"] > 0].sort_values(by="DoB", ascending=True)
    #print(dob_df.values)

    # Decade of death
    dod_df["Count"] = dod_df["PeopleQIDs"].apply(len)
    dod_df = dod_df[dod_df["Count"] > 0].sort_values(by="DoD", ascending=True)

    # Wikipedia language versions
    # Countries of citizenship
    pc_df["Count"] = pc_df["PeopleQIDs"].apply(len)
    pc_df = pc_df[pc_df["Count"] > 0].sort_values(
        by=["Count", "FullLanguageName"], ascending=[False, True],
        key=lambda col: col.str.lower() if col.name == "FullLanguageName" else col
    )

except Exception as e:
    sys.exit(f"❌ Error preparing facet summaries: {e}")


# ====================== Build dropdowns ======================
from delpher_humans_q5_gallery_functions import _safe_join_options

# --- Safe defaults (so the page can still render) ---
person_to_occs = defaultdict(set) # Person can have multiple occupations
person_to_gender = defaultdict(set) # Person has one gender
person_to_countries = defaultdict(set) # Person can have multiple countries of citizenship
person_to_dob = defaultdict(str) # Person is born in only one decade
person_to_dod = defaultdict(str) # Person died in only one decade
person_to_pcs = defaultdict(set) # Person can be described in multiple Wikipedia languages (pc = project code , 'nl.wikipedia')

occ_options_html = '<option value="">All</option>' # Occupation filter
gender_options_html = '<option value="">All</option>' # Gender filter
country_options_html = '<option value="">All</option>' # Country of citizenship filter
dob_options_html = '<option value="">All</option>' # Decade of birth filter
dod_options_html = '<option value="">All</option>' # Decade of death filter
pc_options_html = '<option value="">All</option>'  # Wikipedia language filter

filters_html = ""
paginator_status_html = ""
paginator_links_html = ""

errors = []  # collect warnings to print once

try:
    # -------- Build mappings (wrapped individually so one failure doesn't kill all) --------
    # Occupations
    try:
        for _, r in occ_df.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            oqid = r.get("OccupationQID", "")
            for pid in pids:
                person_to_occs[pid].add(oqid)
    except Exception as e:
        errors.append(f"Building person_to_occs failed: {e}")

    # Genders
    try:
        for _, r in gdf.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            gqid = r.get("GenderQID", "")
            for pid in pids:
                # keep first seen gender if multiple
                person_to_gender.setdefault(pid, gqid)
    except Exception as e:
        errors.append(f"Building person_to_gender failed: {e}")

    # Countries of citizenship
    try:
        for _, r in country_df.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            cqid = r.get("CountryOfCitizenshipQID", "")
            for pid in pids:
                person_to_countries[pid].add(cqid)
    except Exception as e:
        errors.append(f"Building person_to_countries failed: {e}")

    # Decade of birth
    try:
        for _, r in dob_df.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            dobqid = r.get("DoB", "")
            for pid in pids:
                person_to_dob[pid] += dobqid
    except Exception as e:
        errors.append(f"Building person_to_dob failed: {e}")

    # Decade of death
    try:
        for _, r in dod_df.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            dodqid = r.get("DoD", "")
            for pid in pids:
                person_to_dod[pid] += dodqid
    except Exception as e:
        errors.append(f"Building person_to_dod failed: {e}")

    # Wikipedia language versions
    try:
        for _, r in pc_df.iterrows():
            pids = r.get("PeopleQIDs", []) or []
            pcqid = r.get("ProjectCodeQID", "")
            for pid in pids:
                person_to_pcs[pid].add(pcqid)
    except Exception as e:
        errors.append(f"Building person_to_pcs failed: {e}")

    # -------- Dropdown options (each block guarded) ---------------------------------------
    # Occupations
    try:
        # Occ options ordered by Count desc, then label asc (assumes your earlier sort)
        occ_rows = occ_df[["OccupationQID", "OccupationQID_LEn", "Count"]].itertuples(index=False)
        occ_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in occ_rows),
            lambda qid, label: f'<option value="{qid}">{label}</option>'
        )
    except Exception as e:
        errors.append(f"Occupation options failed: {e}")

    # Gender
    try:
        g_rows = gdf[["GenderQID", "GenderQID_LEn", "Count"]].itertuples(index=False)
        gender_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in g_rows),
            lambda qid, label: f'<option value="{qid}">{label}</option>'
        )
    except Exception as e:
        errors.append(f"Gender options failed: {e}")

    # Country of citizenship
    try:
        c_rows = country_df[
            ["CountryOfCitizenshipQID", "CountryOfCitizenshipQID_LEn", "PeopleQIDs"]
        ].itertuples(index=False)
        country_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in c_rows),
            lambda qid, label: f'<option value="{qid}">{label}</option>'
        )
    except Exception as e:
        errors.append(f"Country options failed: {e}")

    # Decade of birth
    try:
        dob_rows = dob_df[["DoB","DoB", "PeopleQIDs"]].itertuples(index=False)
        dob_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in dob_rows),
            lambda qid, label: f'<option value="{qid}">{label}s</option>'
        )
    except Exception as e:
        errors.append(f"Decade of birth options failed: {e}")

    # Decade of death
    try:
        dod_rows = dod_df[["DoD","DoD", "PeopleQIDs"]].itertuples(index=False)
        dod_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in dod_rows),
            lambda qid, label: f'<option value="{qid}">{label}s</option>'
        )
    except Exception as e:
        errors.append(f"Decade of death options failed: {e}")

    # Wikipedia language versions
    try:
        # Project code options ordered by Count desc, then label asc (assumes your earlier sort)
        pc_rows = pc_df[["ProjectCodeQID", "FullLanguageName", "Count"]].itertuples(index=False)
        pc_options_html = _safe_join_options(
            ((qid, html.escape(label)) for qid, label, _ in pc_rows),
            lambda qid, label: f'<option value="{qid.replace(".wikipedia", "")}">{label}</option>'
        )
    except Exception as e:
        errors.append(f"Project code (Wikipedia language) options failed: {e}")


    # -------- Assemble filters and pagination HTML blocks (never fail hard here) ---------------------------------
    try:
        filters_html = build_filters_html(occ_options_html,
                                          gender_options_html,
                                          country_options_html,
                                          dob_options_html,
                                          dod_options_html,
                                          pc_options_html)
    except Exception as e:
        errors.append(f"build_filters_html failed: {e}")
        # Minimal, disabled fallback so layout holds:
        filters_html = """
        <div class="filters-bar error">
          <label>Occupation</label>
          <select id="occFilter" disabled><option>Unavailable</option></select>
          <label>Gender</label>
          <select id="genderFilter" disabled><option>Unavailable</option></select>
          <label>Country</label>
          <select id="countryFilter" disabled><option>Unavailable</option></select>
          <label>Born in</label>
          <select id="dobFilter" disabled><option>Unavailable</option></select>
          <label>Died in</label>
          <select  id="dodFilter" disabled><option>Unavailable</option></select>
          <label>Wikipedia language:</label>
          <select id="pcFilter" disabled><option>Unavailable</option></select>
          
          <button id="clearFilter" type="button" disabled>Reset all</button>
          <small style="color:#a00;margin-left:8px;">Filters not configured correctly</small>
        </div>
        """

    try:
        paginator_status_html = build_paginator_status_html()
    except Exception as e:
        errors.append(f"build_paginator_status_html failed: {e}")
        paginator_status_html = """
            <div class="paginator error">
                <div class="paginator">
                  <!-- lines 2–4 -->
                  <div class="results-extras-wrapper">
                    <div class="results-extras">
                      <div class="search-status"></div>
                      <div class="filters-status"></div>
                      <div class="sort-status"></div>
                    </div>
                  </div>
                  <!-- line 1 -->
                  <div class="paginator-status">
                    <span id="resultsSummary" class="results-summary"></span>
                    <span class="page-status"></span>
                  </div>
                </div>
            </div>
        """

    try:
        paginator_links_html = build_paginator_links_html()
    except Exception as e:
        errors.append(f"build_paginator_links_html failed: {e}")
        paginator_links_html = """
        <div class="paginator error">
          <div class="paginator-links"></div>
        </div>
        """

except Exception as e:
    # Truly unexpected: print and keep the (already set) safe fallbacks
    errors.append(f"Unexpected error while building dropdowns/mappings: {e}")

# ---- Afterward: emit a concise summary so you notice issues, but continue ----
if errors:
    print("⚠️ Dropdowns/mappings built with warnings:")
    for msg in errors:
        print("  -", msg)
else:
    print("✅ Dropdowns/mappings built successfully.")


# ====================== Build person blocks ======================
gallery_blocks = []
fail_count = 0  # track how many blocks failed

for i, row in enumerate(df.itertuples(index=False)):
    try:
        page_number = (i // BLOCKS_PER_PAGE) + 1
        person_qid = row.WikidataQID

        # Facets
        occs_for_person = sorted(person_to_occs.get(person_qid, []))
        countries_for_person = sorted(person_to_countries.get(person_qid, []))
        data_gender = person_to_gender.get(person_qid, "")
        data_dob = person_to_dob.get(person_qid, "")  #  decade of birth
        data_dod = person_to_dod.get(person_qid, "")  #  decade of death
        pcs_for_person = [
            pc.replace(".wikipedia", "") for pc in sorted(person_to_pcs.get(person_qid, []))
        ] # Wikipedia languages (pcs = project codes , strip off .wikipedia --> 'nl.wikipedia' --> 'nl')

        # Metadata
        name = row.WikidataQIDLabelEn
        dateofbirth = row.P569_dob_str[1:11] if isinstance(row.P569_dob_str, str) else ""
        dateofdeath = row.P570_dod_str[1:11] if isinstance(row.P570_dod_str, str) else ""
        yob = dateofbirth[:4] if dateofbirth else ""
        yod = dateofdeath[:4] if dateofdeath else ""
        yob_yod = (
            f"({yob} – {yod})" if yob and yod else
            f"({yob} – )" if yob else
            f"( – {yod})" if yod else ""
        )

        cocs = row.P27_coc_LEn if isinstance(row.P27_coc_LEn, list) else []
        occupations = row.P106_occupation_LEn if isinstance(row.P106_occupation_LEn, list) else [DEFAULT_OCCUPATION]
        formatted_cocs = format_list_with_separator(cocs[:MAX_CITIZENSHIPS], ", ")
        formatted_occs = format_list_with_separator(occupations[:MAX_OCCUPATIONS], ", ").capitalize()

        person_subtitle = f"{formatted_occs} from {formatted_cocs}" if formatted_cocs else formatted_occs
        person_subtitle_block = (
            f"<h4>{person_subtitle}<br/><i>{yob_yod}</i></h4>"
            if person_subtitle or yob_yod else ""
        )

        # Carousel + links
        images = row.Images if isinstance(row.Images, list) else []
        langs = row.FullLanguageName if isinstance(row.FullLanguageName, list) else []
        urls = row.ArticleURL if isinstance(row.ArticleURL, list) else []
        swiper_class = f"swiper-{i}"

        img_carousel_html = build_carousel_html(images, name, swiper_class, PLACEHOLDER_IMAGE)

        # Article links
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
        credit_html = (
            f'<div class="credit-line">{credit_text} <img src="media/delpher_logo.svg" alt="Delpher"/></div>'
        )

        block = f"""
        <div class="person-block" 
            data-page="{page_number}" 
            data-qid="{person_qid}"
            data-name="{name}" 
            data-occs="{','.join(occs_for_person)}" 
            data-gender="{data_gender}" 
            data-countries="{','.join(countries_for_person)}"
            data-yob="{yob}"    
            data-dob="{data_dob}" 
            data-yod="{yod}" 
            data-dod="{data_dod}" 
            data-pcs="{','.join(pcs_for_person)}"
            style="display:none">
            <h3>{name}</h3>
            {person_subtitle_block}
            <div class="article-links-flex">
                <div class="wikipedia-logo"><img src="media/icon_wp.svg" alt="Wikipedia logo" /></div>
                <div class="article-text"><p>Read more on Wikipedia in {formatted_article_links}</p></div>
            </div>
            {img_carousel_html}
            {credit_html}
        </div>
        """
        gallery_blocks.append(block)

    except Exception as e:
        fail_count += 1
        print(f"⚠️ Error building block for row {i} (QID={getattr(row, 'WikidataQID', 'unknown')}): {e}")
        fallback_block = f"""
        <div class="person-block error" data-page="{(i // BLOCKS_PER_PAGE) + 1}">
            <h3>⚠️ Error loading person</h3>
            <p>Data unavailable for this entry.</p>
        </div>
        """
        gallery_blocks.append(fallback_block)

# --- After loop: print summary ---
if fail_count > 0:
    print(f"⚠️ Finished building gallery: {fail_count} blocks failed to render (see warnings above).")
else:
    print("✅ Finished building gallery: all blocks rendered successfully.")


# --- Build footer HTML ---
try:
    footer_html = build_footer_html(latest_update=LATEST_UPDATE)
except Exception as e:
    # Log to stderr so it's visible in error output
    print(f"❌ Error building footer: {e}", file=sys.stderr)
    # Provide a minimal safe fallback instead of killing the whole script
    footer_html = """
    <div class="bottom-banner error">
        <p>⚠️ Footer unavailable.</p>
    </div>
    """

# =================== Write output ======================
def main(outputile):
    try:
        html_output = build_html(
            title=TITLE,
            subtitle=SUBTITLE,
            gallery_blocks=gallery_blocks,
            css_file=CSS_FILE,
            js_file= JS_FILE,
            blocks_per_page=BLOCKS_PER_PAGE,
            filters_html=filters_html,
            paginator_status_html=paginator_status_html,
            paginator_links_html=paginator_links_html,
            footer_html=footer_html
        )
        with open(outputile, "w", encoding="utf-8") as f:
            f.write(html_output)

        print(f"✅ Gallery saved to: {outputile.resolve()}")

    except Exception as e:
        sys.exit(f"❌ Error writing HTML output: {e}")

if __name__ == "__main__":
    main(outputile=OUTPUT_FILE)
