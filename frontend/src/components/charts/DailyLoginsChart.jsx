import { useEffect, useState } from "react";
import { Line } from "react-chartjs-2";
import { fetchChart } from "../../api";
import ChartPanel from "./ChartPanel";

export default function DailyLoginsChart() {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: "Daily Logins",
        data: [],
        borderColor: "#2563EB",
        backgroundColor: "rgba(37, 99, 235, 0.15)",
        pointBackgroundColor: "#2563EB",
        pointBorderColor: "#2563EB",
        tension: 0.4,
        fill: true,
        borderWidth: 2,
      },
    ],
  });

  useEffect(() => {
    async function loadChart() {
      try {
        const result = await fetchChart("charts/daily-logins");

        setChartData({
          labels: result.labels || [],
          datasets: [
            {
              label: result.datasets?.[0]?.label || "Daily Logins",
              data: result.datasets?.[0]?.data || [],
              borderColor: "#2563EB",
              backgroundColor: "rgba(37, 99, 235, 0.15)",
              pointBackgroundColor: "#2563EB",
              pointBorderColor: "#2563EB",
              tension: 0.4,
              fill: true,
              borderWidth: 2,
            },
          ],
        });
      } catch (err) {
        console.error("Failed to load daily logins chart:", err);
      }
    }

    loadChart();
  }, []);

  return (
    <ChartPanel title="Daily Logins" subtitle="Unique users logging in each day">
      <div className="h-[220px]">
        <Line
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                labels: { color: "#475569" },
              },
              tooltip: {
                backgroundColor: "#1E293B",
                titleColor: "#FFFFFF",
                bodyColor: "#CBD5E1",
              },
            },
            scales: {
              x: {
                ticks: { color: "#64748B" },
                grid: { color: "#E5E7EB" },
              },
              y: {
                beginAtZero: true,
                ticks: { color: "#64748B", precision: 0 },
                grid: { color: "#E5E7EB" },
              },
            },
          }}
        />
      </div>
    </ChartPanel>
  );
}