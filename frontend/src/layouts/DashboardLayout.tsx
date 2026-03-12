import React, { useEffect } from 'react';
import Sidebar from './Sidebar';
import { useLocation } from 'react-router-dom';
import { activityApi } from '../api/activity';
import { useAuth } from '../context/AuthContext';

interface LayoutProps {
  children: React.ReactNode;
}

const DashboardLayout: React.FC<LayoutProps> = ({ children }) => {
  const { user } = useAuth();
  const location = useLocation();

  // Activity tracking for page views
  useEffect(() => {
    if (user && user.role === 'STUDENT') {
      activityApi.logActivity({
        course_id: 0, // 0 for global pages like dashboard
        activity_type: `page_view_${location.pathname.split('/').pop()}`,
        duration_seconds: 0 // Duration will be computed by backend or we can setup a ping timer later
      }).catch(err => console.error("Could not log activity", err));
    }
  }, [location.pathname, user]);

  return (
    <div className="flex h-screen w-full bg-dark-bg text-white overflow-hidden selection:bg-primary-500/30">
      <Sidebar />
      <main className="flex-1 overflow-y-auto relative">
        {/* Subtle background glow effect for the main content area */}
        <div className="absolute top-0 left-1/2 -translate-x-1/2 w-full h-96 bg-primary-900/10 blur-[100px] pointer-events-none -mr-20"></div>
        
        <div className="container mx-auto p-8 relative z-10 min-h-full">
          {children}
        </div>
      </main>
    </div>
  );
};

export default DashboardLayout;
