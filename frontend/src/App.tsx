import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ProjectList from './components/ProjectManager/ProjectList'
import ProjectDetail from './components/ProjectManager/ProjectDetail'
import ArchitectureView from './components/ArchitectureView'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/projects" replace />} />
        <Route path="projects" element={<ProjectList />} />
        <Route path="projects/:projectId" element={<ProjectDetail />}>
          <Route path="architecture" element={<ArchitectureView />} />
        </Route>
      </Route>
    </Routes>
  )
}

export default App
