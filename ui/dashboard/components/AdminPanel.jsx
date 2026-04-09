import React from 'react';
import UserPanel from './UserPanel';
import AIPilotWorkspace from './AIPilotWorkspace';
import UsersPanel from './UsersPanel';
import BillingPanel from './BillingPanel';
import AdvancedLogsPanel from './AdvancedLogsPanel';
import SnapshotRollbackPanel from './SnapshotRollbackPanel';

export default function AdminPanel() {
  return (
    <div className="dashboard admin">
      <UserPanel />
      <AIPilotWorkspace />
      <UsersPanel />
      <BillingPanel />
      <AdvancedLogsPanel />
      <SnapshotRollbackPanel />
    </div>
  );
}
