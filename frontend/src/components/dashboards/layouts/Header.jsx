import { logoutUser } from "../../../api";

export default function Header() {
  function handleLogout() {
    logoutUser();
    window.location.reload();
  }

  return (
    <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
      
      {/* Left side */}
      <div>
        <h1 className="text-3xl font-bold text-slate-900">
          Dashboard
        </h1>
        <p className="text-sm text-slate-500">
          Track users, activity, and growth from one place.
        </p>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-3">

        <input
          type="text"
          placeholder="Search users..."
          className="w-64 rounded-xl border border-slate-300 px-4 py-3 text-sm"
        />

        <button className="rounded-2xl bg-blue-600 px-5 py-3 text-white transition duration-200 hover:bg-blue-700 hover:shadow-md">
          Export
        </button>

        <button
          onClick={handleLogout}
          className="rounded-xl border border-slate-300 bg-white px-5 py-3 text-slate-700 transition hover:bg-slate-50"
        >
          Logout
        </button>

      </div>

    </header>
  );
}