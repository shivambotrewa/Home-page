const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
app.use(cors());

app.get('/scrape-songs', async (req, res) => {
    try {
        const url = 'https://www.genyt.net/cat.php?id=10&sort=chart';
        const response = await axios.get(url);
        res.send(response.data);
    } catch (error) {
        res.status(500).send('Error fetching data');
    }
});

app.listen(8000, () => {
    console.log('Server running on port 3000');
});
