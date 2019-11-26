import geopandas as gpd
import pandas as pd
import json
shapefile = 'ne_110m_admin_0_countries/ne_110m_admin_0_countries.shp'
gdf = gpd.read_file(shapefile)[['ADMIN', 'ADM0_A3', 'geometry']]
gdf.columns = ['country', 'country_code', 'geometry']
gdf=gdf.drop(gdf.index[159])
df='life-expectancy.csv'
df=pd.read_csv(df,names=['entity','code','year','life_expectancy'],skiprows=1)

#Filter data for year 2016.
df_2016 = df[df['year'] == 2016]
#Merge dataframes gdf and df_2016.
merged = gdf.merge(df_2016, left_on = 'country_code', right_on = 'code', how = 'left')
merged['code'].fillna('No data', inplace = True)
merged['entity'].fillna('No data', inplace = True)
merged['year'].fillna('No data', inplace = True)
merged['life_expectancy'].fillna('No data', inplace = True)

merged_json = json.loads(merged.to_json())
#Convert to String like object.
json_data = json.dumps(merged_json)

from bokeh.io import curdoc, output_notebook,show
from bokeh.models import Slider, HoverTool,GeoJSONDataSource, LinearColorMapper, ColorBar
from bokeh.layouts import widgetbox, row, column
from bokeh.plotting import figure
from bokeh.palettes import brewer,all_palettes    
def json_data(selectedYear):
    yr = selectedYear
    df_yr = df[df['year'] == yr]
    merged = gdf.merge(df_yr, left_on = 'country_code', right_on = 'code', how = 'left')
    merged['code'].fillna('No data', inplace = True)
    merged['entity'].fillna('No data', inplace = True)
    merged['year'].fillna('No data', inplace = True)
    merged['life_expectancy'].fillna('No data', inplace = True)
    merged_json = json.loads(merged.to_json())
    json_data = json.dumps(merged_json)
    return json_data
#Input GeoJSON source that contains features for plotting.
geosource = GeoJSONDataSource(geojson = json_data(2016))
#Define a sequential multi-hue color palette.
palette = all_palettes['PuOr'][10]
#Reverse color order so that dark blue is highest obesity.
palette = palette[::-1]
#Instantiate LinearColorMapper that linearly maps numbers in a range, into a sequence of colors. Input nan_color.
color_mapper = LinearColorMapper(palette = palette, low = 20, high = 85, nan_color = '#A9A9A9')
#Define custom tick labels for color bar.
tick_labels = {'20': '20%','30':'30%','40': '40%', '50':'50%', '55' : '55%', '60':'60%', '65':'65%', '70':'70%', '75':'75%','80':'80%', '85': '>85%'}
#Define custom tick labels for color bar.
#Add hover tool
hover = HoverTool(tooltips = [ ('Country/region','@country'),('Life Expectancy', '@life_expectancy')])
#Create color bar. 
color_bar = ColorBar(color_mapper=color_mapper, label_standoff=8,width = 500, height = 20,
                     border_line_color=None,location = (0,0), orientation = 'horizontal', major_label_overrides = tick_labels)
#Create figure object.
p = figure(title = 'Life Expectancy, 2016', plot_height = 600 , plot_width = 950, toolbar_location = None, tools = [hover])
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
#Add patch renderer to figure. 
p.patches('xs','ys', source = geosource,fill_color = {'field' :'life_expectancy', 'transform' : color_mapper},
          line_color = 'black', line_width = 0.25, fill_alpha = 1)
#Specify layout
p.add_layout(color_bar, 'below')
# Define the callback function: update_plot
def update_plot(attr, old, new):
    yr = slider.value
    new_data = json_data(yr)
    geosource.geojson = new_data
    p.title.text = 'Life Expectancy, %d' %yr
    
# Make a slider object: slider 
slider = Slider(title = 'Year',start = 1975, end = 2016, step = 1, value = 2016)
slider.on_change('value', update_plot)
# Make a column layout of widgetbox(slider) and plot, and add it to the current document
layout = column(p,widgetbox(slider))
curdoc().add_root(layout)
#Display plot
show(layout)