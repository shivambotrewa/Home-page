from flask import Flask, jsonify
import requests
from bs4 import BeautifulSoup

app = Flask(__name__)

@app.route('/get_video_ids', methods=['GET'])
def get_video_ids():
    # URL of the website to scrape
    url = "https://www.genyt.net"
    
    # Send a GET request to fetch the page content
    response = requests.get(url)
    
    # Parse the page content using BeautifulSoup
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Find all divs with the class 'col-lg-12 col-md-12 gytbox mb-3'
    divs = soup.find_all('div', class_='col-lg-12 col-md-12 gytbox mb-3')
    
    # Extract video IDs and associate them with a number
    video_data = {}
    for i, div in enumerate(divs, start=1):
        # Find the 'a' tag within the div
        a_tag = div.find('a', href=True)
        if a_tag:
            href = a_tag['href']
            # Remove the 'https://video.genyt.net/' part to get only the video ID
            video_id = href.replace('https://video.genyt.net/', '')
            video_data[f"Video {i}"] = video_id
    
    # Return the video IDs as a JSON response
    return jsonify(video_data)

if __name__ == '__main__':
    # Bind to 0.0.0.0 to make it accessible over the network
    app.run(debug=True, host='0.0.0.0', port=5000)
