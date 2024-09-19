from flask import Flask, jsonify
from ytmusicapi import YTMusic
from flask_cors import CORS

# Initialize the Flask app
app = Flask(__name__)
CORS(app)
# Initialize YTMusic API
ytmusic = YTMusic()

@app.route('/charts', methods=['GET'])
def get_charts():
    # Fetch chart data for India
    chart_data = ytmusic.get_charts("IN")
    
    # Prepare response with video metadata (videoId, title, artists, etc.)
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

        video_data = {
            "title": str(item.get('title', 'Unknown Title')),
            "videoId": str(video_id),
            "artists": [str(artist.get('name', 'Unknown Artist')) for artist in item.get('artists', [])],
            "views": str(item.get('views', 'Unknown Views')),
            "thumbnail": item.get('thumbnails', [{}])[0].get('url', 'No Thumbnail')
        }
        response.append(video_data)
    
    return jsonify(response)

# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug =True, port=8000)
    
