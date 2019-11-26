import geopandas as gpd
import pandas as pd
import numpy as np
import json
from bokeh.io import output_notebook, show, output_file
from bokeh.plotting import figure
from bokeh.models import GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.palettes import brewer, all_palettes
from bokeh.io import curdoc, output_notebook
from bokeh.models import Slider, HoverTool
from bokeh.layouts import widgetbox, row, column

#read the csv file
df = pd.read_csv("energy-use-per-capita.csv", names = ['entity', 'code', 'year', 'kg_of_oil_equivalent_per_capita'], skiprows = 1)
#read the shapefile
shapefile = "ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp"
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']

#drop the column for antarctica
gdf = gdf.drop(gdf.index[159])


import numpy as np
df_2015 = df[df['year'] == 2015]
#Perform left merge to preserve every row in gdf.
merged = gdf.merge(df_2015, left_on = 'country_code', right_on = 'code', how = 'left')
#Replace NaN values to string 'No data'.
merged['code'].fillna('No data', inplace = True)
merged['entity'].fillna('No data', inplace = True)
merged['year'].fillna('No data', inplace = True)
merged['kg_of_oil_equivalent_per_capita'].fillna('No data', inplace = True)

import json
#Read data to json.
merged_json = json.loads(merged.to_json())
#Convert to String like object.
json_data = json.dumps(merged_json)

def json_data(selectedYear):
    yr = selectedYear
    df_yr = df[df['year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country_code', right_on = 'code', how = 'left')
    merged['code'].fillna('No data', inplace = True)
    merged['entity'].fillna('No data', inplace = True)
    merged['year'].fillna('No data', inplace = True)
    merged['kg_of_oil_equivalent_per_capita'].fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data
  
def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Energy usage per capita, %d' %yr

#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(1990))
#Define a sequential multi-hue color palette.
palette = all_palettes['PuOr'][9]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0, high = 100000, nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
tick_labels = {'0': '0kWh', '1000': '1000kWh', '2500':'2500kWh', '5000':'5000kWh', '10000':'10000kWh', '25000':'25000kWh', '50000':'50000kWh','75000':'75000kWh', '100000': '>100000kWh'}
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('energy usage', '@kg_of_oil_equivalent_per_capita')])
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Energy usage per capita, 2015', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'kg_of_oil_equivalent_per_capita', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')

# Make a slider object: slider 
slider = Slider(title = 'Year',start = 1960, end = 2015, step = 1, value = 2015)
slider.on_change('value', update_plot)

# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)

show(layout, notebook_handle = True)