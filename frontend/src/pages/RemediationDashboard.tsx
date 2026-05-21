import React, { useEffect, useState, useCallback } from 'react';
import { fetchStudentModules, updateModuleProgress, type RemediationModule } from '../api/alerts';
import { BookOpen, CheckCircle, Loader } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { coursesApi } from '../api/courses';

const RemediationDashboard: React.FC = () => {
  const { user } = useAuth();
  const studentId = user?.id || 1;
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number>(1);
  const [modules, setModules] = useState<RemediationModule[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedModule, setSelectedModule] = useState<RemediationModule | null>(null);

  useEffect(() => {
    const loadCourses = async () => {
      try {
        const data = await coursesApi.getCourses();
        setCourses(data);
        if (data.length > 0) {
          setSelectedCourseId(data[0].id);
        }
      } catch (err) {
        console.error('Failed to load courses:', err);
      }
    };
    loadCourses();
  }, []);

  const loadModules = useCallback(async () => {
    if (!selectedCourseId) return;
    try {
      setLoading(true);
      const data = await fetchStudentModules(studentId, selectedCourseId);
      setModules(data);
    } catch (err) {
      console.error('Failed to load modules:', err);
    } finally {
      setLoading(false);
    }
  }, [studentId, selectedCourseId]);

  useEffect(() => {
    loadModules();
  }, [loadModules]);

  const handleModuleStart = (module: RemediationModule) => {
    setSelectedModule(module);
    if (module.completion_percentage === 0) {
      handleUpdateProgress(module.id, 10);
    }
  };

  const handleUpdateProgress = async (moduleId: number, progress: number) => {
    try {
      const updated = await updateModuleProgress(moduleId, progress);
      if (updated && selectedModule && selectedModule.id === moduleId) {
        setSelectedModule(updated);
      }
      loadModules();
    } catch (err) {
      console.error('Failed to update progress:', err);
    }
  };

  const getDifficultyColor = (level: string) => {
    switch (level) {
      case 'BEGINNER':
        return 'bg-green-500/10 text-green-400 border border-green-500/20';
      case 'INTERMEDIATE':
        return 'bg-yellow-500/10 text-yellow-400 border border-yellow-500/20';
      case 'ADVANCED':
        return 'bg-red-500/10 text-red-400 border border-red-500/20';
      default:
        return 'bg-gray-500/10 text-gray-400 border border-gray-500/20';
    }
  };

  if (loading && modules.length === 0 && courses.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-24">
        <Loader className="w-8 h-8 text-primary-500 animate-spin" />
        <span className="ml-3 text-gray-400 mt-4">Loading modules...</span>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto py-8 px-4">
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 mb-8">
        <div>
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary-400 to-primary-200">Learning Modules</h1>
          <p className="text-gray-400 mt-2">Access your assigned remediation and learning resources</p>
        </div>
        {courses.length > 0 && !selectedModule && (
          <div className="flex items-center gap-2">
            <label htmlFor="course-select" className="text-sm font-medium text-gray-300">Course:</label>
            <select
              id="course-select"
              value={selectedCourseId}
              onChange={(e) => setSelectedCourseId(Number(e.target.value))}
              className="bg-dark-card border border-dark-border text-white rounded-lg px-3 py-1.5 text-sm focus:outline-none focus:border-primary-500"
            >
              {courses.map(course => (
                <option key={course.id} value={course.id} className="bg-dark-card text-white">
                  {course.title}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      {selectedModule ? (
        // Module Player
        <div className="glass-card p-8">
          <div className="flex items-center justify-between mb-6">
            <button
              onClick={() => setSelectedModule(null)}
              className="text-primary-400 hover:text-primary-300 font-medium flex items-center gap-1 transition-colors"
            >
              ← Back to Modules
            </button>
            <span className={`px-4 py-1.5 rounded-full text-xs font-medium ${getDifficultyColor(selectedModule.difficulty_level)}`}>
              {selectedModule.difficulty_level}
            </span>
          </div>

          <h2 className="text-2xl font-bold text-white mb-4">{selectedModule.title}</h2>
          <p className="text-gray-300 mb-6">{selectedModule.description}</p>

          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between mb-2">
              <span className="text-sm font-medium text-gray-300">Progress</span>
              <span className="text-sm font-medium text-gray-300">{selectedModule.completion_percentage}%</span>
            </div>
            <div className="w-full bg-dark-bg border border-dark-border rounded-full h-2.5">
              <div
                className="bg-primary-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${selectedModule.completion_percentage}%` }}
              ></div>
            </div>
          </div>

          {/* Content */}
          <div className="bg-dark-bg/50 border border-dark-border rounded-lg p-6 mb-8 max-h-96 overflow-y-auto">
            <div className="prose prose-invert prose-sm max-w-none">
              {selectedModule.content.split('\n').map((line: string, idx: number) => (
                <p key={idx} className="text-gray-300 mb-3 whitespace-pre-wrap leading-relaxed">
                  {line}
                </p>
              ))}
            </div>
          </div>

          {/* Progress Controls */}
          <div className="flex gap-4 items-center">
            <button
              onClick={() => {
                if (selectedModule.completion_percentage < 100) {
                  handleUpdateProgress(selectedModule.id, Math.min(selectedModule.completion_percentage + 25, 100));
                }
              }}
              disabled={selectedModule.completion_percentage >= 100}
              className="btn-primary"
            >
              Continue Learning
            </button>
            {selectedModule.completion_percentage >= 100 && (
              <div className="flex items-center gap-2 text-green-400">
                <CheckCircle className="w-5 h-5" />
                <span className="font-medium">Completed!</span>
              </div>
            )}
          </div>

          {/* Score Section */}
          {selectedModule.score !== null && (
            <div className="mt-8 p-6 bg-primary-500/10 rounded-lg border border-primary-500/20">
              <p className="text-sm text-primary-300">
                <span className="font-bold">Your Score:</span> {selectedModule.score}/100
              </p>
            </div>
          )}
        </div>
      ) : (
        // Modules Grid
        <div>
          {loading ? (
            <div className="flex flex-col items-center justify-center py-12">
              <Loader className="w-8 h-8 text-primary-500 animate-spin" />
              <span className="ml-3 text-gray-400 mt-4">Updating module list...</span>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {modules.length === 0 ? (
                <div className="col-span-full text-center py-16 border border-dashed border-dark-border rounded-xl">
                  <BookOpen className="w-12 h-12 text-gray-500 mx-auto mb-4" />
                  <p className="text-gray-400">No remedial modules assigned yet</p>
                </div>
              ) : (
                modules.map(module => (
                  <div
                    key={module.id}
                    className="glass-card hover:-translate-y-1 transition-all duration-300 overflow-hidden flex flex-col justify-between"
                  >
                    <div className="p-6">
                      <div className="flex items-start justify-between mb-3 gap-2">
                        <h3 className="text-lg font-semibold text-white flex-1 leading-snug">
                          {module.title}
                        </h3>
                        {module.completion_percentage === 100 && (
                          <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0" />
                        )}
                      </div>

                      <p className="text-sm text-gray-400 mb-4 line-clamp-2">
                        {module.skill_gap}
                      </p>

                      {/* Progress Bar */}
                      <div className="mb-4">
                        <div className="w-full bg-dark-bg border border-dark-border rounded-full h-2">
                          <div
                            className="bg-primary-500 h-1.5 rounded-full"
                            style={{ width: `${module.completion_percentage}%` }}
                          ></div>
                        </div>
                        <p className="text-xs text-gray-400 mt-1.5 font-medium">
                          {module.completion_percentage}% Complete
                        </p>
                      </div>

                      <div className="flex items-center gap-2 mb-4">
                        <span className={`px-2.5 py-1 rounded-full text-xs font-medium ${getDifficultyColor(module.difficulty_level)}`}>
                          {module.difficulty_level}
                        </span>
                      </div>
                    </div>
                    <div className="p-6 pt-0 mt-auto">
                      <button
                        onClick={() => handleModuleStart(module)}
                        className="w-full btn-primary py-2 text-center"
                      >
                        {module.completion_percentage === 0 ? 'Start' : 'Continue'}
                      </button>
                    </div>
                  </div>
                ))
              )}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default RemediationDashboard;
