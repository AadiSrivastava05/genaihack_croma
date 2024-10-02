import React, { useState, useEffect } from 'react';
import { Bar } from 'react-chartjs-2';
import axios from 'axios';
import { Chart as ChartJS, CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend);

const BarChart = () => {
  const [chartData, setChartData] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Make sure the port and URL match your backend's
    axios.get('http://localhost:5006/api/data')
      .then((response) => {
        console.log('Response from backend:', response.data); // Log the response

        const data = response.data;

        if (data && data.labels && data.data) {
          setChartData({
            labels: data.labels,
            datasets: [
              {
                label: 'Number of Transactions',
                data: data.data,
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1,
              },
            ],
          });
        } else {
          throw new Error('Data format is incorrect');
        }
      })
      .catch((error) => {
        console.error('Error fetching data:', error);
        setError(error.message);
      })
      .finally(() => {
        setLoading(false);
      });
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <div>
      <h2>Loyalty Points vs Number of Transactions</h2>
      <Bar
        data={chartData}
        options={{
          responsive: true,
          plugins: {
            legend: {
              position: 'top',
            },
            title: {
              display: true,
              text: 'Number of Transactions per Loyalty Points Range',
            },
          },
        }}
      />
    </div>
  );
};

export default BarChart;
