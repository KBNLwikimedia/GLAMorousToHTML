"""
Gallery Page HTML Builders
==========================

Utilities to generate the HTML fragments used by the **Delpher × Wikipedia —
Portrait Explorer** client-side gallery. These helpers keep the page assembly
logic in Python while the interactions (filtering, sorting, search, pagination,
and Swiper carousels) run in the browser.

What this module builds
-----------------------
- **Filters bar** (`build_filters_html`)
  Occupation, Gender, Country of citizenship, Decade of birth/death, Wikipedia
  language, and Sort selector, plus a “Reset all” button.

- **Paginator status row** (`build_paginator_status_html`)
  A container for: results summary, current page indicator, and a right-side
  “extras” stack that shows **Search**, **Filters**, and **Sort** chips.

- **Paginator links row** (`build_paginator_links_html`)
  A container into which client-side JS injects First/Prev/…/Next/Last links.

- **Swiper carousel** (`build_carousel_html`)
  A minimal Swiper block (wrapper + slides + pagination element). It renders a
  placeholder if no images are available. Actual Swiper JS/CSS is loaded on the
  page and initialized client-side.

- **Footer block** (`build_footer_html`)
  Attribution text, last update date, contact, and KB/Delpher branding.

- **Full HTML page** (`build_html`)
  Assembles the complete, single-file gallery page. Injects links to the project
  CSS/JS and Swiper from CDN, exposes `window.BLOCKS_PER_PAGE`, includes a
  lightweight loading spinner, the header area (logos, title, subtitle, search),
  the filters/paginator rows, the gallery grid (list of prebuilt person cards),
  and the footer.

Inputs & expectations
---------------------
- This module **does not read data**. Callers provide pre-rendered `<option>`
  tag strings for each facet selector and a list of HTML person cards.
- Person cards are expected to include `data-*` attributes consumed by the
  client JS (e.g., `data-occs`, `data-gender`, `data-countries`, `data-yob`,
  `data-yod`, `data-dob`, `data-dod`, `data-pcs`, `data-name`).

Error handling philosophy
-------------------------
- All builders validate argument types and common preconditions.
- On **non-fatal** errors, functions log a concise message (via `print`) and
  return a **safe fallback HTML** block so the page still renders.
- On **fatal** validation errors in `build_html`, a minimal error page is
  returned instead of raising, to keep CLI pipelines robust.

Performance & UX notes
----------------------
- Uses `dns-prefetch`/`preconnect` for common CDNs and Commons thumbnails.
- Swiper CSS/Google Fonts/project CSS are **preloaded** and swapped to
  `rel="stylesheet"` on load to improve start render.
- A small **loading spinner** is shown until your main JS hides it.

Dependencies
------------
- Local helper: `general.safe_eval`
- External: Swiper (CSS/JS via CDN) initialized by the page JS
- CSS/JS files referenced by paths passed into `build_html`.

Accessibility
-------------
- Carousel images include `alt` text (person name + file).
- Labels are associated with their `<select>` via `for`/`id`.
- Buttons include `aria-label` where appropriate.

Author: Olaf Janssen, Wikimedia coordinator of the KB, National Library of the Netherlands
Supported by: ChatGPT
Last updated: 1 September 2025
"""

from pathlib import Path
import sys
# Extend sys.path for imports
sys.path.append(str(Path(__file__).resolve().parent.parent.parent))
from general import safe_eval
from typing import Sequence

def parse_qids(val):
    """
    Safely parse a stringified list of QIDs into a Python list of strings.
    Args:
        val (str|list): Input value (stringified list, list, or other).
    Returns:
        list[str]: List of QIDs (strings only). Returns [] if parsing fails.
    """
    try:
        lst = safe_eval(val)
        return [q for q in lst if isinstance(q, str)]
    except Exception:
        return []

def _safe_join_options(iterable, fmt):
    """Join <option> items; if iterable is empty, return just All."""
    out = []
    for tup in iterable:
        try:
            out.append(fmt(*tup))
        except Exception as e:
            errors.append(f"Option format failed on row {tup}: {e}")
    return "".join(out) or '<option value="">All</option>'


def build_filters_html(
    occ_options_html: str,
    gender_options_html: str,
    country_options_html: str,
    dob_options_html: str,
    dod_options_html: str,
    pc_options_html: str) -> str:
    """
    Generate the HTML markup for the filters bar, including
    occupation, gender, country, decades of birth & death and Wikipedia language dropdowns,
    plus a reset button.

    Args:
        occ_options_html (str): Pre-rendered <option> tags for occupations.
        gender_options_html (str): Pre-rendered <option> tags for gender.
        country_options_html (str): Pre-rendered <option> tags for country of citizenship.
        dob_options_html (str): Pre-rendered <option> tags for birth decades.
        dod_options_html (str): Pre-rendered <option> tags for death decades.
        pc_options_html (str): Pre-rendered <option> tags for project code, Wikipedia languages.

    Returns:
        str: Complete HTML string for the filters bar.

    Raises:
        TypeError: If any of the inputs are not strings.
        ValueError: If any of the inputs are empty or None.
    """
    try:
        # Type checking
        for arg_name, arg_val in {
            "occ_options_html": occ_options_html,
            "gender_options_html": gender_options_html,
            "country_options_html": country_options_html,
            "dob_options_html": dob_options_html,
            "dod_options_html": dod_options_html,
            "pc_options_html": pc_options_html
        }.items():
            if not isinstance(arg_val, str):
                raise TypeError(f"{arg_name} must be a string, got {type(arg_val).__name__}")
            if arg_val is None or arg_val.strip() == "":
                raise ValueError(f"{arg_name} cannot be empty or None")

        return f"""
        <section class="center-wrap">
              <div class="filters-container">
                <div class="filters-bar">
                 
                  <div class="filter-item">
                    <label for="sortOrder">Sort by</label>
                    <select id="sortOrder">
                      <option value="name_asc">Default (Name A–Z)</option>
                      <option value="name_desc">Name Z–A</option>
                      <option value="yob_asc">Year of birth (0-9)</option>
                      <option value="yob_desc">Year of birth (9-0)</option>
                      <option value="yod_asc">Year of death (0-9)</option>
                      <option value="yod_desc">Year of death (9-0)</option>
                    </select>
                  </div>
                 
                  <div class="filter-item">
                    <label for="occFilter">Occupation</label>
                    <select id="occFilter">
                      <option value="">All</option>
                      {occ_options_html}
                    </select>
                  </div>
                
                  <div class="filter-item">
                    <label for="genderFilter">Gender</label>
                    <select id="genderFilter">
                      <option value="">All</option>
                      {gender_options_html}
                    </select>
                  </div>
                
                  <div class="filter-item">
                    <label for="countryFilter">Country</label>
                    <select id="countryFilter">
                      <option value="">All</option>
                      {country_options_html}
                    </select>
                  </div>
                
                  <div class="filter-item">
                    <label for="dobFilter">Was born in</label>
                    <select id="dobFilter">
                      <option value="">All</option>
                      {dob_options_html}
                    </select>
                  </div>
                
                  <div class="filter-item">
                    <label for="dodFilter">Died in</label>
                    <select id="dodFilter">
                      <option value="">All</option>
                      {dod_options_html}
                    </select>
                  </div>
                
                  <div class="filter-item">
                    <label for="pcFilter">Wikipedia language</label>
                    <select id="pcFilter">
                      <option value="">All</option>
                      {pc_options_html}
                    </select>
                  </div>
                  
                  <button id="clearFilter" type="button">Reset all</button>

                </div>
              </div>
            </div>
        </section>
        """

    except (TypeError, ValueError) as e:
        # Log error and return a minimal safe fallback
        print(f"Error in build_filters_html: {e}")
        return """
        <div class="filters-bar error">
          <p>⚠️ Unable to load filters.</p>
        </div>
        """


def build_paginator_status_html() -> str:
    """
    Generate the HTML for the paginator status row, which contains:
      - Results summary (e.g., "Showing results 1–36 of 820")
      - Page status (e.g., "Page 1 of 23")

    Returns:
        str: HTML string for the paginator status block.

    Raises:
        RuntimeError: If HTML generation unexpectedly fails.
    """
    try:
        return """
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
        """
    except Exception as e:
        # Log and return a safe fallback
        print(f"Error in build_paginator_status_html: {e}")
        return """
        <div class="paginator error">
          <p>⚠️ Unable to load paginator status.</p>
        </div>
        """


def build_paginator_links_html() -> str:
    """
    Generate the HTML for the paginator links row.
    This block will later be populated dynamically with pagination controls
    (e.g., "First", "Prev", page numbers, "Next", "Last").

    Returns:
        str: HTML string for the paginator links container.

    Raises:
        RuntimeError: If HTML generation unexpectedly fails.
    """
    try:
        return """
        <div class="paginator">
          <div class="paginator-links"></div>
        </div>
        """
    except Exception as e:
        # Log and return a safe fallback so the page still renders
        print(f"Error in build_paginator_links_html: {e}")
        return """
        <div class="paginator error">
          <p>⚠️ Unable to load paginator links.</p>
        </div>
        """


def build_carousel_html(images, name, swiper_class, placeholder_image) -> str:
    """
    Generate HTML for a Swiper image carousel.

    Args:
        images (list[str]): List of image file names from Wikimedia Commons.
        name (str): Person's name (used in alt text for accessibility).
        swiper_class (str): Additional CSS class to distinguish this Swiper instance.
        placeholder_image (str): Path or URL to a placeholder image if no images exist.

    Returns:
        str: HTML string for a complete Swiper carousel block.

    Raises:
        RuntimeError: If carousel HTML generation fails unexpectedly.
    """
    try:
        # Case: no images available → return a placeholder carousel
        if not images:
            return f"""
            <div class="swiper {swiper_class}">
                <div class="swiper-wrapper">
                    <div class="swiper-slide">
                        <img src="{placeholder_image}" alt="No portrait available"/>
                    </div>
                </div>
                <div class="swiper-pagination"></div>
            </div>
            """

        # Case: valid images → generate slides
        slides = "".join(
            f"""
            <div class="swiper-slide">
                <a href="https://commons.wikimedia.org/wiki/File:{img}" 
                   target="_blank" 
                   title="Click to view image on Wikimedia Commons">
                    <img src="https://commons.wikimedia.org/wiki/Special:FilePath/{img.replace(' ', '_')}?width=300" 
                          width="300" alt="{name} – {img}" 
                         class="thumb" loading="lazy" decoding="async" referrerpolicy="no-referrer" />
                </a>
            </div>
            """ for img in images if isinstance(img, str) and img.strip()
        )

        return f"""
        <div class="swiper {swiper_class}">
            <div class="swiper-wrapper">
                {slides}
            </div>
            <div class="swiper-pagination"></div>
        </div>
        """
    except Exception as e:
        print(f"Error in build_carousel_html: {e}")
        return f"""
        <div class="swiper error">
            <p>⚠️ Unable to load carousel for {name}.</p>
        </div>
        """

def build_footer_html(latest_update: str) -> str:
    """
    Generate the HTML markup for the page footer.

    The footer includes:
      - KB national library logo
      - Attribution text (Wikipedia, Wikidata, Wikimedia Commons, Delpher)
      - Last update date
      - Contact information

    Args:
        latest_update (str, optional): A string indicating the date of the latest update.
                                       Defaults to "22 August 2025".

    Returns:
        str: The complete HTML string for the footer block.

    Raises:
        TypeError: If `latest_update` is not a string.
    """
    try:
        if not isinstance(latest_update, str):
            raise TypeError(f"latest_update must be a string, got {type(latest_update).__name__}")

        return f"""
        <!-- FOOTER BLOCK -->
        <div class="bottom-banner">
            <div class="footer-flex">
                <img src="media/KB_Nationale-Bibliotheek_Logo_CMYK-Wit-EN.svg"
                     alt="Logo KB national library of the Netherlands"
                     title="Logo KB national library of the Netherlands"
                     class="footer-logo" />
                <div class="footer-text">
                    <p>Made with ❤️ using data from Wikipedia, 
                    <a href="https://commons.wikimedia.org/wiki/Category:Media_from_Delpher" target="_blank">Wikimedia Commons</a>
                    and <a href="https://www.delpher.nl" target="_blank" title="Go to the Delpher website">Delpher</a>,
                       a service of the KB national library of the Netherlands. It extends the
                        <a href="https://kbnlwikimedia.github.io/GLAMorousToHTML/site/MediafromDelpher_Wikipedia_NS0_01072025.html" target="_blank">output of the GLAMorousToHTML tool</a> 
                       with data from Wikidata, and renders it as a interactive portrait gallery.</p>
                    <p>Latest update: {latest_update}</p>
                    <p>Contact: Olaf Janssen,
                       <a href="https://www.kb.nl/over-ons/experts/olaf-janssen" target="_blank">
                       Wikimedia coordinator of the KB</a> - olaf.janssen@kb.nl</p>
                    <p><i>Disclaimer: This app is not part of the official Delpher ecosystem. 
                        It is a 'labs' proof-of-concept designed to provide insight into which Delpher images are being reused on Wikipedia.</i></p>
                </div>
            </div>
        </div>
        """
    except Exception as e:
        print(f"⚠️ Error in build_footer_html: {e}")
        return """
        <!-- FOOTER BLOCK (error fallback) -->
        <div class="bottom-banner error">
            <p>⚠️ Unable to load footer.</p>
        </div>
        """

def build_html(
    title: str,
    subtitle: str,
    gallery_blocks: Sequence[str],
    css_file: str,
    js_file:  str,
    blocks_per_page: int,
    filters_html: str,
    paginator_status_html: str,
    paginator_links_html: str,
    footer_html: str) -> str:
    """
    Construct the complete HTML for the gallery page.

    Args:
        - title (str): Main page title (also used in <title> and H1).
        - subtitle (str): Subtitle shown under the top banner title.
        - gallery_blocks (Sequence[str]): List/sequence of pre-rendered person-block HTML strings.
        - css_file (str): Path/URL to the main CSS file for the gallery.
        - js_file (str): Path/URL to the JS file for the page.
        - blocks_per_page (int): Page size exposed to JS as `window.BLOCKS_PER_PAGE`.
        - filters_html (str): Pre-rendered HTML for the facet filters bar.
        - paginator_status_html (str): Pre-rendered HTML for the paginator status row
                                     (results summary + page status).
        - paginator_links_html (str): Pre-rendered HTML for the paginator links row.
        - footer_html (str): Pre-rendered HTML for the footer block.

    Returns:
        str: Full HTML document as a string.

    Raises:
        TypeError: If any parameter has an unexpected type.
        ValueError: If required string parameters are empty or if blocks_per_page < 1.
    """

    try:
        # --- Basic validation ---
        for name, val in {
            "title": title,
            "subtitle": subtitle,
            "css_file": css_file,
            "js_file": js_file,
            "filters_html": filters_html,
            "paginator_status_html": paginator_status_html,
            "paginator_links_html": paginator_links_html,
            "footer_html": footer_html
        }.items():
            if not isinstance(val, str):
                raise TypeError(f"{name} must be a string, got {type(val).__name__}")
            if val.strip() == "" and name in {"title", "css_file"}:
                raise ValueError(f"{name} cannot be empty")

        if not isinstance(blocks_per_page, int):
            raise TypeError(f"blocks_per_page must be an int, got {type(blocks_per_page).__name__}")
        if blocks_per_page < 1:
            raise ValueError("blocks_per_page must be >= 1")

        if not isinstance(gallery_blocks, (list, tuple)):
            raise TypeError("gallery_blocks must be a list or tuple of strings")
        if not all(isinstance(b, str) for b in gallery_blocks):
            raise TypeError("All items in gallery_blocks must be strings")

        # --- Build the HTML (join once for performance) ---
        blocks_html = "".join(gallery_blocks)

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <!-- DNS prefetch & preconnect for better performance -->
    <link rel="dns-prefetch" href="https://commons.wikimedia.org">
    <link rel="dns-prefetch" href="https://cdn.jsdelivr.net/">
    <link rel="dns-prefetch" href="https://fonts.googleapis.com/">
    <link rel="preconnect" href="https://commons.wikimedia.org" crossorigin>
    <link rel="preconnect" href="https://cdn.jsdelivr.net" crossorigin>
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <!-- Preload CSS for better performance -->
    <link rel="preload" href="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.css" as="style" onload="this.rel='stylesheet'"/>
    <link rel="preload" href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700&family=Roboto:wght@400;600;700&display=swap" as="style" onload="this.rel='stylesheet'"/>
    <link rel="preload" href="{css_file}" as="style" onload="this.rel='stylesheet'">
    <noscript><link rel="stylesheet" href="href="{css_file}"></noscript>
    
    <title>{title}</title>
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <script>
      // Make BLOCKS_PER_PAGE available to all JS on the page
      window.BLOCKS_PER_PAGE = {blocks_per_page};
    </script>
</head>
<body>
    <!-- Loading Spinner -->
    <div id="loading-spinner">
      <div class="spinner"></div>
    </div>
    <div id="page-content" style="display:none;">
        <!-- HEADER BLOCK -->
        <div class="top-banner">
          <div class="top-banner-flex">
            <!-- Logos on the left -->
            <div class="top-logo-block">
              <img src="media/icon_wp.svg" alt="Wikipedia logo" class="logo" title="Wikipedia logo"/>
              <img src="media/delpher_logo.svg" alt="Delpher logo" class="logo" title="Delpher logo"/>
            </div>
            <!-- Title + subtitle centered -->
            <div class="top-text-block">
              <h1>{title}</h1>
              <p class="subtitle">{subtitle}</p>
            </div>
            <!-- Search box -->
            <div class="search">
              <div class="search-box-wrapper">
                <input id="searchBox" type="search" aria-label="Search" placeholder="Search (type 2 or more) ..." />
                <button id="clearSearch" type="button" aria-label="Clear search">×</button>
              </div>
            </div>
          </div>
        </div>
    
        {filters_html}
        {paginator_status_html}
        {paginator_links_html}
    
        <!--Grid layout (see CSS) -->
        <div class="gallery-container">
            {blocks_html}
        </div>
    
        {paginator_links_html}
    
        <noscript>
          <p style="text-align:center;color:#a00">This page works much better with JavaScript enabled.</p>
        </noscript>
    
        <!-- Swiper JS -->
        <script src="https://cdn.jsdelivr.net/npm/swiper@11/swiper-bundle.min.js"></script>
        <!-- Filter/gallery controller script -->
        <script src="{js_file}"></script>
        <!-- Include footer JS -->
        {footer_html}
    </div>
</body>
</html>
"""
    except (TypeError, ValueError) as e:
        # Known validation issues → show a minimal, safe page
        print(f"Validation error in build_html: {e}")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Gallery – Error</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>body{{font-family:sans-serif;padding:2rem;}}</style>
</head>
<body>
  <h1>Unable to render gallery</h1>
  <p>{str(e)}</p>
</body>
</html>"""
    except Exception as e:
        # Unexpected failure → log and provide generic fallback
        print(f"Unexpected error in build_html: {e}")
        return """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>Gallery – Error</title>
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <style>body{font-family:sans-serif;padding:2rem;}</style>
</head>
<body>
  <h1>Something went wrong</h1>
  <p>⚠️ An unexpected error occurred while generating the gallery.</p>
</body>
</html>
"""

