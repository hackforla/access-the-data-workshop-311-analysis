"""Data abstractions for geoprocessing.

   01/17/2022 - For starters includes initial stub for KG.
"""

from collections import namedtuple

import json

import pandas as pd
import geopandas as gpd

from ipywidgets import Layout, HTML, Text, interact, Output, HBox, interactive

from ipyleaflet import (Map, Rectangle, GeoJSON, FullScreenControl,
                        MarkerCluster, GeoData, LayersControl,
                        LayerGroup, Marker, WidgetControl,
                        CircleMarker, LegendControl, Choropleth,
                        TileLayer, basemaps, basemap_to_tiles)

from branca.colormap import linear

from utils import read_ncs

NCGroup = namedtuple("NCGroup", "color_code nc_list")

empowerla_service_regions = {
    1: NCGroup("#00BFFF",
               [4, 114, 99, 113, 118, 120, 124, 111]),
    2: NCGroup("#FFFF00",
               [5, 101, 7, 9, 10, 8, 6, 112, 100]),
    3: NCGroup("#EE82EE",
               [11, 13, 14, 15, 19, 16, 17, 18]),
    4: NCGroup("#32CD32",
               [20, 21, 22, 23, 24, 25, 26, 27, 28]),
    5: NCGroup("#DC143C",
               [64, 127, 63, 66, 62, 61, 115, 67, 68, 70, 71]),
    6: NCGroup("#CD853F",
               [29, 30, 32, 33, 34, 58, 119, 60]),
    7: NCGroup("#87CEEB",
               [36, 37, 38, 53, 44, 43]),
    8: NCGroup("#FF8C00",
               [39, 40, 41, 42, 102, 47, 48, 50]),
    9: NCGroup("#FF00FF",
               [104, 55, 76, 52, 121, 128, 54, 97]),
    10: NCGroup("#800080",
                [73, 75, 79, 80, 81, 77, 74]),
    11: NCGroup("#7FFFD4",
                [78, 109, 125, 110, 86, 84, 87, 88]),
    12: NCGroup("#DB7093",
                [90, 91, 92, 93, 94, 95, 96])
}

nc_map = []

class LAMap:

    def __init__(self):
        self.map_display = self._build_foundation()

    def _build_foundation(self):

        imagery = basemap_to_tiles(basemaps.Esri.WorldImagery)
        imagery.base = True
        osm = basemap_to_tiles(basemaps.OpenStreetMap.Mapnik)
        osm.base = True
        google_map = TileLayer(
            url="https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}",
            attribution="Google",
            name="Google Maps",
        )
        google_map.base = True

        google_satellite = TileLayer(
            url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
            attribution="Google",
            name="Google Satellite"
        )
        google_satellite.base = True

        map_display = Map(center=(34.05, -118.25), zoom=12,
                          layers=[google_satellite, google_map,imagery, osm],
                          layout=Layout(height="700px"),
                          scroll_wheel_zoom=True)

        map_display.add_control(LayersControl())

        map_display.add_control(FullScreenControl())
        
        #map_display += nc_layer
        return map_display

neighborhood_default = "/home/mcmorgan/SOCALKG/data/LA_city/neighborhoods/Neighborhood_Councils_(Certified)_cleaned.shp"
class NCMap:

        def __init__(self, nc_file=neighborhood_default):

            self.neighborhoods_gdf = gpd.read_file(nc_file)
            self.nc_layer = GeoData(geo_dataframe = self.neighborhoods_gdf,
                                    style={'color': 'black',
                                           'fillColor': '#3366cc',
                                           'opacity':0.8,
                                           'weight':1.9,
                                           'dashArray':'5',
                                           'fillOpacity':0.2},
                                    hover_style={'fillColor': 'red' ,
                                                 'fillOpacity': 0.2},
                                    name = 'Neighborhood Council')

            self.map_display = LAMap().map_display
            self.map_display.add_control(self.nc_layer)
            self.map_display.add_layer(self._build_overlay())

        def _build_overlay(self):

            a_geojson = json.loads(self.neighborhoods_gdf.to_json())

            def region_color(feature):
                return {
                    'color': 'black',
                    'fillColor': feature['properties']['color_code']
                }

            geo_json = GeoJSON(
                data=a_geojson,
                style={
                    'opacity': 1, 'dashArray': '9', 'fillOpacity': 0.6, 'weight': 1
                },
                hover_style={
                    'color': 'white', 'dashArray': '0', 'fillOpacity': 0.5
                },
                style_callback=region_color,
                name='Regions'
            )

            #map_display.add_layer(geo_json)

            html = HTML('''Hover over a district''')
            html.layout.margin = '0px 20px 20px 20 px'
            control = WidgetControl(widget=html, position='bottomright')

            def update_html(feature, **kwargs):
                html.value = '''<h3><b>NC: {}</b></h3>
                <h4>NC ID: {}</h4>
                <h4>region id: {}</h4>'''.format(feature['properties']['NAME'], 
                                                     feature['properties']['NC_ID'],
                                                     feature['properties']['region_id'])
    
            #map_display.add_control(control)  # does += work for this?

            geo_json.on_hover(update_html)

            return geo_json

class NCChoropleth:

    def __init__(self, gdf):
        self.neighborhoods_gdf = read_ncs()
        self._counts_df = gdf['nc'].value_counts().to_frame().reset_index().rename(columns={'index': 'nc_id', 'nc': 'count'})
        self._merged_gdf = pd.merge(self.neighborhoods_gdf, self._counts_df, how="left", on=["nc_id"])
        
        self._overlay = self._choropleth_overlay()
        self._hover = self._hover_control()
        self._add_hover_message()

        self.map_display = LAMap().map_display
        self.map_display.add_layer(self._overlay)
        self.map_display.add_control(self._hover)


    def _choropleth_overlay(self):
        """
        This always scares me.  I'm using the instance variables.
        """
        a_geojson = json.loads(self._merged_gdf.to_json())

        count_density = dict(zip(self._merged_gdf['name'].tolist(), self._merged_gdf['count'].tolist()))
        for i in a_geojson['features']:
            i['id'] = i['properties']['name']

        layer = Choropleth(
            geo_data=a_geojson,
            choro_data=count_density,
            colormap=linear.YlOrRd_09, #linear.Blues_05,
            style={'fillOpacity': 1.0, "color":"black"},
            name="Counts")

        return layer

    def _hover_control(self):
        
        html = HTML('''Hover over a district''')
        html.layout.margin = '0px 20px 20px 20 px'
        control = WidgetControl(widget=html, position='bottomright')

        def update_html(feature, **kwargs):
            html.value = '''<h3><b>NC: {}</b></h3>
            <h4><b>Region: {}</b></h4>
            <h4>Count: {}'''.format(feature['properties']['name'],
                                    feature['properties']['service_region'],
                                    feature['properties']['count'])

        #layer.on_hover(update_html)

        return control

    def _add_hover_message(self):
        
        def update_html(feature, **kwargs):
            self.control.widget.value = '''<h3><b>NC: {}</b></h3>
            <h4><b>Region: {}</b></h4>
            <h4>Count: {}'''.format(feature['properties']['name'],
                                    feature['properties']['service_region'],
                                    feature['properties']['count'])

        self._overlay.on_hover(update_html)

        
class KG:

    def __init__(self, nc_file=neighborhood_default):

        self.neighborhoods_gdf = gpd.read_file(nc_file)


    def nc_poly(self, nc_id):

        self.nc_gfd = self.neighborhoods_gdf.query(f"NC_ID == @nc_id").reset_index()

        return self.nc_gfd.iloc[0]['geometry']

        
