import React, { useEffect, useState } from 'react';
import api from '../api';
import AutoSystemPanel from './AutoSystemPanel';
import EngineBrainsPanel from './EngineBrainsPanel';
import EngineStatusPanel from './EngineStatusPanel';
import LiveLogsPanel from './LiveLogsPanel';
import DashboardCards from './DashboardCards';
import LivePreviewPanel from './LivePreviewPanel';
import BrainSystemPanel from './BrainSystemPanel';

export default function WorkspacePanel() {
  const [workspace, setWorkspace] = useState(null);
  useEffect(() => {
    api.get('/workspace').then(res => setWorkspace(res.data));
  }, []);
  return (
    <div className="panel workspace command-center">
      <div className="workspace-title">
        Workspace: {workspace ? workspace.name : 'Loading...'}
      </div>
      <div className="workspace-grid">
        <div className="workspace-col left">
          <BrainSystemPanel />
          <EngineStatusPanel />
          <LiveLogsPanel />
        </div>
        <div className="workspace-col center">
          <DashboardCards />
          <AutoSystemPanel />
          <EngineBrainsPanel />
        </div>
        <div className="workspace-col right">
          <LivePreviewPanel />
        </div>
      </div>
    </div>
  );
}
