import React, { useEffect, useState } from 'react';
import api from '../api';

export default function DashboardCards() {
  const [cards, setCards] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    let mounted = true;
    api
      .get('/dashboard/cards')
      .then((res) => {
        if (!mounted) return;
        setCards(Array.isArray(res.data) ? res.data : []);
      })
      .catch((err) => {
        if (!mounted) return;
        setError(err?.message || 'Failed to load dashboard cards');
      });
    return () => {
      mounted = false;
    };
  }, []);

  return (
    <div className="dashboard-cards">
      <h3>Dashboard Cards</h3>
      {error ? <div className="error">{error}</div> : null}
      <div className="card-grid">
        {cards.map((card, i) => (
          <div key={`${card.name}-${i}`} className="card-item">
            <h4>{card.name}</h4>
            <p>{card.type}</p>
            <span>{card.status}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
