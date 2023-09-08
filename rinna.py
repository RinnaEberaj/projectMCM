#rinna project


from dash import Dash, html, dcc, Input, Output
import plotly.express as px
import pandas as pd

app = Dash(__name__)
server = app.server

app.title = "MCM7003 Data Visualization Interactive Project"

# Specify the encoding as 'ISO-8859-1' when reading the CSV file
csv_file_path = "https://raw.githubusercontent.com/RinnaEberaj/assign3MCMRinna/main/Global%20YouTube%20Statistics.csv"

# Read the CSV file from the specified path with 'ISO-8859-1' encoding
df = pd.read_csv(csv_file_path, encoding='ISO-8859-1')

# Your data transformation code here
df["Youtuber"]=df["Youtuber"].astype("string")
df["category"]=df["category"].astype("string")
df["Country"]=df["Country"].astype("string")
df["video_views_for_the_last_30_days"]=df["video_views_for_the_last_30_days"]/1000000
df["video views"]=df["video views"]/1000000000
df["subscribers_for_last_30_days"]=df["subscribers_for_last_30_days"]/1000000
df["subscribers"]=df["subscribers"]/1000000
df.rename(columns = {'subscribers':'subscribers_per_millon',
                     'subscribers_for_last_30_days':'subscribers_last_30_days_per_millon',
                    'video_views_for_the_last_30_days':'video_views_last_30_days_per_millon',
                    'video views':'video_views_per_thousands_millions'}, inplace = True)

df_views_category=df[["category","video_views_per_thousands_millions"]].groupby(by="category").sum()
df_views_category=df_views_category.sort_values(by=["video_views_per_thousands_millions"],ascending=False)

fig = px.bar(
    df_views_category, 
    x="video_views_per_thousands_millions",
    y=df_views_category.index,
    orientation='h',
    color_discrete_sequence=['red', 'white'],  # You can customize colors here
    labels={"video_views_per_thousands_millions": "Video views", "category": "Category"}
)

fig.update_layout(
    title="Category vs Video views (thousands millions)",
    xaxis_title="Video views",
    yaxis_title="Category",
    xaxis=dict(tickmode='linear', tick0=0, dtick=1000),  # Customize x-axis ticks
    yaxis=dict(tickmode='linear', tick0=0, dtick=1),  # Customize y-axis ticks
    height=600,
    width=1000,
)

# Dropdown options for selecting the number of top YouTubers
top_youtuber_options = [
    {"label": "Top 3", "value": 3},
    {"label": "Top 5", "value": 5},
    {"label": "Top 10", "value": 10},
]

# Create a callback to update the second graph based on the selected dropdown value
@app.callback(
    Output('graph-output-2', 'figure'),
    Input('top-youtuber-dropdown', 'value')
)

def update_top_youtuber_graph(selected_value):
    # Filter the DataFrame based on the selected number of top YouTubers
    df_filtered = df_views30[df_views30["Rank"] <= selected_value].sort_values(by=["Rank"])

    # Create a Plotly Express bar chart
    fig2 = px.bar(
        df_filtered,
        x="Youtuber",
        y="video_views_last_30_days_per_millon",
        color_discrete_sequence=['red', 'white'],  # You can customize colors here
        labels={"video_views_last_30_days_per_millon": "Video views", "Youtuber": "Youtuber"}
    )

    fig2.update_layout(
        title=f"Top {selected_value} YouTuber's Video Views in Last 30 Days",
        xaxis_title="Youtuber",
        yaxis_title="Video views",
        xaxis=dict(tickmode='linear', tick0=0, dtick=1),  # Customize x-axis ticks
        yaxis=dict(tickmode='linear', tick0=0, dtick=1000),  # Customize y-axis ticks
        height=600,
        width=1000,
    )

    fig2.update_xaxes(tickangle=45)
    return fig2


# Create a DataFrame for the top 5 countries with the most YouTubers
countriess = df[["Youtuber", "Country"]]
countriess = countriess.groupby("Country").agg("count")
countriess = countriess.reset_index()
countriess = countriess.sort_values(by="Youtuber", ascending=False).head()

# Define the DataFrame df_views30 globally
df_views30 = df[["Youtuber", "video_views_last_30_days_per_millon"]]
df_views30.loc[:, "Rank"] = df_views30["video_views_last_30_days_per_millon"].rank(ascending=False)
df_views30 = df_views30[df_views30["Rank"] <= 10].sort_values(by=["Rank"])

# Create a pie chart using Plotly Express
fig3 = px.pie(
    countriess,
    names="Country",
    values="Youtuber",
    title="Top 5 Countries with the Most YouTubers",
)

fig3.update_traces(
    textinfo="percent+label"
)

fig3.update_layout(
    showlegend=False,
    height=600,
    width=1000,
)

# Create another DataFrame for the top 3 countries with the most YouTubers
countriess_top3 = countriess.head(3)

# Create a pie chart for the top 3 countries
fig4 = px.pie(
    countriess_top3,
    names="Country",
    values="Youtuber",
    title="Top 3 Countries with the Most YouTubers",
)

fig4.update_traces(
    textinfo="percent+label"
)

fig4.update_layout(
    showlegend=False,
    height=600,
    width=1000,
)

app.layout = html.Div(
    [
        html.H1("Data Visualization Rinna Project"),
        
        # Tabs component
        dcc.Tabs([
            # Tab for the first graph
            dcc.Tab(label='Category vs Video Views', children=[
                dcc.Graph(id='graph-output', figure=fig),  # First graph with 'graph-output' ID
            ]),
            
            # Tab for the second graph
            dcc.Tab(label='Top YouTuber\'s Video Views', children=[
                html.Br(),
                html.Label("Select the number of top YouTubers:"),
                dcc.Dropdown(
                    id='top-youtuber-dropdown',
                    options=top_youtuber_options,
                    value=5,  # Default value
                )
                #dcc.Graph(id='graph-output-2', figure=fig2),
            ]),
            
            # Tab for the pie chart or top 3 countries pie chart
            dcc.Tab(label='Countries with Most YouTubers', children=[
                html.Div([
                    html.Br(),
                    dcc.RadioItems(
                        id='pie-chart-selector',
                        options=[
                            {'label': 'Top 3 Countries', 'value': 'fig4'},
                            {'label': 'Top 5 Countries', 'value': 'fig3'},
                        ],
                        value='fig3',  # Default selection
                        labelStyle={'display': 'block'}
                    ),
                    dcc.Graph(id='pie-chart', config={'displayModeBar': False}),  # Empty graph for initial display
                ])
            ]),
            
        ])
    ]
)

# Callback to update the pie chart based on radio button selection
@app.callback(
    Output('pie-chart', 'figure'),
    Input('pie-chart-selector', 'value')
)
def update_pie_chart(selected_chart):
    if selected_chart == 'fig3':
        return fig3
    else:
        return fig4

if __name__ == '__main__':
    app.run_server(debug=True, port=8057)
