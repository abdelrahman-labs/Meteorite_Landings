import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objs as go

# Set page title and icon
st.set_page_config(
    page_title="A.Rahman's Projects",
    page_icon=":bar_chart:",
    layout="wide"
)


@st.cache(allow_output_mutation=True)
def load_data() -> pd.DataFrame:
    df = pd.read_csv("Meteorite_Landings(1).csv")
    return df.dropna()


@st.cache(allow_output_mutation=True)
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    geo_data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.reclong, df.reclat))
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    merged = gpd.sjoin(geo_data, world, how="inner", op='intersects')
    merged.drop(columns=['index_right', 'geometry'], inplace=True)
    merged.rename(columns={'continent': 'Continent Name', 'name_right': 'Country Name'}, inplace=True)
    return merged


# Define the title and subtitle
st.title('Data Analysis Portfolio')
st.markdown('### Showcase of data analysis projects')

# Create a sidebar menu
st.sidebar.title('Navigation')
page = st.sidebar.radio('Go to:', ('Home', 'Project 1', 'Project 2', 'Project 3'))

# Define the content for each page
if page == 'Home':
    st.write('Welcome to my data analysis portfolio! Use the sidebar to navigate to different projects.')
elif page == 'Project 1':
    st.header('Project 1: Meteorite Landings')

    df = load_data()
    merged = preprocess_data(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Raw Data",
        data=csv,
        file_name='Meteorite_Landings.csv',
        mime='text/csv',
    )

    st.markdown("---")
    st.subheader("Meteorite Landing Distribution")

    ## Distribution map
    df[["lat", 'lon']] = df[['reclat', 'reclong']]
    st.map(df[['lat', 'lon']].dropna())

    one, two = st.columns(2)

    ## Distribution per continent (pie)
    continents = merged['Continent Name'].value_counts().reset_index().set_index("index")
    total_meteorites = continents['Continent Name'].sum()
    continents['Percentage'] = 100 * continents['Continent Name'] / total_meteorites
    fig_location = px.pie(continents, values="Percentage", names=continents.index, title="<b>Meteorites Per Continent</b>",
                          color_discrete_sequence=px.colors.qualitative.Dark2,
                          labels={'Percentage': 'Percentage of Meteorites'},
                          hole=0.5, )
    one, two = st.columns(2)
    one.plotly_chart(fig_location, use_container_width=True)
    one.write("About {:.1f}% of landed meteorites were found in Antarctica.".format(continents.loc['Antarctica', 'Percentage']))

    ## Distribution per country

    # Get data
    countries = merged.loc[merged['Country Name'] != "Antarctica", "Country Name"].value_counts().head(10)

    # Create figure
    fig = go.Figure()

    # Add bars
    fig.add_trace(go.Bar(
        x=countries.index,
        y=countries,
        text=countries,
        textposition="auto",
        marker=dict(
            color=countries,
            colorscale="Blues"
        )
    ))

    # Update layout
    fig.update_layout(
        title="<b>Meteorites Per Country (excluding Antarctica)</b>",
        xaxis=dict(title="Country"),
        yaxis=dict(title="Number of Meteorites"),
        plot_bgcolor="rgba(0,0,0,0)",
        showlegend=False
    )
    fig.update_xaxes(showgrid=False)
    fig.update_yaxes(showgrid=False, visible=False)

    with two:
        st.plotly_chart(fig, use_container_width=True)
    with two:
        st.write("After ruling out Antarctica, Oman has the most recorded meteorite landings, although it has a small area.")

    st.markdown("---")
    st.subheader("Meteorite Classes")
    one1, two1 = st.columns(2)

    ## Classes Counts
    top_classes = df['recclass'].value_counts().head(15)
    top_classes = top_classes.reset_index().set_index("index")
    fig_noofd = px.bar(top_classes, y="recclass", x=top_classes.index, title="<b>Meteorite Classes</b>", text="recclass", height=500)
    fig_noofd.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)), barmode="stack")
    fig_noofd.update_yaxes(visible=False)
    fig_noofd.update_traces(marker_color=['indianred' if y > 5000 else 'lightblue' for y in top_classes['recclass']])
    one1.plotly_chart(fig_noofd, use_container_width=True)
    one1.write("Both Classes L6 and H5 are the most popular among other landed meteorites")

    ## Average Mass per meteorite class
    dff = df.groupby(['recclass'])['mass (g)'].mean().reset_index().set_index('recclass').sort_values(by='mass (g)', ascending=False).head(20)
    dff["mass (g)"] = dff["mass (g)"].round()
    fig_mass = px.bar(dff.sort_values(by='mass (g)', ascending=False), y="mass (g)", x=dff.index, title="<b>Meteorite Average Mass (G)</b>", text="mass (g)", height=500)
    fig_mass.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)), barmode="stack")
    fig_mass.update_yaxes(visible=False)
    fig_mass.update_traces(marker_color=['indianred' if y > 1000000 else 'lightblue' for y in dff['mass (g)']])
    two1.plotly_chart(fig_mass, use_container_width=True)
    two1.write('Average Mass for the class "iron, IVB" is about 4,323 Kilo Grams which is very high compared to other Classes')
    two1.write('The classes Iron IVB, Iron IIIE and Iron IAB-MG have an average of more than 1,000 Kilogram mass landed meteorites.')

    st.markdown("---")
    st.subheader("Changes over the years")
    one2, two2 = st.columns(2)

    ## Landings over time
    df_from_1970_2013 = df.loc[(df["year"] >= 1970) & (df["year"] <= 2013)]
    df_from_1970_2013 = df_from_1970_2013.groupby(['year'])['id'].count().reset_index().set_index('year')
    df_from_1970_2013 = df_from_1970_2013.rename(columns={"id": "# of Meteorites"})
    fig = px.line(df_from_1970_2013, x=df_from_1970_2013.index, y='# of Meteorites', markers=True, title="<b>Yearly Meteorite Landings</b>")
    fig.update_yaxes(title_text="# of Meteorites")
    fig.update_traces(line_color='blue')
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    one2.plotly_chart(fig, use_container_width=False)
    st.write("The number of meteorite landings increased sharply in the early 2000s, possibly due to increased efforts in meteorite hunting or advances in detection technology.")

    ## Animated Yearly landings per continent
    yearly_counts = merged.loc[merged['year'].between(1970, 2013), :]
    yearly_counts = yearly_counts.groupby(['year', 'Continent Name'])['id'].count().reset_index()
    yearly_counts = yearly_counts.sort_values(['Continent Name', 'year'])
    yearly_counts['Running Total'] = yearly_counts.groupby('Continent Name')['id'].cumsum()

    colors = px.colors.qualitative.Safe

    fig = go.Figure()
    for i, continent in enumerate(yearly_counts['Continent Name'].unique()):
        data = yearly_counts.loc[yearly_counts['Continent Name'] == continent, :]
        fig.add_trace(go.Scatter(
            x=data['year'],
            y=data['Running Total'],
            name=continent,
            mode='lines',
            line=dict(color=colors[i], width=2),
            fill='tozeroy',
            hovertemplate="%{y:.0f}"
        ))
    fig.update_layout(
        title="<b>Yearly Landings per Continent</b>",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Running Total", showgrid=False),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        transition=dict(duration=500, easing="linear")
    )
    two2.plotly_chart(fig, use_container_width=True)

    ## average mass every year
    df_from_1980_2013_mass = df.loc[(df["year"] >= 1980) & (df["year"] <= 2013)]
    df_from_1980_2013_mass = df_from_1980_2013_mass.groupby(['year'])['mass (g)'].mean().reset_index().set_index('year').sort_values(by='mass (g)', ascending=False)
    df_from_1980_2013_mass["mass (g)"] = df_from_1980_2013_mass["mass (g)"].round()
    fig_mass = px.bar(df_from_1980_2013_mass.sort_values(by='mass (g)', ascending=False), y="mass (g)", x=df_from_1980_2013_mass.index, title="Yearly Average Mass of Meteorites (1980-2013)", labels={"x": "Year", "mass (g)": "Average Mass (g)"},
                      text="mass (g)", height=500)
    fig_mass.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=(dict(showgrid=False)), yaxis=(dict(showgrid=False)), barmode="stack")
    fig_mass.update_yaxes(visible=False)
    fig_mass.update_traces(marker_color=['indianred' if y > 5000 else 'lightblue' for y in df_from_1980_2013_mass['mass (g)']])
    st.plotly_chart(fig_mass, use_container_width=True)
    st.write(
        "The average mass of meteorites from 1980 to 2013 was 2143.38 grams. Note that the high average mass in the mid-1970s is due to the low number of recorded meteorites at that time, and that more recent years have seen a trend toward larger average masses, with some years exceeding 5 kilograms.")

elif page == 'Project 2':
    st.header('Project 2: test')
elif page == 'Project 3':
    st.header('Project 3: test')

# Add footer
st.write('')
st.write('')
st.write('')
st.write('')
st.write('Created by A.Rahman Zaki, 2023')
