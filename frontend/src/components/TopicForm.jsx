const labelClass = "mb-2 block text-sm font-semibold text-slate-700";

export default function TopicForm({ models, options, value, loading, disabled, onChange, onSubmit }) {
  const toggleSection = (sectionId) => {
    const optionalSections = value.optional_sections.includes(sectionId)
      ? value.optional_sections.filter((item) => item !== sectionId)
      : [...value.optional_sections, sectionId];
    onChange({ ...value, optional_sections: optionalSections });
  };

  return (
    <form onSubmit={onSubmit} className="rounded-2xl bg-white p-6 shadow-soft sm:p-8">
      <div className="mb-6">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600">Study setup</p>
        <h2 className="mt-2 text-2xl font-bold text-slate-900">Create your notes</h2>
        <p className="mt-2 text-sm leading-6 text-slate-600">Tailor the explanation to your learning goal, then generate a ready-to-review study guide.</p>
      </div>
      <div className="grid gap-5 sm:grid-cols-2">
        <label>
          <span className={labelClass}>Classification algorithm</span>
          <select value={value.algorithm} onChange={(event) => onChange({ ...value, algorithm: event.target.value })} disabled={disabled} className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-slate-900 disabled:cursor-not-allowed disabled:bg-slate-100">
            {models.map((model) => <option key={model.id} value={model.id}>{model.name}</option>)}
          </select>
        </label>
        <label>
          <span className={labelClass}>Difficulty</span>
          <select value={value.difficulty} onChange={(event) => onChange({ ...value, difficulty: event.target.value })} disabled={disabled} className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-slate-900 disabled:cursor-not-allowed disabled:bg-slate-100">
            {options.difficulties.map((option) => <option key={option.id} value={option.id}>{option.name}</option>)}
          </select>
        </label>
        <label className="sm:col-span-2">
          <span className={labelClass}>Notes format</span>
          <select value={value.notes_format} onChange={(event) => onChange({ ...value, notes_format: event.target.value })} disabled={disabled} className="w-full rounded-xl border border-slate-300 bg-white px-3 py-2.5 text-slate-900 disabled:cursor-not-allowed disabled:bg-slate-100">
            {options.notes_formats.map((option) => <option key={option.id} value={option.id}>{option.name}</option>)}
          </select>
        </label>
      </div>
      <fieldset className="mt-7">
        <legend className={labelClass}>Include optional sections</legend>
        <div className="grid gap-3 sm:grid-cols-2">
          {options.optional_sections.map((section) => (
            <label key={section.id} className="flex cursor-pointer items-center gap-3 rounded-xl border border-slate-200 p-3 text-sm text-slate-700 transition hover:border-sky-300">
              <input type="checkbox" checked={value.optional_sections.includes(section.id)} onChange={() => toggleSection(section.id)} disabled={disabled} className="h-4 w-4 rounded border-slate-300 text-sky-600" />
              {section.name}
            </label>
          ))}
        </div>
      </fieldset>
      <button type="submit" disabled={disabled || loading} className="mt-7 w-full rounded-xl bg-sky-600 px-4 py-3 font-semibold text-white transition hover:bg-sky-700 disabled:cursor-not-allowed disabled:bg-slate-400">
        {loading ? "Generating notes..." : "Generate notes"}
      </button>
    </form>
  );
}
