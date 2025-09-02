"""

**Author:**
Olaf Janssen – Wikimedia coordinator at KB, the national library of the Netherlands
**Supported by:** ChatGPT
**Last updated:** 20 August 2025
"""

import folium
from general import format_list_with_separator, safe_eval

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
                        <img src="{placeholder_image}" alt="No portrait available" style="height:400px; width:auto;"/>
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
                         alt="{name} – {img}" style="height:80%; width:auto;" class="thumb" loading="lazy"/>
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

# Function to add a marker to the specified cluster
def add_marker_to_cluster(location, popup_html, icon_color, icon, tooltip_html, cluster):
    iframe = folium.IFrame(html=popup_html, width=520, height=550)
    popup = folium.Popup(iframe, max_width=500)

    tooltip = folium.Tooltip(tooltip_html, sticky=False, direction="top")
    folium.Marker(
        location=location,
        popup=popup,
        icon=folium.Icon(color=icon_color, icon=icon, prefix="fa"),
        tooltip=tooltip,
    ).add_to(cluster)
