
import plotly.graph_objects as go
import pandas as pd
import sys, datetime

#where is the data source file. Contains 'name' and 'data'
data_source_file=sys.argv[1]
#Getting the start date like 2020-03-28
if len(sys.argv) > 2:
    start_date = sys.argv[2]

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
    appendFrame={'name' : count, 'layout' : {'title_text':convertedDate.strftime('%Y-%m-%d'), 'title_x':0.5},
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

# fig=go.Figure()
# animals=['giraffes', 'orangutans', 'monkeys']
# fig.add_trace(go.Bar
#                 (x=animals, 
#                  y=[20, 14, 23]
#                  )
#                 )


fig.show()


