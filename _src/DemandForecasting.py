import pandas as pd
import numpy as np
from prophet import Prophet
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import praw
from datetime import datetime, timedelta
from statsforecast.adapters.prophet import AutoARIMAProphet

# Reddit API setup
reddit = praw.Reddit(
    client_id='SkU-NWalPVvpptffRjcYSQ',
    client_secret='-ag_R_M2VcgyYJXIYLyVkbyFk9YLsw',
    user_agent='demand'
)

def fetch_reddit_data(search_term, days=365):  # Increased to 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = []
    subreddit = reddit.subreddit(search_term)
    try:
        posts = subreddit.search(search_term, limit=1000, sort='new')  # Increased limit
        
        for post in posts:
            post_date = datetime.fromtimestamp(post.created_utc)
            if start_date <= post_date <= end_date:
                interest_score = post.score + post.num_comments
                data.append({'date': post_date.date(), 'interest': interest_score})
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.groupby('date').agg({'interest': 'sum'}).reset_index()
            df = df.rename(columns={'date': 'ds', 'interest': 'y'})
            df = df.sort_values('ds')
        return df
    except Exception as e:
        print(f"Error fetching Reddit data: {e}")
        return pd.DataFrame(columns=['ds', 'y'])

def train_model_and_forecast(data):
    if len(data) < 2:
        return None, None
    
    model = AutoARIMAProphet(yearly_seasonality=True, weekly_seasonality=True, daily_seasonality=False)
    # model = AutoARIMAProphet()
    model.fit(data)
    
    future_dates = model.make_future_dataframe(periods=50)
    forecast = model.predict(future_dates)
    return model, forecast.tail(50)[['ds', 'yhat']]

app = Dash(__name__)

app.layout = html.Div([
    html.H1("Product Interest Forecast based on Reddit Activity"),
    dcc.Input(id='search-term', type='text', placeholder='Enter product name...'),
    html.Button('Update Forecast', id='update-button', n_clicks=0),
    dcc.Graph(id='forecast-graph'),
    html.Div(id='forecast-table'),
    html.Div(id='error-message')
])

@app.callback(
    [Output('forecast-graph', 'figure'),
     Output('forecast-table', 'children'),
     Output('error-message', 'children')],
    [Input('update-button', 'n_clicks')],
    [State('search-term', 'value')]
)
def update_dashboard(n_clicks, search_term):
    if not search_term:
        return go.Figure(), None, "Please enter a product name"
    
    try:
        data = fetch_reddit_data(search_term)
        if data.empty:
            return go.Figure(), None, f"No data found for '{search_term}'. Try a different product name."
        
        if len(data) < 2:
            return go.Figure(), None, f"Not enough data for '{search_term}' to make a forecast. Try a more popular product."
        
        model, forecast = train_model_and_forecast(data)
        if model is None:
            return go.Figure(), None, f"Unable to create a forecast for '{search_term}'. Not enough data."
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data['ds'], y=data['y'], mode='markers', name='Historical Data'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
        fig.update_layout(title=f'50-Day Interest Forecast for "{search_term}"', 
                          xaxis_title='Date', yaxis_title='Interest Score')
        
        table = html.Table([
            html.Thead(html.Tr([html.Th(col) for col in ['Date', 'Forecast']])),
            html.Tbody([
                html.Tr([
                    html.Td(forecast.iloc[i]['ds'].strftime('%Y-%m-%d')),
                    html.Td(f"{forecast.iloc[i]['yhat']:.2f}")
                ])
                for i in range(10)
            ])
        ])
        
        return fig, table, None
    except Exception as e:
        print(f"Error in update_dashboard: {e}")
        return go.Figure(), None, f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run_server(debug=True)
