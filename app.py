from flask import Flask, jsonify, request
import syncedlyrics
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

def fetch_charts():
    """Fetch and cache chart data for India."""
    global cached_charts, last_update_time
    try:
        chart_data = ytmusic.get_charts("IN")
        response = []

        for item in chart_data.get('videos', {}).get('items', []):
            video_id = item.get('videoId') or extract_video_id(item)
            video_data = {
                "title": str(item.get('title', 'Unknown Title')),
                "videoId": str(video_id),
                "artists": [str(artist.get('name', 'Unknown Artist')) for artist in item.get('artists', [])],
                "views": str(item.get('views', 'Unknown Views')),
                "thumbnail": f"https://i.ytimg.com/vi/{video_id}/sddefault.jpg"  # Clean thumbnail URL
            }
            response.append(video_data)

        # Update cache and timestamp
        cached_charts = response
        last_update_time = datetime.now()
        return response

    except Exception as e:
        print(f"Error in fetch_charts: {e}")
        return None

def extract_video_id(item):
    """Extract video ID from thumbnail URL if videoId is invalid."""
    thumbnail_url = item.get('thumbnails', [{}])[0].get('url', '')
    if '/vi/' in thumbnail_url:
        return thumbnail_url.split('/vi/')[1].split('/')[0]
    return 'Unknown VideoID'

@app.route('/charts', methods=['GET'])
def get_charts():
    """Route to fetch YouTube music charts for India."""
    global cached_charts, last_update_time

    try:
        if cached_charts and last_update_time and datetime.now() - last_update_time < CACHE_DURATION:
            return jsonify({"Response": 200, "data": cached_charts})
        else:
            new_data = fetch_charts()
            if new_data:
                return jsonify({"Response": 200, "data": new_data})
            else:
                return jsonify({"Response": 500, "error": "Failed to fetch charts data"}), 500

    except Exception as e:
        print(f"Error in get_charts: {e}")
        return jsonify({"Response": 500, "error": "An error occurred while fetching charts"}), 500

def get_song_info(video_id):
    """Fetch song title and artist from video ID."""
    song_info = ytmusic.get_song(video_id)
    return song_info['videoDetails']['title'], song_info['videoDetails']['author']

def get_lyrics(title, artist):
    """Fetch lyrics for a song given its title and artist."""
    return syncedlyrics.search(f"{title} {artist}")

def parse_lyrics(lrc):
    """Parse synchronized lyrics into a dictionary."""
    lyrics_dict = {}
    if lrc:
        for line in lrc.split('\n'):
            if line.strip():
                try:
                    timestamp, lyric = line.split(']', 1)
                    timestamp = timestamp[1:]  # Remove the opening bracket
                    lyrics_dict[timestamp] = lyric.strip()
                except ValueError:
                    continue  # Skip lines that don't match the expected format
    return lyrics_dict

@app.route('/lyrics', methods=['GET'])
def get_lyrics_route():
    """Route to fetch lyrics for a given video ID."""
    video_id = request.args.get('video_id')
    if not video_id:
        return jsonify({"Response": 400, "error": "Missing video_id parameter"}), 400

    try:
        title, artist = get_song_info(video_id)
        lrc = get_lyrics(title, artist)
        lyrics_dict = parse_lyrics(lrc)

        # Decode byte strings for each lyric
        lyrics_dict = {time: bytes(lyric, 'utf-8').decode('utf-8') for time, lyric in lyrics_dict.items()}

        if not lyrics_dict:
            return jsonify({"Response": 404, "error": "Lyrics not found"}), 404

        response = {
            "Response": 200,
            "lyrics": lyrics_dict
        }
        return jsonify(response)

    except Exception as e:
        print(f"Error in get_lyrics_route: {e}")
        return jsonify({"Response": 500, "error": str(e)}), 500

# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=8000)
        
