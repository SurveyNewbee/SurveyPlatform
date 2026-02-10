import { Routes, Route } from 'react-router-dom';
import Header from './components/Header';
import Dashboard from './pages/Dashboard';
import SetupPage from './pages/SetupPage';
import ProjectPage from './pages/ProjectPage';
import PreviewPage from './pages/PreviewPage';

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/setup" element={<SetupPage />} />
        <Route path="/project/:projectId" element={<ProjectPage />} />
        <Route path="/project/:projectId/preview" element={<PreviewPage />} />
      </Routes>
    </div>
  );
}

export default App;
