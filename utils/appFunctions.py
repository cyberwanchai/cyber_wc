import pandas as pd
import geopandas as gpd
import plotly.graph_objects as go
from shapely.geometry import Point
from dash import html

from layouts.layout_main import (
    # michelin_stars,
    # bib_gourmand,
    # green_star,
    color_map,
    condition_color_map,
)


def plot_geometry_outline(fig, geometry, line_width=0.2):
    """
    Draw the geographic boundary of a district or region on a Plotly map.

    Parameters:
        fig (go.Figure): The Plotly figure to which the outline will be added.
        geometry (shapely.geometry.Polygon or MultiPolygon):
            A geometry object representing the area to be outlined.
            Typically obtained via `geometry = geo_df['geometry'].iloc[0]`
        line_width (float): Width of the outline line in pixels.

    Notes:
        This function handles both single Polygon and MultiPolygon geometries, and plots their exterior boundaries
        using black lines on the map.
    """
    if geometry.geom_type == 'Polygon':
        x, y = geometry.exterior.xy
        fig.add_trace(
            go.Scattermap(
                lat=list(y),
                lon=list(x),
                mode='lines',
                line=dict(width=line_width, color='rgba(194, 40, 45, 0.8)'),
                hoverinfo='none',
                showlegend=False,
            )
        )
    elif geometry.geom_type == 'MultiPolygon':
        for poly in geometry.geoms:
            x, y = poly.exterior.xy
            fig.add_trace(
                go.Scattermap(
                    lat=list(y),
                    lon=list(x),
                    mode='lines',
                    line=dict(width=line_width, color='rgba(194, 40, 45, 0.8)'),
                    hoverinfo='none',
                    showlegend=False,
                )
            )


def plot_regional_outlines(region_df, region):
    """
    Plot the outlines of a selected region on a map.

    Args:
        region_df (GeoDataFrame): A GeoDataFrame containing geometries of regions with a 'region' column.
        region (str): The name of the region to plot.

    Returns:
        fig (plotly.graph_objs.Figure): A Plotly Figure object with the region outlines plotted.

    Raises:
        ValueError: If the specified region is not found in region_df.
    """
    fig = go.Figure(go.Scattermap())  # Initialize empty figure with mapbox

    # Filter the GeoDataFrame for the selected region
    filtered_region = region_df[region_df['region'] == region]

    if filtered_region.empty:
        # Handle case when the region is not found
        raise ValueError(f"Region '{region}' not found in the provided GeoDataFrame.")

    # Loop through the filtered GeoDataFrame
    for _, row in filtered_region.iterrows():
        specific_geometry = row['geometry']
        plot_geometry_outline(fig, specific_geometry, line_width=1)

    # Default to geometry centroid
    try:
        combined_geom = filtered_region.unary_union
        default_center_lat = combined_geom.centroid.y
        default_center_lon = combined_geom.centroid.x
    except Exception:
        default_center_lat = 22.3193
        default_center_lon = 114.1694

    # Hardcoded centers and zooms per HK region
    region_view = {
        'New Territories': {'lat': 22.445222, 'lon': 114.095495, 'zoom': 11},
        'Kowloon': {'lat': 22.321008, 'lon': 114.184753, 'zoom': 12.5},
        'Hong Kong Island': {'lat': 22.270787, 'lon': 114.176715, 'zoom': 12.5},
    }

    view = region_view.get(region)
    center_lat = view['lat'] if view else default_center_lat
    center_lon = view['lon'] if view else default_center_lon
    map_zoom = view['zoom'] if view else 11

    # Update map layout settings for Hong Kong regions
    fig.update_layout(
        map_style='carto-positron',
        map_zoom=map_zoom,
        map_center_lat=center_lat,
        map_center_lon=center_lon,
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        showlegend=False,
    )
    return fig


def plot_region_center_view(region_df, region):
    """
    Center and zoom the map to the centroid of a selected region without plotting boundaries.

    Args:
        region_df (GeoDataFrame): GeoDataFrame with 'region' and 'geometry' columns (Hong Kong districts).
        region (str): Region name to center on.

    Returns:
        fig (go.Figure): Plotly map figure centered on the region centroid.
    """
    # Filter to selected region
    filtered_region = region_df[region_df['region'] == region]
    if filtered_region.empty:
        # Fallback to default Hong Kong view
        return go.Figure(go.Scattermap()).update_layout(
            map_style='carto-positron',
            map_zoom=11,
            map_center_lat=22.3193,
            map_center_lon=114.1694,
            margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
            showlegend=False,
        )

    # Compute centroid of the combined geometry
    try:
        combined_geom = filtered_region.unary_union
        center_lat = combined_geom.centroid.y
        center_lon = combined_geom.centroid.x
    except Exception:
        center_lat, center_lon = 22.3193, 114.1694

    # Region-specific zoom defaults for Hong Kong
    region_view = {
        'New Territories': {'lat': 22.445222, 'lon': 114.095495, 'zoom': 11},
        'Kowloon': {'lat': 22.321008, 'lon': 114.184753, 'zoom': 12.5},
        'Hong Kong Island': {'lat': 22.270787, 'lon': 114.176715, 'zoom': 12.5},
    }

    view = region_view.get(region)
    zoom = view['zoom'] if view else 11
    # Prefer pre-defined center for better framing if available
    center_lat = view['lat'] if view else center_lat
    center_lon = view['lon'] if view else center_lon

    # Build a bare map centered on the region (no outlines)
    fig = go.Figure(go.Scattermap())
    fig.update_layout(
        map_style='carto-positron',
        map_zoom=zoom,
        map_center_lat=center_lat,
        map_center_lon=center_lon,
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
        showlegend=False,
    )

    return fig


def get_place_details(row):
    """
    Generate an HTML Div containing detailed information about a place.

    Parameters:
        row (pd.Series): Place information

    Returns:
        details_layout (html.Div): Place details card
    """
    try:
        name = row['name']
        description = row['description']
        # Prefer explicit dates if available; otherwise show nothing
        st_date = row.get('st_date', '')
        end_date = row.get('end_date', '')
        curr_condition = row.get('curr_condition', 'Unknown')
        address = row.get('address', '')
        location = row['location']
    except KeyError as e:
        raise KeyError(f'Missing expected key in row data: {e}')

    # Generate slug for gallery link
    from utils.markdownRenderer import generate_slug

    place_slug = generate_slug(name)

    # Simple border color for places (reuse existing color)
    border_color = '#640A64'

    location_info = html.Span(f'{location}', className='place-location')

    details_layout = html.Div(
        [
            html.Div(
                [
                    html.Div(
                        [html.Span(name, className='place-name')],
                        className='details-header',
                    ),
                    html.Div(
                        [
                            html.Span(
                                f'{str(st_date) if pd.notna(st_date) and st_date != "" else ""}'
                                f'{(" - " + str(end_date)) if pd.notna(end_date) and end_date != "" else ""}',
                                className='place-date',
                            )
                        ],
                        className='details-date',
                    ),
                    html.Div(
                        [html.Span(f'{description}', className='place-description')],
                        className='details-description',
                    ),
                    html.Div(
                        [
                            html.Span(
                                f'{curr_condition}',
                                className='place-condition',
                                style={'fontStyle': 'italic'},
                            )
                        ],
                        className='details-condition',
                    ),
                ],
                className='place-info',
            ),
            html.Div(
                [
                    html.Div(
                        [html.Span(f'{address}', className='place-address')],
                        className='details-address',
                    ),
                    html.Div([location_info], className='details-location'),
                ],
                className='address-info',
            ),
            html.Div(
                [
                    html.A(
                        'Read Full Article',
                        href=f'/gallery/{place_slug}',
                        className='place-link',
                        style={'display': 'block', 'marginTop': '10px'},
                    )
                ],
                className='details-link',
            ),
        ],
        className='place-details',
        style={'borderColor': border_color},
    )

    return details_layout


def generate_hover_text(row):
    """
    Generate HTML-formatted hover text for a place.

    Parameters:
        row (pd.Series or dict): A pandas Series or dictionary containing place information.

    Returns:
        hover_text (str): An HTML-formatted string for hover text.
    """
    try:
        name = row['name']
        location = row['location']
    except KeyError as e:
        raise KeyError(f'Missing expected key in row data: {e}')

    text_color = '#000'

    hover_text = (
        f'<span style="font-family: \'Libre Franklin\', sans-serif; font-size: 12px; color: {text_color};">'
        f"<span style='font-size: 14px;'>{name}</span><br>"
        f'{location}<br>'
    )
    return hover_text


def label_properties(star):
    """
    Return:
        display label
        marker size
        opacity
        colour
    for a given star rating.
    """
    if star == 0.25:
        return 'Selected', 9, 0.9, color_map[0.25]
    elif star == 0.5:
        return 'Bib', 11, 1, color_map[0.5]
    else:
        return '★' * int(star), 11, 1, color_map[star]


def add_star_trace(fig, subset, label_name, marker_size, marker_opacity, marker_color):
    """
    Add a scatter marker layer to a Plotly map for a specific group of places.

    Each trace corresponds to a single condition category and is styled with a consistent
    marker size, opacity, and colour. Hover text and clickData are included for interactivity.

    Parameters:
        fig (go.Figure): The Plotly figure to which the trace will be added.
        subset (pd.DataFrame): Subset of places sharing a specific condition.
        label_name (str): Label used in the legend and for identifying the trace.
        marker_size (int): Marker size for the place points.
        marker_opacity (float): Opacity level for the markers.
        marker_color (str): Colour to apply to the markers (hex or CSS format).
    """
    if subset.empty:
        return

    fig.add_trace(
        go.Scattermap(
            lat=subset['latitude'],
            lon=subset['longitude'],
            mode='markers',
            marker=dict(size=marker_size, color=marker_color, opacity=marker_opacity),
            text=subset['hover_text'],
            customdata=subset.index,
            hovertemplate='%{text}',
            name=label_name,
            showlegend=False,
            meta=subset.index,  # <- NEW: include explicitly for clickData
        )
    )


def plot_interactive_district(data_df, geo_df, district_code, zoom_data=None):
    """
    Plot an interactive map of a district, including place points.

    Args:
        data_df (pd.DataFrame): DataFrame containing place data with 'district_num', 'latitude', 'longitude', etc.
        geo_df (GeoDataFrame): GeoDataFrame containing geometries of districts with 'code' and 'geometry'.
        district_code (str or int): The code of the district to plot.
        zoom_data (dict): Dictionary containing zoom level and center information.

    Returns:
        fig (plotly.graph_objs.Figure): A Plotly Figure object with the district and places plotted.

    Raises:
        ValueError: If the specified district code is not found in geo_df.
    """
    # Initialize zoom_data if not provided
    if zoom_data is None:
        zoom_data = {}

    # Get the zoom and center from zoom_data or fallback to district defaults
    zoom = zoom_data.get('zoom', 14.5)
    center_lat = zoom_data.get('center', {}).get('lat', None)
    center_lon = zoom_data.get('center', {}).get('lon', None)

    # Initialize a blank figure
    fig = go.Figure()
    fig.update_layout(autosize=True)

    # Get the specific geometry for the district
    filtered_geo = geo_df[geo_df['code'] == str(district_code)]
    if filtered_geo.empty:
        raise ValueError(f"District code '{district_code}' not found in the provided GeoDataFrame.")

    specific_geometry = filtered_geo['geometry'].iloc[0]
    # Plot district boundaries
    plot_geometry_outline(fig, specific_geometry, line_width=1)

    # Get all places in the district
    dept_data = data_df[data_df['district_num'] == str(district_code)].copy()

    # If dept_data is not empty, add place points
    if not dept_data.empty:
        dept_data['color'] = dept_data['curr_condition'].map(condition_color_map).fillna('#FFB84D')
        dept_data['hover_text'] = dept_data.apply(generate_hover_text, axis=1)

        # Plot each group by condition
        for condition in dept_data['curr_condition'].unique():
            subset = dept_data[dept_data['curr_condition'] == condition]
            if subset.empty:
                continue

            marker_color = condition_color_map.get(condition, '#FFB84D')
            marker_size = 11
            marker_opacity = 1

            add_star_trace(
                fig,
                subset,
                condition,
                marker_size,
                marker_opacity,
                marker_color,
            )

        # Calculate the center if zoom_data doesn't have it
        if center_lat is None or center_lon is None:
            map_center_lat = dept_data['latitude'].mean()
            map_center_lon = dept_data['longitude'].mean()
        else:
            map_center_lat = center_lat
            map_center_lon = center_lon
    else:
        # If no place data, center based on geometry's centroid
        centroid = specific_geometry.centroid
        map_center_lat = centroid.y
        map_center_lon = centroid.x

    # Update the layout with the correct zoom and center
    fig.update_layout(
        font=dict(family='Courier New, monospace', size=18, color='white'),
        width=800,
        height=600,
        hovermode='closest',
        hoverdistance=10,
        map_style='carto-positron',
        map_zoom=zoom,  # Zoom level from zoom_data or default
        map_center_lat=map_center_lat,
        map_center_lon=map_center_lon,
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},  # Remove margins
    )
    return fig


def default_map_figure():
    """
    Generate a default map figure centered on Hong Kong.

    Returns:
        - fig (plotly.graph_objs.Figure): A Plotly Figure object with default map settings.
    """
    return go.Figure(go.Scattermap()).update_layout(
        font=dict(family='Courier New, monospace', size=18, color='white'),
        width=800,
        height=600,
        map_style='carto-positron',
        map_zoom=11,
        map_center_lat=22.3193,
        map_center_lon=114.1694,
        margin={'r': 0, 't': 0, 'l': 0, 'b': 0},
    )
