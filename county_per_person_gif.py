import plotly.graph_objects as go, plotly.figure_factory as ff
import plotly
import pandas as pd
import numpy as np
from PIL import Image
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

covid['date'] = pd.to_datetime(covid['date'])

# Select the ones you want
census_filter = census[['STATE', 'COUNTY','POPESTIMATE2019']]
census_filter['fips'] = census_filter.apply(lambda row: int(str("{:03d}".format(row.STATE)) +
                                                            str("{:03d}".format(row.COUNTY))), axis=1)


print(covid.head())
print(census_filter.head())
print(county_geo.head())


covid_geo = pd.merge(covid,
                  county_geo,
                  left_on='fips',
                  right_on='FIPS',
                  how='inner')

covid_pop = pd.merge(covid_geo,
                  census_filter,
                  left_on='FIPS',
                  right_on='fips',
                  how='inner')

covid_pop['cases_per_mil'] = covid_pop.cases/covid_pop.POPESTIMATE2019*1000000
covid_pop['log_cases_per_mil'] = np.log(covid_pop['cases_per_mil'])

today = covid_pop[covid_pop['date'] == '2020-04-07']



print(covid_geo.head())
print(covid_pop.head())


plotly.io.orca.config.executable = '/Users/ndefrancis/opt/anaconda3/bin/orca'

n = 1
im = []
scale = 1
colorscale = ["#f7fbff", "#ebf3fb", "#deebf7", "#d2e3f3", "#c6dbef", "#b3d2e9", "#9ecae1",
    "#85bcdb", "#6baed6", "#57a0ce", "#4292c6", "#3082be", "#2171b5", "#1361a9",
    "#08519c", "#0b4083", "#08306b"
]
endpts = list(np.linspace(0, 500, len(colorscale) - 1))



for dates in pd.date_range(start="2020-03-01",end="2020-04-07"):
    df = covid_pop[covid_pop['date'] == dates]
    timestampStr = dates.strftime("%b %d")
    print(timestampStr)
    fig = ff.create_choropleth(
        fips=df['FIPS'], values=df['cases_per_mil'], scope=['usa'],
        colorscale=colorscale,
        binning_endpoints=endpts,
        round_legend_values=True,
        showlegend = True,
        state_outline={'width': 0.75, 'color': 'white'},
        asp=2.9,
        title_text='USA COVID Density',
        plot_bgcolor='rgb(229,229,229)',
        paper_bgcolor='rgb(229,229,229)',
        county_outline={'color': 'rgb(255,255,255)', 'width': 0.5}
    )
#    fig.layout.template = None

    fig.update_layout(
        title_text='County-level COVID cases per 1M population: '+timestampStr,
        font=dict(
            size=14
        ),
        geo=dict(
            resolution=110,
            scope='usa',
            #landcolor='rgb(217, 217, 217)',
        ),
        width=1200, height=600,
        annotations=[
            go.layout.Annotation(
                showarrow=False,
                text='by Nick DeFrancis',
                xanchor='right',
                x=1,
                xshift=0,
                yanchor='top',
                y=0,
                font=dict(
                    size=10
                )
            )
        ]
    )
    filename = "images/pop_"+str(n)+".png"
    n+=1
    fig.write_image(filename)
    im.append(Image.open(filename))
    #im.append(go.Figure(fig))

im[0].save('out_pop.gif', save_all=True, append_images=im[1:], duration=300, loop = 0)

fig.show()


#fig.show() ## this loads url