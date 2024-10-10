import pandas as pd
import numpy as np
import plotly.graph_objs as go
from dash import Dash, dcc, html
from dash.dependencies import Input, Output, State
import praw
from datetime import datetime, timedelta
from googleapiclient.discovery import build
from statsmodels.tsa.statespace.sarimax import SARIMAX

# Reddit API setup --> FILL IN THE REDACTED VALUES
reddit = praw.Reddit(
    client_id='pR7-_ABfQacFRs-Xk5zApg',
    client_secret='ZbuPOkiTkSKZNTapz5N03Dw-1zXViA',
    user_agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
)

# YouTube API setup --> FILL IN THE DEVELOPER KEY
youtube = build('youtube', 'v3', developerKey='AIzaSyBW4NnpsbAjXbOfZ7r16x9NicsH00X00mA')

# Normalization functions
def normalize_score(score, min_score, max_score):
    if min_score == max_score:
        return 50
    return 1 + (score - min_score) * 99 / (max_score - min_score)

def normalize_dataframe(df, score_column):
    min_score = df[score_column].min()
    max_score = df[score_column].max()
    df['normalized_score'] = df[score_column].apply(lambda x: normalize_score(x, min_score, max_score))
    return df

# Reddit data fetching function
def fetch_reddit_data(search_term, days=365):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    data = []
    subreddit = reddit.subreddit(search_term)
    try:
        posts = subreddit.search(search_term, limit=10000, sort='new', time_filter='year')
        for post in posts:
            post_date = datetime.fromtimestamp(post.created_utc)
            if start_date <= post_date <= end_date:
                interest_score = post.score + post.num_comments
                data.append({'date': post_date.date(), 'interest': interest_score})
        
        df = pd.DataFrame(data)
        if not df.empty:
            df = df.groupby('date').agg({'interest': 'sum'}).reset_index()
            df = df.rename(columns={'date': 'ds', 'interest': 'reddit_score'})
            df = df.sort_values('ds')
        
        print(f"Collected {len(df)} days of Reddit data for '{search_term}'")
        return df
    except Exception as e:
        print(f"Error fetching Reddit data: {e}")
        return pd.DataFrame(columns=['ds', 'reddit_score'])

# YouTube data fetching function
def fetch_youtube_data(search_term, days=300):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    
    try:
        request = youtube.search().list(
            q=search_term,
            type='video',
            part='id,snippet',
            order='date',
            publishedAfter=start_date.isoformat() + 'Z',
            publishedBefore=end_date.isoformat() + 'Z',
            maxResults=50  # Limit the max results per API request
        )
        response = request.execute()
        
        data = []
        for item in response['items']:
            video_id = item['id']['videoId']
            stats_request = youtube.videos().list(part='statistics', id=video_id)
            stats_response = stats_request.execute()
            
            view_count = int(stats_response['items'][0]['statistics']['viewCount'])
            like_count = int(stats_response['items'][0]['statistics'].get('likeCount', 0))
            comment_count = int(stats_response['items'][0]['statistics'].get('commentCount', 0))
            
            interest_score = (like_count * 2) + (comment_count * 3)
            published_at = datetime.strptime(item['snippet']['publishedAt'], '%Y-%m-%dT%H:%M:%SZ')
            
            data.append({'date': published_at.date(), 'interest': interest_score})
        
        df = pd.DataFrame(data)
        df = df.groupby('date').agg({'interest': 'sum'}).reset_index()
        df = df.rename(columns={'date': 'ds', 'interest': 'youtube_score'})
        df = df.sort_values('ds')
        
        print(f"Collected {len(df)} days of YouTube data for '{search_term}'")
        return df
    except Exception as e:
        print(f"Error fetching YouTube data: {e}")
        return pd.DataFrame(columns=['ds', 'youtube_score'])

# Combine Reddit and YouTube data
def combine_data(reddit_data, youtube_data):
    if not reddit_data.empty:
        reddit_data = normalize_dataframe(reddit_data, 'reddit_score')
    else:
        reddit_data['normalized_score_x'] = 0

    if not youtube_data.empty:
        youtube_data = normalize_dataframe(youtube_data, 'youtube_score')
    else:
        youtube_data['normalized_score_y'] = 0

    combined = pd.merge(reddit_data, youtube_data, on='ds', how='outer').fillna(0)
    combined['y'] = (combined['normalized_score_x'] + combined['normalized_score_y']) / 2
    
    return combined[['ds', 'y']]

# Train SARIMAX and forecast
def train_model_and_forecast(data, forecast_days):
    if len(data) < 2:
        return None, None
    
    model = SARIMAX(data['y'], order=(1, 1, 1), seasonal_order=(1, 1, 1, 12))
    model_fit = model.fit()
    
    forecast = model_fit.forecast(steps=forecast_days)
    last_date = data['ds'].iloc[-1]
    forecast_dates = pd.date_range(last_date, periods=forecast_days+1, freq='D')[1:]

    forecast_df = pd.DataFrame({'ds': forecast_dates, 'yhat': forecast})
    return forecast_df

# Initialize Dash app
app = Dash(__name__)

app.layout = html.Div([
    html.H1("Product Interest Forecast based on Social Media Activity"),
    html.Div([
        dcc.Input(id='search-term', type='text', placeholder='Enter product name...', style={'marginRight': '10px'}),
        dcc.Input(id='forecast-days', type='number', placeholder='Forecast days (5-90)', min=5, max=90, step=1, value=5, style={'marginRight': '10px'}),
        html.Button('Update Forecast', id='update-button', n_clicks=0)
    ], style={'marginBottom': '20px'}),
    dcc.Graph(id='forecast-graph', style={'height': '80vh'}),
    html.Div(id='error-message')
])

# Callback for updating dashboard
@app.callback(
    [Output('forecast-graph', 'figure'),
     Output('error-message', 'children')],
    [Input('update-button', 'n_clicks')],
    [State('search-term', 'value'),
     State('forecast-days', 'value')]
)
def update_dashboard(n_clicks, search_term, forecast_days):
    if not search_term:
        return go.Figure(), "Please enter a product name"
    
    if not forecast_days or forecast_days < 5 or forecast_days > 90:
        return go.Figure(), "Please enter a valid number of forecast days (5-90)"
    
    try:
        reddit_data = fetch_reddit_data(search_term)
        youtube_data = fetch_youtube_data(search_term)
        combined_data = combine_data(reddit_data, youtube_data)
        
        if combined_data.empty:
            return go.Figure(), f"No data found for '{search_term}'. Try a different product name."
        
        forecast = train_model_and_forecast(combined_data, forecast_days)
        if forecast is None:
            return go.Figure(), f"Unable to create a forecast for '{search_term}'. Not enough data."
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=combined_data['ds'], y=combined_data['y'], mode='markers', name='Historical Data'))
        fig.add_trace(go.Scatter(x=forecast['ds'], y=forecast['yhat'], mode='lines', name='Forecast'))
        
        fig.update_layout(
            title=f'{forecast_days}-Day Interest Forecast for "{search_term}"', 
            xaxis_title='Date',
            yaxis_title='Interest Score',
            height=700,
            autosize=True,
            margin=dict(l=50, r=50, t=50, b=50, autoexpand=True),
        )
        
        return fig, None
    except Exception as e:
        print(f"Error in update_dashboard: {e}")
        return go.Figure(), f"An error occurred: {str(e)}"

if __name__ == '__main__':
    app.run_server(debug=False, port=8050)
