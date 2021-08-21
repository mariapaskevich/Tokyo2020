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


###Title and initial text

st.image('logo.png', width=100)
st.title('Tokyo Olympics 2020')
st.write('')
st.write('This dashboard includes data from <a href="https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/medal-standings.htm">Tokyo 2020 Olympics Website</a>. You can switch between two views in the side menu: total medals by country or check statistics by gender',unsafe_allow_html=True)

st.write('')

###Sidebar menu

MODE = st.sidebar.radio('Select view',['Total Medals by country','Statistics by by gender'])


###Map

if MODE == 'Total Medals by country':
    
    MEDALS = st.selectbox('Type of medals',
               options = ['Total','Gold','Silver','Bronze'])
    
    COLOR_THEME = {'Total':"lightgreyred",
                   'Gold':"lightorange",
                   'Silver':"lightgreyteal",
                   'Bronze':"lightgreyred"}
    
    olympic_medal_map['Medals'] = olympic_medal_map[MEDALS]

    source = alt.topo_feature(data.world_110m.url, "countries")

    background = alt.Chart(source).mark_geoshape(fill="white")

    foreground = (
        alt.Chart(source, title=f'Countries by number of {MEDALS} medals')
        .mark_geoshape(stroke="black", strokeWidth=0.15)
        .encode(
            color=alt.Color(
                "Medals:N", scale=alt.Scale(scheme=COLOR_THEME[MEDALS]), legend=None
            ),
            tooltip=[
                alt.Tooltip("Team/NOC:N", title="Team"),
                alt.Tooltip("Medals:Q", title="Medals"),
            ],
        )
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(olympic_medal_map, "id", ["Team/NOC", "Medals"]),
        )
    )

    final_map = (
        (background + foreground)
        .configure_view(strokeWidth=0)
        .properties(width=600, height=400)
        .project("naturalEarth1")
    )

    st.write(final_map)
    st.table(olympic_medal_map.reset_index().set_index('Team/NOC')[['Medals']].sort_values(by='Medals', ascending=False))

### Split by gender
else:
    
    COUNTRY = st.multiselect('Select a team',
               list(medal_count_by_gender['Team/NOC'].drop_duplicates().values),
                            ['Japan','ROC','Sweden'])
    
    chart = alt.Chart(medal_count_by_gender.loc[(medal_count_by_gender['Medal type'] != 'Total')&(medal_count_by_gender['Team/NOC'].isin(COUNTRY))], title='Total medals earned by female and male athlets').mark_circle(size=300).encode(
    x=alt.X('count_male', title='Male Athlets'),
    y=alt.Y('count_female', title='Female Athlets'),
    color=alt.Color('Medal type', 
                    scale=alt.Scale(domain=['Gold','Silver','Bronze'],range=['orange','grey','brown'])),
    tooltip=['Team/NOC', 'Medal type','count_female','count_male']
).properties(
    width=600,
    height=400
)
    line = alt.Chart(
    pd.DataFrame({'var1': [0, 30], 'var2': [0, 30]})).mark_line(color='grey',opacity=.3,strokeDash=[5,5]).encode(
            alt.X('var1'),
            alt.Y('var2'),
)
    
    st.write(chart+line)
    st.write('Medals won by selected countries')
    st.table(medal_count_by_gender.loc[medal_count_by_gender['Team/NOC'].isin(COUNTRY),['Team/NOC','Medal type','count_female','count_male']])
    