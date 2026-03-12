import { useState } from 'react';
import { assignmentsApi } from '../api/assignments';
import { useAuth } from '../context/AuthContext';
import { Send, Plus } from 'lucide-react';

const Assignments = () => {
  const { user } = useAuth();
  
  // Instructor props
  const [courseId, setCourseId] = useState('');
  const [title, setTitle] = useState('');
  const [description, setDescription] = useState('');
  const [dueDate, setDueDate] = useState('');
  
  // Student props
  const [assignmentId, setAssignmentId] = useState('');
  const [submissionText, setSubmissionText] = useState('');
  const [reflectionText, setReflectionText] = useState('');
  
  const [message, setMessage] = useState({ text: '', type: '' });
  const [loading, setLoading] = useState(false);

  const handleCreateAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ text: '', type: '' });
    try {
      await assignmentsApi.createAssignment({
        course_id: Number(courseId),
        title,
        description,
        due_date: new Date(dueDate).toISOString()
      });
      setMessage({ text: 'Assignment created successfully!', type: 'success' });
      setCourseId(''); setTitle(''); setDescription(''); setDueDate('');
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to create assignment', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const handleSubmitAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setMessage({ text: '', type: '' });
    try {
      await assignmentsApi.submitAssignment({
        assignment_id: Number(assignmentId),
        submission_text: submissionText,
        reflection_text: reflectionText
      });
      setMessage({ text: 'Assignment submitted successfully!', type: 'success' });
      setAssignmentId(''); setSubmissionText(''); setReflectionText('');
    } catch (err: any) {
      setMessage({ text: err.response?.data?.detail || 'Failed to submit assignment', type: 'error' });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Assignments</h1>
        <p className="text-gray-400 mt-1">Manage course coursework</p>
      </div>

      {message.text && (
        <div className={`p-4 rounded-lg mb-6 text-sm flex items-center gap-2 ${message.type === 'success' ? 'bg-primary-500/10 border border-primary-500/50 text-primary-400' : 'bg-red-500/10 border border-red-500/50 text-red-400'}`}>
          <span>{message.text}</span>
        </div>
      )}

      {(user?.role === 'INSTRUCTOR' || user?.role === 'ADMIN') && (
        <div className="glass-card p-6 mb-8">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary-500/10 rounded-lg text-primary-400">
              <Plus className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-semibold text-white">Create New Assignment</h2>
          </div>
          <form onSubmit={handleCreateAssignment} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Course ID</label>
                <input type="number" className="input-field" placeholder="E.g. 1" value={courseId} onChange={e => setCourseId(e.target.value)} required />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-300 mb-1">Due Date</label>
                <input type="datetime-local" className="input-field" value={dueDate} onChange={e => setDueDate(e.target.value)} required />
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Title</label>
              <input type="text" className="input-field" placeholder="Assignment Title" value={title} onChange={e => setTitle(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Description</label>
              <textarea className="input-field h-24" placeholder="Give details about what is required..." value={description} onChange={e => setDescription(e.target.value)} required />
            </div>
            <div className="flex justify-end pt-2">
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Processing...' : 'Create Assignment'}
              </button>
            </div>
          </form>
        </div>
      )}

      {user?.role === 'STUDENT' && (
        <div className="glass-card p-6">
          <div className="flex items-center gap-3 mb-6">
            <div className="p-2 bg-primary-500/10 rounded-lg text-primary-400">
              <Send className="h-5 w-5" />
            </div>
            <h2 className="text-xl font-semibold text-white">Submit Assignment</h2>
          </div>
          <form onSubmit={handleSubmitAssignment} className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Assignment ID</label>
              <input type="number" className="input-field" placeholder="Enter Assignment ID" value={assignmentId} onChange={e => setAssignmentId(e.target.value)} required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Submission Context / Answer</label>
              <textarea className="input-field h-32" value={submissionText} onChange={e => setSubmissionText(e.target.value)} placeholder="Type your answer or provide a link to your work here" required />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-300 mb-1">Reflection Text</label>
              <textarea className="input-field h-24" value={reflectionText} onChange={e => setReflectionText(e.target.value)} placeholder="Reflect on your learning experience while doing this assignment" required />
            </div>
            <div className="flex justify-end pt-2">
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Submitting...' : 'Submit Assignment'}
              </button>
            </div>
          </form>
        </div>
      )}
    </div>
  );
};

export default Assignments;
