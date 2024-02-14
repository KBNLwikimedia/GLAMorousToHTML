"""
This Python module automates the generation and publication of HTML pages that display Wikipedia articles,
organized by their respective language and project codes. The articles are presented in blocks, each headed
by the language name and the total count of articles within that language. Counts exceeding 999 are neatly
formatted with a dot as the thousand separator for better readability.

The module processes articles data, calculates the number of articles and distinct languages, generates
a languages menu and articles block in HTML format, and writes the final HTML output to specified files.
It supports customization of the output directory, file names, and includes error handling for robustness.

Functions:
- format_article_count(count): Formats article counts > 999 for readability. (1234 --> 1.234)
- get_number_of_articles(df): Returns the total number of articles in the DataFrame.
- get_number_of_languages(df): Returns the count of unique languages (project codes) in the DataFrame.
- transform_df_to_languages_menu(df): Generates an HTML formatted languages menu sorted 1) by article count,
  and 2) by full language names in case of equal article counts.
- transform_df_to_articles_block(df): Creates HTML blocks for articles, organized by language/project.
- write_payload_to_html(): Writes the provided HTML content to a file, creating directories if necessary.
- build_html(): Orchestrates the generation of HTML content from a DataFrame and writes it to an output file.

Latest update: 14 February 2024 - Olaf Janssen
Author: Olaf Janssen, Wikimedia coordinator @KB, national library of the Netherlands
Supported by ChatGPT
"""

import os
from setup import commons_cat, logo, xml_url
from general import today, today2
from buildExcel import excel_path

html_template_path = 'pagetemplate.html'
html_dir = "site" #Output directory containing: generated html pages, the logos folder and style.css file
html_file = "%s_Wikipedia_NS0_%s.html" % (commons_cat.replace(" ", ""), str(today))
html_path = os.path.join(html_dir, html_file)  # datestamped name of the HTML output file

def format_article_count(count):
    """Formats the article count with a dot as the thousand separator if greater than 999."""
    return f"{count // 1000}.{count % 1000:03d}" if count >= 1000 else f"{count}"

def get_number_of_articles(df):
    return format_article_count(len(df))

def get_number_of_lanquages(df):
    return df['ProjectCode'].nunique()

def transform_df_to_languages_menu(df):
    """
    Generates an HTML formatted string representing a menu of available languages, sorted by the number of Wikipedia
    articles for each language. This function uniquely handles cases where multiple project codes
    ('no.wikipedia' and 'nn.wikipedia') correspond to the same full language ('Nynorsk') by initially
    grouping by 'ProjectCode' to maintain accurate article counts.
    The output string formats each language entry as an HTML anchor tag, linking to an element with an ID matching
    the project code, and displays the article count for that language.
    Parameters:
    - df (pd.DataFrame): DataFrame containing at least 'ProjectCode', 'FullLanguageName', and 'ArticleURL' columns.
                         'ProjectCode' is used for unique article counts and IDs in the output menu.
                         'FullLanguageName' represents the language name to display.
                         'ArticleURL' is used to count the articles associated with each project code.

    Returns:
    - str: A single string composed of HTML anchor tags for each language, sorted by article count in descending
           order and by full language name in ascending order as a secondary criterion. Each anchor tag includes
           the language name, article count, and is linked to an HTML ID based on the project code.
           Languages with the same full name ('Nynorsk')  but different project codes ('no.wikipedia' and 'nn.wikipedia')
           are treated as separate entries.
   """
    # Group by 'ProjectCode' and count the number of articles for each ProjectCode
    article_counts = df.groupby('ProjectCode').size().reset_index(name='ArticleCount')
    # Map ProjectCode to FullLanguageName without losing the relation due to duplication
    project_to_language = df[['ProjectCode', 'FullLanguageName']].drop_duplicates().set_index('ProjectCode')['FullLanguageName']
    # Replace ProjectCode with FullLanguageName in the article_counts DataFrame
    article_counts['FullLanguageName'] = article_counts['ProjectCode'].map(project_to_language)
    # Sort the results by 'ArticleCount' in descending order, then by 'FullLanguageName' in ascending order
    sorted_final_counts = article_counts.sort_values(by=['ArticleCount', 'FullLanguageName'], ascending=[False, True])
    # Format each entry as an HTML anchor tag and combine into a single string
    language_menu_string = ' '.join(
        '<a href="#{id}">{language}</a> ({count})'.format(
            id = row['ProjectCode'],
            language = row['FullLanguageName'],
            count = format_article_count(row['ArticleCount']) # Format thousands, 1234 --> 1.234
        ) for row in sorted_final_counts.to_dict('records')
    )
    return language_menu_string


def transform_df_to_articles_block(df):
    """
    Generates an HTML block displaying Wikipedia articles organized by language/project.
    The articles are grouped by their project code ('es.wikipedia' - indicating Spanish language), with each group
    headed by an H4 tag showing the full language name and the total number of articles in that language.
    Article counts greater than 999 are formatted with a dot as the thousands separator (see def 'format_article_count()').
    Each article title within a group is presented as a clickable link, separated by a pipe symbol from the next title.
    Parameters:
    - df (pandas.DataFrame): A DataFrame containing at least 'ProjectCode', 'FullLanguageName',
      'ArticleTitle', and 'ArticleURL' columns. It is assumed to be pre-sorted according to the desired
      article order within each language/project group.
    Returns:
    - str: A string of HTML content with articles organized and formatted as described.
    Notes:
    - The function assumes 'df' is pre-sorted by the desired criteria, maintaining this sort order in the output.
    - This implementation directly formats large numbers using string manipulation for the thousands separator,
      which is locale-independent and ensures consistency across different environments.
    """
    html_output = ""
    last_project_code = None
    articles_html_list = []

    for _, row in df.iterrows():
        if row['ProjectCode'] != last_project_code:
            if articles_html_list:
                articles_html = " | ".join(articles_html_list)
                html_output += f" ({format_article_count(articles_count)})</h4>\n{articles_html}\n"
                articles_html_list = []
            html_output += f"<h4 id='{row['ProjectCode']}'>{row['FullLanguageName']}"
            last_project_code = row['ProjectCode']
            articles_count = 0

        articles_count += 1
        article_html = f'<a href="{row["ArticleURL"]}" target="_blank">{row["ArticleTitle"]}</a>'
        articles_html_list.append(article_html)

    if articles_html_list:
        articles_html = " | ".join(articles_html_list)
        html_output += f" ({format_article_count(articles_count)})</h4>\n{articles_html}\n"

    return html_output

def write_payload_to_html(htmltemplatepath=html_template_path, payload={}, htmldir=html_dir, htmlpath=html_path):
    """
    Reads an HTML template, formats it with the provided payload, and writes the result to a new HTML file.
    This function includes error handling for file reading, directory creation, and file writing processes.
    Parameters:
    - htmltemplatepath (str): Path to the HTML template file.
    - payload (dict): A dictionary containing all the variables to be parsed into the HTML template.
    - htmldir (str): The directory path where the HTML file will be saved. This function will attempt to create
                     the directory if it does not already exist.
    - htmlpath (str): The complete path, including the file name, where the output HTML file will be saved.
    Exceptions:
    - IOError: If there's an issue opening the template file or writing the output file.
    - OSError: If there's an issue creating the output directory.
    """
    try:
        # Attempt to read the HTML template from the file
        with open(htmltemplatepath, 'r', encoding='utf-8') as file:
            htmltemplate = file.read()
    except IOError as e:
        print(f"Failed to read the HTML template from {htmltemplatepath}: {e}")
        return
    try:
        # Format the template with the provided payload
        html = htmltemplate.format(**payload)
    except KeyError as e:
        print(f"A key in the payload is missing in the HTML template: {e}")
        return
    except Exception as e:
        print(f"An error occurred during formatting the HTML template: {e}")
        return
    try:
        # Ensure the output directory exists
        os.makedirs(htmldir, exist_ok=True)
    except OSError as e:
        print(f"Failed to create the directory {htmldir}: {e}")
        return
    try:
        # Write the formatted HTML to the output file
        with open(htmlpath, 'w', encoding='utf-8') as f:
            f.write(html)
        print(f"Successfully wrote the HTML file to {htmlpath}")
    except IOError as e:
        print(f"Failed to write the HTML file to {htmlpath}: {e}")


def build_html(df):
    num_articles = get_number_of_articles(df)
    num_languages = get_number_of_lanquages(df)
    languages_menu = transform_df_to_languages_menu(df)
    articles_block = transform_df_to_articles_block(df)

    # All the input that need to be parsed to the html template
    html_payload = {
        'numarticles' : num_articles,
        'numlanguages': num_languages,
        'commonscat': commons_cat,
        'xmlurl': xml_url,
        'xmlurl_trunc': xml_url.replace('&format=xml',''),
        'date': str(today2),
        'logo': logo,
        'languagesmenu': languages_menu,
        'articlesblock': articles_block,
        'excelpath' : excel_path
    }

    write_payload_to_html(payload=html_payload)