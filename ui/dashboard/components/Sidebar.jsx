import React from 'react';

export default function Sidebar({ modules = [], activeModule, onSelect }) {
  return (
    <div className="builder-sidebar">
      <div className="builder-sidebar-title">ODEX Workspace</div>
      <div className="builder-sidebar-subtitle">Tools</div>
      <nav className="builder-sidebar-nav">
        {modules.map((module) => (
          <button
            key={module}
            className={`builder-sidebar-item ${activeModule === module ? 'active' : ''}`}
            onClick={() => onSelect?.(module)}
            type="button"
          >
            {module}
          </button>
        ))}
      </nav>
    </div>
  );
}
