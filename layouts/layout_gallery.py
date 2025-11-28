"""
Gallery Layout
Shows all historic Hong Kong places in a card grid format
"""

from dash import html, dcc
from .layout_main import get_header_with_buttons, condition_color_map


def create_place_card(place_data, slug):
    """
    Create a card for a single place in the gallery.

    Parameters:
        place_data (pd.Series): Place information from the dataframe
        slug (str): URL-friendly slug for the place

    Returns:
        html.Div: Card component
    """
    name = place_data['name']
    description = place_data['description']
    st_date = place_data.get('st_date', '')
    end_date = place_data.get('end_date', '')
    curr_condition = place_data.get('curr_condition', 'Unknown')
    district = place_data['district']

    # Get condition color
    condition_color = condition_color_map.get(curr_condition, '#808080')

    # Format date range
    date_range = ''
    if st_date and st_date != '':
        date_range = f'{st_date}'
        if end_date and end_date != '':
            date_range += f' - {end_date}'

    # Truncate description for card view
    if not isinstance(description, str):
        description = ''
    short_description = description[:150] + '...' if len(description) > 150 else description

    card = html.Div(
        [
            # Card header with place name
            html.Div(
                [
                    html.H3(name, className='gallery-card-title'),
                    html.Div(
                        [
                            html.Span(
                                curr_condition,
                                className='gallery-card-status',
                                style={'backgroundColor': condition_color},
                            )
                        ],
                        className='gallery-card-status-container',
                    ),
                ],
                className='gallery-card-header',
            ),
            # Card body with details
            html.Div(
                [
                    html.P(
                        [
                            html.Span('📍 ', className='gallery-card-icon'),
                            html.Span(district, className='gallery-card-district'),
                        ],
                        className='gallery-card-location',
                    ),
                    html.P(
                        [
                            html.Span('📅 ', className='gallery-card-icon'),
                            html.Span(
                                date_range if date_range else 'Date unknown',
                                className='gallery-card-dates',
                            ),
                        ],
                        className='gallery-card-date-info',
                    )
                    if date_range
                    else None,
                    html.P(short_description, className='gallery-card-description'),
                ],
                className='gallery-card-body',
            ),
            # Card footer with link
            html.Div(
                [
                    dcc.Link(
                        'Read Full Article →',
                        href=f'/gallery/{slug}',
                        className='gallery-card-link',
                    )
                ],
                className='gallery-card-footer',
            ),
        ],
        className='gallery-card',
        id=f'gallery-card-{slug}',
    )

    return card


def get_gallery_layout(places_df, slug_map):
    """
    Create the main gallery layout with all place cards.

    Parameters:
        places_df (pd.DataFrame): DataFrame containing all places
        slug_map (dict): Mapping of place names to slugs

    Returns:
        html.Div: Complete gallery layout
    """
    # Header
    header = html.Div(children=[get_header_with_buttons()], className='header')

    # Gallery header section
    gallery_header = html.Div(
        [
            html.H1('Hong Kong Historic Places Gallery', className='gallery-title'),
            html.P(
                "Explore the historic streets, buildings, and landmarks that shaped Hong Kong's past.",
                className='gallery-subtitle',
            ),
        ],
        className='gallery-header-section',
    )

    # Filter section (region/district filters)
    filter_section = html.Div(
        [
            html.Div(
                [
                    html.Label('Filter by Region:', className='filter-label'),
                    dcc.Dropdown(
                        id='gallery-region-filter',
                        options=[
                            {'label': 'All Regions', 'value': 'all'},
                            {'label': 'Hong Kong Island', 'value': 'Hong Kong Island'},
                            {'label': 'Kowloon', 'value': 'Kowloon'},
                            {'label': 'New Territories', 'value': 'New Territories'},
                        ],
                        value='all',
                        className='gallery-filter-dropdown',
                        clearable=False,
                    ),
                ],
                className='filter-item',
            ),
            html.Div(
                [
                    html.Label('Filter by Status:', className='filter-label'),
                    dcc.Dropdown(
                        id='gallery-status-filter',
                        options=[
                            {'label': 'All', 'value': 'all'},
                            {'label': 'In Use', 'value': 'In use'},
                            {
                                'label': 'Demolished / No Longer Exists',
                                'value': 'Demolished / No longer exists',
                            },
                            {'label': 'Ruin', 'value': 'Ruin'},
                        ],
                        value='all',
                        className='gallery-filter-dropdown',
                        clearable=False,
                    ),
                ],
                className='filter-item',
            ),
        ],
        className='gallery-filter-section',
    )

    # Create cards for all places
    place_cards = []
    for _, place in places_df.iterrows():
        if place['name'] and place['name'] != '':  # Skip empty rows
            slug = slug_map.get(place['name'])
            if slug:
                card = create_place_card(place, slug)
                place_cards.append(card)

    # Gallery grid container
    gallery_grid = html.Div(place_cards, className='gallery-grid', id='gallery-grid-container')

    # Main content area
    gallery_content = html.Div(
        [
            gallery_header,
            filter_section,
            gallery_grid,
        ],
        className='gallery-content',
    )

    # Complete layout
    # Note: Chat widget is included at root level in app.layout for persistence
    return html.Div(
        [
            header,
            gallery_content,
        ],
        className='gallery-layout',
    )
