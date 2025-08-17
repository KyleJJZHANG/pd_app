import React from 'react';
import { useLocation, Link } from 'react-router-dom';
import { Home, MessageCircle, Map, BookOpen, User } from 'lucide-react';
import { cn } from '../lib/utils';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const location = useLocation();

  const navItems = [
    { path: '/', icon: Home, label: '首页' },
    { path: '/chat', icon: MessageCircle, label: '聊天' },
    { path: '/map', icon: Map, label: '地图' },
    { path: '/memories', icon: BookOpen, label: '记忆馆' },
    { path: '/profile', icon: User, label: '我的' },
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-amber-50 to-blue-50 flex flex-col">
      {/* Main Content */}
      <main className="flex-1 pb-20">
        {children}
      </main>

      {/* Bottom Navigation */}
      <nav className="fixed bottom-0 left-0 right-0 bg-white/80 backdrop-blur-md border-t border-amber-200/50 px-4 py-2">
        <div className="flex justify-around items-center max-w-md mx-auto">
          {navItems.map(({ path, icon: Icon, label }) => (
            <Link
              key={path}
              to={path}
              className={cn(
                "flex flex-col items-center py-2 px-3 rounded-xl transition-all duration-200",
                location.pathname === path
                  ? "text-amber-600 bg-amber-100/50 scale-110"
                  : "text-gray-500 hover:text-amber-500 hover:bg-amber-50/50"
              )}
            >
              <Icon size={24} />
              <span className="text-xs mt-1 font-medium">{label}</span>
            </Link>
          ))}
        </div>
      </nav>
    </div>
  );
};

export default Layout;