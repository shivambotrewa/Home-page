import string
from flask import Flask, jsonify
from ytmusicapi import YTMusic
import re
from datetime import datetime, timedelta
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Initialize ytmusicapi
ytmusic = YTMusic("oauth.json")

def rmpun(query):
# Characters you want to keep
    keep_chars = "-,:"
    # Remove all punctuation except characters in keep_chars
    clean_query = ''.join(char for char in query if char not in string.punctuation or char in keep_chars)
    return clean_query

def format_views(views):
    views = int(views)
    if views >= 1_000_000_000:
        return f"{views / 1_000_000_000:.1f}B"
    elif views >= 1_000_000:
        return f"{views / 1_000_000:.1f}M"
    elif views >= 1_000:
        return f"{views / 1_000:.1f}K"
    else:
        return str(views)

# Example usage

# Variables to store cached chart data and the last update time
cached_charts = None
last_update_time = None
CACHE_DURATION = timedelta(hours=12)  # 12-hour cache duration


# Function to extract videoId from thumbnail URL
def extract_video_id_from_thumbnail(url):
    match = re.search(r'/vi/([^/]+)/', url)
    if match:
        return match.group(1)
    return None

# Function to get song details using videoId
def get_song_details(video_id):
    song_data = ytmusic.get_song(video_id)
    
    # Extract song details with safe access
    title = song_data['videoDetails'].get('title','')
    artists = song_data['videoDetails'].get('author', '')
    duration = song_data['videoDetails'].get('lengthSeconds', 0)  # duration in seconds
    views = song_data['videoDetails'].get('viewCount', 'Unknown')
    sea = f"{title} {artists}"
    search = rmpun(sea)

    # Use the search method to find the YouTube Music version of the video
    search_results = ytmusic.search(search,"songs")
    
    if search_results:
        aimed_video_id = search_results[0].get('videoId')
    else:
        return None

    if aimed_video_id == 'Unknown VideoID':
        return None

    return {
        'title': title,
        'videoId': aimed_video_id,
        'artists': artists,
        'duration': duration,
        'views': views
    }

# Replace 'your_playlist_id' with the actual playlist ID
playlist_id = 'PL4fGSI1pDJn4pTWyM3t61lOyZ6_4jcNOw'

#@app.route('/get_playlist_details', methods=['GET'])
def get_playlist_details():
    global cached_charts, last_update_time
    try:
        playlist = ytmusic.get_playlist(playlist_id)
        songs = []

        # Iterate over tracks, extract videoId and get song details
        for track in playlist['tracks']:
            if 'thumbnails' in track and track['thumbnails']:
                video_id = extract_video_id_from_thumbnail(track['thumbnails'][-1].get('url'))
                if video_id:
                    song_details = get_song_details(video_id)
                    if song_details:
                        views = format_views(song_details['views'])
                        vId = song_details['videoId']
                        thumbnail = f'https://i.ytimg.com/vi/{vId}/sddefault.jpg'
                        song_data = {
                            'title': song_details['title'],
                            'videoId': vId,
                            'thumbnail': thumbnail,
                            'artists': song_details['artists'],
                            'duration': f"{int(song_details['duration']) // 60}:{int(song_details['duration']) % 60:02}",
                            'views': views
                        }
                        songs.append(song_data)

        # Cache the result after processing the entire playlist
        cached_charts = songs
        last_update_time = datetime.now()

        return songs
    except Exception as e:
        print(f"Error fetching playlist details: {e}")
        return None
    

# Route to fetch YouTube music charts for India
@app.route('/charts', methods=['GET'])
def get_charts():
    global cached_charts, last_update_time

    try:
        # Check if cached data exists and is still valid
        if cached_charts and last_update_time and datetime.now() - last_update_time < CACHE_DURATION:
            return jsonify(cached_charts)
        else:
            # Fetch new chart data and update cache
            new_data = get_playlist_details()
            if new_data:
                return jsonify(new_data)
            else:
                return jsonify({"error": "Failed to fetch charts data"}), 500

    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": "An error occurred"}), 500

# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)

    
