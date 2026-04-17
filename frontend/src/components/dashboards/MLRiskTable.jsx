import { useEffect, useState } from "react";
import Card from "../ui/Card";
import { fetchMLPredictions } from "../../api";

export default function MLRiskTable() {
  const [data, setData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadData() {
      try {
        const result = await fetchMLPredictions();
        setData(result);
      } catch (err) {
        console.error("Failed to load ML predictions:", err);
      } finally {
        setLoading(false);
      }
    }
    loadData();
  }, []);

  const getRiskColor = (prob) => {
    if (prob > 0.7) return "text-red-600";
    if (prob > 0.4) return "text-yellow-600";
    return "text-green-600";
  };

  const getBadgeClass = (level) => {
    if (level === "High") return "bg-red-100 text-red-800";
    if (level === "Medium") return "bg-yellow-100 text-yellow-800";
    return "bg-green-100 text-green-800";
  };

  const getProgressBarColor = (prob) => {
    if (prob > 0.7) return "bg-red-500";
    if (prob > 0.4) return "bg-yellow-500";
    return "bg-green-500";
  };

  // Skeleton loader
  if (loading) {
    return (
      <Card title="ML Churn Predictions" subtitle="XGBoost + SHAP explainability">
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="rounded-xl border border-slate-200 p-4 animate-pulse">
              <div className="h-5 bg-slate-200 rounded w-1/3 mb-2"></div>
              <div className="h-4 bg-slate-100 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </Card>
    );
  }

  if (!loading && data.length === 0) {
    return (
      <Card title="ML Churn Predictions" subtitle="XGBoost + SHAP explainability">
        <div className="text-center py-8">
          <p className="text-slate-500">No predictions available yet.</p>
          <p className="text-sm text-slate-400 mt-1">
            Run <code className="bg-slate-100 px-1 rounded">score_customers.py</code> to generate data.
          </p>
        </div>
      </Card>
    );
  }

  return (
    <Card title="ML Churn Predictions" subtitle="XGBoost + SHAP explainability">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {data.slice(0, 8).map((row, idx) => (
          <div
            key={idx}
            className="rounded-xl border border-slate-200 p-4 hover:shadow-md transition-shadow duration-200"
          >
            {/* Header: Name + Risk */}
            <div className="flex justify-between items-start">
              <div>
                <p className="font-semibold text-slate-900">{row.full_name}</p>
                <p className="text-sm text-slate-500">{row.email}</p>
              </div>
              <div className="text-right">
                <span
                  className={`inline-block rounded-full px-3 py-1 text-xs font-semibold ${getBadgeClass(
                    row.risk_level
                  )}`}
                >
                  {row.risk_level}
                </span>
              </div>
            </div>

            {/* Progress bar for probability */}
            <div className="mt-3">
              <div className="flex justify-between text-xs text-slate-500 mb-1">
                <span>Churn risk</span>
                <span className={`font-bold ${getRiskColor(row.churn_probability)}`}>
                  {(row.churn_probability * 100).toFixed(1)}%
                </span>
              </div>
              <div className="w-full bg-slate-100 rounded-full h-2">
                <div
                  className={`h-2 rounded-full ${getProgressBarColor(row.churn_probability)}`}
                  style={{ width: `${row.churn_probability * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Meta tags */}
            <div className="mt-3 flex flex-wrap gap-2 text-xs">
              <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">
                {row.role}
              </span>
              <span className="rounded-full bg-slate-100 px-3 py-1 text-slate-600">
                {row.status}
              </span>
            </div>

            {/* SHAP drivers with arrows */}
            <div className="mt-3">
              <p className="mb-2 text-sm font-medium text-slate-700">Top drivers</p>
              <div className="space-y-1 text-sm">
                {row.top_features?.map((item, i) => (
                  <div key={i} className="flex items-center gap-2">
                    <span
                      className={`text-xs ${item.impact >= 0 ? "text-red-500" : "text-green-500"}`}
                    >
                      {item.impact >= 0 ? "↑" : "↓"}
                    </span>
                    <span className="text-slate-600">{item.label}</span>
                    <span className="text-xs text-slate-400 ml-auto">
                      {item.impact > 0 ? "+" : ""}
                      {item.impact.toFixed(3)}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>
    </Card>
  );
}