
import { NavLink } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { 
  Home, BookOpen, FileText, CheckSquare, 
  Calendar, Activity, BrainCircuit,
  Users, Settings, LogOut, Target
} from 'lucide-react';

const Sidebar = () => {
  const { user, logout } = useAuth();

  const getLinks = () => {
    const role = user?.role || 'STUDENT';
    const baseUrl = `/${role.toLowerCase()}`;

    if (role === 'STUDENT') {
      return [
        { name: 'Dashboard', path: `${baseUrl}/dashboard`, icon: Home },
        { name: 'Courses', path: `${baseUrl}/courses`, icon: BookOpen },
        { name: 'Assignments', path: `${baseUrl}/assignments`, icon: FileText },
        { name: 'Quizzes', path: `${baseUrl}/quizzes`, icon: CheckSquare },
        { name: 'Attendance', path: `${baseUrl}/attendance`, icon: Calendar },
        { name: 'Knowledge Tracing', path: `${baseUrl}/knowledge`, icon: Target },
      ];
    } else if (role === 'INSTRUCTOR') {
      return [
        { name: 'Dashboard', path: `${baseUrl}/dashboard`, icon: Home },
        { name: 'Courses', path: `${baseUrl}/courses`, icon: BookOpen },
        { name: 'Topics', path: `${baseUrl}/topics`, icon: BookOpen },
        { name: 'Quiz Mgmt', path: `${baseUrl}/quiz`, icon: CheckSquare },
        { name: 'Assignments', path: `${baseUrl}/assignments`, icon: FileText },
        { name: 'Attendance', path: `${baseUrl}/attendance`, icon: Calendar },
        { name: 'Predictions', path: `${baseUrl}/predictions`, icon: Activity },
        { name: 'Fatigue Monitor', path: `${baseUrl}/fatigue`, icon: BrainCircuit },
        { name: 'Knowledge Tracing', path: `${baseUrl}/knowledge`, icon: Target },
      ];
    } else if (role === 'ADMIN') {
      return [
        { name: 'Dashboard', path: `${baseUrl}/dashboard`, icon: Home },
        { name: 'Users', path: `${baseUrl}/users`, icon: Users },
        { name: 'Courses', path: `${baseUrl}/courses`, icon: BookOpen },
        { name: 'Topics', path: `${baseUrl}/topics`, icon: BookOpen },
        { name: 'Quiz Mgmt', path: `${baseUrl}/quiz`, icon: CheckSquare },
        { name: 'Predictions', path: `${baseUrl}/predictions`, icon: Activity },
        { name: 'System Monitor', path: `${baseUrl}/system`, icon: Settings },
        { name: 'Knowledge Tracing', path: `${baseUrl}/knowledge`, icon: Target },
      ];
    }
    return [];
  };

  const links = getLinks();

  return (
    <aside className="w-64 bg-dark-card border-r border-dark-border h-full flex flex-col relative z-20">
      <div className="p-6 border-b border-dark-border">
        <div className="flex items-center gap-3 text-primary-400">
          <BrainCircuit className="h-8 w-8" />
          <h1 className="text-xl font-bold text-white tracking-wide">SOUL LMS</h1>
        </div>
        <p className="text-xs text-gray-400 mt-2 font-medium tracking-wider uppercase">{user?.role} Portal</p>
      </div>

      <nav className="flex-1 overflow-y-auto py-6 px-3 space-y-2">
        {links.map((link) => {
          const Icon = link.icon;
          return (
            <NavLink
              key={link.path}
              to={link.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                  isActive 
                    ? 'bg-primary-500/10 text-primary-400 shadow-[inset_0_0_0_1px_rgba(16,185,129,0.2)] relative after:absolute after:left-0 after:top-1/2 after:-translate-y-1/2 after:w-1.5 after:h-8 after:bg-primary-500 after:rounded-r-full' 
                    : 'text-gray-400 hover:bg-white/5 hover:text-white'
                }`
              }
            >
              <Icon className={`h-5 w-5 transition-transform duration-200`} />
              {link.name}
            </NavLink>
          );
        })}
      </nav>

      <div className="p-4 border-t border-dark-border mt-auto">
        <button 
          onClick={logout}
          className="flex items-center gap-3 w-full px-3 py-3 text-sm font-medium text-gray-400 rounded-xl hover:bg-red-500/10 hover:text-red-400 transition-colors"
        >
          <LogOut className="h-5 w-5" />
          Sign Out
        </button>
      </div>
    </aside>
  );
};

export default Sidebar;
