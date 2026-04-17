import { useEffect, useState } from "react";
import { Doughnut } from "react-chartjs-2";
import { fetchChart } from "../../api";
import ChartPanel from "./ChartPanel";

export default function UsersByStatusChart() {
  const [chartData, setChartData] = useState({
    labels: [],
    datasets: [
      {
        label: "Users by Status",
        data: [],
        backgroundColor: ["#2563EB", "#60A5FA", "#BFDBFE"],
        borderColor: "#FFFFFF",
        borderWidth: 2,
      },
    ],
  });

  useEffect(() => {
    async function loadChart() {
      try {
        const result = await fetchChart("charts/users-by-status");

        setChartData({
          labels: result.labels || [],
          datasets: [
            {
              label: result.datasets?.[0]?.label || "Users by Status",
              data: result.datasets?.[0]?.data || [],
              backgroundColor: ["#2563EB", "#60A5FA", "#BFDBFE"],
              borderColor: "#FFFFFF",
              borderWidth: 2,
            },
          ],
        });
      } catch (err) {
        console.error("Failed to load users by status chart:", err);
      }
    }

    loadChart();
  }, []);

  return (
    <ChartPanel title="Users by Status" subtitle="Current account state distribution">
      <div className="h-[220px]">
        <Doughnut
          data={chartData}
          options={{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
              legend: {
                position: "bottom",
                labels: { color: "#475569" },
              },
              tooltip: {
                backgroundColor: "#1E293B",
                titleColor: "#FFFFFF",
                bodyColor: "#CBD5E1",
              },
            },
          }}
        />
      </div>
    </ChartPanel>
  );
}