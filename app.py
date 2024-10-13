from flask import Flask, jsonify, request
import requests
import re
from ytmusicapi import YTMusic
from flask_cors import CORS
from datetime import datetime, timedelta

# Initialize the Flask app
app = Flask(__name__)
CORS(app)

# Initialize YTMusic API
ytmusic = YTMusic()

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

        for item in chart_data.get('videos', {}).get('items', []):
            # Extract videoId from thumbnail URL if videoId is invalid
            video_id = item.get('videoId')
            if not video_id or "built-in" in str(video_id):
                thumbnail_url = item.get('thumbnails', [{}])[0].get('url', '')
                if '/vi/' in thumbnail_url:
                    video_id = thumbnail_url.split('/vi/')[1].split('/')[0]
                else:
                    video_id = 'Unknown VideoID'

            # Clean thumbnail URL to remove query parameters
            

            video_data = {
                "title": str(item.get('title', 'Unknown Title')),
                "videoId": str(video_id),
                "artists": [str(artist.get('name', 'Unknown Artist')) for artist in item.get('artists', [])],
                "views": str(item.get('views', 'Unknown Views')),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg"  # Use the cleaned thumbnail URL
            }
            response.append(video_data)

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
