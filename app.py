from flask import Flask, jsonify, request
import requests
import re
from ytmusicapi import YTMusic
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)


# Initialize YTMusic API
ytmusic = YTMusic()

chart_cache = None
last_updated = 0
CACHE_EXPIRATION = 12 * 60 * 60  # 12 hours in seconds

@app.route('/charts', methods=['GET'])
# Function to fetch and cache the charts
def fetch_charts():
    global chart_cache, last_updated
    current_time = time.time()

    # Check if cache needs to be updated
    if current_time - last_updated > CACHE_EXPIRATION:
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

                # Clean the thumbnail URL to remove query parameters
                if thumbnail_url.endswith('.jpg'):
                    thumbnail_url = thumbnail_url.split('.jpg')[0] + '.jpg'

                video_data = {
                    "title": str(item.get('title', 'Unknown Title')),
                    "videoId": str(video_id),
                    "artists": [str(artist.get('name', 'Unknown Artist')) for artist in item.get('artists', [])],
                    "views": str(item.get('views', 'Unknown Views')),
                    "thumbnail": thumbnail_url
                }
                response.append(video_data)

            # Update cache and timestamp
            chart_cache = response
            last_updated = current_time
        except Exception as e:
            print(f"Error fetching charts: {e}")
            return None  # Return None if there's an error

    return chart_cache
    
# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
