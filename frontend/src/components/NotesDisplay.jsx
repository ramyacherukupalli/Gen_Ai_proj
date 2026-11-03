import { useEffect, useRef, useState } from "react";
import ReactMarkdown from "react-markdown";
import mermaid from "mermaid";
import rehypeKatex from "rehype-katex";
import remarkMath from "remark-math";

let diagramCounter = 0;

function MermaidDiagram({ source }) {
  const containerRef = useRef(null);
  const [error, setError] = useState(false);

  useEffect(() => {
    let cancelled = false;
    const renderDiagram = async () => {
      const id = `notes-mermaid-${diagramCounter++}`;
      try {
        mermaid.initialize({ startOnLoad: false, securityLevel: "strict", theme: "neutral" });
        const { svg } = await mermaid.render(id, source);
        if (!cancelled && containerRef.current) {
          containerRef.current.innerHTML = svg;
          setError(false);
        }
      } catch {
        if (!cancelled) setError(true);
      }
    };
    renderDiagram();
    return () => {
      cancelled = true;
    };
  }, [source]);

  if (error) {
    return (
      <pre className="my-5 overflow-x-auto rounded-xl border border-amber-200 bg-amber-50 p-4 text-sm leading-6 text-amber-950">
        <code>{source}</code>
      </pre>
    );
  }

  return <div ref={containerRef} className="my-5 overflow-x-auto rounded-xl border border-slate-200 bg-slate-50 p-4" aria-label="Generated learning diagram" />;
}

function MarkdownCode({ className, children, inline, ...props }) {
  const language = /language-(\w+)/.exec(className || "")?.[1];
  const source = String(children).replace(/\n$/, "");
  
  if (language === "mermaid") return <MermaidDiagram source={source} />;
  
  // Render inline code naturally without the block-level <pre> container
  if (inline || !className) {
    return <code className={className} {...props}>{children}</code>;
  }

  // Render standard multiline code blocks
  return (
    <pre className="my-5 overflow-x-auto rounded-xl border border-slate-700 bg-slate-900 p-4 text-sm leading-6 text-slate-100">
      <code className={className} {...props}>{source}</code>
    </pre>
  );
}

function MarkdownTable({ children }) {
  return <div className="my-5 overflow-x-auto rounded-xl border border-slate-200"><table className="min-w-full border-collapse text-left text-sm">{children}</table></div>;
}

function normalizeMathDelimiters(markdown) {
  return markdown
    .replace(/\\\[([\s\S]*?)\\\]/g, (_, formula) => `$$${formula}$$`)
    .replace(/\\\(([\s\S]*?)\\\)/g, (_, formula) => `$${formula}$`);
}

export default function NotesDisplay({ notes, loading }) {
  if (loading) {
    return (
      <section aria-live="polite" className="rounded-2xl border border-sky-100 bg-sky-50 p-8 text-center text-slate-700">
        <div className="mx-auto mb-4 h-8 w-8 animate-spin rounded-full border-4 border-sky-200 border-t-sky-600" />
        <h2 className="font-semibold text-slate-900">Building your study notes</h2>
        <p className="mt-2 text-sm">This can take a moment while the explanation is prepared.</p>
      </section>
    );
  }

  if (!notes) {
    return (
      <section className="rounded-2xl border border-dashed border-slate-300 bg-white p-8 text-center text-slate-500">
        <h2 className="font-semibold text-slate-800">Your notes will appear here</h2>
        <p className="mt-2 text-sm">Choose your study setup and select Generate notes to begin.</p>
      </section>
    );
  }

  return (
    <section className="min-w-0 overflow-hidden rounded-2xl bg-white shadow-soft">
      <div className="border-b border-slate-100 px-6 py-5 sm:px-8">
        <p className="text-sm font-semibold uppercase tracking-[0.18em] text-sky-600">Generated notes</p>
        <h2 className="mt-1 text-xl font-bold text-slate-900">Ready for review</h2>
      </div>
      <article className="max-h-[70vh] overflow-y-auto px-6 py-5 text-[0.97rem] sm:px-8 sm:py-7">
        <ReactMarkdown
          remarkPlugins={[remarkMath]}
          rehypePlugins={[rehypeKatex]}
          components={{
            code: MarkdownCode,
            table: MarkdownTable,
            th: ({ children }) => <th className="border-b border-slate-200 bg-slate-50 px-4 py-3 font-semibold text-slate-900">{children}</th>,
            td: ({ children }) => <td className="border-b border-slate-100 px-4 py-3 align-top">{children}</td>,
            h1: ({ children }) => <h1 className="mb-4 mt-2 text-2xl font-bold text-slate-950">{children}</h1>,
            h2: ({ children }) => <h2 className="mb-3 mt-6 text-xl font-bold text-slate-900">{children}</h2>,
            h3: ({ children }) => <h3 className="mb-3 mt-5 text-lg font-semibold text-slate-900">{children}</h3>,
            p: ({ children }) => <p className="my-4 leading-7 text-slate-700">{children}</p>,
            ul: ({ children }) => <ul className="my-4 list-disc space-y-2 pl-6">{children}</ul>,
            ol: ({ children }) => <ol className="my-4 list-decimal space-y-2 pl-6">{children}</ol>,
          }}
        >
          {normalizeMathDelimiters(notes)}
        </ReactMarkdown>
      </article>
    </section>
  );
}
