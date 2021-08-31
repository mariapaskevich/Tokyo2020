import pandas as pd
import altair as alt
from vega_datasets import data
import streamlit as st

#Country codes are needed for building map visualization in Altair
country_codes = pd.read_csv('country_codes.csv',sep=',', encoding='latin-1')
country_codes.set_index('Alpha-3 code', inplace = True)

#Reading file with total medals
olympic_medal_map = pd.read_csv('olympic_medal_count.csv',sep=',', encoding='latin-1')

# Russia was participating as ROC that year, so need to change NOCCode in the table to match with country_codes
olympic_medal_map.loc[olympic_medal_map['Team/NOC']=='ROC','NOCCode'] = 'RUS' 

olympic_medal_map.set_index('NOCCode', inplace = True)
olympic_medal_map['id'] = country_codes['Numeric']

#Reading data by gender
medal_count_by_gender = pd.read_csv('medal_count_by_gender.csv',sep=',', encoding='latin-1')

###Drawing a map

def draw_map(mtype='Total'):
    
    COLOR_THEME = {'Total':"lightgreyred",
                   'Gold':"lightorange",
                   'Silver':"lightgreyteal",
                   'Bronze':"lightgreyred"}
    
    olympic_medal_map['Medals'] = olympic_medal_map[mtype]

    source = alt.topo_feature(data.world_110m.url, "countries")

    world_map = (
        alt.Chart(source, title=f'Countries by number of {mtype} medals')
        .mark_geoshape(stroke="black", strokeWidth=0.15)
        .encode(
            color=alt.Color(
                "Medals:N", 
                scale=alt.Scale(scheme=COLOR_THEME[mtype]), 
                legend=None),
            tooltip=[
                alt.Tooltip("Team/NOC:N", title="Team"),
                alt.Tooltip("Medals:Q", title="Medals"),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(olympic_medal_map, "id", ["Team/NOC", "Medals"]),
        )
    ).configure_view(strokeWidth=0).properties(width=700, height=400).project("naturalEarth1")
    
    return world_map

### Medals by gender

def medals_by_gender(countries=['Japan']):
    chart = alt.Chart(medal_count_by_gender.loc[(medal_count_by_gender['Team/NOC'].isin(countries))], title='Total medals earned by female and male athlets').mark_circle(size=300).encode(
        x=alt.X('count_male', title='Male Athlets'),
        y=alt.Y('count_female', title='Female Athlets'),
        color=alt.Color('Medal type',
                        scale=alt.Scale(domain=['Gold','Silver','Bronze'],
                                        range=['orange','grey','brown'])),
        tooltip=['Team/NOC', 'Medal type','count_female','count_male']
    ).properties(
        width=600,
        height=400
    )
    
    line = alt.Chart(pd.DataFrame({'var1': [0, 30], 'var2': [0, 30]})
                    ).mark_line(color='grey',
                                opacity=.3,
                                strokeDash=[5,5]
                               ).encode(alt.X('var1'),
                                        alt.Y('var2')
                                       )
    return chart+line

#---------- STREAMLIT APP ---------------

#Display page title and some text about the app
st.image('logo.png', width=100)
st.title('Tokyo Olympics 2020')
st.write('')
st.write('This interactive dashboard includes data from <a href="https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/medal-standings.htm">Tokyo 2020 Olympics Website</a>. You can switch between two views in the side menu: total medals by country or check statistics by gender',unsafe_allow_html=True)

#Display sidebar menu to choose between two views

MODE = st.sidebar.radio('Select view',['Total Medals by country','Statistics by by gender'])

#If Map view was chosen

if MODE == 'Total Medals by country':
    
    #add select for type of medal. The first one in options is the default value
    MEDALS = st.selectbox('Type of medals',
               options = ['Total','Gold','Silver','Bronze'])
    

    #display the map
    st.write(draw_map(MEDALS))
    #display the datatable below the map
    st.table(olympic_medal_map.reset_index().set_index('Team/NOC')[['Medals']].sort_values(by='Medals', ascending=False))

#If split by gender was chosen
else:
    
    #add select option for countries with multiple choice. Default values would be Japan, ROC and Sweden
    COUNTRY = st.multiselect('Select a team',
               list(medal_count_by_gender['Team/NOC'].drop_duplicates().values),
                            ['Japan','ROC','Sweden'])
    
    #display the graph and table with the results
    st.write(medals_by_gender(COUNTRY))
    st.write('Medals won by selected countries')
    st.table(medal_count_by_gender.loc[medal_count_by_gender['Team/NOC'].isin(COUNTRY),['Team/NOC','Medal type','count_female','count_male']])
    