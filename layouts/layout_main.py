from dash import html, dcc
import dash_bootstrap_components as dbc


color_map = {0.25: '#808080', 0.5: '#B40505', 1: '#FFB84D', 2: '#FE6F64', 3: '#C2282D'}

condition_color_map = {
    'In use': '#689c44',
    'Demolished / No longer exists': '#FFB84D',
    'Ruin': '#C2282D',
}

star_placeholder = (0.25, 0.5, 1, 2, 3)

unique_regions = ['Hong Kong Island', 'Kowloon', 'New Territories']


# Inverted star images (legacy - used in hidden star filter)
def inverted_michelin_stars(count):
    # Returns a list of star image components each with inverted colors
    return [
        html.Img(
            src='assets/Images/Michelin_star.png',
            className='michelin-star-invert',
            style={
                'width': '16px',
                'vertical-align': 'middle',
                'margin-right': '2px',
                'filter': 'brightness(0) invert(1)',
            },
        )
        for _ in range(int(count))
    ]


def inverted_bib_gourmand():
    # Returns the Bib Gourmand image component with inverted colors
    return html.Img(
        src='assets/Images/Michelin_Bib.png',
        className='bib-image-invert',
        style={'width': '18px', 'vertical-align': 'middle', 'filter': 'brightness(0) invert(1)'},
    )


def get_header_with_buttons():
    return html.Div(
        children=[
            html.Div(
                [
                    html.H1(
                        [
                            'Cyber ',
                            html.Span('Wan Chai', className='year-text'),
                        ],
                        className='title-section',
                    ),
                ],
                className='header-title',
            ),
            # Hamburger toggle
            html.Div(
                id='hamburger-icon',
                n_clicks=0,
                className='hamburger-menu',
                children=[
                    html.Div(className='bar'),
                    html.Div(className='bar'),
                    html.Div(className='bar'),
                ],
            ),
            html.Div(
                id='navigation-menu',
                className='nav-dropdown',
                children=[
                    html.A('Explore', href='/', id='home-button', className='nav-link'),
                    html.A('Gallery', href='/gallery', id='gallery-button', className='nav-link'),
                ],
            ),
        ],
        className='header-container',
    )


def get_city_match_section():
    return html.Div(
        className='city-match-content-wrapper-mainpage clearfix',
        children=[
            # Info tab to unfold the search bar
            html.Div(
                children=[
                    html.Button(
                        'Search Locations', id='info-toggle-button', className='info-toggle-button'
                    )
                ],
                className='info-tab-container',
            ),
            # Collapsible content for the search bar
            dbc.Collapse(
                id='info-collapse',
                is_open=False,  # Initially closed
                children=[
                    html.Div(
                        className='city-match-sidebar-mainpage',
                        children=[
                            html.Div(
                                className='city-input-container-mainpage',
                                children=[
                                    dcc.Input(
                                        id='city-input-mainpage',
                                        type='text',
                                        placeholder='Enter a location in Hong Kong',
                                        debounce=True,
                                        className='city-input-field',
                                    ),
                                    # Submit button
                                    html.Button(
                                        'Submit',
                                        id='submit-city-button-mainpage',
                                        n_clicks=0,
                                        className='submit-city-button-mainpage',
                                    ),
                                    # Clear button
                                    html.Button(
                                        'Clear',
                                        id='clear-city-button-mainpage',
                                        n_clicks=0,
                                        className='clear-city-button-mainpage',
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
            ),
            # Main content for matched results - 70% width
            html.Div(
                className='city-match-main-content-mainpage',
                children=[
                    # Placeholder for the matched city content
                    html.Div(
                        id='matched-city-output-mainpage',
                        className='city-match-output-container-mainpage',
                    )
                ],
            ),
        ],
    )


def get_footer():
    return html.Div(
        children=[
            html.Div(
                children=[
                    html.Img(src='assets/Images/github-mark.png', className='info-image'),
                    html.Div(
                        children=[
                            # Info text on one line
                            html.Div(
                                children=[
                                    html.Span(
                                        'This project was built from ',
                                        className='info-text',
                                    ),
                                    dcc.Link(
                                        'this GitHub Repository',
                                        href='https://github.com/pineapple-bois/Michelin_Rated_Restaurants',
                                        target='_blank',
                                        className='info-link',
                                    ),
                                ],
                                className='info-line',  # New class for the first line
                            ),
                            # Copyright and disclaimer on another line
                            html.Div(
                                children=[
                                    html.Span('© pineapple-bois 2024', className='info-footer'),
                                    html.Span(
                                        ' | This website is an independent project showcasing historic Hong Kong places.',
                                        className='disclaimer-text',
                                    ),
                                ],
                                className='footer-inline',
                            ),
                        ],
                        className='text-container',
                    ),
                ],
                className='info-container',
            )
        ],
        className='footer-main',
    )


# Define the row with buttons logic as functions
def create_star_button(value, label, type_name='filter-button-mainpage'):
    # Generate color with reduced opacity for active state
    normal_bg_color = color_map[value]
    return dbc.Button(
        label,
        id={
            'type': type_name,
            'index': value,
        },
        className='me-1 star-button',
        outline=True,
        style={
            'display': 'inline-block',
            'backgroundColor': normal_bg_color,
            'width': '100%',
            'opacity': 1,
        },
        n_clicks=0,
    )


def star_filter_section(available_stars=star_placeholder):
    standard_stars = [s for s in available_stars if s != 0.25]
    has_selected = 0.25 in available_stars

    star_buttons = [
        create_star_button(
            star,
            inverted_michelin_stars(star) if star in [1, 2, 3] else inverted_bib_gourmand(),
            type_name='filter-button-mainpage',
        )
        for star in standard_stars
    ]

    toggle_button = html.Button(
        'Selected',
        id='toggle-selected-btn',
        n_clicks=0,
        className='selected-toggle-button',
        style={'display': 'block'},
    )

    def hidden_toggle_button():
        return html.Button('', id='toggle-selected-btn', n_clicks=1, style={'display': 'none'})

    # Shared layout title (filter is hidden but title remains for consistency)
    title = html.H6('Filter by Rating', className='star-select-title')

    # Case 1: inline (fits in same row)
    if has_selected and 1 <= len(standard_stars) <= 3:
        star_buttons.append(toggle_button)
        return html.Div(
            [title, html.Div(star_buttons, className='star-filter-buttons')],
            className='star-filter-section',
            id='star-filter',
            style={'display': 'none'},
        )

    # Case 2: only 0.25 available → show selected on its own row, 50% width
    elif has_selected and not standard_stars:
        return html.Div(
            [
                title,
                html.Div(
                    [
                        html.Div(toggle_button, className='selected-toggle-inner'),
                        html.Div(className='selected-toggle-spacer'),
                    ],
                    className='selected-toggle-wrapper',
                ),
            ],
            className='star-filter-section',
            id='star-filter',
            style={'display': 'none'},
        )

    # Case 3: single available bib → show on its own row, 50% width
    elif not has_selected and standard_stars == [0.5]:
        return html.Div(
            [
                title,
                html.Div(
                    [
                        html.Div(star_buttons[0], className='selected-toggle-inner'),
                        html.Div(className='selected-toggle-spacer'),
                    ],
                    className='selected-toggle-wrapper',
                ),
                hidden_toggle_button(),
            ],
            className='star-filter-section',
            id='star-filter',
            style={'display': 'none'},
        )

    # Case 4: selected on a new row, wrapped in its own aligned container
    elif has_selected:
        return html.Div(
            [
                title,
                html.Div(star_buttons, className='star-filter-buttons'),
                html.Div(
                    [
                        html.Div(toggle_button, className='selected-toggle-inner'),
                        html.Div(className='selected-toggle-spacer'),
                        html.Div(className='selected-toggle-spacer'),
                        html.Div(className='selected-toggle-spacer'),
                    ],
                    className='selected-toggle-wrapper',
                ),
            ],
            className='star-filter-section',
            id='star-filter',
            style={'display': 'none'},
        )

    # Case 5: no toggle at all (fallback)
    else:
        return html.Div(
            [
                title,
                html.Div(star_buttons, className='star-filter-buttons'),
                hidden_toggle_button(),
            ],
            className='star-filter-section',
            id='star-filter',
            style={'display': 'none'},
        )


def get_main_content_with_city_match(unique_regions):
    # City match section
    city_match_section = get_city_match_section()

    # Sidebar content (existing sidebar)
    sidebar_content = html.Div(
        [
            html.Div(
                [
                    html.H5(
                        'Explore historic streets of Hong Kong through photographs and stories.',
                        className='site-description',
                    )
                ],
                className='description-container',
            ),
            html.Div(
                [
                    html.P(
                        'Select a region and district to see historic streets and their stories.',
                        className='instructions',
                    )
                ],
                className='instructions-container',
            ),
            # Dropdown blocks wrapped in a flex container
            html.Div(
                [
                    html.Div(
                        [
                            html.H6('Select a Region', className='dropdown-title'),
                            dcc.Dropdown(
                                id='region-dropdown',
                                options=[
                                    {'label': region, 'value': region} for region in unique_regions
                                ],
                                value=None,
                                placeholder='Select a Region',
                                className='dropdown-style',
                                clearable=False,
                            ),
                        ],
                        className='dropdown-block',
                    ),
                    html.Div(
                        [
                            html.H6('Select a District', className='dropdown-title'),
                            dcc.Dropdown(id='district-dropdown', className='dropdown-style'),
                        ],
                        className='dropdown-block',
                    ),
                ],
                className='dropdowns-container-main',
            ),  # Flex container for dropdowns
            # Buttons and restaurant details
            html.Div(
                [
                    star_filter_section(star_placeholder),
                    # html.Button(
                    #     "Selected Restaurants",
                    #     id="toggle-selected-btn",
                    #     n_clicks=0,
                    #     className="selected-toggle-button",
                    #     style={'display': 'none'}
                    # ),
                    # dcc.Store(id='show-selected-toggle', data='none'),
                    html.Div(
                        id='place-details',
                        children=[],
                        className='place-details-container',
                    ),
                ],
                className='filters-and-details-container',
            ),
        ],
        className='sidebar-container',
    )

    # Map section (existing map)
    map_section = html.Div(
        [
            dcc.Graph(
                id='map-display',
                responsive=True,
                className='map-display',
                config={
                    'displayModeBar': True,
                    'scrollZoom': True,
                    'modeBarButtonsToRemove': [
                        'pan2d',
                        'select2d',
                        'lasso2d',
                        'zoomIn2d',
                        'zoomOut2d',
                        'autoScale2d',
                        'resetScale2d',
                        'hoverClosestCartesian',
                        'hoverCompareCartesian',
                        'toggleSpikelines',
                        'toImage',
                    ],
                    'modeBarButtonsToAdd': ['zoom2d', 'resetScale2d'],
                },
            ),
            dcc.Store(id='map-view-store-mainpage', data={}),
        ],
        className='map-section',
    )

    # Combine all sections into the main content layout
    return html.Div(
        [
            city_match_section,
            html.Div(
                [
                    map_section,
                    sidebar_content,
                ],
                className='map-sidebar-container',
            ),
        ],
        className='main-content',
    )


def get_main_layout():
    # Header with buttons
    header = html.Div(children=[get_header_with_buttons()], className='header')

    body = html.Div(children=[get_main_content_with_city_match(unique_regions)], className='body')

    # Chat widget moved to root app.layout for persistence across page navigation
    return html.Div([header, body], className='main-layout')
