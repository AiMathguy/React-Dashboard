import { useState } from "react";
import { loginUser } from "./api";

export default function Login({ onLogin }) {
  const [email, setEmail] = useState("thato@example.com");
  const [password, setPassword] = useState("admin123");
  const [error, setError] = useState("");

  async function handleSubmit(e) {
    e.preventDefault();
    setError("");

    try {
      const data = await loginUser(email, password);
      onLogin(data.user);
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-[#F5F7FB] p-6">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-md rounded-[24px] border border-slate-200 bg-white p-8 shadow-[0_14px_35px_rgba(15,23,42,0.06)]"
      >
        <h1 className="text-3xl font-bold text-slate-900">Login</h1>
        <p className="mt-2 text-sm text-slate-500">
          Sign in to access the dashboard
        </p>

        {error && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div className="mt-6">
          <label className="mb-2 block text-sm font-medium text-slate-700">Email</label>
          <input
            type="email"
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
        </div>

        <div className="mt-4">
          <label className="mb-2 block text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            className="w-full rounded-xl border border-slate-300 px-4 py-3 text-sm outline-none focus:border-blue-500"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
        </div>

        <button
          type="submit"
          className="mt-6 w-full rounded-xl bg-blue-600 px-5 py-3 text-white transition hover:bg-blue-700"
        >
          Sign In
        </button>
      </form>
    </div>
  );
}