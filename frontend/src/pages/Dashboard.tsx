import { useAuth } from '../context/AuthContext';
import { Activity, BookOpen, Clock, Users, Target, CheckSquare, LayoutDashboard } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { Link } from 'react-router-dom';

const mockActivityData = [
  { name: 'Mon', hours: 2 }, { name: 'Tue', hours: 3 }, 
  { name: 'Wed', hours: 1.5 }, { name: 'Thu', hours: 4 }, 
  { name: 'Fri', hours: 2.5 }, { name: 'Sat', hours: 5 }, { name: 'Sun', hours: 3 }
];

const Dashboard = () => {
  const { user } = useAuth();
  
  return (
    <div className="space-y-8 animate-fade-in relative z-10 w-full">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">
            Welcome back, {user?.email.split('@')[0]}!
          </h1>
          <p className="text-gray-400 mt-1">Here's your learning overview for today.</p>
        </div>
        <div className="hidden md:flex items-center gap-2 px-4 py-2 bg-dark-card border border-dark-border shadow-sm rounded-lg">
          <Clock className="h-4 w-4 text-primary-400" />
          <span className="text-sm text-gray-300 font-medium">{new Date().toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' })}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div className="glass-card p-6 border-t-4 border-t-primary-500 hover:-translate-y-1 transition-transform cursor-pointer relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5">
            <BookOpen className="h-24 w-24" />
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-gray-400 text-sm font-medium">Courses</p>
              <h3 className="text-3xl font-bold text-white mt-1 drop-shadow-[0_0_10px_rgba(16,185,129,0.3)]">4</h3>
            </div>
            <div className="p-3 bg-primary-500/10 rounded-lg text-primary-400"><BookOpen className="h-6 w-6" /></div>
          </div>
        </div>
        
        <div className="glass-card p-6 border-t-4 border-t-blue-500 hover:-translate-y-1 transition-transform cursor-pointer relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5">
            {user?.role === 'STUDENT' ? <Activity className="h-24 w-24" /> : <Users className="h-24 w-24" />}
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-gray-400 text-sm font-medium">
                {user?.role === 'STUDENT' ? 'Avg Engagement' : 'Total Students'}
              </p>
              <h3 className="text-3xl font-bold text-white mt-1 drop-shadow-[0_0_10px_rgba(59,130,246,0.3)]">
                {user?.role === 'STUDENT' ? '82%' : '142'}
              </h3>
            </div>
            <div className="p-3 bg-blue-500/10 rounded-lg text-blue-400">
              {user?.role === 'STUDENT' ? <Activity className="h-6 w-6" /> : <Users className="h-6 w-6" />}
            </div>
          </div>
        </div>
        
        <div className="glass-card p-6 border-t-4 border-t-purple-500 hover:-translate-y-1 transition-transform cursor-pointer relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5">
            {user?.role === 'STUDENT' ? <Users className="h-24 w-24" /> : <BookOpen className="h-24 w-24" />}
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-gray-400 text-sm font-medium">
                {user?.role === 'STUDENT' ? 'Attendance Rate' : 'Total Course Modules'}
              </p>
              <h3 className="text-3xl font-bold text-white mt-1 drop-shadow-[0_0_10px_rgba(168,85,247,0.3)]">
                {user?.role === 'STUDENT' ? '94%' : '24'}
              </h3>
            </div>
            <div className="p-3 bg-purple-500/10 rounded-lg text-purple-400">
              {user?.role === 'STUDENT' ? <Users className="h-6 w-6" /> : <BookOpen className="h-6 w-6" />}
            </div>
          </div>
        </div>

        <div className="glass-card p-6 border-t-4 border-t-yellow-500 hover:-translate-y-1 transition-transform cursor-pointer relative overflow-hidden">
          <div className="absolute top-0 right-0 p-4 opacity-5">
            {user?.role === 'STUDENT' ? <CheckSquare className="h-24 w-24" /> : <Activity className="h-24 w-24" />}
          </div>
          <div className="flex justify-between items-start relative z-10">
            <div>
              <p className="text-gray-400 text-sm font-medium">
                {user?.role === 'STUDENT' ? 'Pending Quizzes' : 'Overall App Health'}
              </p>
              <h3 className={`text-2xl font-bold mt-2 uppercase tracking-wider ${user?.role === 'STUDENT' ? 'text-yellow-500 drop-shadow-[0_0_10px_rgba(234,179,8,0.3)]' : 'text-green-400 drop-shadow-[0_0_10px_rgba(34,197,94,0.3)]'}`}>
                {user?.role === 'STUDENT' ? '2' : 'Excellent'}
              </h3>
            </div>
            <div className={`p-3 rounded-lg ${user?.role === 'STUDENT' ? 'bg-yellow-500/10 text-yellow-400' : 'bg-green-500/10 text-green-400'}`}>
              {user?.role === 'STUDENT' ? <CheckSquare className="h-6 w-6" /> : <Activity className="h-6 w-6" />}
            </div>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 lg:col-span-2 shadow-lg">
          <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
            <Target className="h-5 w-5 text-primary-400" />
            Weekly Activity Log
          </h3>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={mockActivityData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorHours" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.5}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1F2937" vertical={false} />
                <XAxis dataKey="name" stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} tickLine={false} axisLine={false} dy={10} />
                <YAxis stroke="#9CA3AF" tick={{fill: '#9CA3AF'}} tickLine={false} axisLine={false} dx={-10} />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#111827', borderColor: '#374151', color: '#fff', borderRadius: '0.5rem' }}
                  itemStyle={{ color: '#10b981', fontWeight: 600 }}
                  labelStyle={{ color: '#9CA3AF' }}
                />
                <Area type="monotone" dataKey="hours" stroke="#10b981" strokeWidth={3} fillOpacity={1} fill="url(#colorHours)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="glass-card p-6 flex flex-col justify-between shadow-lg">
          <div>
            <h3 className="text-xl font-semibold text-white mb-6 flex items-center gap-2">
              <LayoutDashboard className="h-5 w-5 text-purple-400" />
              Quick Actions
            </h3>
            <div className="space-y-4">
              <Link to={`/${user?.role.toLowerCase()}/courses`} className="block p-4 rounded-xl bg-dark-bg border border-dark-border hover:border-primary-500 hover:bg-primary-500/10 transition-all duration-300 group">
                <div className="font-semibold text-gray-200 group-hover:text-primary-400 flex justify-between items-center">
                  Browse Courses
                  <span className="text-primary-500 opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">View available modules</div>
              </Link>
              <Link to={`/${user?.role.toLowerCase()}/assignments`} className="block p-4 rounded-xl bg-dark-bg border border-dark-border hover:border-blue-500 hover:bg-blue-500/10 transition-all duration-300 group">
                <div className="font-semibold text-gray-200 group-hover:text-blue-400 flex justify-between items-center">
                  Assignments
                  <span className="text-blue-500 opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
                </div>
                <div className="text-xs text-gray-500 mt-1">Submit your upcoming work</div>
              </Link>
              {user?.role === 'STUDENT' && (
                <Link to='/student/quizzes' className="block p-4 rounded-xl bg-dark-bg border border-dark-border hover:border-purple-500 hover:bg-purple-500/10 transition-all duration-300 group">
                  <div className="font-semibold text-gray-200 group-hover:text-purple-400 flex justify-between items-center">
                    Quizzes
                    <span className="text-purple-500 opacity-0 group-hover:opacity-100 transition-opacity">&rarr;</span>
                  </div>
                  <div className="text-xs text-gray-500 mt-1">Take active course quizzes</div>
                </Link>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
