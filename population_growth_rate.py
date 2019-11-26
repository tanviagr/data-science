import geopandas as gpd
import pandas as pd
import json
shapefile = 'ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
gdf=gdf.drop(gdf.index[159])
df='population.csv'
df=pd.read_csv(df,names=['entity','code','year','estimates','population_growth_rate'],skiprows=1)

merged = gdf.merge(df,left_on='country_code',right_on='code',how='left')
merged_json = json.loads(merged.to_json())
json_data = json.dumps(merged_json)

from bokeh.io import curdoc, output_notebook,show
from bokeh.models import Slider, HoverTool,GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure
from bokeh.palettes import brewer    
def json_data(selectedYear):
    yr = selectedYear
    df_yr = df[df['year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country_code', right_on ='code', how = 'left')
    merged['code'].fillna('No data', inplace = True)
    merged['entity'].fillna('No data', inplace = True)
    merged['year'].fillna('No data', inplace = True)
    merged['population_growth_rate'].fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data
#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(2016))
#Define a sequential multi-hue color palette.
palette = brewer['YlGnBu'][8]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 0.0, high = 3.0, nan_color = '#d9d9d9')
#Define custom tick labels for color bar.
tick_labels = {'-0.06': '0.1%', '-0.04': '0.3%', '-0.02':'0.5%', '0.0':'0.7%', '1.0':'0.9%', '2.0':'1.1%', '3.0':'1.3%','4.0':'1.5%', '5.0': '>2.0%'}
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('growth_rate', '@population_growth_rate')])
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Population growth over the years', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'population_growth_rate', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')
# Define the callback function: update_plot
def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Population growth over the year, %d' %yr
    
# Make a slider object: slider 
slider = Slider(title = 'Year',start = 1975, end = 2015, step = 1, value = 2015)
slider.on_change('value', update_plot)
# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)
#Display plot
show(layout)