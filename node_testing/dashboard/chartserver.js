const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');

const app = express();
const PORT = 5006;

// Enable CORS
app.use(cors());

// Root route (optional)
app.get('/', (req, res) => {
  res.send('Backend is running!');
});

// API route to send data
app.get('/api/data', (req, res) => {
  const csvFilePath = path.join(__dirname, 'data', 'data.csv');

  // Read the CSV file
  fs.readFile(csvFilePath, 'utf8', (err, csvData) => {
    if (err) {
      console.error('Error reading CSV file:', err);
      return res.status(500).json({ error: 'Failed to read data' });
    }

    // Parse the CSV file and prepare data for the chart
    const rows = csvData.split('\n');
    const bins = {}; // Object to hold bins for 0-500, 500-1000, etc.

    // Assume first row is the header and skip it
    for (let i = 1; i < rows.length; i++) {
      const row = rows[i].split(',');
      if (row.length >= 2) {
        const loyaltyPoints = parseInt(row[0], 10);
        const transactions = parseInt(row[1], 10);

        // Determine the bin for the loyalty points
        const bin = Math.floor(loyaltyPoints / 500) * 500;
        const range = `${bin}-${bin + 500}`;

        // Add transactions to the corresponding bin
        if (!bins[range]) {
          bins[range] = 0;
        }
        bins[range] += transactions;
      }
    }

    // Prepare the data to send to the frontend
    const combinedData = Object.keys(bins).map((label, index) => ({
      label,
      value: bins[label],
    }));

    // Sort based on the lower bound of the range (the numerical value)
    combinedData.sort((a, b) => {
      const lowerA = parseInt(a.label.split('-')[0], 10);
      const lowerB = parseInt(b.label.split('-')[0], 10);
      return lowerA - lowerB; // Sort in ascending order
    });

    // Separate sorted labels and data
    const sortedLabels = combinedData.map(item => item.label);
    const sortedData = combinedData.map(item => item.value);

    res.json({
      labels: sortedLabels,
      data: sortedData,
    });
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`Server running on http://localhost:${PORT}`);
});