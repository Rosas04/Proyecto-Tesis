/**
 * TypeBadge — Visual badge for interface type identification.
 *
 * Used in Capture.jsx and HtmlReplica.jsx to visually distinguish
 * interface types (url routes, html files, combined views, etc.).
 */

const TYPE_STYLES = {
  combined: { bg: "#eff6ff", color: "#1d4ed8", label: "ALL" },
  url:      { bg: "#f0fdf4", color: "#15803d", label: "URL" },
  html:     { bg: "#fef3c7", color: "#b45309", label: "HTML" },
  htm:      { bg: "#fef3c7", color: "#b45309", label: "HTM" },
  jsx:      { bg: "#ede9fe", color: "#7c3aed", label: "JSX" },
  tsx:      { bg: "#ede9fe", color: "#7c3aed", label: "TSX" },
  vue:      { bg: "#dcfce7", color: "#16a34a", label: "VUE" },
  js:       { bg: "#fef9c3", color: "#a16207", label: "JS" },
  ts:       { bg: "#dbeafe", color: "#2563eb", label: "TS" },
  css:      { bg: "#fce7f3", color: "#be185d", label: "CSS" },
  route:    { bg: "#f0fdf4", color: "#15803d", label: "RUTA" },
};

const DEFAULT_STYLE = { bg: "#f3f4f6", color: "#374151", label: "—" };

export function TypeBadge({ type }) {
  const key = (type || "").toLowerCase();
  const style = TYPE_STYLES[key] || DEFAULT_STYLE;

  return (
    <span
      style={{
        display: "inline-flex",
        alignItems: "center",
        justifyContent: "center",
        padding: "2px 8px",
        borderRadius: "6px",
        fontSize: "11px",
        fontWeight: 700,
        letterSpacing: "0.5px",
        backgroundColor: style.bg,
        color: style.color,
        lineHeight: "1.4",
        minWidth: "36px",
        textAlign: "center",
      }}
    >
      {style.label}
    </span>
  );
}
