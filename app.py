from flask import Flask, jsonify, request
from ytmusicapi import YTMusic
from flask_cors import CORS
from datetime import datetime, timedelta

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Initialize YTMusic API
ytmusic = YTMusic("oauth.json")

# Variables to store cached chart data and the last update time
cached_charts = None
last_update_time = None
CACHE_DURATION = timedelta(hours=12)  # 12-hour cache duration

# Helper function to fetch and cache chart data
def fetch_charts():
    global cached_charts, last_update_time
    try:
        # Fetch chart data for India
        chart_data = ytmusic.get_charts("IN")
        response = []

        # Extract videoIds from the 'videos' section
        for item in chart_data.get('videos', {}).get('items', []):
            thumbnail_url = item.get('thumbnails', [{}])[0].get('url', '')

            if '/vi/' in thumbnail_url:
                video_id = thumbnail_url.split('/vi/')[1].split('/')[0]
            else:
                video_id = 'Unknown VideoID'

            # Skip unknown VideoID cases
            if video_id == 'Unknown VideoID':
                continue

            # Fetch detailed song info using the videoId
            song_data = ytmusic.get_song(video_id)

            # Extract relevant details: title, artist, duration, view count
            title = song_data['videoDetails'].get('title', 'Unknown Title')
            artist = song_data['videoDetails'].get('author', 'Unknown Artist')
            search = f"{title} {artist}"

            # Use the search method to find the YouTube Music version of the video
            search_results = ytmusic.search(search, filter="songs")
            
            if search_results:
                # Extract the video ID from the first result
                aimed_video_id = search_results[0]['videoId']
            else:
                continue

            # Skip unknown videoID cases in search results
            if aimed_video_id == 'Unknown VideoID':
                continue

            duration = song_data['videoDetails'].get('lengthSeconds', 'Unknown Duration')
            view_count = song_data['videoDetails'].get('viewCount', 'Unknown Views')

            # Convert duration from seconds to minutes and seconds
            duration_minutes = int(duration) // 60
            duration_seconds = int(duration) % 60
            formatted_duration = f"{duration_minutes}:{duration_seconds:02d}"

            # Append the information to the response
            response.append({
                'aimedVideoId': aimed_video_id,  # Aimed videoId from search result
                'title': title,
                'artist': artist,
                'duration': formatted_duration,
                'views': view_count,
                'thumbnail': f"https://i.ytimg.com/vi/{aimed_video_id}/sddefault.jpg"  # Use the aimed video ID for thumbnail
            })

        # Update cache and timestamp
        cached_charts = response
        last_update_time = datetime.now()
        return response

    except Exception as e:
        print(f"Error: {e}")
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
            new_data = fetch_charts()
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
