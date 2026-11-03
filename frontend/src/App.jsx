import { useEffect, useState } from "react";

import ExportButtons from "./components/ExportButtons";
import NotesDisplay from "./components/NotesDisplay";
import TopicForm from "./components/TopicForm";
import { downloadNotes, generateNotes, getModels, getOptions } from "./services/api";

const EMPTY_OPTIONS = { difficulties: [], notes_formats: [], optional_sections: [] };

export default function App() {
  const [models, setModels] = useState([]);
  const [options, setOptions] = useState(EMPTY_OPTIONS);
  const [selection, setSelection] = useState({
    algorithm: "logistic_regression",
    difficulty: "beginner",
    notes_format: "detailed",
    optional_sections: [],
  });
  const [notes, setNotes] = useState("");
  const [loadingSetup, setLoadingSetup] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const loadSetup = async () => {
      try {
        const [modelsResponse, optionsResponse] = await Promise.all([
          getModels(),
          getOptions(),
        ]);
        setModels(modelsResponse.models);
        setOptions(optionsResponse);
        setSelection((current) => ({
          ...current,
          algorithm: modelsResponse.models[0]?.id ?? current.algorithm,
          difficulty: optionsResponse.difficulties[0]?.id ?? current.difficulty,
          notes_format: optionsResponse.notes_formats[0]?.id ?? current.notes_format,
        }));
      } catch (setupError) {
        setError(setupError.message);
      } finally {
        setLoadingSetup(false);
      }
    };
    loadSetup();
  }, []);

  const handleGenerate = async (event) => {
    event.preventDefault();
    setGenerating(true);
    setError("");
    try {
      const response = await generateNotes(selection);
      setNotes(response.notes);
    } catch (generationError) {
      setError(generationError.message);
    } finally {
      setGenerating(false);
    }
  };
  const handleExport = async (format) => {
    setExporting(true);
    setError("");
    try {
      await downloadNotes(notes, format);
    } catch (exportError) {
      setError(exportError.message);
    } finally {
      setExporting(false);
    }
  };

  return (
    <main className="min-h-screen bg-[radial-gradient(circle_at_top_left,_#e0f2fe,_transparent_38%),linear-gradient(#f8fafc,#f1f5f9)] px-4 py-8 sm:px-6 lg:px-8">
      <div className="mx-auto max-w-6xl">
        <header className="mb-8 max-w-3xl">
          <p className="text-sm font-semibold uppercase tracking-[0.2em] text-sky-600">Machine learning study companion</p>
          <h1 className="mt-3 text-4xl font-bold tracking-tight text-slate-950 sm:text-5xl">Intelligent ML Notes</h1>
          <p className="mt-4 text-lg leading-8 text-slate-600">Generate focused classification-algorithm notes that meet you at your current level.</p>
        </header>
        {error && <div role="alert" className="mb-6 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-800">{error}</div>}
        <div className="grid items-start gap-8 lg:grid-cols-[minmax(0,0.85fr)_minmax(0,1.15fr)]">
          <TopicForm models={models} options={options} value={selection} loading={generating} disabled={loadingSetup} onChange={setSelection} onSubmit={handleGenerate} />
          <div className="space-y-4">
            <NotesDisplay notes={notes} loading={generating} />
            {notes && <ExportButtons disabled={!notes} exporting={exporting} onExport={handleExport} />}
          </div>
        </div>
      </div>
    </main>
  );
}
