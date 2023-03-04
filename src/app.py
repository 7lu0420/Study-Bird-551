import dash
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from dash import Dash, dcc, html
import plotly.express as px
import numpy as np
import altair as alt
from vega_datasets import data
import pandas as pd


# create a dash
app = dash.Dash(external_stylesheets=[dbc.themes.QUARTZ])

# location settings for sidebar
SIDEBAR_STYLE = {
    # "position": "fixed",
    "top": '10px',
    "flex":'0 1 10%',
    "left": 0,
    "bottom": 0,
    "width": "10px",
    "padding": "2px 1px"}

# location settings for sidebar
CONTENT_STYLE = {
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem"}

# create three tabs in the sidebar
nav_items = [
    dbc.NavItem(dbc.NavLink("Artist", id="page-artist",href="artist")),
    dbc.NavItem(dbc.NavLink("Lyrics", id="page-lyrics",href="lyrics")),
    dbc.NavItem(dbc.NavLink("Tracks", id="page-tracks",href="tracks"))]

# group three tabs together and list them virtically
nav = dbc.Nav(nav_items, vertical=True)


years=[]
mark = {}
for i in range(2012,2023):
    years.append(str(i))
for year in years:
    mark[year] = {
        'label': year,
        'style': {'color': 'white'}}
    
# layout of the dash app
app.layout = dbc.Container([    
    dcc.Location(id='url', refresh=False),
    dbc.Row([html.Div([   
                html.H3("BillBoard Top100 Hot 🔥🔥Songs🔥🔥 Analysis", className="display-4"),
                html.H5("Study Bird 551"),
                html.Hr()])]),
    dbc.Row([
    # sidebar includes 2 labels and 3 tabs
    dbc.Col([nav],style=SIDEBAR_STYLE),
    
    # content page includes 1 time slider at the top and 3 graphs below
    dbc.Col([dcc.RangeSlider(id='year-slider',min=2012,max=2022,value=[2012, 2022],step=1,marks=mark),
            html.Div(id="page-content"),
            html.Iframe(id='chart1',style={'border-width': '0', 'width': '100%', 'height': '400px'}),
            html.Div(id="describe1"),
            html.Iframe(id='chart2',style={'border-width': '0', 'width': '100%', 'height': '400px'}),
            html.Div(id="describe2"),
            html.Iframe(id='chart3',style={'border-width': '0', 'width': '100%', 'height': '400px'}),
            html.Div(id="describe3")],style=CONTENT_STYLE),]),
    dbc.Row([html.Hr(),
            html.P("Data from BillBoard, Spotify, Musixmatch and Genius.")])],
    fluid=True,)

# 4 outputs (one page content and three charts) and 4 inputs (three tabs and one year slider)
@app.callback(
    [Output("page-content", "children"),
    Output("chart1", "srcDoc"),
    Output("describe1", "children"),
    Output("chart2", "srcDoc"),
    Output("describe2", "children"),
    Output("chart3", "srcDoc"),
    Output("describe3", "children")],
    [Input('url', 'pathname'),
    Input("year-slider", "value")])


# render page content
def render_page_content(pathname,year):
    if "artist" in pathname:
        return generate_page_content("Artist Analysis", year)
    elif "lyrics" in pathname:
        return generate_page_content("Lyrics Analysis", year)
    elif "tracks" in  pathname:
        return generate_page_content("Tracks Analysis", year)
    else:
        return generate_page_content("Artist Analysis", year)

# output page content
def generate_page_content(page_title, year):
    start_year=int(year[0])
    end_year=int(year[1])
    alt.renderers.set_embed_options(theme='dark')
    if page_title=="Artist Analysis":
        df = pd.read_csv('../data/processed/second.csv')
        df = df.loc[(start_year <= df['Year']) & (df['Year'] <= end_year)]
        df = df.drop_duplicates(subset=['Artist'])
        pop=df[df['popularity']>85]
        
        chart=alt.Chart(pop).mark_bar().encode(
            y=alt.Y('popularity:Q',scale=alt.Scale(zero=False)),
            x=alt.X('Artist:N',sort='-y'))
        chart1=alt.Chart(pop).mark_bar().encode(
            x=alt.X('popularity:Q',scale=alt.Scale(zero=False)),
            y=alt.Y('Artist:N',sort='-x'))
        chart2=alt.Chart(pop).mark_bar().encode(
            x=alt.X('popularity:Q',scale=alt.Scale(zero=False)),
            y=alt.Y('Artist:N',sort='-x'))
        
        chart_describ=""
        chart1_describ=""
        chart2_describ=""
        
    elif page_title=="Lyrics Analysis":
        df = pd.read_excel('../data/processed/lyrics_dataset.xlsx')
        df = df.loc[(start_year <= df['Year']) & (df['Year'] <= end_year)]
        df['rank_bin'] = pd.cut(df['Rank'],bins=4,labels=['1-25','26-50','51-75','76-100'])
        df_bin = df.groupby(['rank_bin','Year']).mean().reset_index()
        sentiment_counts = df['Sentiment'].value_counts()
        source = pd.DataFrame({"category": ['Positive','Negative','Neutral'], "sentiment_counts": [sentiment_counts[0], sentiment_counts[1], sentiment_counts[2]]})

        chart = alt.Chart(df_bin).mark_bar().encode(
            x='Year:N',
            y=alt.Y('Word Count:Q', axis=alt.Axis(title='Lyrics Length')),
            column=alt.Column('rank_bin:O',title=None),
            color='Year:N',
            ).properties(
            title={'text':"Lyrics Length and Rank by Year", "anchor": "middle"},width=180)
        
        chart1 = alt.Chart(source).mark_arc().encode(
            theta=alt.Theta(field="sentiment_counts", type="quantitative"),
            color=alt.Color(field="category", type="nominal"),
            tooltip=["sentiment_counts","category"]).properties(
            title={'text':"Sentiment Counts in {}".format(year), "anchor": "middle"})
        
        chart1 = chart1|alt.Chart(df).mark_boxplot().encode(
            x=alt.X('Year:N'),
            y=alt.Y('Sentiment Polarity:Q', axis=alt.Axis(title='Sentiment Score')),
           ).properties(
            title={'text':"Boxplot of Sentiment Score in {}".format(year), "anchor": "middle"},width=300)
        
        chart2 = alt.Chart(df).mark_area(interpolate='basis').encode(
            x=alt.X('Rank'),
            y=alt.Y('Frequency_love:Q', axis=alt.Axis(title='Frequency'),scale=alt.Scale(domain=[0, 35])),
            color='Year:N',
            tooltip=['Year','Frequency_love','Artist']).properties(
            title={'text':"Frequency of 'love' in {}".format(year), "anchor": "middle"},width=780)
        
        chart_describ=""
        chart1_describ=""
        chart2_describ=""
        
    elif page_title=="Tracks Analysis":
        # alt.renderers.set_embed_options(theme='dark')
        

        hits = pd.read_csv('../data/processed/audio_data_processed.csv')
        hits.drop(["Unnamed: 0",'type','uri','track_href','analysis_url','id'], axis=1, inplace=True)
        titleParams=[alt.TitleParams(text = x,subtitle=y,anchor='start',fontSize = 24) for (x,y) in [
                    ("Vibe Features Over Rank","Energy, speechiness, instrumentalness,valence in different strata of the charts"),
                    ("Rhythm Features Over Year", "Time signature, tempo, duration occurences"),
                    ("Musical Features Interaction", "Musical key, mode occurences")]]

        hits['rank_bin'] = pd.cut(hits['Rank'],bins=10,labels=['1-10','11-20','21-30','31-40','41-50','51-60','61-70','71-80','81-90','91-100'])
        hits_c = hits[(start_year <= hits['Year']) & (hits['Year'] <= end_year)]
        hits_c_bin = hits_c.groupby('rank_bin').mean().reset_index()
        hits_c_bin = hits_c_bin[['rank_bin','popularity','energy','speechiness','instrumentalness','valence']].set_index(['rank_bin','popularity']).stack().reset_index(name='value').rename(columns={'level_2':'features'})
        charts=[]


        for i in ['energy','speechiness','instrumentalness','valence']:
            charts.append(alt.Chart(hits_c_bin[hits_c_bin['features'] == i]).mark_square().encode(
            x=alt.X('rank_bin:N',title='Rank bins'),
            y=alt.Y('value',scale=alt.Scale(zero=False),title='Occurences'),
            color='features:N',
            opacity='popularity:Q',
            size= 'popularity:Q'
            ))
        chart = (charts[0]+charts[1]+charts[2]+charts[3]).properties(
                width=900,height=250, title = titleParams[0])
    
        hits_c1 = hits.groupby(['Year','time_signature']).size().reset_index(name='cnt')
        hits_c1['ts_perct']=hits_c1['cnt']/100
        chart1 = (alt.Chart(hits_c1[hits_c1['time_signature']==4]).mark_line(point=True).encode(
            x=alt.X('Year',scale=alt.Scale(zero=False)),
            y=alt.Y('ts_perct:Q',scale=alt.Scale(zero=False),title=' ')
        ).properties(width=250,height=250,title="4/4 Time signature percentage")| alt.Chart(hits[['Year','duration_ms','tempo']]).mark_boxplot().encode(
            x=alt.X('Year',scale=alt.Scale(zero=False)),
            y=alt.Y('tempo:Q',title=' ')
        ).properties(width=250,height=250,title="Tempo")| alt.Chart(hits[['Year','duration_ms','tempo']]).mark_boxplot().encode(
            x=alt.X('Year',scale=alt.Scale(zero=False)),
            y=alt.Y('duration_ms:Q',title=' ')
        ).properties(width=250,height=250,title="Duration(ms)")).properties(title=titleParams[1])
        
        hits_c2 = hits.groupby(['key','mode']).size().reset_index(name='cnt')

        # hits_c2_2 = hits[['Year','tempo','duration_ms']].set_index(['Year']).stack().reset_index(name='value').rename(columns={'level_1':'features'})
        chart2 = alt.Chart(hits_c2).mark_bar().encode(
            x=alt.X('key:N',title='Musical Key'),
            y=alt.Y('cnt:Q',title='Occurrence'),
            color='mode:N'
        ).properties(width=900,height=250, title=titleParams[2])

        chart_describ=dcc.Markdown("""
        - The **energy** represents the intensity and activity; 
        - The **speechness** detects the degree of presence spoken words; 
        - The **instrumentalness** predicts whether a track contains no vocals; 
        - The **valence** describing the musical positiveness.
        """)
        chart1_describ=dcc.Markdown("""
        - The **time signiture** (aka. meter) is a notational convention to specify how many beats are in each bar (or measure). The time signature ranges from 3 to 7 indicating time signatures of "3/4", to "7/4"; 
        - The **tempo** (aka. beats per minute, BPM), which is the speed or pace of a given piece and derives directly from the average beat duration; 
        - The **duration** is the duration of the track in milliseconds.
        """)
        chart2_describ=dcc.Markdown("""
        - The **musical** key represents the scale, where values are integers that can map to pitches using standard Pitch Class notation. E.g. 0 = C, 1 = C♯/D♭, 2 = D, and so on; 
        - The **mode** indicates the modality (major or minor), which is the type of scale from which its melodic content is derived. Major is represented by 1 and minor is 0.
        """)

    return html.Div(
        [html.H4(f"{page_title} between {year[0]} and {year[1]}:"),]
        # html.Div("This is data visualization content for {} in {}:".format(page_title, year))]
    ),chart.to_html(),html.Div(chart_describ),chart1.to_html(),html.Div(chart1_describ),chart2.to_html(),html.Div(chart2_describ)

if __name__ == "__main__":
    app.run_server(debug=True)
