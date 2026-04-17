import Card from "../ui/Card";

export default function ChartPanel({ title, subtitle, children }) {
  return (
    <Card title={title} subtitle={subtitle}>
      <div className="h-[220px]">{children}</div>
    </Card>
  );
}

