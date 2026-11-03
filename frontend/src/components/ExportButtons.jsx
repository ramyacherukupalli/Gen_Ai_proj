export default function ExportButtons({ disabled, exporting, onExport }) {
  return (
    <div className="flex">
      <button type="button" disabled={disabled || exporting} onClick={() => onExport("pdf")} className="rounded-xl border border-slate-300 bg-white px-4 py-2.5 text-sm font-semibold text-slate-800 transition hover:border-slate-400 disabled:cursor-not-allowed disabled:text-slate-400">
        {exporting ? "Preparing download..." : "Download PDF"}
      </button>
    </div>
  );
}
