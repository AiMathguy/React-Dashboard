import Card from "../ui/Card";

const rows = [
  {
    name: "Jane Smith",
    role: "Teacher",
    status: "Unverified",
    lastLogin: "12 days ago",
    priority: "High",
  },
  {
    name: "Neo Mokoena",
    role: "Student",
    status: "Suspended",
    lastLogin: "2 days ago",
    priority: "High",
  },
  {
    name: "Sarah Lee",
    role: "Admin",
    status: "Active",
    lastLogin: "35 days ago",
    priority: "Medium",
  },
  {
    name: "Mike Brown",
    role: "User",
    status: "Inactive",
    lastLogin: "48 days ago",
    priority: "Medium",
  },
];

function statusBadge(status) {
  const base = "rounded-full px-3 py-1 text-xs font-medium";

  if (status === "Suspended") {
    return `${base} bg-red-100 text-red-700`;
  }

  if (status === "Unverified") {
    return `${base} bg-amber-100 text-amber-700`;
  }

  if (status === "Inactive") {
    return `${base} bg-slate-200 text-slate-700`;
  }

  return `${base} bg-emerald-100 text-emerald-700`;
}

function priorityBadge(priority) {
  const base = "rounded-full px-3 py-1 text-xs font-medium";

  if (priority === "High") {
    return `${base} bg-red-100 text-red-700`;
  }

  if (priority === "Medium") {
    return `${base} bg-amber-100 text-amber-700`;
  }

  return `${base} bg-blue-100 text-blue-700`;
}

export default function ImportantUsersTable() {
  return (
    <Card
      title="Needs Attention"
      subtitle="Accounts that may require admin action"
      className="overflow-hidden"
    >
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead>
            <tr className="border-b border-slate-200 text-left text-sm text-slate-500">
              <th className="px-4 py-3 font-medium">User</th>
              <th className="px-4 py-3 font-medium">Role</th>
              <th className="px-4 py-3 font-medium">Status</th>
              <th className="px-4 py-3 font-medium">Last Login</th>
              <th className="px-4 py-3 font-medium">Priority</th>
              <th className="px-4 py-3 font-medium">Action</th>
            </tr>
          </thead>

          <tbody>
            {rows.map((row, index) => (
              <tr
                key={index}
                className="border-b border-slate-100 last:border-0 hover:bg-slate-50"
              >
                <td className="px-4 py-4 font-medium text-slate-900">{row.name}</td>
                <td className="px-4 py-4 text-slate-600">{row.role}</td>
                <td className="px-4 py-4">
                  <span className={statusBadge(row.status)}>{row.status}</span>
                </td>
                <td className="px-4 py-4 text-slate-600">{row.lastLogin}</td>
                <td className="px-4 py-4">
                  <span className={priorityBadge(row.priority)}>{row.priority}</span>
                </td>
                <td className="px-4 py-4">
                  <button className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-medium text-white hover:bg-blue-700">
                    Review
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </Card>
  );
}