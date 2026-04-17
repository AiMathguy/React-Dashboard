import { useEffect, useState } from "react";
import Card from "../ui/Card";
import { fetchKPIs } from "../../api";

export default function KPIGrid() {
  const [data, setData] = useState({
    total_users: 0,
    active_users: 0,
    suspended_users: 0,
    new_users_last_7_days: 0,
  });

  useEffect(() => {
    async function loadKPIs() {
      try {
        const result = await fetchKPIs();
        setData(result);
      } catch (err) {
        console.error("Failed to load KPIs", err);
      }
    }

    loadKPIs();
  }, []);

  const cards = [
    { label: "Total Users", value: data.total_users, note: "All registered accounts" },
    { label: "Active Users", value: data.active_users, note: "Currently active" },
    { label: "Suspended", value: data.suspended_users, note: "Restricted accounts" },
    { label: "New (7d)", value: data.new_users_last_7_days, note: "Recent signups" },
  ];

  return (
    <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.label} className="h-full">
          <p className="text-sm font-medium text-slate-500">{card.label}</p>

          <h3 className="mt-4 text-4xl font-bold tracking-tight text-slate-900">
            {card.value}
          </h3>

          <div className="mt-4 h-1.5 w-14 rounded-full bg-blue-500" />

          <p className="mt-4 text-sm text-slate-400">{card.note}</p>
        </Card>
      ))}
    </div>
  );
}