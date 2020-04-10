import plotly.graph_objects as go, plotly.figure_factory as ff
import pandas as pd
import plotly
import numpy as np

import plotly.express as px
import os

from urllib.request import urlopen
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)

if not os.path.exists("images"):
    os.mkdir("images")

url = 'https://raw.githubusercontent.com/nytimes/covid-19-data/master/us-counties.csv'

covid = pd.read_csv(url, error_bad_lines=False)
census = pd.read_csv('census_counties.csv', encoding = 'ISO-8859-1')
county_geo = pd.read_csv('county_geo.csv')[['FIPS', 'LAT', 'LONG']]
# census cols:
# county = fips code, popestimate2019

covid['datetime'] = pd.to_datetime(covid['date'])

# Select the ones you want
census_filter = census[['STATE', 'COUNTY','POPESTIMATE2019']]
census_filter['fips'] = census_filter.apply(lambda row: int(str(row.STATE) +
                                                            str("{:03d}".format(row.COUNTY))), axis=1)

print(covid[covid['state']=='California'])
covid_geo = pd.merge(covid,
                  county_geo,
                  left_on='fips',
                  right_on='FIPS',
                  how='inner')
print(covid_geo[covid_geo['state']=='California'])

covid_pop = pd.merge(covid_geo,
                  census_filter,
                  left_on='FIPS',
                  right_on='fips',
                  how='inner')

print(covid_pop[covid_pop['state']=='California'])

covid_pop['cases_per_mil'] = covid_pop.cases/covid_pop.POPESTIMATE2019*1000000
covid_pop['log_cases_per_mil'] = np.log(covid_pop['cases_per_mil'])

covid_pop['label'] = covid_pop['county']+', '+covid_pop['state']
covid_pop['FIPS'] = covid_pop['FIPS'].apply(lambda x: '{0:0>5}'.format(x))


plotly.io.orca.config.executable = '/Users/ndefrancis/opt/anaconda3/bin/orca'

n = 1
im = []
scale = 1
colorscale = ["#f7fbff", "#ebf3fb", "#deebf7", "#d2e3f3", "#c6dbef", "#b3d2e9", "#9ecae1",
    "#85bcdb", "#6baed6", "#57a0ce", "#4292c6", "#3082be", "#2171b5", "#1361a9",
    "#08519c", "#0b4083", "#08306b"
]
endpts = list(np.linspace(0, 500, len(colorscale) - 1))





data = covid_pop[covid_pop['date'] >= '2020-03-01']

fig = px.choropleth(data, geojson=counties, locations='FIPS', color='cases_per_mil',
                           color_continuous_scale=[[0.0, "rgb(197, 213, 235)"],
                                                   [0.5, "rgb(7, 57, 133)"],
                                                   [1.0, 'rgb(153, 5, 146)']],
                           range_color=(0, 1000),
                           hover_name="label",
                           hover_data=['cases', 'deaths', 'cases_per_mil'],
                           scope="usa",
                           animation_frame='date',
                           labels={'cases_per_mil':'Cases per 1M'}
                  )
fig.update_layout(
    margin={"r":5,"t":50,"l":5,"b":10},
    title_text='Cases per 1M people<br>By US counties',
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
fig.update_traces(
     marker=dict(
         line=dict(
             color='rgb(197, 213, 235)',
             width=0.25)
     )
)

fig.show()
plotly.offline.plot(fig, filename='testplot.html')



#fig.show() ## this loads url