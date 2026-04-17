import { useEffect, useState } from "react";
import { Bar } from "react-chartjs-2";
import { fetchChart } from "../../api";
import ChartPanel from "./ChartPanel";

export default function UsersByRoleChart() {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: "Users by Role",
        data: [],
        backgroundColor: ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"],
        borderRadius: 10,
        borderSkipped: false,
        barThickness: 30,
        categoryPercentage: 0.6,
      },
    ],
  });

  useEffect(() => {
    async function loadChart() {
      try {
        const result = await fetchChart("charts/users-by-role");

        setChartData({
          labels: result.labels || [],
          datasets: [
            {
              label: result.datasets?.[0]?.label || "Users by Role",
              data: result.datasets?.[0]?.data || [],
              backgroundColor: ["#2563EB", "#3B82F6", "#60A5FA", "#93C5FD", "#BFDBFE"],
              borderRadius: 10,
              borderSkipped: false,
              barThickness: 30,
              categoryPercentage: 0.6,
            },
          ],
        });
      } catch (err) {
        console.error("Failed to load users by role chart:", err);
      }
    }

    loadChart();
  }, []);

  return (
    <ChartPanel title="Users by Role" subtitle="Role-based user distribution">
      <div className="h-[220px]">
        <Bar
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