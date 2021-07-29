import streamlit as st
import pandas as pd
import base64
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

st.write('')
st.title('NBA Player Stats Explorer')

st.markdown("""
This app does simple web scraping for NBA player stats data!
* ** Datasource: ** [Basketball-reference.com](https://www.basketball-reference.com/)
""")

st.sidebar.header('')
st.sidebar.header('User Input Features')
selected_year = st.sidebar.selectbox('Year', list(reversed(range(1950, 2022))))


####################
# Web scraping of NBA player stats
####################
@st.cache
def load_data(year):
    url = 'https://www.basketball-reference.com/leagues/NBA_' + str(year) + '_per_game.html'
    html = pd.read_html(url, header=0)
    df = html[0]
    return df


playerstats = load_data(selected_year)

#############################
# Sidebar - Team selection
#############################
sorted_unique_teams = sorted(playerstats.Tm.unique())  # unique Teams for selection Box
selected_teams = st.sidebar.multiselect('Teams', sorted_unique_teams, sorted_unique_teams)


#############################
# Sidebar - Player Position selection
#############################
unique_positions = ['C', 'PF', 'PG', 'SG']
selected_pos = st.sidebar.multiselect('Player Positions', unique_positions, unique_positions)

##############################
# Filtering Data
##############################
df_selected_teams = playerstats[(playerstats.Tm.isin(selected_teams)) & (playerstats.Pos.isin(selected_pos))] # Pandas Filterung - entspannt af


if len(selected_teams) > 1:
    teams_title = 'Teams'
else:
    teams_title = 'Team'


############################
# Download NBA player stats data function
############################
def filedownload(df):
    csv = df.to_csv(index=False)
    b64 = base64.b64encode(csv.encode()).decode()  # strings <-> bytes conversions
    href = f'<a href="data:file/csv;base64,{b64}" download="playerstats.csv">Download CSV File</a>'
    return href


#############################
# Table Header and Table
#############################
if len(selected_teams) >= 1:
    st.header('Display Player Stats of Selected ' + teams_title)
    st.write('Data Dimension: ' + str(df_selected_teams.shape[0]) + ' rows and ' + str(df_selected_teams.shape[1]) + ' columns.')
    st.dataframe(df_selected_teams)  # Show Table
    st.markdown(filedownload(df_selected_teams), unsafe_allow_html=True)  # Download CSV

    # Heatmap
    # Errors with df while generating heatmap - output to csv and read back in = fix
    if st.button('Intercorrelation Heatmap'):
        st.header('Intercorrelation Matrix Heatmap')
        df_selected_teams.to_csv('output_csv', index=False)
        df = pd.read_csv('output_csv')

        # Generate Heatmap
        corr = df.corr()          # finds correlations between all columns
        mask = np.zeros_like(corr) # convert df to zero df
        mask[np.triu_indices_from(mask)] = True
        with sns.axes_style("white"):
            f, ax = plt.subplots(figsize=(7, 5))
            ax = sns.heatmap(corr, mask=mask, vmax=1, square=True)
        st.pyplot(f)


else:
    st.header('No Teams Selected')


