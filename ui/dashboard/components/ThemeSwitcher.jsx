import React, { useState } from 'react';

export default function ThemeSwitcher() {
  const [theme, setTheme] = useState('light');
  const switchTheme = (t) => {
    setTheme(t);
    document.body.setAttribute('data-theme', t);
  };
  return (
    <div className="theme-switcher">
      <button onClick={() => switchTheme('light')}>Light</button>
      <button onClick={() => switchTheme('dark')}>Dark</button>
      <button onClick={() => switchTheme('system')}>System</button>
    </div>
  );
}
