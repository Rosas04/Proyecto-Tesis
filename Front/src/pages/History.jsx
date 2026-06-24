import React, { useEffect, useState, useRef } from 'react';
import { fetchHistory } from '../historyService';

export default function History() {
  const [entries, setEntries] = useState([]);
  const [page, setPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [filter, setFilter] = useState('');
  const loader = useRef(null);

  useEffect(() => {
    const load = async () => {
      const data = await fetchHistory({ page, pageSize: 20, analysisType: filter || null });
      setEntries(prev => [...prev, ...data]);
      if (data.length < 20) setHasMore(false);
    };
    load();
  }, [page, filter]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      entries => {
        if (entries[0].isIntersecting && hasMore) {
          setPage(prev => prev + 1);
        }
      },
      { rootMargin: '200px' }
    );
    if (loader.current) observer.observe(loader.current);
    return () => observer.disconnect();
  }, [loader.current, hasMore]);

  const handleFilterChange = e => {
    setFilter(e.target.value);
    setEntries([]);
    setPage(1);
    setHasMore(true);
  };

  return (
    <div className="section">
      <h2 className="page-title">Historial de Análisis</h2>
      <select className="filter-dropdown" value={filter} onChange={handleFilterChange}>
        <option value="">Todas</option>
        <option value="typeA">Tipo A</option>
        <option value="typeB">Tipo B</option>
        {/* Add more types as needed */}
      </select>
      <ul className="history-list">
        {entries.map(entry => (
          <li key={entry.id} className="history-item">
            <strong>{new Date(entry.created_at).toLocaleString()}</strong> – {entry.analysis_type}
          </li>
        ))}
      </ul>
      {hasMore && <div ref={loader} className="infinite-scroll-loader">Cargando...</div>}
    </div>
  );
}
