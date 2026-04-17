const items = ["Overview", "Users", "Analytics", "Activity", "Reports", "Settings"];

export default function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col bg-[#0B5FFF] text-white lg:flex">
      <div className="border-b border-white/20 px-6 py-5">
        <h1 className="text-xl font-bold">Admin Panel</h1>
        <p className="mt-1 text-sm text-blue-100">Analytics dashboard</p>
      </div>

      <nav className="flex-1 px-4 py-6">
        <ul className="space-y-3">
          {items.map((item, index) => (
            <li key={item}>
              <button
                className={`w-full rounded-xl px-4 py-3 text-left text-sm font-medium transition ${
                  index === 0
                    ? "bg-white text-[#0B5FFF] shadow-sm"
                    : "text-blue-100 hover:bg-white/10 hover:text-white"
                }`}
              >
                {item}
              </button>
            </li>
          ))}
        </ul>
      </nav>
    </aside>
  );
}