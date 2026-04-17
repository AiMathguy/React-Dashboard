import { useState } from "react";
import Sidebar from "./components/dashboards/layouts/Sidebar";
import Header from "./components/dashboards/layouts/Header";
import KPIGrid from "./components/dashboards/KPIGrid";
import UserGrowthChart from "./components/charts/UserGrowthChart";
import UsersByStatusChart from "./components/charts/UsersByStatusChart";
import DailyLoginsChart from "./components/charts/DailyLoginsChart";
import UsersByRoleChart from "./components/charts/UsersByRoleChart";
import ImportantUsersTable from "./components/dashboards/ImportantUsersTable";
import RecentActivity from "./components/dashboards/RecentActivity";
import Login from "./Login";
import MLRiskTable from "./components/dashboards/MLRiskTable";

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(
    !!localStorage.getItem("token")
  );

  if (!isAuthenticated) {
    return <Login onLogin={() => setIsAuthenticated(true)} />;
  }

  return (
    <div className="min-h-screen bg-[#F5F7FB] text-slate-900">
      <div className="flex min-h-screen">
        <Sidebar />

        <div className="flex min-w-0 flex-1 flex-col">
          <main className="flex-1 space-y-8 p-8">
            <Header />
            <KPIGrid />

            <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <UserGrowthChart />
              <UsersByStatusChart />
              <DailyLoginsChart />
              <UsersByRoleChart />
            </section>

            <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <ImportantUsersTable />
              <MLRiskTable />
            </section>

            <section className="grid grid-cols-1 gap-6 md:grid-cols-2">
              <RecentActivity />
              <div />
            </section>
          </main>
        </div>
      </div>
    </div>
  );
}