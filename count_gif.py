import plotly.graph_objects as go
import plotly
import pandas as pd
from PIL import Image
import os

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
census_filter = census[['COUNTY','POPESTIMATE2019']]

today = covid[covid['date'] == '2020-03-28']

print(covid.head())
print(today.head())
print(census_filter.head())
print(county_geo.head())


covid_geo = pd.merge(covid,
                  county_geo,
                  left_on='fips',
                  right_on='FIPS',
                  how='inner')



scale = 1

fig = go.Figure()



plotly.io.orca.config.executable = '/Users/ndefrancis/opt/anaconda3/bin/orca'

n = 1
im = []
for dates in pd.date_range(start="2020-03-01",end="2020-03-29"):
    df = covid_geo[covid_geo['date'] == dates]
    timestampStr = dates.strftime("%b %d")
    print(timestampStr)
    fig.add_trace(go.Scattergeo(
        locationmode = 'USA-states',
        lon = df['LONG'],
        lat = df['LAT'],
        text = df['county'],
        marker = dict(
            size = df['cases']/scale,
            color = "red",
            line_color='rgb(40,40,40)',
            line_width=0.5,
            sizemode = 'area',
            opacity = 0.1
        )
    ))

    fig.update_layout(
        title_text='Covid Cases: '+timestampStr+'<br>Total Case Count by US County',
        font=dict(
            size=18
        ),
        showlegend=False,
        geo=dict(
            resolution=110,
            scope='usa',
            landcolor='rgb(217, 217, 217)',
        ),
        width=1050, height=750,
        annotations=[
            go.layout.Annotation(
                showarrow=False,
                text='by Nick DeFrancis',
                xanchor='right',
                x=1.03,
                xshift=0,
                yanchor='top',
                y=-.03,
                font=dict(
                    size=10
                )
            )
        ]
    )
    filename = "images/fig_"+str(n)+".png"
    n+=1
    fig.write_image(filename)
    im.append(Image.open(filename))

im[0].save('out.gif', save_all=True, append_images=im[1:], duration=200, loop   = True)




#fig.show() ## this loads url