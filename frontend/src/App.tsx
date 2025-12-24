import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Landing from './pages/Landing';
import Upload from './pages/Upload';
import Results from './pages/Results';
import DataBrowser from './pages/DataBrowser';
import Collaboration from './pages/Collaboration';
import Settings from './pages/Settings';
import Navigation from './components/ui/Navigation';

function App() {
  return (
    <Router>
      <div className="min-h-screen">
        <Navigation />
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/upload" element={<Upload />} />
          <Route path="/results/:experimentId" element={<Results />} />
          <Route path="/browse" element={<DataBrowser />} />
          <Route path="/collaboration" element={<Collaboration />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/shared/:shareToken" element={<Results />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
