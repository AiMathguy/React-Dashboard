const API_BASE = "http://127.0.0.1:8000/api";

function getAuthHeaders() {
  const token = localStorage.getItem("token");

  return token
    ? {
        Authorization: `Bearer ${token}`,
      }
    : {};
}

export async function loginUser(email, password) {
  const res = await fetch(`${API_BASE}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Login failed");
  }

  localStorage.setItem("token", data.access_token);
  return data;
}

export async function fetchKPIs() {
  const res = await fetch(`${API_BASE}/dashboard/kpis`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Failed to fetch KPIs");
  }

  return data;
}

export async function fetchChart(endpoint) {
  const res = await fetch(`${API_BASE}/dashboard/${endpoint}`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || `Failed to fetch ${endpoint}`);
  }

  return data;
}

export async function fetchAttentionItems() {
  const res = await fetch(`${API_BASE}/dashboard/attention`, {
    headers: {
      ...getAuthHeaders(),
    },
  });

  const data = await res.json();

  if (!res.ok) {
    throw new Error(data.detail || "Failed to fetch attention items");
  }

  return data;
}

export function logoutUser() {
  localStorage.removeItem("token");
}

export async function fetchMLPredictions() {
  const token = localStorage.getItem("token");

  const res = await fetch("http://127.0.0.1:8000/api/ml/predict", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  if (!res.ok) {
    throw new Error("Failed to fetch ML predictions");
  }

  return res.json();
}