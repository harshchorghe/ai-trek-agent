import React from "react";

interface MarkdownProps {
  content: string;
}

export function Markdown({ content }: MarkdownProps) {
  if (!content) return null;

  const lines = content.split("\n");
  const elements: React.ReactNode[] = [];
  
  let currentList: string[] = [];
  let currentTable: string[][] = [];
  let isParsingTable = false;

  const renderTextWithBold = (text: string) => {
    // Basic bold **text** parsing
    const parts = text.split(/\*\*(.*?)\*\*/g);
    return parts.map((part, index) => {
      if (index % 2 === 1) {
        return <strong key={index} className="font-semibold text-emerald-400">{part}</strong>;
      }
      // Parse inline `code`
      const subparts = part.split(/`(.*?)`/g);
      return subparts.map((subpart, subindex) => {
        if (subindex % 2 === 1) {
          return (
            <code key={subindex} className="px-1.5 py-0.5 rounded bg-slate-950 font-mono text-xs text-amber-300 border border-slate-800">
              {subpart}
            </code>
          );
        }
        return subpart;
      });
    });
  };

  const flushList = (key: number) => {
    if (currentList.length > 0) {
      elements.push(
        <ul key={`list-${key}`} className="list-disc pl-5 my-2.5 space-y-1 text-slate-300">
          {currentList.map((item, idx) => (
            <li key={idx} className="leading-relaxed">
              {renderTextWithBold(item)}
            </li>
          ))}
        </ul>
      );
      currentList = [];
    }
  };

  const flushTable = (key: number) => {
    if (currentTable.length > 0) {
      // Filter out separator rows like | :--- | :--- |
      const rows = currentTable.filter(
        (row) => !row.every((cell) => cell.trim().match(/^:?-+:?$/))
      );

      if (rows.length > 0) {
        const headers = rows[0];
        const bodyRows = rows.slice(1);

        elements.push(
          <div key={`table-${key}`} className="my-4 overflow-x-auto rounded-xl border border-slate-800 bg-slate-950/60 shadow-lg">
            <table className="min-w-full divide-y divide-slate-800 text-left text-xs">
              <thead className="bg-slate-900/80 text-slate-300 uppercase tracking-wider font-semibold">
                <tr>
                  {headers.map((header, idx) => (
                    <th key={idx} className="px-4 py-3 font-medium">
                      {header.trim()}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-slate-300">
                {bodyRows.map((row, rowIdx) => (
                  <tr key={rowIdx} className="hover:bg-slate-900/35 transition-colors">
                    {row.map((cell, cellIdx) => (
                      <td key={cellIdx} className="px-4 py-2.5 font-sans whitespace-pre-wrap">
                        {renderTextWithBold(cell.trim())}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        );
      }
      currentTable = [];
      isParsingTable = false;
    }
  };

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    const trimmedLine = line.trim();

    // 1. Table Parsing
    if (trimmedLine.startsWith("|") && trimmedLine.endsWith("|")) {
      flushList(i);
      isParsingTable = true;
      const cells = trimmedLine
        .split("|")
        .slice(1, -1) // remove empty elements at start and end
        .map((cell) => cell.trim());
      currentTable.push(cells);
      continue;
    } else if (isParsingTable) {
      flushTable(i);
    }

    // 2. Horizontal Rules
    if (trimmedLine.match(/^[=\-]{5,}$/)) {
      flushList(i);
      elements.push(<hr key={i} className="border-slate-800 my-4" />);
      continue;
    }

    // 3. Headings
    if (trimmedLine.startsWith("### ")) {
      flushList(i);
      elements.push(
        <h4 key={i} className="text-sm font-semibold text-slate-100 mt-4 mb-2 flex items-center gap-1.5">
          {renderTextWithBold(trimmedLine.substring(4))}
        </h4>
      );
      continue;
    } else if (trimmedLine.startsWith("## ")) {
      flushList(i);
      elements.push(
        <h3 key={i} className="text-base font-bold text-white mt-5 mb-2.5 border-b border-slate-800 pb-1 flex items-center gap-2">
          {renderTextWithBold(trimmedLine.substring(3))}
        </h3>
      );
      continue;
    } else if (trimmedLine.startsWith("# ")) {
      flushList(i);
      elements.push(
        <h2 key={i} className="text-lg font-extrabold text-white mt-6 mb-3 flex items-center gap-2">
          {renderTextWithBold(trimmedLine.substring(2))}
        </h2>
      );
      continue;
    }

    // 4. Bullet lists
    if (trimmedLine.startsWith("- ") || trimmedLine.startsWith("* ")) {
      currentList.push(trimmedLine.substring(2));
      continue;
    } else {
      flushList(i);
    }

    // 5. Empty lines
    if (trimmedLine === "") {
      elements.push(<div key={i} className="h-2" />);
      continue;
    }

    // 6. Normal Paragraph
    elements.push(
      <p key={i} className="text-sm text-slate-300 leading-relaxed mb-1.5">
        {renderTextWithBold(line)}
      </p>
    );
  }

  // Flush remaining elements
  flushList(lines.length);
  flushTable(lines.length);

  return <div className="space-y-1 font-sans">{elements}</div>;
}
