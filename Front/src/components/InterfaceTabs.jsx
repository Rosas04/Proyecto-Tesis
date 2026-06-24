import React, { useState } from 'react';
import JSZip from 'jszip';

export default function InterfaceTabs() {
  const [interfaces, setInterfaces] = useState([]);
  const [selectedIdx, setSelectedIdx] = useState(0);

  const handleFile = async (e) => {
    const file = e.target.files[0];
    if (!file) return;
    const arrayBuffer = await file.arrayBuffer();
    const zip = await JSZip.loadAsync(arrayBuffer);
    const ifaceList = [];
    zip.forEach((relativePath, zipEntry) => {
      if (!zipEntry.dir && /\.(jsx?|tsx?|html?)$/i.test(relativePath)) {
        zipEntry.async('string').then(content => {
          ifaceList.push({ name: relativePath, content });
          // When all files processed, update state
          if (ifaceList.length === Object.keys(zip.files).filter(p => !zip.files[p].dir && /\.(jsx?|tsx?|html?)$/i.test(p)).length) {
            setInterfaces(ifaceList);
            setSelectedIdx(0);
          }
        });
      }
    });
  };

  return (
    <div className="section">
      <h2 className="page-title">Interfaces del ZIP</h2>
      <input type="file" accept=".zip" onChange={handleFile} />
      {interfaces.length > 0 && (
        <div className="tabs-container" style={{ marginTop: '20px' }}>
          <div className="tab-list" style={{ display: 'flex', gap: '8px', overflowX: 'auto' }}>
            {interfaces.map((iface, idx) => (
              <button
                key={idx}
                className={`tab-button ${idx === selectedIdx ? 'active' : ''}`}
                style={{
                  padding: '6px 12px',
                  borderRadius: '6px',
                  border: idx === selectedIdx ? '2px solid #2563eb' : '1px solid #d1d5db',
                  background: idx === selectedIdx ? '#e0f2fe' : '#fff',
                  cursor: 'pointer'
                }}
                onClick={() => setSelectedIdx(idx)}
              >
                {iface.name.split('/').pop()}
              </button>
            ))}
          </div>
          <pre style={{ marginTop: '12px', maxHeight: '400px', overflow: 'auto', background: '#f5f7fb', padding: '12px', borderRadius: '8px' }}>
            <code>{interfaces[selectedIdx].content}</code>
          </pre>
        </div>
      )}
    </div>
  );
}
