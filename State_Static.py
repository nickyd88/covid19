
import plotly.graph_objects as go, plotly.figure_factory as ff
import pandas as pd
import plotly
import numpy as np
from PIL import Image
import math

import plotly.express as px

globaldata = 'https://github.com/CSSEGISandData/COVID-19/blob/master/csse_covid_19_data/csse_covid_19_daily_reports/01-27-2020.csv'

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
covid['Cases 1 Week Ago'] = covid['lastweek']
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
covid_states['Label'] = covid_states['state'].apply(lambda x: str(x) if x in showstates else '')
covid_states['Opacity'] = covid_states['state'].apply(lambda x: 1 if x in showstates else 0.3)
covid_states['Cases per 1M'] = covid_states['cases']*1000000.0/covid_states['POPESTIMATE2019']
covid_states['Last 3 Days Deaths per 1M'] = covid_states['New Deaths Last 3 Days']*1000000.0/covid_states['POPESTIMATE2019']
covid_states['Cases per 1M 3 Days Ago'] = covid_states['lastweek']*1000000.0/covid_states['POPESTIMATE2019']
covid_states['New Cases per 1M Last 3 Days'] = covid_states['New Cases Last 3 Days']*1000000.0/covid_states['POPESTIMATE2019']


state_list = np.unique(covid_states['state'])

fig = go.Figure()


xvar = 'Cases per 1M 3 Days Ago'
yvar = 'New Cases per 1M Last 3 Days' #'New Cases Last 3 Days'

xlab = xvar
ylab = yvar
xmin = 0 #10^0
xmax = 4 #10^xmax
ymin = 0
ymax = 4

for state in state_list:
    df = covid_states[covid_states['state'] == state]

    #For Deaths:
    df = df[df['lastweek'] > 100]

    print(state, df[['POPESTIMATE2019', 'New Deaths Last 3 Days', 'Last 3 Days Deaths per 1M']].tail(1))

    fig.add_trace(
        go.Scatter(
            x=df[xvar],
            y=df[yvar],
            mode='lines',
            name='lines',
            line=dict(
                color='rgb(186, 186, 186, 0.5)',
                width=1
            ),
            showlegend=False)
    )

fig.update_xaxes(range=[xmin, xmax], type="log")
fig.update_yaxes(range=[ymin, ymax], type="log")


latest = max(np.unique(covid_states['date']))
latestdf=covid_states[covid_states['date'] == latest]
latestdf['size']= latestdf['POPESTIMATE2019'].apply(lambda x: math.sqrt(x)/200)

fig.add_trace(go.Scatter(
    x=latestdf[xvar],
    y=latestdf[yvar],
    mode='markers+text',
    marker_color='darkred',
    text=latestdf['Label'],
    marker=dict(size=latestdf['size']),
    name='Data as of '+latest,
    showlegend=False
)
)
fig.update_traces(
    textposition='bottom right'
)
fig.update_layout(
    title_text='US COVID Case Growth by State<br>Through '+latest,
    xaxis_title = xvar,
    yaxis_title = yvar,
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
fig.add_shape(
        # Line Diagonal
            type="line",
            x0=1,
            y0=1,
            x1=10000,
            y1=2500,
            line=dict(
                color="darkred",
                width=3,
                dash="dot",
            )
)

fig.add_trace(go.Scatter(
    x=[3500],
    y=[1500],
    text=["Early Trendline"],
    mode="text",
    showlegend=False

))

fig.show()

plotly.offline.plot(fig, filename='state_map_static/index.html')



