import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { authApi } from '../api/auth';
import { Activity } from 'lucide-react';

const Register: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);
    
    try {
      await authApi.register({ email, password });
      setSuccess('Registration successful! Redirecting to login...');
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to register. Email may already exist.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex h-screen items-center justify-center bg-dark-bg text-white px-4 relative overflow-hidden">
      {/* Background decoration elements */}
      <div className="absolute top-[-10%] right-[-10%] w-96 h-96 bg-primary-600/20 rounded-full blur-3xl"></div>
      <div className="absolute bottom-[-10%] left-[-10%] w-96 h-96 bg-primary-900/40 rounded-full blur-3xl"></div>

      <div className="glass-card w-full max-w-md p-8 relative z-10">
        <div className="flex flex-col items-center mb-8">
          <div className="p-3 bg-primary-500/20 rounded-full mb-3 ring-1 ring-primary-500/50 shadow-lg shadow-primary-500/20">
            <Activity className="h-8 w-8 text-primary-400" />
          </div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-gray-400">Join SOUL LMS</h1>
          <p className="text-gray-400 text-sm mt-1">Start your adaptive learning journey</p>
        </div>
        
        {error && <div className="bg-red-500/10 border border-red-500/50 text-red-400 p-3 rounded-lg mb-6 text-sm">{error}</div>}
        {success && <div className="bg-green-500/10 border border-green-500/50 text-green-400 p-3 rounded-lg mb-6 text-sm">{success}</div>}
        
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
              placeholder="Create a strong password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required 
            />
          </div>
          <button type="submit" className="btn-primary w-full mt-4 py-3" disabled={loading || !!success}>
            {loading ? 'Creating account...' : 'Sign Up'}
          </button>
        </form>
        
        <div className="mt-8 text-center text-sm text-gray-400">
          Already have an account? <Link to="/login" className="text-primary-400 hover:text-primary-300 transition-colors font-medium">Sign in here</Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
