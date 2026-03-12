import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { authApi } from '../api/auth';
import { Activity } from 'lucide-react';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setLoading(true);
    
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);
      
      const data = await authApi.login(formData as any);
      const token = data.access_token;
      
      // Simple JWT decode hack for frontend to extract user details
      try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        const user = {
          id: payload.sub || 1, // Assume sub carries ID if not string
          email: email,
          role: payload.role || 'STUDENT'
        };
        login(token, user as any);
        navigate(`/${user.role.toLowerCase()}/dashboard`);
      } catch (decodeErr) {
        console.error("Failed to decode token", decodeErr);
        // Fallback user if token is opaque
        const fbUser = { id: 1, email, role: 'STUDENT' };
        login(token, fbUser as any);
        navigate('/student/dashboard');
      }

    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-dark-bg text-white px-4 relative overflow-hidden">
      {/* Background decoration elements */}
      <div className="absolute top-[-10%] left-[-10%] w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
      <div className="absolute bottom-[-10%] right-[-10%] w-96 h-96 bg-primary-900/40 rounded-full blur-3xl"></div>

      <div className="glass-card w-full max-w-md p-8 relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-primary-500/20 rounded-full mb-3 ring-1 ring-primary-500/50 shadow-lg shadow-primary-500/20">
            <Activity className="h-8 w-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Welcome Back</h1>
          <p className="text-gray-400 text-sm mt-1">Sign in to SOUL Adaptive LMS</p>
        </div>
        
        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg mb-6 text-sm">{error}</div>}
        
        <form onSubmit={handleSubmit} className="space-y-5">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Email Address</label>
            <input 
              type="email" 
              className="input-field" 
              placeholder="you@example.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required 
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-1">Password</label>
            <input 
              type="password" 
              className="input-field" 
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          <button type="submit" className="btn-primary w-full mt-4 py-3" disabled={loading}>
            {loading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>
        
        <div className="mt-8 text-center text-sm text-gray-400">
          Don't have an account? <Link to="/register" className="text-primary-400 hover:text-primary-300 transition-colors font-medium">Create one now</Link>
        </div>
      </div>
    </div>
  );
};

export default Login;
