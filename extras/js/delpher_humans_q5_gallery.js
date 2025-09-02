"use strict";

/**
 * Gallery controller script
 *
 * - Faceted filtering (occupation, gender, country, DoB decade, DoD decade, WP language)
 * - Sorting (name asc/desc, YOB asc/desc, YOD asc/desc)
 * - URL state (?page=…&occ=…&gender=…&country=…&dob=…&dod=…&pc=…&sort=…)
 * - Client-side pagination when filtering/sorting is active
 * - Updates paginator links, page status, and results summary
 *
 * Assumptions:
 * - Each person card has class ".person-block" and data attributes:
 *   data-page, data-occs, data-gender, data-countries, and (for sorting) data-yob, data-yod, data-name (optional).
 *   If data-name is missing, text from the <h3> inside the card is used.
 *
 * Errors are logged to console; UI degrades gracefully.
 */

// ====================== Config for facets (easy to extend) ======================
/** @type {{[k:string]: {param:string, attr:string, kind:"list"|"scalar"}}} */
const FACETS = {
  occ:     { param: "occ",     attr: "occs",      kind: "list"   },
  gender:  { param: "gender",  attr: "gender",    kind: "scalar" },
  country: { param: "country", attr: "countries", kind: "list"   },
  dob:     { param: "dob",     attr: "dob",       kind: "scalar" },
  dod:     { param: "dod",     attr: "dod",       kind: "scalar" },
  pc:      { param: "pc",      attr: "pcs",       kind: "list"   }
};

// Sort keys we understand (values should match <option value="..."> in #sortOrder)
const DEFAULT_SORT = "name_asc";
const SORT_KEYS = new Set(["name_asc", "name_desc", "yob_asc", "yob_desc", "yod_asc", "yod_desc"]);
const MIN_QUERY_LENGTH = 2; // minimum characters to trigger search

// ============================ Utilities =====================================
function esc(s) {
  return String(s)
    .replace(/&/g, "&amp;").replace(/</g, "&lt;")
    .replace(/>/g, "&gt;").replace(/"/g, "&quot;")
    .replace(/'/g, "&#39;");
}

// ============================= URL helpers =====================================

/**
 * Read current state (page + facet params + sort) from URL.
 * @returns {{page:number, sort:string, [k:string]:string}}
 */
function getParams() {
  try {
    const p = new URLSearchParams(window.location.search);
    const pageRaw = parseInt(p.get("page"), 10);
    const page = Number.isFinite(pageRaw) && pageRaw > 0 ? pageRaw : 1;

    const state = { page, sort: p.get('sort') || DEFAULT_SORT, q: "" };
    // facets
    for (const key in FACETS) {
      const v = p.get(FACETS[key].param);
      state[key] = v ? String(v) : "";
    }
    // sort
    const s = p.get("sort") || DEFAULT_SORT;
    state.sort = SORT_KEYS.has(s) ? s : "";

    // Handle search query
    let q = p.get("q") || "";
    q = q.trim();
    // enforce minimum 2 characters
    state.q = q.length >=  MIN_QUERY_LENGTH ? q : "";

    return state;
  } catch (err) {
    console.error("getParams() failed:", err);
    return { page: 1 };
  }
}

/**
 * Update URL with provided next state (without reloading the page).
 * Missing/empty facet values are removed from the query string.
 * Supports special key "sort".
 * @param {{page?:number, sort?:string, [k:string]:string}} next
 */
function setParams(next) {
  try {
    const p = new URLSearchParams(window.location.search);

    // page
    if (next.page != null) {
      const n = parseInt(next.page, 10);
      p.set("page", Number.isFinite(n) && n > 0 ? String(n) : "1");
    }

    // facets
    for (const key in FACETS) {
      if (!(key in next)) continue;
      const v = next[key];
      if (v) p.set(FACETS[key].param, v);
      else p.delete(FACETS[key].param);
    }

    // sort
    if ("sort" in next) {
      const s = next.sort || "";
      if (s && SORT_KEYS.has(s)) p.set("sort", s);
      else p.delete("sort");
    }

    // search query
    if ("q" in next) {
      const q = (next.q || "").trim();
      if (q) p.set("q", q); else p.delete("q");
    }

    history.replaceState(null, "", `${location.pathname}?${p.toString()}`);
  } catch (err) {
    console.error("setParams() failed:", err);
  }
}


//========================Search box=================================
function onSearchInput() {
  const input = document.getElementById("searchBox");
  const q = input ? input.value.trim() : "";
 // Query must be 2 chars or longer to trigger search, or 0 to clear
  if (q.length >= 2) {
    setParams({ page: 1, q });
    render();
  } else if (q.length === 0) {
    setParams({ page: 1, q: "" });
    render();
  }
  // else: length 1, do nothing
}

function clearSearch() {
  const input = document.getElementById("searchBox");
  if (input) input.value = "";
  setParams({ page: 1, q: "" });
  render();
}

// tiny debounce to avoid re-render on every keystroke
function debounce(fn, wait = 250) {
  let t;
  return (...args) => {
    clearTimeout(t);
    t = setTimeout(() => fn(...args), wait);
  };
}

// Filter by text in getFilteredCards
// We’ll combine with your facet filtering. To speed up, we cache each card’s lower-cased text in data-index on first use.
function cardIndexText(card) {
  if (!card.dataset.index) {
    const ALLOWED_SELECTORS = ["h3", "h4"];
    const parts = [];

    ALLOWED_SELECTORS.forEach(sel => {
      card.querySelectorAll(sel).forEach(el => {
        // Only collect direct text nodes (ignore <br>, <span>, etc.)
        const nodeTexts = Array.from(el.childNodes)
          .filter(node => node.nodeType === Node.TEXT_NODE) // only plain text
          .map(node => node.textContent.trim())
          .filter(Boolean);

        if (nodeTexts.length) {
          parts.push(nodeTexts.join(" "));
        }
      });
    });

    const txt = parts.join(" ")
      .replace(/\s+/g, " ") // collapse whitespace
      .trim()
      .toLowerCase();

    card.dataset.index = txt; // memoize
  }
  return card.dataset.index;
}



function getFilteredCards(state) {
  try {
    const cards   = Array.from(document.querySelectorAll(".person-block"));
    const actives = activeFacets(state);
    const query = (state.q || "").toLowerCase();
    if (query && query.length <  MIN_QUERY_LENGTH) return cards; // don’t filter

    // Cheap normalizer for facet values in data-attrs
    const splitList = (s) => (s || "").split(",").map(v => v.trim()).filter(Boolean);

    // Fallback indexer if cardIndexText isn't defined
    const getIndexText = (el) => {
      if (typeof cardIndexText === "function") return cardIndexText(el);
      // fallback: name + visible text + some data attrs
      const name = el.dataset.name || (el.querySelector("h3")?.textContent  ?? "");
      const extra = [
        el.dataset.occs, el.dataset.countries, el.dataset.gender,
        el.dataset.pcs, el.dataset.dob, el.dataset.dod
      ].filter(Boolean).join(" ");
      return (name + " " + el.textContent + " " + extra).toLowerCase();
    };

    return cards.filter(card => {
      // --- facet filtering ---
      for (const key of actives) {
        const { attr, kind } = FACETS[key];
        const val  = (state[key] || "").trim();
        const data = (card.dataset[attr] || "");

        if (kind === "list") {
          const arr = splitList(data);
          if (!arr.includes(val)) return false;
        } else {
          if (data !== val) return false;
        }
      }

      // --- text search ---
      if (query) {
        // memoize per card for performance
        if (!card.__idx) card.__idx = getIndexText(card);
        if (!card.__idx.includes(query)) return false;
      }

      return true;
    });
  } catch (err) {
    console.error("getFilteredCards() failed:", err);
    return [];
  }
}


// We’ll highlight inside a couple of safe areas
// (e.g., title <h3>, subtitle <h4>, article links). We also keep original HTML in data-orig so we can unhighlight cleanly.
function highlightWithin(el, q) {
  if (!el) return;

  // Keep the original HTML so we can reset cleanly
  if (!el.dataset.orig) el.dataset.orig = el.innerHTML;
  el.innerHTML = el.dataset.orig;

  if (!q) return;

  // Escape the query for literal match and build a case-insensitive regex
  const safeQ = q.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  const re = new RegExp(safeQ, "gi");

  // Walk only text nodes so we never touch markup like <br>
  const walker = document.createTreeWalker(
    el,
    NodeFilter.SHOW_TEXT,
    {
      acceptNode(node) {
        // Skip empty/whitespace-only text nodes
        return node.nodeValue.trim()
          ? NodeFilter.FILTER_ACCEPT
          : NodeFilter.FILTER_REJECT;
      }
    }
  );

  const textNodes = [];
  while (walker.nextNode()) textNodes.push(walker.currentNode);

  textNodes.forEach(node => {
    const text = node.nodeValue;
    let match;
    let lastIndex = 0;
    const frag = document.createDocumentFragment();

    // reset regex state per node
    re.lastIndex = 0;

    while ((match = re.exec(text)) !== null) {
      const start = match.index;
      const end = start + match[0].length;

      if (start > lastIndex) {
        frag.appendChild(document.createTextNode(text.slice(lastIndex, start)));
      }

      const mark = document.createElement("mark");
      mark.className = "search-hit";
      mark.textContent = text.slice(start, end);
      frag.appendChild(mark);

      lastIndex = end;
    }

    if (lastIndex === 0) return; // no matches in this node

    if (lastIndex < text.length) {
      frag.appendChild(document.createTextNode(text.slice(lastIndex)));
    }

    node.parentNode.replaceChild(frag, node);
  });
}


function applyHighlightsToCard(card, q) {
  // pick targets that are mostly text (avoid the whole card to prevent breaking Swiper markup)
  highlightWithin(card.querySelector("h4"), q);
  highlightWithin(card.querySelector("h3"), q);

}

function clearHighlights(cards) {
  cards.forEach(card => applyHighlightsToCard(card, "")); // passing empty restores orig
}



// ============================= Core render =====================================

/**
 * Determine active facets (those with a truthy value in state).
 * @param {{[k:string]:any}} state
 * @returns {string[]}
 */
function activeFacets(state) {
  try {
    return Object.keys(FACETS).filter(k => !!state[k]);
  } catch (err) {
    console.error("activeFacets() failed:", err);
    return [];
  }
}

/**
 * Entry point: decides filtered vs unfiltered render.
 * - If any facet is active OR sort is not default, use filtered path (sort+paginate).
 * - Else use precomputed data-page rendering.
 */
function render() {
  try {
    const state = getParams();
    const active = activeFacets(state);
    const sortIsDefault = !state.sort || state.sort === DEFAULT_SORT || state.sort === "";
    const hasFacets = Object.keys(FACETS).some(k => !!state[k]);
    const hasQuery = !!(state.q && state.q.trim());

    if (active.length || !sortIsDefault) {
      renderFiltered(state);
    } else {
      renderUnfiltered(state.page);
    }

     if (hasQuery || hasFacets ) {
      renderFiltered(state);   // will filter by facets AND q
    } else {
      renderUnfiltered(state.page);
    }

  } catch (err) {
    console.error("render() failed, falling back to unfiltered:", err);
    renderUnfiltered(1);
  }
}

// --------------------------- Results summary -----------------------------------

function formatRange(page, perPage, total) {
  if (!Number.isFinite(total) || total <= 0) return { start: 0, end: 0 };
  const p = Number.isFinite(page) && page > 0 ? page : 1;
  const pp = Number.isFinite(perPage) && perPage > 0 ? perPage : 25;
  const start = (p - 1) * pp + 1;
  const end = Math.min(p * pp, total);
  return { start, end };
}

function labelFromSelect(selectId) {
  try {
    const sel = document.getElementById(selectId);
    if (!sel) return "";
    const opt = sel.options[sel.selectedIndex];
    return (opt?.text || "").replace(/\s*\(\d+\)\s*$/, "");
  } catch (err) {
    console.error("labelFromSelect() failed:", err);
    return "";
  }
}

function sortLabel(sortKey) {
  switch (sortKey) {
    case "name_asc":  return "Name - ascending";
    case "name_desc": return "Name - descending";
    case "yob_asc":   return "Year of birth - ascending";
    case "yob_desc":  return "Year of birth - descending";
    case "yod_asc":   return "Year of death - ascending";
    case "yod_desc":  return "Year of death - descending";
    default:          return "Name A–Z";
  }
}

function updateResultsSummary({ total, page, perPage, state }) {
  // Line 1
  try {
    const resultsEl = document.getElementById("resultsSummary");
    const pageEl    = document.querySelector(".page-status");
    if (resultsEl) {
      const { start, end } = formatRange(page, perPage, total);
      resultsEl.textContent = `Showing results ${start}–${end} of ${total}`;
    }
    if (pageEl) {
      const totalPages = Math.max(1, Math.ceil(total / (perPage || 1)));
      pageEl.textContent = `Page ${page} of ${totalPages}`;
    }
  } catch (err) { console.error("updateResultsSummary line 1 failed:", err); }

  // Line 2: Search + clear chip (only if q present)
  try {
    const qEl = document.querySelector(".search-status");
    if (qEl) {
      const q = (state.q || "").trim();
      qEl.innerHTML = q
        ? `<button class="clear-chip" data-action="clear-search" aria-label="Clear search">×</button><b>Search:</b> “${esc(q)}”`
        : "";
    }
  } catch (err) { console.error("updateResultsSummary search failed:", err); }

  // Line 3: Filters + clear chip (only if any facet active)
  try {
    const fEl = document.querySelector(".filters-status");
    if (fEl) {
      const active = [];
      if (state.occ)     active.push(`“${esc(labelFromSelect("occFilter"))}”`);
      if (state.gender)  active.push(`“${esc(labelFromSelect("genderFilter"))}”`);
      if (state.country) active.push(`“${esc(labelFromSelect("countryFilter"))}”`);
      if (state.dob)     active.push(`“${esc(labelFromSelect("dobFilter"))}”`);
      if (state.dod)     active.push(`“${esc(labelFromSelect("dodFilter"))}”`);
      if (state.pc)      active.push(`“${esc(labelFromSelect("pcFilter"))}”`);

      fEl.innerHTML = active.length
        ? `<button class="clear-chip" data-action="clear-filters" aria-label="Clear all filters">×</button><b>Filters:</b> ${active.join(" + ")}`
        : "";
    }
  } catch (err) { console.error("updateResultsSummary filters failed:", err); }

    // Line 4: Sort + clear chip (show chip only if non-default)
    try {
      const sEl = document.querySelector(".sort-status");
      if (sEl) {
        const key = state.sort || DEFAULT_SORT;
        if (key === DEFAULT_SORT) {
          // hide the sort-status completely
          sEl.innerHTML = "";
        } else {
          const label = sortLabel(key);
          sEl.innerHTML = `
            <button class="clear-chip" data-action="clear-sort" aria-label="Reset sort">×</button>
            <b>Sort:</b> ${esc(label)}
          `;
        }
      }
    } catch (err) {
      console.error("updateResultsSummary sort failed:", err);
    }
}


// ----------------------------- Sorting helpers ---------------------------------

function readIntOrNull(v) {
  const n = parseInt(v, 10);
  return Number.isFinite(n) ? n : null;
}

function getCardName(card) {
  return (
    card?.dataset?.name ||
    card?.querySelector("h3")?.textContent?.trim() ||
    ""
  );
}

function getCardYOB(card) {
  // Prefer explicit data-yob; else try data-dob (e.g., "1916" or "1916-..."); else null
  if (card?.dataset?.yob) return readIntOrNull(card.dataset.yob);
  if (card?.dataset?.dob) {
    // handle "1916" or "1916-xx" or "+1916-..."
    const m = String(card.dataset.dob).match(/[+-]?(\d{3,6})/);
    if (m) return readIntOrNull(m[1]);
  }
  return null;
}

function getCardYOD(card) {
  // Prefer explicit data-yod; else try data-dod (e.g., "1916" or "1916-..."); else null
  if (card?.dataset?.yod) return readIntOrNull(card.dataset.yod);
  if (card?.dataset?.dod) {
    // handle "1916" or "1916-xx" or "+1916-..."
    const m = String(card.dataset.dod).match(/[+-]?(\d{3,6})/);
    if (m) return readIntOrNull(m[1]);
  }
  return null;
}

function comparatorFor(sortKey) {
  // helper: normalize to null if not a finite number
  const norm = v => (Number.isFinite(v) ? v : null);

  // generic year comparator (getter is getCardYOB or getCardYOD)
  const byYear = (getter, asc = true) => (a, b) => {
    const ya = norm(getter(a));
    const yb = norm(getter(b));

    // nulls always go last
    if (ya == null && yb == null) {
      return getCardName(a).localeCompare(getCardName(b), undefined, { numeric: true, sensitivity: "base" });
    }
    if (ya == null) return 1;
    if (yb == null) return -1;

    if (ya !== yb) return asc ? (ya - yb) : (yb - ya);
    // tie-break by name
    return getCardName(a).localeCompare(getCardName(b), undefined, { numeric: true, sensitivity: "base" });
  };

  switch (sortKey) {
    case "yob_asc":  return byYear(getCardYOB, true);
    case "yob_desc": return byYear(getCardYOB, false);
    case "yod_asc":  return byYear(getCardYOD, true);
    case "yod_desc": return byYear(getCardYOD, false);
    case "name_desc":
      return (a, b) => getCardName(b).localeCompare(getCardName(a), undefined, { numeric: true, sensitivity: "base" });
    case "name_asc":
    default:
      return (a, b) => getCardName(a).localeCompare(getCardName(b), undefined, { numeric: true, sensitivity: "base" });
  }
}


function sortCards(cards, sortKey) {
  try {
    const key = SORT_KEYS.has(sortKey) ? sortKey : DEFAULT_SORT;
    const arr = cards.slice();
    arr.sort(comparatorFor(key));
    return arr;
  } catch (err) {
    console.error("sortCards() failed, returning original order:", err);
    return cards.slice();
  }
}

// ----------------------------- Unfiltered --------------------------------------

function renderUnfiltered(page) {
  try {
    const sort = getParams().sort;
    // If sort is non-default, treat like filtered path so we can reorder
    if (sort && sort !== "" && sort !== DEFAULT_SORT) {
      return renderFiltered({ page, sort });
    }

    const perPage = window.BLOCKS_PER_PAGE || 50;
    const cards = Array.from(document.querySelectorAll(".person-block"));
    const total = cards.length;

    cards.forEach(el => {
      const blockPage = parseInt(el.dataset.page, 10);
      el.style.display = blockPage === page ? "inline-block" : "none";
    });

    // highlight for visible ones if a query is set
    const state = getParams();
    const q = (state.q || "").trim();
    const visible = cards.filter(el => el.style.display !== "none");
    clearHighlights(visible);
    if (q) visible.forEach(c => applyHighlightsToCard(c, q));

    const pageNums = cards
      .map(el => parseInt(el.dataset.page, 10))
      .filter(n => Number.isFinite(n));
    const totalPages = pageNums.length ? Math.max(...pageNums) : 1;

    updatePaginator(page, totalPages, state);
    updateResultsSummary({ total, page, perPage, state });
  } catch (err) {
    console.error("renderUnfiltered() failed:", err);
  }
}

// ----------------------------- Filtered ----------------------------------------

function getFilteredCards(state) {
  try {
    const cards = Array.from(document.querySelectorAll(".person-block"));
    const actives = activeFacets(state);
    const query = (state.q || "").toLowerCase();

    return cards.filter(card => {
      for (const key of actives) {
        const { attr, kind } = FACETS[key];
        const val = state[key];
        const data = card.dataset[attr] || "";
        if (kind === "list") {
          const arr = data.split(",").filter(Boolean);
          if (!arr.includes(val)) return false;
        } else {
          if (data !== val) return false;
        }
      }
      // text search filter
      if (query) {
        const hay = cardIndexText(card); // cached lower-cased text
        if (!hay.includes(query)) return false;
      }
      return true;
    });
  } catch (err) {
    console.error("getFilteredCards() failed:", err);
    return [];
  }
}

function renderFiltered(state) {
  try {
    const perPage   = window.BLOCKS_PER_PAGE || 50;
    const container = document.querySelector(".gallery-container");
    const allCards  = Array.from(document.querySelectorAll(".person-block"));
    const matches   = getFilteredCards(state);

    // ---------- helpers ----------
    const parseYearFromISO = (iso) => {
      if (!iso) return null;
      const m = /^[+-]?(\d{1,6})-/.exec(iso);
      return m ? +m[1] : null;
    };

    const getYOB = (el) => {
      const d = el.dataset;
      if (d.yob && !Number.isNaN(+d.yob)) return +d.yob;
      return parseYearFromISO(d.dob) ?? null;
    };

    const getYOD = (el) => {
      const d = el.dataset;
      if (d.yod && !Number.isNaN(+d.yod)) return +d.yod;
      return parseYearFromISO(d.dod) ?? null;
    };

    const getName = (el) => {
      if (el.dataset.name) return el.dataset.name.toLowerCase();
      const h3 = el.querySelector("h3");
      if (h3 && h3.textContent) return h3.textContent.trim().toLowerCase();
      return (el.textContent || "").trim().toLowerCase();
    };

    // Unknown-year safe compare: unknowns (null) always go to the END, both asc & desc.
    const compareYears = (aYear, bYear, direction /* "asc"|"desc" */) => {
      const aNull = (aYear == null);
      const bNull = (bYear == null);
      if (aNull && bNull) return 0;
      if (aNull) return 1;   // a after b
      if (bNull) return -1;  // b after a
      return direction === "asc" ? (aYear - bYear) : (bYear - aYear);
    };

    const sortKey = (state && state.sort) || DEFAULT_SORT;
    const ordered = matches.slice().sort((a, b) => {
      switch (sortKey) {
        case "yob_asc":  {
          const r = compareYears(getYOB(a), getYOB(b), "asc");
          return r !== 0 ? r : getName(a).localeCompare(getName(b), undefined, {sensitivity: "base"});
        }
        case "yob_desc": {
          const r = compareYears(getYOB(a), getYOB(b), "desc");
          return r !== 0 ? r : getName(a).localeCompare(getName(b), undefined, {sensitivity: "base"});
        }
        case "yod_asc":  {
          const r = compareYears(getYOD(a), getYOD(b), "asc");
          return r !== 0 ? r : getName(a).localeCompare(getName(b), undefined, {sensitivity: "base"});
        }
        case "yod_desc": {
          const r = compareYears(getYOD(a), getYOD(b), "desc");
          return r !== 0 ? r : getName(a).localeCompare(getName(b), undefined, {sensitivity: "base"});
        }
        case "name_desc": {
          return getName(b).localeCompare(getName(a), undefined, {sensitivity: "base"});
        }
        case "name_asc":
        default:
          return getName(a).localeCompare(getName(b), undefined, {sensitivity: "base"});
      }
    });

    // ---------- paginate ----------
    const total      = ordered.length;
    const totalPages = Math.max(1, Math.ceil(total / perPage));
    const page       = Math.min(Math.max(1, state.page || 1), totalPages);
    const start      = (page - 1) * perPage;
    const end        = start + perPage;
    const pageItems  = ordered.slice(start, end);

    // ---------- render to DOM ----------
    allCards.forEach(c => (c.style.display = "none"));
    if (container) {
      const frag = document.createDocumentFragment();
      pageItems.forEach(c => {
        // column layout expects inline-block; grid may just use default
        c.style.display = "inline-block";
        frag.appendChild(c);            // reorders in DOM to match sort
      });
      container.appendChild(frag);
    } else {
      pageItems.forEach(c => (c.style.display = "inline-block"));
    }

    // ---------- highlighting ----------
    const q = (state.q || "").trim();
    clearHighlights(allCards);          // clear everywhere first
    if (q) pageItems.forEach(c => applyHighlightsToCard(c, q));


    // ---------- chrome ----------
    updatePaginator(page, totalPages, state);
    updateResultsSummary({ total, page, perPage, state });
  } catch (err) {
    console.error("renderFiltered() failed:", err);
  }
}

// ----------------------------- Paginator ---------------------------------------

function updatePaginator(currentPage, totalPages, state) {
  try {
    // Build href with current facets + sort preserved
    function linkHref(page) {
      const p = new URLSearchParams(window.location.search);
      p.set("page", page);
      for (const key in FACETS) {
        const v = state[key];
        if (v) p.set(FACETS[key].param, v);
        else p.delete(FACETS[key].param);
      }
      if (state.sort && SORT_KEYS.has(state.sort)) p.set("sort", state.sort);
      else p.delete("sort");
      return `?${p.toString()}`;
    }

    function createLink(page, label, disabled = false, active = false) {
      if (disabled) return `<span class="disabled">${label}</span>`;
      if (active)   return `<span class="current-page">${label}</span>`;
      return `<a href="${linkHref(page)}">${label}</a>`;
    }

    function buildPaginatorLinks() {
      const maxVisible = 4;
      const out = [];

      // First / Prev
      out.push(createLink(1, "First", currentPage === 1));
      out.push(createLink(Math.max(1, currentPage - 1), "Prev", currentPage === 1));

      // Numbered pages with ellipses
      const visible = [];
      if (totalPages <= 9) {
        for (let i = 1; i <= totalPages; i++) visible.push(i);
      } else {
        visible.push(1, 2, 3);
        if (currentPage > maxVisible + 2) visible.push("...");
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          if (i > 2 && i < totalPages - 1) visible.push(i);
        }
        if (currentPage < totalPages - maxVisible - 1) visible.push("...");
        visible.push(totalPages - 1, totalPages);
      }

      const seen = new Set();
      visible.forEach(i => {
        if (seen.has(i)) return; seen.add(i);
        out.push(i === "..." ? '<span class="dots">...</span>'
                             : createLink(i, i, false, i === currentPage));
      });

      // Next / Last
      out.push(createLink(Math.min(totalPages, currentPage + 1), "Next", currentPage === totalPages));
      out.push(createLink(totalPages, "Last", currentPage === totalPages));

      return out.join(" ");
    }

    document.querySelectorAll(".paginator").forEach(pg => {
      const statusEl = pg.querySelector(".page-status");
      const linksEl  = pg.querySelector(".paginator-links");

      if (statusEl) statusEl.textContent = `Page ${currentPage} of ${totalPages}`;
      if (linksEl)  linksEl.innerHTML = buildPaginatorLinks();
    });
  } catch (err) {
    console.error("updatePaginator() failed:", err);
  }
}

// ----------------------------- Controls wiring ---------------------------------

function syncSelectsFromURL() {
  try {
    const state = getParams();
    const occSel  = document.getElementById("occFilter");
    const gSel    = document.getElementById("genderFilter");
    const cSel    = document.getElementById("countryFilter");
    const dobSel  = document.getElementById("dobFilter");
    const dodSel  = document.getElementById("dodFilter");
    const pcSel   = document.getElementById("pcFilter");
    const sortSel = document.getElementById("sortOrder");

    if (occSel)  occSel.value  = state.occ || "";
    if (gSel)    gSel.value    = state.gender || "";
    if (cSel)    cSel.value    = state.country || "";
    if (dobSel)  dobSel.value  = state.dob || "";
    if (dodSel)  dodSel.value  = state.dod || "";
    if (pcSel)   pcSel.value   = state.pc || "";
    if (sortSel) sortSel.value = SORT_KEYS.has(state.sort) ? state.sort : DEFAULT_SORT;
  } catch (err) {
    console.error("syncSelectsFromURL() failed:", err);
  }
}

function syncSearchFromURL() {
  try {
    const { q } = getParams();
    const input = document.getElementById("searchBox");
    if (input) input.value = q.length >= MIN_QUERY_LENGTH ? q : "";
  } catch (err) {
    console.error("syncSearchFromURL() failed:", err);
  }
}

function onFacetChange() {
  try {
    const occSel  = document.getElementById("occFilter");
    const gSel    = document.getElementById("genderFilter");
    const cSel    = document.getElementById("countryFilter");
    const dobSel  = document.getElementById("dobFilter");
    const dodSel  = document.getElementById("dodFilter");
    const pcSel   = document.getElementById("pcFilter");
    const sortSel = document.getElementById("sortOrder");

    setParams({
      page: 1,
      occ:     occSel ? occSel.value.trim()  : "",
      gender:  gSel   ? gSel.value.trim()    : "",
      country: cSel   ? cSel.value.trim()    : "",
      dob:     dobSel ? dobSel.value.trim()  : "",
      dod:     dodSel ? dodSel.value.trim()  : "",
      pc:      pcSel  ? pcSel.value.trim()   : "",
      sort:    sortSel? sortSel.value.trim() : DEFAULT_SORT
    });
    render();
  } catch (err) {
    console.error("onFacetChange() failed:", err);
  }
}

// ----------------------------- Boot, load page --------------------------------------------

document.addEventListener("DOMContentLoaded", () => {
  try {
    // Hook filters + sort
    const occSel  = document.getElementById("occFilter");
    const gSel    = document.getElementById("genderFilter");
    const cSel    = document.getElementById("countryFilter");
    const dobSel  = document.getElementById("dobFilter");
    const dodSel  = document.getElementById("dodFilter");
    const pcSel   = document.getElementById("pcFilter");
    const sortSel = document.getElementById("sortOrder");
    const clear   = document.getElementById("clearFilter");
    const input   = document.getElementById("searchBox");
    const clearSearchBtn = document.getElementById("clearSearch");
    const spinner = document.getElementById("loading-spinner");
    const page    = document.getElementById("page-content");

    // Hide spinner, show content
    if (spinner) spinner.style.display = "none";
    if (page)    page.style.display = "block";

    [occSel, gSel, cSel, dobSel, dodSel, pcSel, sortSel].forEach(sel => {
      if (sel) sel.addEventListener("change", onFacetChange);
    });

    // Search
    if (input)    input.addEventListener("input", debounce(onSearchInput, 250));
    if (clearSearchBtn) clearSearchBtn.addEventListener("click", clearSearch);

    //Clear all filters + sort button
    if (clear) clear.addEventListener("click", () => {
      try {
        if (occSel)  occSel.value  = "";
        if (gSel)    gSel.value    = "";
        if (cSel)    cSel.value    = "";
        if (dobSel)  dobSel.value  = "";
        if (dodSel)  dodSel.value  = "";
        if (pcSel)   pcSel.value   = "";
        if (sortSel) sortSel.value = DEFAULT_SORT;
        setParams({ page: 1, occ: "", gender: "", country: "", dob: "", dod: "", pc: "", sort: DEFAULT_SORT });
        render();
      } catch (err) {
        console.error("Clear filters failed:", err);
      }
    });

    // Swiper init (guard for missing containers)
    document.querySelectorAll(".swiper").forEach(container => {
      try {
        new Swiper(container, {
          slidesPerView: 1,
          spaceBetween: 10,
          pagination: { el: container.querySelector(".swiper-pagination"), clickable: true }
        });
      } catch (err) {
        console.error("Swiper init failed for a container:", err);
      }
    });

    // Clear  search, sort and filters summaries in result summary (via red crosses
    document.querySelector(".results-extras")?.addEventListener("click", (e) => {
      const btn = e.target.closest(".clear-chip");
      if (!btn) return;

      const action = btn.dataset.action;
      try {
        if (action === "clear-search") {
          const input = document.getElementById("searchBox");
          if (input) input.value = "";
          // keep current facets/sort, just clear q + reset to first page
          const next = { ...getParams(), q: "", page: 1 };
          setParams(next);
          render();
        }

        if (action === "clear-filters") {
          // clear selects in UI
          ["occFilter","genderFilter","countryFilter","dobFilter","dodFilter","pcFilter"]
            .forEach(id => { const el = document.getElementById(id); if (el) el.value = ""; });
          // clear in URL/state (preserve search & sort)
          const cur = getParams();
          setParams({ ...cur, occ:"", gender:"", country:"", dob:"", dod:"", pc:"", page:1 });
          render();
        }

        if (action === "clear-sort") {
          const sortSel = document.getElementById("sortOrder");
          if (sortSel) sortSel.value = DEFAULT_SORT;
          // reset sort in URL/state
          const cur = getParams();
          setParams({ ...cur, sort: DEFAULT_SORT, page: 1 });
          render();
        }
      } catch (err) {
        console.error("Clear action failed:", err);
      }
    });

    // Sync selects + search query from URL and initial render
    syncSelectsFromURL();
    syncSearchFromURL()
    render();
  } catch (err) {
    console.error("DOMContentLoaded handler failed:", err);
  }
});
