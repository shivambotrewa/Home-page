from flask import Flask, jsonify
from ytmusicapi import YTMusic

# Initialize the Flask app
app = Flask(__name__)

# Initialize YTMusic API
ytmusic = YTMusic()

@app.route('/charts', methods=['GET'])
def get_charts():
    # Fetch chart data for India
    chart_data = ytmusic.get_charts("IN")
    
    # Prepare response with video metadata (videoId, title, artists, etc.)
    response = []
    for item in chart_data.get('videos', {}).get('items', []):
        video_data = {
            "title": str(item.get('title', 'Unknown Title')),
            "videoId": str(item.get('videoId', 'Unknown VideoID')),
            "artists": [str(artist.get('name', 'Unknown Artist')) for artist in item.get('artists', [])],
            "views": str(item.get('views', 'Unknown Views')),
            "thumbnail": item.get('thumbnails', [{}])[0].get('url', 'No Thumbnail')
        }
        response.append(video_data)
    
    return jsonify(response)

# Run the Flask web server
if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True, port=8000)
    
