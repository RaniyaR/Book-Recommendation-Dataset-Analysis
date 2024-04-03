
import dash
from dash import dcc, html, Input, Output
import pandas as pd
import plotly.graph_objects as go


# Load datasets + Preprocessing
books_df = pd.read_csv('Books.csv', nrows=1000)
books_df = books_df.dropna(subset=['Year-Of-Publication'])
ratings_df = pd.read_csv('Ratings.csv')
users_df = pd.read_csv('Users.csv', nrows=1000)
books_copy = pd.read_csv('Books.csv', nrows=30000)

merged_df = pd.merge(ratings_df, books_df, on='ISBN')
merged_df = merged_df.dropna(subset=['Book-Rating'])
merged_df = merged_df.groupby('Book-Title').filter(lambda x: len(x) > 1)

users_df['Country'] = users_df['Location'].str.split(',').str[-1].str.strip()
users_df['Country'] = users_df['Country'].str.replace('"', '')
unique_countries = users_df['Country'].unique()
filtered_countries = [country for country in unique_countries if country not in ['lj', 'quit', '', ' ', 'somewherein space', 'distrito federal', 'london', 'españa','germany', 'russia', 'slovenia', 'peru', 'u.a.e', 'colombia', 'sweden', 'bulgaria', 'albania', 'poland']]
n = len(filtered_countries) // 3
countries1 = filtered_countries[:n]
countries2 = filtered_countries[n:2*n]
countries3 = filtered_countries[2*n:]

all_df = pd.merge(books_df, ratings_df, on='ISBN')
all_df = pd.merge(all_df, users_df, on='User-ID')
all_df = all_df.dropna(subset=['Book-Rating'])
all_df = all_df.dropna(subset=['Age'])
all_df = all_df.groupby('Book-Title').filter(lambda x: len(x) > 1)


age_brackets = [(10, 14), (15, 19), (20, 24), (25, 29), (30, 34), (35, 39), (40, 44), (45, 49), (50, 54),
                (55, 59), (60, 64), (65, 69), (70, 74), (75, 79)]

app = dash.Dash(__name__, suppress_callback_exceptions=True)
# Dash layout
app.layout = html.Div([
    dcc.Tabs(id='tabs', value='tab-1', children=[
        dcc.Tab(label='Book Rating Distribution', value='tab-1', className='tabs-selected'),
        dcc.Tab(label='Age Distribution by Location', value='tab-2', className='tabs-selected'),
        dcc.Tab(label='Publication Trends by Year', value='tab-3', className='tabs-selected'),
        dcc.Tab(label='User Age VS Book Rating', value='tab-4', className='tabs-selected'),
    ]),
    html.Div(id='tabs-content')
])

@app.callback(Output('tabs-content', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H1("Book Rating Distribution", id='ratings'),
            dcc.Dropdown(
                id='book-dropdown',
                options=[{'label': title, 'value': title} for title in merged_df['Book-Title'].unique()],
                value=None,
                placeholder="Select a book",
                style={'height': '60px', 'width': '1500px', 'font-size': '28px'}

            ),
            dcc.Graph(id='rating-distribution',
                      figure= {
                          'layout': {
                            'xaxis': {'title': 'Rating', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}, 'range': [0.5, 10.5]},
                            'yaxis': {'title': 'Frequency', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}},
                            'autosize': False,
                            'autoscale': True,
                            'width': 1500,
                            'height': 800,
                            'bargap': 0.2
                          }
                      }),
        ], style={'width': '50%', 'height': '50%', 'position': 'absolute', 'top': '25%', 'left': '25%'})
    elif tab == 'tab-2':
        return html.Div([
            html.H1("Age Distribution by Location", id='ages'),
            html.Div([
                html.Div([
                    dcc.Checklist(
                    id='country-checklist1',
                    options=[{'label': country, 'value': country} for country in countries1],
                    value=[countries1[0]],
                ),], style={'display': 'inline-block'}),
                html.Div([
                    dcc.Checklist(
                    id='country-checklist2',
                    options=[{'label': country, 'value': country} for country in countries2],
                    value=[countries2[0]],
                ),], style={'display': 'inline-block'}),
                html.Div([
                    dcc.Checklist(
                    id='country-checklist3',
                    options=[{'label': country, 'value': country} for country in countries3],
                    value=[countries3[0]],
                ),], style={'display': 'inline-block'}),
                ]),
                dcc.Graph(id='age-distribution',),
            ], style={'width': '50%', 'height': '50%', 'position': 'absolute', 'top': '25%', 'left': '25%'})
    elif tab == 'tab-3':
        return html.Div([
            html.H1("Publication Trends by Year", id='publishers'),
            dcc.Dropdown(
                id='publisher-dropdown',
                options=[{'label': publisher, 'value': publisher} for publisher in books_copy['Publisher'].unique()],
                value=None,
                placeholder="Select a publisher",
                style={'height': '60px', 'width': '1500px', 'font-size': '28px'}

            ),
            dcc.Graph(id='publisher-chart'),
        ], style={'width': '50%', 'height': '50%', 'position': 'absolute', 'top': '25%', 'left': '25%'})
    elif tab == 'tab-4':
        return html.Div([
            html.H1("User Age VS Book Rating", id='user-age'),
            dcc.Dropdown(
                id='bk-dropdown',
                options=[{'label': title, 'value': title} for title in all_df['Book-Title'].unique()],
                value=None,
                placeholder="Select a book",
                style={'height': '60px', 'width': '1500px', 'font-size': '28px'}
            ),
            dcc.Graph(id='user-age-chart'),
        ], style={'width': '50%', 'height': '50%', 'position': 'absolute', 'top': '25%', 'left': '25%'})


@app.callback(
    Output('rating-distribution', 'figure'),
    [Input('book-dropdown', 'value'), Input('tabs', 'value')]
)
def update_chart(selected_book, selected_tab):
    if selected_tab == 'tab-1' and selected_book:
        book_data = merged_df[merged_df['Book-Title'] == selected_book]
        rating_counts = book_data['Book-Rating'].value_counts().sort_index()
        rating_counts = rating_counts.reindex(range(1, 11), fill_value=0)
        colors = ['#FF8BA7', '#C3F0CA'] * (len(rating_counts) // 2)

        fig = {
            'data': [{'x': rating_counts.index, 'y': rating_counts.values, 'type': 'bar', 'marker': {'color': colors}}],
            'layout': {
                'title': {'text':f'Rating Distribution for {selected_book}', 'font': {'size': 35, 'family': 'Poppins'}},
                'xaxis': {'title': 'Rating', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}, 'range': [0.5, 10.5]},
                'yaxis': {'title': 'Frequency', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}},
                'autosize': False,
                'autoscale': True,
                'width': 1500,
                'height': 800,
                'bargap': 0.2
            }
        }
        return fig
    else:
        return {'data': [], 'layout': {
            'xaxis': {'title': 'Rating', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}, 'range': [0.5, 10.5]},
            'yaxis': {'title': 'Frequency', 'titlefont': {'size': 30, 'family': 'Poppins'}, 'tickfont': {'size': 25, 'family': 'Poppins'}},
            'autosize': False,
            'autoscale': True,
            'width': 1500,
            'height': 800,
            'bargap': 0.2
        }}
    
@app.callback(
    Output('age-distribution', 'figure'),
    [Input('country-checklist1', 'value'), Input('country-checklist2', 'value'), Input('country-checklist3', 'value'), Input('tabs', 'value')]
)
def update_age_chart(selected_countries1, selected_countries2, selected_countries3, selected_tab):
    if selected_tab == 'tab-2':
        selected_countries = selected_countries1 + selected_countries2 + selected_countries3
        user_data_df = users_df[users_df['Country'].isin(selected_countries)]
        def get_age_bracket(age):
            for bracket in sorted(age_brackets):
                if bracket[0] <= age <= bracket[1]:
                    return bracket[0]
            return None
        user_data_df['Age-Bracket'] = user_data_df['Age'].apply(get_age_bracket)
        age_bracket_mapping = {bracket[0]: str(bracket) for bracket in sorted(age_brackets)}



        fig = go.Figure()

        for country in selected_countries:
            country_df = user_data_df[user_data_df['Country'] == country]
            
            fig.add_trace(go.Histogram(
                x=country_df['Age-Bracket'],
                name=country,  
                histnorm='percent' 
            ))
        fig.update_xaxes(tickvals=list(age_bracket_mapping.keys()), ticktext=list(age_bracket_mapping.values()))

        fig.update_layout(
            
            xaxis=dict(
            title_text='Age Bracket',
            title_font=dict(
            size=30, 
                ),
            ),      
            yaxis=dict(
            title_text='Percentage',
            title_font=dict(
            size=30,  
                ),
            ),
            bargap=0,
            bargroupgap=0.02,
            barmode='stack',
            width=1500,
            height=800,
            font=dict(
                family='Poppins',
                size=25
            ),
        )
        return fig
@app.callback(
    Output('publisher-chart', 'figure'),
    [Input('publisher-dropdown', 'value'), Input('tabs', 'value')]
)
def update_publisher_chart(selected_publisher, selected_tab):
    if selected_tab == 'tab-3':
        publisher_df = books_copy[books_copy['Publisher'] == selected_publisher]
        publisher_counts = publisher_df.groupby('Year-Of-Publication').size()
        fig = go.Figure(data=go.Scatter(x=publisher_counts.index, y=publisher_counts.values, mode='lines', line=dict(color='#FF7F7F', width=5)))
        fig.update_layout(
            xaxis_title='Year',
            yaxis_title='Number of Publications',
            width=1500,
            height=800,
            font=dict(
                family='Poppins',
                size=25
            ),
            plot_bgcolor='white',
            xaxis=dict(
                gridcolor='lightgray',
            ),
            yaxis=dict(
                gridcolor='lightgray',
            ),
        )
        return fig

@app.callback(
    Output('user-age-chart', 'figure'),
    [Input('bk-dropdown', 'value'), Input('tabs', 'value')]
)
def update_user_age_chart(selected_book, selected_tab):
    if selected_book is None or selected_tab is None:
        fig = go.Figure()
        fig.update_layout(
            xaxis_title='Age',
            yaxis_title='Rating',
            font=dict(
                family='Poppins',
                size=25
            ),
            width=1500,
            height=800,
            plot_bgcolor='white',
            xaxis=dict(
                gridcolor='lightgray',
            ),
            yaxis=dict(
                gridcolor='lightgray',
            ),
        )
        return fig 

    if selected_tab == 'tab-4':
        book_data = all_df[all_df['Book-Title'] == selected_book]
        book_data = book_data.dropna(subset=['Age', 'Book-Rating'])
        fig = go.Figure()

        age_groups = [(10, 15), (16, 20), (21, 25), (26, 30), (31, 35), (36, 40), (41, 45), (46, 50), (51, 55), (56, 60), (61, 65), (66, 70), (71, 75), (76, 80), (81, 85), (86, 90), (91, 95), (96, 100)]
        group_names = ['10-15', '16-20', '21-25', '26-30', '31-35', '36-40', '41-45', '46-50', '51-55', '56-60', '61-65', '66-70', '71-75', '76-80', '81-85', '86-90', '91-95', '96-100']

        for group, name in zip(age_groups, group_names):
            group_data = book_data[(book_data['Age'] >= group[0]) & (book_data['Age'] <= group[1])]
            fig.add_trace(go.Scatter(
                x=group_data['Age'], 
                y=group_data['Book-Rating'], 
                mode='markers',
                marker=dict(size=15),
                name=name
            ))

        fig.update_layout(
            xaxis_title='Age', 
            yaxis_title='Rating',
            font=dict(
                family='Poppins', 
                size=25
                ), 
                width=1500, 
                height=800,
            plot_bgcolor='white',
            xaxis=dict(
                gridcolor='lightgray',
            ),
            yaxis=dict(
                gridcolor='lightgray',
            ),
        )
        return fig
    

if __name__ == '__main__':
    app.run_server(debug=True)
