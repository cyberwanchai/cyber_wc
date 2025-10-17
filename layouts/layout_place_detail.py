"""
Place Detail Layout
Shows individual place article with markdown content
"""

from dash import html, dcc
import dash_bootstrap_components as dbc
from .layout_main import get_header_with_buttons, get_footer, condition_color_map
from utils.markdownRenderer import render_markdown_file


def get_place_detail_layout(place_data, slug):
    """
    Create the detail page layout for a single place.

    Parameters:
        place_data (pd.Series): Place information from the dataframe
        slug (str): URL-friendly slug for the place

    Returns:
        html.Div: Complete place detail layout
    """
    if place_data is None:
        # Place not found
        return get_404_place_layout()

    # Extract place information
    name = place_data['name']
    address = place_data.get('address', '')
    location = place_data['location']
    district = place_data['district']
    district_zh = place_data.get('district_zh', '')
    region = place_data['region']
    st_date = place_data.get('st_date', '')
    end_date = place_data.get('end_date', '')
    curr_condition = place_data.get('curr_condition', 'Unknown')
    url = place_data.get('url', '')

    # Get condition color
    condition_color = condition_color_map.get(curr_condition, '#808080')

    # Format date range
    date_range = ''
    if st_date and st_date != '':
        date_range = f'{st_date}'
        if end_date and end_date != '':
            date_range += f' - {end_date}'

    # Render markdown content
    article_html = render_markdown_file(slug)

    # Header
    header = html.Div(children=[get_header_with_buttons()], className='header')

    # Breadcrumb navigation
    breadcrumb = html.Div(
        [
            dcc.Link('Home', href='/', className='breadcrumb-link'),
            html.Span(' / ', className='breadcrumb-separator'),
            dcc.Link('Gallery', href='/gallery', className='breadcrumb-link'),
            html.Span(' / ', className='breadcrumb-separator'),
            html.Span(name, className='breadcrumb-current'),
        ],
        className='breadcrumb-nav',
    )

    # Place header section
    place_header = html.Div(
        [
            html.H1(name, className='place-title'),
            html.Div(
                [
                    html.Span(
                        curr_condition,
                        className='place-status-badge',
                        style={'backgroundColor': condition_color, 'color': 'white'},
                    ),
                ],
                className='place-status-container',
            ),
        ],
        className='place-header',
    )

    # Place metadata section
    metadata = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong('📍 Location:', className='metadata-label'),
                            html.Span(f' {location}', className='metadata-value'),
                        ],
                        className='metadata-item',
                    ),
                    html.Div(
                        [
                            html.Strong('🏛️ District:', className='metadata-label'),
                            html.Span(f' {district}', className='metadata-value'),
                            html.Span(f' ({district_zh})', className='metadata-value-zh')
                            if district_zh
                            else None,
                        ],
                        className='metadata-item',
                    ),
                    html.Div(
                        [
                            html.Strong('🗺️ Region:', className='metadata-label'),
                            html.Span(f' {region}', className='metadata-value'),
                        ],
                        className='metadata-item',
                    ),
                ],
                className='metadata-column',
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Strong('📅 Period:', className='metadata-label'),
                            html.Span(
                                f' {date_range}' if date_range else ' Date unknown',
                                className='metadata-value',
                            ),
                        ],
                        className='metadata-item',
                    )
                    if date_range
                    else None,
                    html.Div(
                        [
                            html.Strong('📧 Address:', className='metadata-label'),
                            html.Span(f' {address}', className='metadata-value'),
                        ],
                        className='metadata-item',
                    )
                    if address
                    else None,
                    html.Div(
                        [
                            html.Strong('🔗 External Link:', className='metadata-label'),
                            html.A(
                                ' Wikipedia', href=url, target='_blank', className='metadata-link'
                            ),
                        ],
                        className='metadata-item',
                    )
                    if url
                    else None,
                ],
                className='metadata-column',
            ),
        ],
        className='place-metadata',
    )

    # Article content (rendered markdown)
    article_content = html.Div(
        [
            html.Div(
                html.Iframe(
                    srcDoc=f"""
                    <!DOCTYPE html>
                    <html>
                    <head>
                        <meta charset="utf-8">
                        <style>
                            body {{
                                font-family: 'Libre Franklin', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                                line-height: 1.8;
                                color: #333;
                                margin: 0;
                                padding: 20px;
                            }}
                            h1, h2, h3, h4 {{ 
                                color: #640A64; 
                                margin-top: 1.5em;
                                margin-bottom: 0.5em;
                            }}
                            h1 {{ font-size: 2em; border-bottom: 2px solid #640A64; padding-bottom: 0.3em; }}
                            h2 {{ font-size: 1.6em; border-bottom: 1px solid #ddd; padding-bottom: 0.2em; }}
                            h3 {{ font-size: 1.3em; }}
                            p {{ margin: 1em 0; }}
                            ul, ol {{ margin: 1em 0; padding-left: 2em; }}
                            li {{ margin: 0.5em 0; }}
                            strong {{ color: #640A64; }}
                            a {{ color: #640A64; text-decoration: none; border-bottom: 1px solid #640A64; }}
                            a:hover {{ color: #FFB84D; border-bottom-color: #FFB84D; }}
                            blockquote {{
                                border-left: 4px solid #640A64;
                                margin: 1.5em 0;
                                padding: 0.5em 1em;
                                background: #f9f9f9;
                                font-style: italic;
                            }}
                            code {{
                                background: #f4f4f4;
                                padding: 2px 6px;
                                border-radius: 3px;
                                font-family: 'Courier New', monospace;
                            }}
                            pre {{
                                background: #f4f4f4;
                                padding: 1em;
                                border-radius: 5px;
                                overflow-x: auto;
                            }}
                            table {{
                                border-collapse: collapse;
                                width: 100%;
                                margin: 1.5em 0;
                            }}
                            th, td {{
                                border: 1px solid #ddd;
                                padding: 0.75em;
                                text-align: left;
                            }}
                            th {{
                                background: #640A64;
                                color: white;
                            }}
                            tr:nth-child(even) {{ background: #f9f9f9; }}
                            .placeholder-article, .error-article {{
                                padding: 2em;
                                text-align: center;
                                color: #666;
                            }}
                        </style>
                    </head>
                    <body>
                        {article_html}
                    </body>
                    </html>
                    """,
                    style={
                        'width': '100%',
                        'height': '100%',
                        'border': 'none',
                        'minHeight': '800px',
                    },
                ),
                className='markdown-content',
            ),
        ],
        className='place-article-content',
    )

    # Back to gallery link
    back_link = html.Div(
        [dcc.Link('← Back to Gallery', href='/gallery', className='back-to-gallery-link')],
        className='back-to-gallery',
    )

    # Footer
    # footer = get_footer()

    # Complete layout
    return html.Div(
        [
            header,
            html.Div(
                [
                    breadcrumb,
                    place_header,
                    metadata,
                    html.Hr(className='place-divider'),
                    article_content,
                    back_link,
                ],
                className='place-detail-content',
            ),
            # footer,
        ],
        className='place-detail-layout',
    )


def get_404_place_layout():
    """
    Create a 404 page for places that don't exist.

    Returns:
        html.Div: 404 layout
    """
    header = html.Div(children=[get_header_with_buttons()], className='header')
    footer = get_footer()

    return html.Div(
        [
            header,
            html.Div(
                [
                    html.H1('Place Not Found', className='error-title'),
                    html.P(
                        "The historic place you're looking for doesn't exist in our gallery.",
                        className='error-message',
                    ),
                    dcc.Link('Return to Gallery', href='/gallery', className='error-link'),
                ],
                className='error-content',
            ),
            footer,
        ],
        className='error-layout',
    )
