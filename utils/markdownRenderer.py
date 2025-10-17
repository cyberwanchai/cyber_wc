"""
Markdown Renderer Utility
Converts markdown files to styled HTML for display in the gallery
"""

import os
import markdown
from pathlib import Path


def generate_slug(name):
    """
    Convert a place name to a URL-friendly slug.

    Parameters:
        name (str): Place name

    Returns:
        str: URL-friendly slug
    """
    # Remove special characters, convert to lowercase, replace spaces with hyphens
    slug = name.lower()
    slug = slug.replace("'", '')
    slug = slug.replace('"', '')
    slug = slug.replace(',', '')
    slug = slug.replace('(', '')
    slug = slug.replace(')', '')
    slug = slug.replace('.', '')
    slug = slug.replace(' ', '-')
    slug = slug.replace('--', '-')
    return slug


def render_markdown_file(place_slug):
    """
    Read and render a markdown file to HTML.

    Parameters:
        place_slug (str): The slug identifier for the place

    Returns:
        str: Rendered HTML content or placeholder message if file not found
    """
    # Construct the file path
    base_path = Path(__file__).parent.parent
    md_file_path = base_path / 'assets' / 'articles' / f'{place_slug}.md'

    # Check if the file exists
    if not md_file_path.exists():
        return f"""
        <div class="placeholder-article">
            <h2>Article Coming Soon</h2>
            <p>The full article for this historic place is currently being prepared.</p>
            <p>Please check back later for more detailed information, photographs, and historical context.</p>
        </div>
        """

    # Read the markdown file
    try:
        with open(md_file_path, 'r', encoding='utf-8') as f:
            md_content = f.read()

        # Convert markdown to HTML with extensions
        html_content = markdown.markdown(
            md_content,
            extensions=[
                'extra',  # Includes tables, fenced code blocks, etc.
                'nl2br',  # Newline to <br>
                'sane_lists',  # Better list handling
            ],
        )

        return html_content
    except Exception as e:
        return f"""
        <div class="error-article">
            <h2>Error Loading Article</h2>
            <p>There was an error loading this article: {str(e)}</p>
        </div>
        """


def get_all_place_slugs(places_df):
    """
    Generate slugs for all places in the dataframe.

    Parameters:
        places_df (pd.DataFrame): DataFrame containing place information

    Returns:
        dict: Mapping of place names to slugs
    """
    slug_map = {}
    for _, row in places_df.iterrows():
        name = row['name']
        slug_map[name] = generate_slug(name)
    return slug_map
