import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Home from './pages/Home';
import Chat from './pages/Chat';
import MapExplore from './pages/MapExplore';
import Memories from './pages/Memories';
import Profile from './pages/Profile';
import './App.css';

function App() {
  return (
    <Router>
      <Routes>
        {/* 聊天页面独立全屏显示，无底部导航栏 */}
        <Route path="/chat" element={<Chat />} />
        
        {/* 其他页面使用Layout布局 */}
        <Route path="/*" element={
          <Layout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/map" element={<MapExplore />} />
              <Route path="/memories" element={<Memories />} />
              <Route path="/profile" element={<Profile />} />
            </Routes>
          </Layout>
        } />
      </Routes>
    </Router>
  );
}

export default App;