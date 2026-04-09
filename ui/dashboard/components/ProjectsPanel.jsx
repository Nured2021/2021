import React, { useEffect, useState } from 'react';
import api from '../api';

export default function ProjectsPanel() {
  const [projects, setProjects] = useState([]);
  useEffect(() => {
    api.get('/projects').then(res => setProjects(res.data));
  }, []);
  return <div className="panel projects">Projects: {projects.length}</div>;
}
