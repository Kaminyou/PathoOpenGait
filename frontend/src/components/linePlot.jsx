import { Line } from 'react-chartjs-2';
import { Chart, registerables } from 'chart.js';
Chart.register(...registerables);

function LinePlot({ token, dataToPlot }) {
  const data = {
    labels: dataToPlot.dates,//['2021-10-03', '2021-12-10', '2022-01-08'],
    datasets: [
      {
        label: dataToPlot.label, //'Stride Length',
        data: dataToPlot.values,//[112.4, 108.5, 109.7],
        fill: false,
        borderColor: 'rgba(204,0,0,1)',
        backgroundColor: 'rgba(204, 0, 0, 0.5)'
      },
    ],
  };

  const options = {
    aspectRatio: 3,
    scales: {
      y: {
        beginAtZero: true,
        title: {
          display: true,
          text: dataToPlot.label, //'Stride Length',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
      },
      x: {
        title: {
          display: true,
          text: 'Date',
          font: {
            size: 14,
            weight: 'bold',
          },
        },
      },
    },
  };

  return (
    <Line data={data} options={options} />
  )
};

export default LinePlot;