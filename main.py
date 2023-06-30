import geopandas as gpd
import pandas as pd
import plotly.express as px
import streamlit as st
import plotly.graph_objs as go
import numpy as np

# Set page title and icon
st.set_page_config(
    page_title="A.Rahman's Portfolio",
    page_icon="Logo_s.png",
    layout="wide"
)

# Hide the Streamlit menu
hide_menu_style = """
        <style>
        #MainMenu {visibility: hidden;}
        </style>
        """
st.markdown(hide_menu_style, unsafe_allow_html=True)


# Function to load data
@st.cache_data()
def load_data(filename: str) -> pd.DataFrame:
    if filename.endswith(".csv"):
        df = pd.read_csv(filename)
    elif filename.endswith(".xlsx"):
        df = pd.read_excel(filename)
    return df


# Function to preprocess data
@st.cache_data()
def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    geo_data = gpd.GeoDataFrame(df, geometry=gpd.points_from_xy(df.reclong, df.reclat))
    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    merged = gpd.sjoin(geo_data, world, how="inner", op='intersects')
    merged.drop(columns=['index_right', 'geometry'], inplace=True)
    merged.rename(columns={'continent': 'Continent Name', 'name_right': 'Country Name'}, inplace=True)
    return merged


# Load data
df_meteorites = load_data("Meteorite_Landings(1).csv").dropna()
df_fetal_health = load_data("fetal_health.csv")
df_agency = load_data("Agency (G).xlsx")

# Preprocess data
merged_data = preprocess_data(df_meteorites)

# Create a sidebar menu
st.sidebar.title('Navigation')
pages = ('Home', 'Project 1: Meteorite Landings', 'Project 2: Fetal Health Classification', 'Project 3: Quality Control System', 'Project 4: Customer Dashboard', 'Contact')
page = st.sidebar.radio('Go to:', pages)

# Add the logo with different sizes based on the page
logo_image = "Logo.png"
if page == 'Home' or page == 'Contact':
    st.image(logo_image, use_column_width=True)
else:
    st.image(logo_image, width=300)

# Define the content for each page
if page == 'Home':
    st.header('Welcome to my Data Analysis Portfolio!')
    st.write(
        'Here, you will find a curated collection of some of my best projects. Please use the sidebar to navigate to different projects and explore their detailed analyses and visualizations.')
    st.markdown("---")
    st.subheader('Project 1: Meteorite Landings')
    st.write(
        'This project involves analyzing a dataset of meteorite landings to gain insights into their characteristics and locations. I have performed various visualizations and statistical analyses to understand patterns and trends in meteorite '
        'landings.')

    st.subheader('Project 2: Fetal Health Classification')
    st.write('In this project, I have developed a classification model to predict fetal health status based on various attributes. The model utilizes machine learning techniques to assist in prenatal care and identify potential risks.')

    st.subheader('Project 3: Quality Control System')
    st.write(
        'The Express Company Quality Control System is an automated system designed to analyze shipping data from an express company and identify problematic waybill numbers. It helps improve the overall quality of the shipping process and '
        'provides insights to address quality control issues.')

    st.subheader('Project 4: Customer Dashboard')
    st.write(
        "A Python and Streamlit-based web application designed to assist the operation department members in a domestic shipping company. The dashboard provides key indicators and insights to help identify issues faced by the company's top 10 customers during any selected period.")
    st.markdown("---")
    st.subheader('Skills and Expertise')
    st.write('I have expertise in the following areas:')
    st.write('- Data analysis and visualization')
    st.write('- Statistical analysis')
    st.write('- Machine learning and predictive modeling')
    st.write('- Python programming')
    st.write('- SQL')
    st.write('- Tableau')
    st.write('- Streamlit web application development')
    st.write('- Spreadsheets (Excel, Google Sheets, Etc.)')
    st.markdown("---")
    st.subheader('Contact Me')
    st.write('If you have any inquiries or would like to collaborate on a project, feel free to reach out to me. You can find my contact information below.')

elif page == 'Project 1: Meteorite Landings':
    st.header('Project 1: Meteorite Landings')
    st.subheader('Introduction')
    st.write('The study of meteorites has long captivated scientists and enthusiasts alike, providing insight into the formation and evolution of our solar system. In this data analysis project, we examine some of the key findings regarding landed '
             'meteorites on Earth, including their distribution, composition, and average mass.')

    csv = df_meteorites.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download Raw Data",
        data=csv,
        file_name='Meteorite_Landings.csv',
        mime='text/csv',
    )

    link = 'https://www.kaggle.com/code/rahman96/meteorite-landings-findings'
    st.markdown(f"To access the source code and analysis steps, click [here]({link})")
    st.markdown("---")
    st.subheader("Dataset Overview")
    st.write(df_meteorites.describe(include='all'))
    st.markdown("---")
    st.subheader("Meteorite Landing Distribution")

    ## Distribution map
    fig_map = px.scatter_mapbox(df_meteorites.loc[(df_meteorites["year"] >= 1900) & (df_meteorites["year"] < 2020)], lat="reclat", lon="reclong", hover_name="recclass", color='year', hover_data=['mass (g)'],
                                color_continuous_scale=px.colors.sequential.Viridis)

    # customize the layout of the Map
    fig_map.update_layout(
        mapbox_style="open-street-map",
        mapbox=dict(center=dict(lat=0, lon=0), zoom=0),
        margin=dict(l=0, r=0, t=0, b=0),
        width=1100, height=1000)

    st.plotly_chart(fig_map)

    one, two = st.columns(2)

    ## Distribution per continent (pie)
    continents = merged_data['Continent Name'].value_counts().reset_index()
    total_meteorites = continents['count'].sum()
    # Convert 'Count' column to numeric values
    continents['count'] = pd.to_numeric(continents['count'])

    continents['Percentage'] = 100 * continents['count'] / total_meteorites

    fig_location = px.pie(continents, values="Percentage", names="Continent Name", title="<b>Meteorites Per Continent</b>",
                          color_discrete_sequence=px.colors.qualitative.Set2,
                          labels={'Percentage': 'Percentage of Meteorites'},
                          hole=0.5)
    one.plotly_chart(fig_location, use_container_width=True)
    one.write("About {:.1f}% of landed meteorites were found in Antarctica.".format(continents.loc[continents['Continent Name'] == 'Antarctica', 'Percentage'].values[0]))
    one.write("There are several reasons why Antarctica has such a high number of recorded meteorite landings. One of the main factors is the continent's vast and pristine expanses of ice, which provide a stark contrast to the dark color of most "
              "meteorites, making them easier to spot. Additionally, Antarctica's cold and dry climate helps to preserve meteorites once they land, preventing them from eroding or being covered by vegetation over time.")
    one.write("Another contributing factor is the fact that Antarctica is relatively free from human activity, which reduces the likelihood of meteorites being disturbed or destroyed by human interference. Furthermore, the high winds and extreme "
              "weather conditions on the continent can expose more of the underlying ice and snow, which may reveal meteorites that have been buried under the surface.")
    one.write("Finally, the scientific community has been actively searching for meteorites in Antarctica for several decades, with numerous research expeditions mounted to collect samples. This sustained effort has led to the accumulation of a "
              "large number of recorded meteorite landings in Antarctica.")

    ## Distribution per country

    # Get data
    countries = merged_data.loc[merged_data['Country Name'] != "Antarctica", "Country Name"].value_counts().head(10)

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
            colorscale="Viridis",
            opacity=0.8
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
        st.write("Despite its small area, Oman has the second-highest number of recorded meteorite landings after Antarctica.")
        st.write("There are various plausible reasons. Firstly, the desert landscape and lack of vegetation in Oman make it easier to detect fallen meteorites. Secondly, the region's extensive history of trade and commerce "
                 "could have attracted more individuals, thereby increasing the chances of meteorite sightings and recoveries being documented. Lastly, the Omani government has proactively encouraged research on meteorites and has implemented "
                 "measures to preserve the country's meteorite heritage, which could have facilitated more meticulous and organized record-keeping over time.")

    st.markdown("---")
    st.subheader("Meteorite Classes")
    one1, two1 = st.columns(2)

    ## Classes Counts
    top_classes = df_meteorites['recclass'].value_counts().head(15).reset_index()
    fig_noofd = px.bar(top_classes, y="count", x="recclass", title="<b>Meteorite Classes</b>", text="recclass", height=500)
    fig_noofd.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False), barmode="stack", legend=dict(
        orientation="h",
        yanchor="bottom",
        y=-0.2,
        xanchor="center",
        x=0.5
    ))
    fig_noofd.update_traces(marker_color=['#B2DBE5' if y < 5000 else '#F2A694' for y in top_classes['count']])
    one1.plotly_chart(fig_noofd, use_container_width=True)
    one1.write("Of all the types of landed meteorites, the L6 and H5 classes are the most commonly found.")
    one1.write("Both classes are relatively common in the asteroid belt, which is where most meteorites originate. Therefore, the higher number of L6 and H5 meteorites in the asteroid belt means that there is a greater likelihood of these types of "
               "meteorites landing on Earth.")

    ## Average Mass per meteorite class
    dff = df_meteorites.groupby(['recclass'])['mass (g)'].mean().reset_index().set_index('recclass').sort_values(by='mass (g)', ascending=False).head(20)
    dff["mass (g)"] = dff["mass (g)"].round()
    fig_mass = px.bar(dff.sort_values(by='mass (g)', ascending=False), y="mass (g)", x=dff.index, title="<b>Meteorite Average Mass (g)</b>", text="mass (g)", height=500)
    fig_mass.update_layout(plot_bgcolor="rgba(0,0,0,0)", xaxis=dict(showgrid=False), yaxis=dict(showgrid=False, title="Average Mass (g)"), barmode="stack")
    fig_mass.update_traces(marker_color=['#E6A0C4' if y > 1000000 else '#B39EB5' for y in dff['mass (g)']])
    two1.plotly_chart(fig_mass, use_container_width=True)
    two1.write('Compared to other meteorite classes, the average mass of the "iron, IVB" class is notably high, at approximately 4,323 kilograms. this class of meteorites is primarily composed of iron, which is a dense and heavy material. This '
               'high density means that iron IVB meteorites can have a relatively large mass for their size, especially when compared to stony meteorites that have a lower density')

    st.markdown("---")
    st.subheader("Changes over the years")
    one2, two2 = st.columns(2)

    ## Landings over time
    df_from_1970_2013 = df_meteorites.loc[(df_meteorites["year"] >= 1970) & (df_meteorites["year"] <= 2013)]
    df_from_1970_2013 = df_from_1970_2013.groupby(['year'])['id'].count().reset_index().set_index('year')
    df_from_1970_2013 = df_from_1970_2013.rename(columns={"id": "# of Meteorites"})

    # Set a new color palette
    colors = ["#1f77b4"]
    fig = px.line(df_from_1970_2013, x=df_from_1970_2013.index, y='# of Meteorites', markers=True, title="<b>Yearly Meteorite Landings</b>", color_discrete_sequence=colors)

    fig.update_yaxes(title_text="# of Meteorites")
    fig.update_layout(plot_bgcolor="rgba(0,0,0,0)")
    one2.plotly_chart(fig, use_container_width=False)
    st.write("The number of meteorite landings increased sharply in the early 2000s, possibly due to increased efforts in meteorite hunting or advances in detection technology.")

    ## Animated Yearly landings per continent
    yearly_counts = merged_data.loc[merged_data['year'].between(1970, 2013), :]
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
            hovertemplate="Year: %{x}<br>Running Total: %{y:.0f}"
        ))
    fig.update_layout(
        title="<b>Yearly Landings per Continent</b>",
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(title="Year", showgrid=False),
        yaxis=dict(title="Running Total"),
        legend=dict(yanchor="top", y=0.99, xanchor="left", x=0.01),
        transition=dict(duration=500, easing="linear")
    )
    two2.plotly_chart(fig, use_container_width=True)

    ## average mass every year
    df_from_1980_2013_mass = df_meteorites.loc[(df_meteorites["year"] >= 1980) & (df_meteorites["year"] <= 2013)]
    df_from_1980_2013_mass = df_from_1980_2013_mass.groupby(['year'])['mass (g)'].mean().reset_index().set_index('year').sort_values(by='mass (g)', ascending=False)
    avg_mass = df_from_1980_2013_mass['mass (g)'].mean()
    df_from_1980_2013_mass["mass (g)"] = df_from_1980_2013_mass["mass (g)"].round()
    fig_mass = px.bar(df_from_1980_2013_mass.sort_values(by='mass (g)', ascending=False), y="mass (g)", x=df_from_1980_2013_mass.index, title="Yearly Average Mass of Meteorites (1980-2013)", labels={"x": "Year", "mass (g)": "Average Mass (g)"},
                      text="mass (g)", height=500)

    fig_mass.add_shape(type="line", x0=df_from_1980_2013_mass.index.min(), y0=avg_mass, x1=df_from_1980_2013_mass.index.max(), y1=avg_mass, line=dict(color="gray", width=2, dash="dot"))

    fig_mass.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        xaxis=dict(showgrid=False, tickmode='linear'),
        yaxis=dict(showgrid=False, visible=False),
        barmode="stack",
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.1,
            xanchor="right",
            x=1
        ),
        font=dict(
            family="Arial",
            size=14
        )
    )

    fig_mass.update_traces(
        marker_color=px.colors.sequential.Blues[::-1],
    )

    st.plotly_chart(fig_mass, use_container_width=True)
    st.write(
        "From 1980 to 2013, the average mass of meteorites was 2143.38 grams. It should be noted that the high average mass in the mid-1970s was a result of the limited number of recorded meteorites during that time. Moreover, "
        "recent years have shown a trend toward larger average masses, and some years have even surpassed 5 kilograms.")
    st.write("One possibility is that the gravitational pull of a nearby planet or asteroid could be influencing the trajectory of larger meteoroids and causing them to collide with Earth. Another possibility is that there could be a concentration "
             "of larger meteoroids in a particular region of space that intersects with Earth's orbit every few years. Additionally, changes in the distribution of meteoroids in the solar system, such as the breakup of a large asteroid or changes "
             "in the orbit of a comet, could also be a factor in the periodic increase in the average meteorite mass. However, without further data and analysis, it is difficult to determine the exact cause of this phenomenon.")
    st.markdown("---")
    st.subheader('Conclusion')
    st.write('In conclusion, The data shows that Antarctica has the highest number of recorded '
             'meteorite landings, followed by Oman, with several factors contributing to this trend. The L6 and H5 classes of meteorites are the most commonly found, reflecting their abundance in the asteroid belt. The "iron, '
             'IVB" class of meteorites stands out with an exceptionally high average mass, owing to their dense iron composition. Moreover, recent years have shown a trend towards larger average masses of landed meteorites, '
             'indicating a possible shift in the distribution of meteoroids in the solar system. This analysis highlights the importance of continued research and monitoring of meteorite landings to deepen our understanding of the universe and its '
             'history.')

elif page == 'Project 3: Quality Control System':
    st.header('Project 3: Quality Control System')
    st.subheader("Introduction")
    st.write(
        "This project is an Express Company Updatable Quality Control System created using Python programming language. The system is designed to analyze shipping data from an express company and identify problematic waybill numbers. It offers an automated and efficient approach to identifying and addressing quality control issues within the company's shipping operations.")
    st.write(
        "The system allows branch supervisors and management to access and review the identified problematic waybill numbers in an easily accessible manner. It provides relevant information and insights to efficiently address and resolve any issues, improving the overall quality of the shipping process.")
    st.write(
        "To update the system, a Python script utilizing the Selenium framework can be used to access the express company's platform and export the required data for analysis. This ensures that the system remains up to date with the latest shipping data, enabling accurate identification of quality control issues.")
    st.markdown("---")
    st.subheader("Dataset Overview")
    st.write(df_agency.describe(include='all'))
    st.markdown("---")
    st.subheader('Quality Control System Link')
    link = "https://abdelrahman-labs-shipping-quality-control-main-sh8g9x.streamlit.app/"
    st.markdown(f"To view the project, [click here]({link})")

elif page == 'Project 2: Fetal Health Classification':
    st.header('Project 2: Fetal Health Classification')
    st.subheader('Introduction')
    st.write(
        'The classification of fetal health plays a crucial role in prenatal care, helping medical professionals identify potential risks and take appropriate actions. In this project, we explore a dataset containing various features related to fetal health and develop a classification model to predict fetal health status based on these attributes.')

    # Link to source code and analysis steps
    link = 'https://www.kaggle.com/code/rahman96/fetal-health-classification'
    st.markdown(f"To access the source code and analysis steps, click [here]({link})")

    st.markdown("---")
    st.subheader("Dataset Overview")

    ## Dataset summary
    st.write(df_fetal_health.describe(include='all'))

    st.markdown("---")
    st.subheader("Fetal Health Classification Model")

    ## Model performance
    st.write("Best model: LGBMClassifier")
    st.write("Model accuracy: 94.82%")

    # Link to model download
    st.markdown(f"To download the trained classification model, click [here]({link})")

elif page == 'Project 4: Customer Dashboard':
    st.header('Project 4: Customer Dashboard')
    st.subheader("Introduction")
    st.write(
        "The Customer Dashboard is a Python and Streamlit-based web application specifically developed for the operation department members of a domestic shipping company. It serves as a powerful tool to identify and address issues faced by the company's top 10 customers during any selected timeframe.")
    st.markdown("---")
    st.subheader("Key Features:")
    st.write("- Comprehensive Indicators: The dashboard provides a range of indicators to monitor customer performance, including on-time delivery, on-time sign rates, sign rates, and overcapacity shipments.")
    st.write("- Agency and Branch Analysis: The dashboard allows users to dive deeper into the data by exploring abnormal reasons for delayed shipments, categorized by agencies and branches within the company.")
    st.write(
        "By utilizing this customer dashboard, the operation department members can efficiently track the performance of their top customers, identify potential challenges, and take proactive measures to ensure smooth operations and customer satisfaction.")
    st.markdown("---")
    st.subheader('Customer Dashboard Link')
    st.write('You can access the Customer Dashboard [here](https://cstdashboardpf-xh6mqv8x3q.streamlit.app/).')


elif page == 'Contact':
    st.header('Contact')
    st.subheader('Get in touch with me!')
    st.write("If you have any questions, feedback, or collaboration opportunities, please feel free to reach out to me using the contact information below.")

    st.markdown('**Name:** Abdelrahman Mahmoud Zaki')
    st.markdown('**Email:** a.rahman.mahmoud195@gmail.com')
    st.markdown('**LinkedIn:** [LinkedIn Profile](https://www.linkedin.com/in/a-rahman-mahmoud-642464136)')
    st.markdown('**GitHub:** [GitHub Profile](https://github.com/abdelrahman-labs)')

# Add footer
st.markdown("---")
st.markdown(
    """
    <style>
    .footer {
        display: flex;
        flex-direction: row;
        justify-content: center;
        align-items: center;
        padding: 10px;
        background-color: #e9ecef;
        font-size: 12px;
        color: #555555;
    }
    .footer a {
        color: #555555;
        text-decoration: none;
        margin-left: 5px;
        margin-right: 5px;
    }
    .footer a:hover {
        color: #333333;
    }
    </style>
    """
    "<div class='footer'>"
    "Created by A.Rahman | "
    "<a href='https://www.linkedin.com/in/a-rahman-mahmoud-642464136'>Linkedin</a> | "
    "<a href='mailto:a.rahman.mahmoud195@gmail.com'>Contact</a>"
    "</div>",
    unsafe_allow_html=True,
)
