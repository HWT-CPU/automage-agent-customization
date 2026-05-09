import { createBrowserRouter } from 'react-router-dom'
import App from '../App'
import { DashboardPage } from '../pages/DashboardPage'
import { DataFlowPage } from '../pages/DataFlowPage'
import { StaffWorkspacePage } from '../pages/StaffWorkspacePage'
import { ManagerWorkspacePage } from '../pages/ManagerWorkspacePage'
import { ExecutiveWorkspacePage } from '../pages/ExecutiveWorkspacePage'
import { TaskCenterPage } from '../pages/TaskCenterPage'
import { IncidentCenterPage } from '../pages/IncidentCenterPage'
import { AgentConsolePage } from '../pages/AgentConsolePage'
import { ApiDbMonitorPage } from '../pages/ApiDbMonitorPage'
import { AuditPage } from '../pages/AuditPage'
import { SettingsPage } from '../pages/SettingsPage'

export const routes = createBrowserRouter([
  {
    path: '/',
    element: <App />,
    children: [
      { index: true, element: <DashboardPage /> },
      { path: 'data-flow', element: <DataFlowPage /> },
      { path: 'staff', element: <StaffWorkspacePage /> },
      { path: 'manager', element: <ManagerWorkspacePage /> },
      { path: 'executive', element: <ExecutiveWorkspacePage /> },
      { path: 'tasks', element: <TaskCenterPage /> },
      { path: 'incidents', element: <IncidentCenterPage /> },
      { path: 'agent-console', element: <AgentConsolePage /> },
      { path: 'api-monitor', element: <ApiDbMonitorPage /> },
      { path: 'audit', element: <AuditPage /> },
      { path: 'settings', element: <SettingsPage /> },
    ],
  },
])
