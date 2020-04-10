import plotly.graph_objects as go, plotly.figure_factory as ff
import pandas as pd
import plotly
import numpy as np
from PIL import Image

import plotly.express as px



url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-states.csv'

covid = pd.read_csv(url, error_bad_lines=False)
census = pd.read_csv('census_counties.csv', encoding = 'ISO-8859-1')
states = census.groupby(['STATE', 'REGION']).sum()
states.reset_index(level=1, inplace=True)

print(states.head())
# census cols:
# county = fips code, popestimate2019

covid['datetime'] = pd.to_datetime(covid['date'])

# datetimeindex makes convenient manipulations
#date = pd.DatetimeIndex(covid['date'])

# compute df2: totals by day
#t = pd.Timedelta(7, unit='d')
def rolling(x, t):
    return x.apply(lambda y: x.loc[x['datetime'].between(y['datetime'] - t,
                                                     y['datetime'],
                                                     inclusive=True),'cases'].min(),axis=1)
def l7deaths(x, t):
    return x.apply(lambda y: x.loc[x['datetime'].between(y['datetime'] - t,
                                                     y['datetime'],
                                                     inclusive=True),'deaths'].min(),axis=1)
def checker(x, t):
    return x.apply(lambda y: x.loc[x['datetime'].between(y['datetime'] - t,
                                                     y['datetime'],
                                                     inclusive=True),'state'].count(),axis=1)

covid['lastweek'] = covid.groupby('state', group_keys=False).apply(rolling, pd.Timedelta(2, unit='d'))
covid['lastweekdeaths'] = covid.groupby('state', group_keys=False).apply(l7deaths, pd.Timedelta(2, unit='d'))
covid['checker'] = covid.groupby('state', group_keys=False).apply(checker, pd.Timedelta(2, unit='d'))
covid['New Cases Last 3 Days'] = covid['cases'] - covid['lastweek']
covid['New Deaths Last 3 Days'] = covid['deaths'] - covid['lastweekdeaths']
covid['Total Cases 3 Days Ago'] = covid['lastweek']
covid['Total Cases'] = covid['cases']
#covid['region']

# compute df3: totals by last seven days


covid_states = pd.merge(covid,
                  states,
                  left_on='fips',
                  right_on='STATE',
                  how='inner')

covid_states['Region'] = covid_states['REGION'].apply(lambda x: 'West' if x == 4 else 'South' if x == 3
                                               else 'Midwest' if x == 2 else 'Northeast')


showstates = ['New York', 'California', 'Washington', 'Florida', 'New Jersey', 'Michigan', 'Texas', 'Louisiana']
covid_states['Label'] = covid_states['state'].apply(lambda x: x if x in showstates else '')
covid_states['Opacity'] = covid_states['state'].apply(lambda x: 1 if x in showstates else 0.3)

fig = px.scatter(
        covid_states[covid_states['date']>='2020-03-01'],
        x="Total Cases 3 Days Ago",
        y="New Cases Last 3 Days",
        animation_frame="date",
        animation_group="state",
        size="POPESTIMATE2019",
        color="Region",
        hover_name="state",
        text= 'Label',
        log_x=True,
        log_y=True,
        size_max=25,
        range_x=[1,1000000],
        range_y=[1,1000000]
)
fig.update_traces(
    textposition='bottom right'
)

fig.add_shape(
        # Line Diagonal
            type="line",
            x0=2,
            y0=1.5,
            x1=500000,
            y1=300000,
            line=dict(
                color="darkred",
                width=3,
                dash="dot",
            )
),

fig.update_layout(
    title_text='US COVID Growth by State Over Time<br>New Cases Last 3 Days vs Case Count 3 Days Ago',
    annotations=[
        go.layout.Annotation(
            showarrow=False,
            text='by Nick DeFrancis',
            xanchor='right',
            x=1,
            xshift=0,
            yanchor='top',
            y=-0.08,
            font=dict(
                size=12
            )
        )
    ]
)

fig.add_trace(go.Scatter(
    x=[400000],
    y=[120000],
    text=["Early Trendline"],
    mode="text",
    showlegend=False

))
fig.show()
plotly.offline.plot(fig, filename='state_map_animated/index.html')



