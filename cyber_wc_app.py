import pandas as pd
import geopandas as gpd
import dash
import dash_bootstrap_components as dbc
from dash import dcc, html, callback_context
from dash.exceptions import PreventUpdate
from dash.dependencies import Input, Output, State, ALL
from flask import Flask
from flask_caching import Cache

from layouts.layout_main import get_main_layout, color_map
from layouts.layout_gallery import get_gallery_layout
from layouts.layout_place_detail import get_place_detail_layout
from layouts.layout_404 import get_404_layout

from utils.locationMatcher import LocationMatcher
from utils.markdownRenderer import get_all_place_slugs
from utils.appFunctions import (
    plot_interactive_district,
    default_map_figure,
    get_place_details,
    plot_region_center_view,
)

# Load Hong Kong places data
all_streets = pd.read_csv('assets/Data/hk_places.csv')

# Generate slug map for gallery routing
slug_map = get_all_place_slugs(all_streets)
# Create reverse mapping (slug -> place name)
reverse_slug_map = {v: k for k, v in slug_map.items()}

# Ensure district_num is a string for consistent comparisons
all_streets['district_num'] = all_streets['district_num'].astype(str)

# Load Hong Kong district GeoJSON data
district_df = gpd.read_file('assets/Data/hk_districts.geojson')

# Removed analysis-only datasets (region and wine) as part of cleanup

# Get unique districts with places
districts_with_places = all_streets['district_num'].unique()
# Filter geo_df to only districts with place data
geo_df = district_df[district_df['code'].isin(districts_with_places)]


# Use geo_df to get unique regions and districts for the initial dropdowns
# Constrain to Hong Kong's three regions
HK_REGIONS = ['Hong Kong Island', 'Kowloon', 'New Territories']
unique_regions = [r for r in sorted(district_df['region'].unique()) if r in HK_REGIONS]
initial_districts = geo_df[['district', 'code']].drop_duplicates().to_dict('records')
initial_options = [{'label': f'{d["district"]}', 'value': d['district']} for d in initial_districts]
district_to_code = (
    district_df.drop_duplicates(subset='district').set_index('district')['code'].to_dict()
)
region_to_name = {region: region for region in unique_regions}

# -----------------> App and server setup

server = Flask(__name__)
app = dash.Dash(
    __name__,
    suppress_callback_exceptions=True,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        'https://fonts.googleapis.com/css2?family=Kaisei+Decol&family=Libre+Franklin:'
        'ital,wght@0,100..900;1,100..900&display=swap',
    ],
    server=server,
)


# Comment out to launch locally (development)
# @server.before_request
# def before_request():
#     if not request.is_secure:
#         url = request.url.replace('http://', 'https://', 1)
#         return redirect(url, code=301)


# App set up
app.title = 'Cyber Wan Chai - A Gallary for Old Hong Kong Memory'
app.index_string = open('assets/custom_header.html', 'r').read()
app.layout = html.Div(
    [
        dcc.Store(id='selected-stars', data=[]),
        dcc.Store(id='available-stars', data=[]),  # will populate with star rating by district
        dcc.Store(id='district-centroid-store', data={}),
        dcc.Location(id='url', refresh=False),  # Tracks the url
        html.Div(id='page-content', children=get_main_layout()),  # Set initial content
    ]
)

# Initialize the cache (Maybe Redis or filesystem-based caching for production...?)
cache = Cache(
    app.server,
    config={
        'CACHE_TYPE': 'simple',
        'CACHE_DEFAULT_TIMEOUT': 3600,  # Cache timeout in seconds (1 hour)
    },
)


# Define callback to handle page navigation
@app.callback(Output('page-content', 'children'), Input('url', 'pathname'))
def display_page(pathname):
    if pathname == '/gallery':
        return get_gallery_layout(all_streets, slug_map)
    elif pathname and pathname.startswith('/gallery/'):
        # Extract slug from URL
        place_slug = pathname.replace('/gallery/', '')
        # Look up place by slug
        place_name = reverse_slug_map.get(place_slug)
        if place_name:
            # Find the place data
            place_data = all_streets[all_streets['name'] == place_name]
            if not place_data.empty:
                return get_place_detail_layout(place_data.iloc[0], place_slug)
        # If place not found, show 404
        return get_404_layout()
    elif pathname == '/home':
        return get_main_layout()
    else:
        return get_main_layout() if pathname == '/' else get_404_layout()


# Toggle nav menu open/closed
@app.callback(
    Output('navigation-menu', 'className'),
    Input('hamburger-icon', 'n_clicks'),
    State('navigation-menu', 'className'),
    prevent_initial_call=True,
)
def toggle_menu_class(n_clicks, current_class):
    if current_class == 'nav-dropdown':
        return 'nav-dropdown visible'
    else:
        return 'nav-dropdown'


@app.callback(
    [Output('home-button', 'className'), Output('gallery-button', 'className')],
    Input('url', 'pathname'),
)
def update_nav_classes(pathname):
    active_class = 'nav-link active'
    inactive_class = 'nav-link'

    if pathname in ['/', '/home']:
        return active_class, inactive_class
    elif pathname and (pathname == '/gallery' or pathname.startswith('/gallery/')):
        return inactive_class, active_class
    else:
        return inactive_class, inactive_class


# -----------------------> "Gallery Page"


@app.callback(
    Output('gallery-grid-container', 'children'),
    [
        Input('gallery-region-filter', 'value'),
        Input('gallery-status-filter', 'value'),
    ],
)
def filter_gallery(selected_region, selected_status):
    """Filter gallery cards based on region and status."""
    filtered_df = all_streets.copy()

    # Apply region filter
    if selected_region != 'all':
        filtered_df = filtered_df[filtered_df['region'] == selected_region]

    # Apply status filter
    if selected_status != 'all':
        filtered_df = filtered_df[filtered_df['curr_condition'] == selected_status]

    # Import here to avoid circular imports
    from layouts.layout_gallery import create_place_card

    # Create cards for filtered places
    place_cards = []
    for _, place in filtered_df.iterrows():
        if place['name'] and place['name'] != '':
            slug = slug_map.get(place['name'])
            if slug:
                card = create_place_card(place, slug)
                place_cards.append(card)

    # If no places found, show message
    if not place_cards:
        return html.Div(
            'No places match the selected filters.',
            className='no-results-message',
            style={'textAlign': 'center', 'padding': '2em', 'color': '#666'},
        )

    return place_cards


# -----------------------> "Guide Page"


# Get rid of the 'hand' when hovering over places (doesn't work with Safari...)
app.clientside_callback(
    """
    function(hoverData) {
        if (hoverData) {
            document.getElementById('map-display').style.cursor = 'pointer';
        } else {
            document.getElementById('map-display').style.cursor = 'default';
        }
    }
    """,
    Output('dummy-output', 'children'),
    Input('map-display', 'hoverData'),
)


"""New version with Enter key functionality"""


@app.callback(
    [
        Output('info-collapse', 'is_open'),
        Output('city-input-mainpage', 'value'),
        Output('matched-city-output-mainpage', 'children'),
        Output('matched-city-output-mainpage', 'className'),
        Output('region-dropdown', 'value'),
        Output('district-dropdown', 'value'),
    ],
    [
        Input('info-toggle-button', 'n_clicks'),
        Input('submit-city-button-mainpage', 'n_clicks'),
        Input('clear-city-button-mainpage', 'n_clicks'),
        Input('city-input-mainpage', 'n_submit'),
    ],  # Add `n_submit` for Enter key
    [State('info-collapse', 'is_open'), State('city-input-mainpage', 'value')],
)
def toggle_collapse_and_handle_search(
    n_info_clicks, n_submit_clicks, n_clear_clicks, n_submit, is_open, city_input
):
    """
    Callback function to manage the information collapse section and handle city search functionality.

    This function handles user interactions:
    - Toggling the information collapse visibility with the info button.
    - Processing city search via submit button or pressing Enter.
    - Clearing input and resetting outputs with the clear button.
    """
    # Ensure clicks are initialized
    n_info_clicks = n_info_clicks or 0
    n_submit_clicks = n_submit_clicks or 0
    n_clear_clicks = n_clear_clicks or 0
    n_submit = n_submit or 0

    # Collapse logic: only triggered by the toggle button
    ctx = dash.callback_context
    if ctx.triggered[0]['prop_id'] == 'info-toggle-button.n_clicks':
        if is_open:
            # Collapse: clear input and match result
            return (
                False,
                '',
                html.Div([html.P('', className='default-message')]),
                'city-match-output-container-mainpage',
                dash.no_update,
                dash.no_update,
            )
        else:
            # Expand the collapse without resetting input/output
            return (
                True,
                dash.no_update,
                dash.no_update,
                'city-match-output-container-mainpage',
                dash.no_update,
                dash.no_update,
            )

    # Handle clearing the input and resetting the output when clear is clicked
    if ctx.triggered[0]['prop_id'] == 'clear-city-button-mainpage.n_clicks':
        return (
            dash.no_update,
            '',
            html.Div([html.P('', className='default-message')]),
            'city-match-output-container-mainpage',
            dash.no_update,
            dash.no_update,
        )

    # Handle the search functionality triggered by the submit button or Enter key
    if ctx.triggered[0]['prop_id'] in {
        'submit-city-button-mainpage.n_clicks',
        'city-input-mainpage.n_submit',
    }:
        if not city_input:
            # Fallback for invalid or empty input
            return (
                dash.no_update,
                '',
                html.Div([html.P('Enter a valid location.', className='default-message')]),
                'city-match-output-container-mainpage',
                dash.no_update,
                dash.no_update,
            )

        matcher = LocationMatcher(all_streets)
        result = matcher.find_region_district(city_input)
        if isinstance(result, dict):
            # Valid result, update outputs
            city_details = [
                html.P(
                    f'Match:  {result.get("Matched Location", "Unknown")},  '
                    f'Region:  {result.get("Region", "Unknown")},  '
                    f'District:  {result.get("District", "Unknown")}',
                    className='match-details',
                ),
            ]
            return (
                dash.no_update,
                dash.no_update,
                html.Div(city_details, className='city-match-container'),
                'city-match-output-container-mainpage visible',
                result.get('Region'),
                result.get('District'),
            )
        else:
            # No match found
            return (
                dash.no_update,
                dash.no_update,
                html.Div(
                    [
                        html.P(
                            f"No match found. '{city_input}' is not represented in our gallery.",
                            className='no-match-message',
                        )
                    ]
                ),
                'city-match-output-container-mainpage visible',
                dash.no_update,
                dash.no_update,
            )

    # Default to no update if no actions were triggered
    return (
        dash.no_update,
        dash.no_update,
        dash.no_update,
        'city-match-output-container-mainpage',
        dash.no_update,
        dash.no_update,
    )


@app.callback(
    [
        Output('district-dropdown', 'options'),
        Output('star-filter', 'children'),
        Output('star-filter', 'style'),
        Output('available-stars', 'data'),
    ],
    [
        Input('region-dropdown', 'value'),
        Input('district-dropdown', 'value'),
    ],
)
def update_district_and_filters(selected_region, selected_district):
    # Use dynamic geo_df for HK districts
    geo_df_dynamic = district_df

    # Fetch district options based on the selected region.
    districts = (
        geo_df_dynamic[geo_df_dynamic['region'] == selected_region][['district', 'code']]
        .drop_duplicates()
        .to_dict('records')
    )
    district_options = [{'label': f'{d["district"]}', 'value': d['district']} for d in districts]

    # Places don't have star ratings, so always hide star filter
    # Return a placeholder list with all places visible
    available_stars = []

    return district_options, [], {'display': 'none'}, available_stars


@app.callback(
    [
        Output({'type': 'filter-button-mainpage', 'index': ALL}, 'className'),
        Output({'type': 'filter-button-mainpage', 'index': ALL}, 'style'),
        Output('selected-stars', 'data'),
        Output('toggle-selected-btn', 'className'),
        Output('toggle-selected-btn', 'style'),
    ],
    [
        Input({'type': 'filter-button-mainpage', 'index': ALL}, 'n_clicks'),
        Input('toggle-selected-btn', 'n_clicks'),
    ],
    [
        State({'type': 'filter-button-mainpage', 'index': ALL}, 'id'),
        State('selected-stars', 'data'),
        State('available-stars', 'data'),
    ],
)
def update_button_active_state(
    n_clicks_list, toggle_selected_clicks, ids, current_stars, available_stars
):
    # Handle cases where not all data is available, especially at initialization
    if (
        not n_clicks_list or not available_stars or len(available_stars) == 0
    ) and available_stars != [0.25]:
        raise PreventUpdate

    # Initialize empty lists to store class names and styles
    class_names = []
    styles = []

    # Initialize the new list of active stars from current state filtered by available stars
    new_stars = [star for star in current_stars if star in available_stars and star != 0.25]

    for i, button_id in enumerate(ids):
        index = button_id['index']
        n_clicks = n_clicks_list[i] if i < len(n_clicks_list) else 0  # fallback to 0

        if index not in available_stars:
            # Still return something so Dash output lengths match
            class_names.append('me-1 star-button inactive')
            styles.append(
                {'display': 'inline-block', 'width': '100%', 'backgroundColor': '#cccccc'}
            )
            continue

        # Determine if the button is active (even number of clicks means active)
        is_active = n_clicks % 2 == 0

        if is_active:
            if index not in new_stars:
                new_stars.append(index)
            background_color = color_map[index]
        else:
            if index in new_stars:
                new_stars.remove(index)
            background_color = (
                f'rgba({int(color_map[index][1:3], 16)},'
                f'{int(color_map[index][3:5], 16)},'
                f'{int(color_map[index][5:7], 16)},0.6)'
            )

        class_name = 'me-1 star-button' + (' active' if is_active else '')
        color_style = {
            'display': 'inline-block',
            'width': '100%',
            'backgroundColor': background_color,
        }
        class_names.append(class_name)
        styles.append(color_style)

    # ---- Toggle Selected Button Logic ----
    selected_active = toggle_selected_clicks % 2 == 0
    if selected_active and 0.25 not in new_stars:
        new_stars.append(0.25)
    elif not selected_active and 0.25 in new_stars:
        new_stars.remove(0.25)

    selected_class = 'selected-toggle-button' + (' active' if selected_active else ' inactive')
    # Compute display: show the toggle button only if 0.25 is an available star rating
    toggle_display = 'block' if 0.25 in available_stars else 'none'
    selected_style = {
        'display': toggle_display,
    }

    return class_names, styles, new_stars, selected_class, selected_style


@app.callback(
    Output('place-details', 'children'),
    [
        Input('map-display', 'clickData'),
        Input('district-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('selected-stars', 'data'),
    ],
)
def update_sidebar(clickData, selected_district, selected_region, selected_stars):
    ctx = dash.callback_context

    # Placeholder messages
    place_placeholder = html.Div(
        'Select a place on the map to see more details', className='placeholder-text'
    )

    select_district_placeholder = html.Div(
        'Select a district to view places.', className='placeholder-text'
    )

    # If no district is selected, prompt the user
    if not selected_district:
        return select_district_placeholder

    # Get place data
    combined_data = all_streets

    # Determine which input triggered the callback
    triggered_id = ctx.triggered[0]['prop_id'].split('.')[0]

    # Handle map clicks
    if triggered_id == 'map-display':
        if clickData and 'points' in clickData and len(clickData['points']) > 0:
            point = clickData['points'][0]
            place_index = point.get('meta') or point.get('customdata')

            if place_index in combined_data.index:
                place_info = combined_data.loc[place_index]
                # Places don't have star filtering, always show
                return get_place_details(place_info)
        return place_placeholder

    # For any other triggers, clear the place details
    return place_placeholder


@app.callback(
    Output('map-display', 'figure'),
    [
        Input('district-dropdown', 'value'),
        Input('region-dropdown', 'value'),
        Input('selected-stars', 'data'),
    ],
    [
        State('map-view-store-mainpage', 'data'),
        State('district-centroid-store', 'data'),
    ],
)
def update_map(
    selected_district,
    selected_region,
    selected_stars,
    mapview_data,
    district_viewdata,
):
    ctx = callback_context
    triggered_id, _ = ctx.triggered[0]['prop_id'].split('.') if ctx.triggered else (None, None)

    # Use HK place data
    place_data = all_streets
    geo_df_dynamic = district_df
    district_to_code_dynamic = (
        geo_df_dynamic.drop_duplicates(subset='district').set_index('district')['code'].to_dict()
    )

    # Case 1: District selected - show all places
    if selected_district:
        district_code = district_to_code_dynamic.get(selected_district)

        # Calculate centroid inline to ensure we zoom to the NEWLY selected district
        # (ignoring district_viewdata which might be stale due to callback race conditions)
        filtered_geo = geo_df_dynamic[geo_df_dynamic['code'] == str(district_code)]
        if not filtered_geo.empty:
            centroid = filtered_geo['geometry'].iloc[0].centroid
            view_data = {'zoom': 13, 'center': {'lat': centroid.y, 'lon': centroid.x}}
        else:
            view_data = {}

        return plot_interactive_district(
            place_data,
            geo_df_dynamic,
            district_code,
            view_data,
        )

    # Case 2: Handle region selection - center only (no outlines)
    if selected_region or triggered_id == 'region-dropdown':
        region_name = region_to_name.get(selected_region)
        if region_name:
            # Center the map on the region centroid without drawing boundaries
            return plot_region_center_view(district_df, region_name)

    # Default fallback case: Show entire Hong Kong map
    return default_map_figure()


@app.callback(
    Output('district-centroid-store', 'data'),
    [Input('district-dropdown', 'value'), Input('region-dropdown', 'value')],
)
def calculate_district_centroid(selected_district, selected_region):
    if not selected_district:
        return {}

    # Get HK districts geo data
    geo_df_dynamic = district_df

    # Generate district_to_code dynamically
    district_to_code_dynamic = (
        geo_df_dynamic.drop_duplicates(subset='district').set_index('district')['code'].to_dict()
    )
    district_code = district_to_code_dynamic.get(selected_district)

    if not district_code:
        return {}

    filtered_geo = geo_df_dynamic[geo_df_dynamic['code'] == str(district_code)]
    if filtered_geo.empty:
        return {}

    specific_geometry = filtered_geo['geometry'].iloc[0]
    centroid = specific_geometry.centroid

    # Hong Kong districts use a standard zoom level
    zoom_level = 13

    return {'zoom': zoom_level, 'center': {'lat': centroid.y, 'lon': centroid.x}}


@app.callback(
    Output('map-view-store-mainpage', 'data'),
    [
        Input('map-display', 'relayoutData'),
        Input('region-dropdown', 'value'),
        Input('district-dropdown', 'value'),
    ],
    [State('map-view-store-mainpage', 'data')],
)
def store_map_view_mainpage(relayout_data, selected_region, selected_district, existing_data):
    # Initialize existing_data if it's None
    if existing_data is None:
        existing_data = {}

    # Reset zoom data when region or district changes
    ctx = dash.callback_context
    triggered_input = ctx.triggered[0]['prop_id'].split('.')[0] if ctx.triggered else None

    if triggered_input in ['region-dropdown', 'district-dropdown']:
        return {}

    # If relayoutData is None or empty, do not update the store
    if not relayout_data:
        raise dash.exceptions.PreventUpdate

    # Define the keys that indicate a user interaction
    user_interaction_keys = {'map.zoom', 'map.center'}

    # Check if relayoutData contains any of the user interaction keys
    if user_interaction_keys.intersection(relayout_data.keys()):
        # Extract zoom and center from relayoutData
        zoom = relayout_data.get('map.zoom', existing_data.get('zoom'))
        center = relayout_data.get('map.center', existing_data.get('center'))

        if zoom is not None and center is not None:
            # Update the existing_data with new zoom and center
            existing_data['zoom'] = zoom
            existing_data['center'] = center

            return existing_data

    # If no user interaction keys are present, prevent updating the store
    raise dash.exceptions.PreventUpdate


# For local development, debug=True
if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
