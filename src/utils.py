"""Utility functions:
  read_new311_shape - read geo type file and rename/process column names
  read_ncs - read nc polygon shape and rename
"""

import geopandas as gpd
import pandas as pd


def read_new311_shape(file_name='../data/311/new311-geo.shp'):

    gdf = gpd.read_file(file_name)

    gdf['created_dt'] = pd.to_datetime(gdf['created_dt'])
    gdf['service_dt'] = pd.to_datetime(gdf['service_dt'])
    gdf['closed_dt'] = pd.to_datetime(gdf['closed_dt'])
    gdf['updated_dt'] = pd.to_datetime(gdf['updated_dt'])

    gdf['nc'] = gdf['nc'].astype('Int64')
    gdf['cd'] = gdf['cd'].astype('Int64')
    if 'region_id' in gdf.columns:
        gdf['region_id'] = gdf['region_id'].astype('Int64')
    gdf = gdf.rename(columns={'days_to_se': 'days_to_service',
                              'days_to_cl': 'days_to_close',
                              'days_to_up': 'days_to_update',
                              'request_ty': 'request_type',
                              'service_re': 'service_region',
                              'marker_col': 'marker_color',
                              'popup_mess': 'popup_message'})

    return gdf

# using computation from 311-ncviz.ipynb

marker_color_map = {'Bulky Items': '#267370',
                    'Graffiti Removal': '#8B508B',
                    'Metal/Household Appliances': '#EDAD08',
                    'Illegal Dumping Pickup': '#1D6996',
                    'Homeless Encampment': '#11975F',
                    'Electronic Waste': '#E17C05',
                    'Other': '#685DB1',
                    'Dead Animal Removal': '#AE3D51',
                    'Single Streetlight Issue': '#79B74E',
                    'Multiple Streetlight Issue': '#BF82BA',
                    'Report Water Waste': '#D05F4E',
                    'Feedback': '#33BBEE'
}

def dt_to_object(gdf):
    
    gdf['created_dt'] = gdf['created_dt'].astype(str)

    gdf['service_dt'] = gdf['service_dt'].astype(str)
    gdf['closed_dt'] = gdf['closed_dt'].astype(str)
    gdf['updated_dt'] = gdf['updated_dt'].astype(str)

    return gdf

def read_ncs(ncs_file='../data/neighborhoods/Neighborhood_Councils_(Certified)_cleaned.shp'):

    ncs_gdf = gpd.read_file(ncs_file)

    ncs_gdf.rename(columns={'NAME': 'name',
                            'NC_ID': 'nc_id',
                            'SERVICE_RE': 'service_region'},
                   inplace=True)

    return ncs_gdf
