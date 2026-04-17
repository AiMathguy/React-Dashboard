export default function Card({ title, subtitle, children, className = "" }) {
  return (
    <div
      className={`rounded-[24px] border border-slate-200 bg-white shadow-[0_14px_35px_rgba(15,23,42,0.06)] transition-all duration-200 ease-out hover:-translate-y-1 hover:shadow-[0_20px_45px_rgba(15,23,42,0.10)] ${className}`}
    >
      {(title || subtitle) && (
        <div className="border-b border-slate-100 px-6 py-5">
          {title && <h3 className="text-xl font-semibold text-slate-900">{title}</h3>}
          {subtitle && <p className="mt-2 text-sm text-slate-500">{subtitle}</p>}
        </div>
      )}

      <div className="px-6 py-5">{children}</div>
    </div>
  );
}