 const express = require('express');
 const axios = require('axios');
 const cheerio = require('cheerio');

 const app = express();

 app.get('/get_video_ids', async (req, res) => {
     // URL of the website to scrape
     const url = "https://www.genyt.net";
    
     // Send a GET request to fetch the page content
const response = await axios.get(url);
    
     // Parse the page content using Cheerio
     const $ = cheerio.load(response.data);
    
     // Find all divs with the class 'col-lg-12 col-md-12 gytbox mb-3'
     const divs = $('div.col-lg-12.col-md-12.gytbox.mb-3');
    
     // Extract video IDs and associate them with a number
     const videoData = {};
     divs.each((i, div) => {
         // Find the 'a' tag within the div
         const aTag = $(div).find('a[href]');
         if (aTag.length) {
             const href = aTag.attr('href');
             // Remove the 'https://video.genyt.net/' part to get only the video ID
             const videoId = href.replace('https://video.genyt.net/', '');
             videoData[`Video ${i + 1}`] = videoId;
         }
     });
    
     // Return the video IDs as a JSON response
     res.json(videoData);
 });

 const PORT = 5000;
 app.listen(PORT, '0.0.0.0', () => {
     // Bind to 0.0.0.0 to make it accessible over the network
     console.log(`Server is running on http://0.0.0.0:${PORT}`);
 });
         
