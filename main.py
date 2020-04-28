# [START gae_python37_app]
from flask import Flask
import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go
from dash.dependencies import Input, Output
import os
import sys, datetime


# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
server = Flask(__name__)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app = dash.Dash(__name__, external_stylesheets=external_stylesheets, server = server)

#external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, server = server) #external_stylesheets=external_stylesheets, 


#where is the data source file. Contains 'name' and 'data'
#data_source_file=sys.argv[1]
data_source_file = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'
#Getting the start date like 2020-03-28
#if len(sys.argv) > 2:
#    start_date = sys.argv[2]
start_date = '2020-03-15'

#Read the Lon, Lat of each state
df = pd.read_csv('./us_state_lonlat.csv')
#read the data set to be displayed on the map
df_data = pd.read_csv(data_source_file)
df.head()
state_df=df

# Let's combine the data source into the  geolocation source
# https://github.com/nytimes/covid-19-data/blob/master/us-states.csv
df['text'] = df['name'] # + df['data'].astype(str)
df = df.set_index('name')
df_data =df_data.set_index('state')

#Turn this on if bubbles are displayed based on categories and size.
#limits = [(0,2),(3,10),(11,20),(21,50),(50,3000)]
limits = [(0,3000)]
colors = ["royalblue","crimson","lightseagreen","orange","lightgrey"]
cities = []
scale = 10 #the scaled used to resize the bubble



# make figure
fig_dict = {
    "data": [],
    "layout": {},
    "frames": []
}
for i in range(len(limits)):
    lim = limits[i]
    # Breaking the list which is based in the order by population. 
    df_sub = df[lim[0]:lim[1]]
fig_dict = dict(
    layout = dict(
        title_text = '',
        showlegend = True,
        height=700,
        geo = dict(
            scope = 'usa',
            landcolor = 'lightblue',#'rgb(217, 217, 217)',
        ),
        updatemenus=[dict(
            type="buttons",
            buttons=[dict(label="Play",
                          method="animate",
                          args=[None])])]
    ),
    data = [
        {'type': 'scattergeo', 
        'locationmode' : 'USA-states',
        },
#    'name' : '{0} - {1}'.format(lim[0],lim[1])
    ],

    frames = []
)

state_df = state_df.set_index('name')
data_source = pd.read_csv(data_source_file)

count=0
for i in pd.date_range(start_date, datetime.date.today()-datetime.timedelta(days=1), freq='1D'):
    count=count+1    

    df_data2=data_source
    df_data2=df_data2.set_index('state')

    df_data2['date'] = pd.to_datetime(df_data2['date']) 
    mask=(df_data2['date'] == i)
    df_data2 = df_data2.loc[mask]
    # Let's combine the data source into the  geolocation source
    # https://github.com/nytimes/covid-19-data/blob/master/us-states.csv
    df['data']=df_data2['cases']
    df=df.fillna(axis=1, value='0')
    convertedDate = i.to_pydatetime()
    appendFrame={'name' : count, 'layout' : {'title_text':convertedDate.strftime('%Y-%m-%d'), 'title_x':0.5,'height':700},
         'data': [
             {'type': 'scattergeo', 
              'locationmode' : 'USA-states',
              'lon' : df['lon']-0.5,
              'lat' : df['lat']-0.5,
              'text' : df['text']+' ' +df['data'].astype(str),
              'marker' : {
                'size' : df['data'].astype(int)/scale, #10,  #df_sub['pop']/scale,
                'color' : 'orange',
                'line_color' : 'rgb(40,40,40)',
                'line_width': 0.5,
                'sizemode' : 'area'
            }
            }
            ]
        }

    fig_dict["frames"].append(appendFrame)

fig = go.Figure(fig_dict)

fig.update_layout(
    title={
        'y':0.9,
        'x':0.5,
        'xanchor': 'center',
        'yanchor': 'top',
        'font':dict(
            family="Courier New, monospace",
            size=40,
            color="#7f7f7f"
    )      }
        )

#Make the date dynamically as the time serious
fig.add_trace(go.Scattergeo(
        lon = df['lon'],
        lat = df['lat'],
        text = df['code'],
        mode = 'text',
        textfont=dict(
           family="sans serif",
           color="white"
        ),
        showlegend = False,
    ))


app.layout  = html.Div([
    dcc.Graph(id='graph', figure=fig)
])


if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run_server(port=8080, debug=True)
# [END gae_python37_app]
