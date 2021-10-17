"""An amended implementation of https://examples.pyviz.org/nyc_buildings/nyc_buildings.html, applied to OSM buildings data.
"""

import os
import osmnx as ox
import geopandas as gpd
import spatialpandas
import spatialpandas.io
from cartopy import crs as ccrs
import geoviews as gv
import datashader as ds
from holoviews.operation.datashader import (
    datashade, inspect_polygons
)
from bokeh.models import HoverTool
from colormap import rgb2hex
import colorcet as cc

gv.extension('bokeh')


# Manual inputs
gpkg_path = 'data.gpkg'
roi_layer = 'study_area'
parq_path = 'buildings.parq'


"""To be considerate of OSM's bandwidth, when we run the script for the first time
we'll write whatever we retrieve to file, to then be retrieved in case the script is re-executed, e.g. when the cloud instance restarts.
"""

if os.path.exists(parq_path):
    
    spd_gdf = spatialpandas.io.read_parquet(parq_path)

    cats = list(spd_gdf.amenity.value_counts().iloc[:10].index.values)

else:
        
    roi = gpd.read_file(gpkg_path, layer=roi_layer)

    # get all the buildings within the ROI
    gpd_gdf = ox.geometries_from_polygon(roi.geometry[0], {'building': True})

    # OSM features with building=True occasionally include point features as well
    # Let's filter those out
    gpd_gdf = gpd_gdf[gpd_gdf.geom_type == 'Polygon'].to_crs(epsg=3857)

    # We're now converting the GeoPandas GDF to a SpatialPandas GDF
    spd_gdf = spatialpandas.GeoDataFrame(gpd_gdf)
    
    """
    OSM's 'nodes' column is a list. Apart from causing trouble when saving to GPKG or SHP, leaving the datatype as is
    also throws a non-obvious value error when using datashader ("ValueError: The truth value of an array with more than one element is ambiguous. Use a.any() or a.all()").
    Therefore we're converting the nodes column to a string, removing the square brackets at either end
    """

    spd_gdf['nodes'] = str(spd_gdf['nodes'])[1:-1]

    # The default no data value for OSM is 'NaN'
    # Let's rename this to make it more obvious to new user
    spd_gdf['amenity'] = spd_gdf.amenity.fillna('No data')
    spd_gdf['name'] = spd_gdf.name.fillna('No data')
    spd_gdf['description'] = spd_gdf.description.fillna('No data')
    
    # Here select the 9 most frequent amentiy categories in the dataset,
    # define all others as 'Other' and create a new category list
    # including 'Other'
    cats = list(spd_gdf.amenity.value_counts().iloc[:9].index.values)
    spd_gdf['amenity'].loc[~spd_gdf['amenity'].isin(cats)] = 'Other'
    cats = list(spd_gdf.amenity.value_counts().iloc[:10].index.values)

    # as we'll be applying datashader to the 'amenity' column we'll have to give it the 'category' type
    spd_gdf['amenity'] = spd_gdf['amenity'].astype('category')

    # then we save the to fastparquet file for future use
    spd_gdf.to_parquet(parq_path)

### Legend and Symbology

"""
We select a categorical color palette suitable for lighter backgrounds,
here with a maximum lightness ("maxl") of 70.
see: https://colorcet.holoviz.org/user_guide/Categorical.html
"""
colors = cc.glasbey_bw_minc_20_maxl_70

"""
create a dict where each category key is assigned a value composed of a three element tuple of integers representing a color in RGB format.
This I then had to convert to hex as Bokeh was throwing errors otherwise.
"""
color_key = {cat: rgb2hex(*tuple(int(e*255.) for e in colors[i])) for i, cat in enumerate(cats)}

# This is a temporary legend workaround
legend = gv.NdOverlay({k: gv.Points([0,0], label=str(k)).opts(
                                        color=v, apply_ranges=False) 
                        for k, v in color_key.items()}, 'amenity')

### GeoViews + Datashader + Bokeh

polys = gv.Polygons(spd_gdf, crs=ccrs.GOOGLE_MERCATOR, vdims='amenity')

# the content of these columns will be seen via the hover tool
tooltips = [('Amenity type', '@amenity'),
            ('Description', '@description'),
            ('Name','@name')]

hover_tool = HoverTool(tooltips=tooltips)

shaded = datashade(polys, color_key=color_key, aggregator=ds.by('amenity', ds.any()))
hover = inspect_polygons(shaded).opts(fill_color='yellow', tools=[hover_tool])

tiles = gv.tile_sources.StamenWatercolor().opts(xaxis=None, yaxis=None,active_tools=['wheel_zoom'], min_height=700, responsive=True)

layout = tiles * shaded * hover * legend

### Bokeh Server

doc = gv.renderer('bokeh').server_doc(layout)
doc.title = 'GeoViews + Datashader + Bokeh App'