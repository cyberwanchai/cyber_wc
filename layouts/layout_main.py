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
                    dcc.Link('Explore', href='/', id='home-button', className='nav-link'),
                    dcc.Link('Gallery', href='/gallery', id='gallery-button', className='nav-link'),
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


def star_filter_section(available_stars=star_placeholder):
    # Return an empty div or simply remove the section entirely,
    # but for structure preservation we'll return a hidden empty div.
    return html.Div(id='star-filter', style={'display': 'none'})


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
