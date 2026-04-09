import React from 'react';
import PreviewPanel from './PreviewPanel';
import ThemeSwitcher from './ThemeSwitcher';
import OdexSymbol from './OdexSymbol';
import ProjectsPanel from './ProjectsPanel';
import FilesPanel from './FilesPanel';
import ToolsPanel from './ToolsPanel';
import WorkspacePanel from './WorkspacePanel';
import EnginesPanel from './EnginesPanel';
import LogsPanel from './LogsPanel';
import SubscriptionPanel from './SubscriptionPanel';
import SupportPanel from './SupportPanel';
import FeedbackPanel from './FeedbackPanel';
import HealthPanel from './HealthPanel';
import ControlsPanel from './ControlsPanel';

export default function UserPanel() {
  return (
    <div className="dashboard user">
      <OdexSymbol />
      <ThemeSwitcher />
      <PreviewPanel />
      <div className="panels">
        <ProjectsPanel />
        <FilesPanel />
        <ToolsPanel />
        <WorkspacePanel />
        <EnginesPanel />
        <LogsPanel />
        <SubscriptionPanel />
        <SupportPanel />
        <FeedbackPanel />
        <HealthPanel />
        <ControlsPanel />
      </div>
    </div>
  );
}
