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

class LA:

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


class NC:

        def __init__(self, nc_file='../data/neighborhoods/Neighborhood_Councils_(Certified)_cleaned.shp'):

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

            self.map_display = LA().map_display
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
        
        self.choropleth_layer = self._choropleth_layer()
        self.hover_control = self._hover_control()
        #self._add_hover_message()

        self.map_display = LA().map_display
        self.map_display.add_layer(self.choropleth_layer)
        self.map_display.add_control(self.hover_control)


    def _choropleth_layer(self):
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
            colormap=linear.YlGn_05,#PuRd_09,#Reds_09,#YlOrRd_09, #linear.Blues_05,
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

        self.choropleth_layer.on_hover(update_html)

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

    def __init__(self, nc_file='../data/neighborhoods/Neighborhood_Councils_(Certified)_cleaned.shp'):

        self.neighborhoods_gdf = gpd.read_file(nc_file)


    def nc_poly(self, nc_id):

        self.nc_gfd = self.neighborhoods_gdf.query(f"NC_ID == @nc_id").reset_index()

        return self.nc_gfd.iloc[0]['geometry']
