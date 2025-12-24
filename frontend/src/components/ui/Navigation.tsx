import { Link, useLocation } from 'react-router-dom';
import { Home, Upload, Database, Users, Settings as SettingsIcon } from 'lucide-react';

const Navigation = () => {
  const location = useLocation();

  const navItems = [
    { path: '/', label: 'Home', icon: Home },
    { path: '/upload', label: 'Upload', icon: Upload },
    { path: '/browse', label: 'Data Browser', icon: Database },
    { path: '/collaboration', label: 'Teams', icon: Users },
    { path: '/settings', label: 'Settings', icon: SettingsIcon },
  ];

  const isActive = (path: string) => location.pathname === path;

  return (
    <nav className="glass-card m-4 p-4">
      <div className="container mx-auto flex items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-10 h-10 bg-gradient-to-br from-purple-500 to-fuchsia-500 rounded-lg flex items-center justify-center font-bold text-xl">
            S
          </div>
          <span className="text-2xl font-bold gradient-text">SynOmix V5</span>
        </Link>

        <div className="flex items-center gap-2">
          {navItems.map((item) => {
            const Icon = item.icon;
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all duration-300 ${
                  isActive(item.path)
                    ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/50'
                    : 'hover:bg-white/10'
                }`}
              >
                <Icon size={20} />
                <span className="hidden md:inline">{item.label}</span>
              </Link>
            );
          })}
        </div>
      </div>
    </nav>
  );
};

export default Navigation;
