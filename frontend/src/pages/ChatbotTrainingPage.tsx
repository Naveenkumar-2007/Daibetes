import { useState, useEffect } from 'react';
import { Brain, Plus, Trash2, RefreshCw, Save, BookOpen, AlertCircle, CheckCircle } from 'lucide-react';

export default function ChatbotTrainingPage() {
  const [trainingData, setTrainingData] = useState('');
  const [newData, setNewData] = useState('');
  const [lastUpdated, setLastUpdated] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => {
    loadTrainingData();
  }, []);

  const loadTrainingData = async () => {
    setIsLoading(true);
    try {
      const response = await fetch('/api/admin/chatbot/training', {
        credentials: 'include',
      });
      const data = await response.json();

      if (data.success) {
        setTrainingData(data.data.custom_knowledge || '');
        setLastUpdated(data.data.last_updated);
      } else {
        showMessage('error', 'Failed to load training data');
      }
    } catch (error) {
      console.error('Error loading training data:', error);
      showMessage('error', 'Error loading training data');
    } finally {
      setIsLoading(false);
    }
  };

  const addTrainingData = async () => {
    if (!newData.trim()) {
      showMessage('error', 'Please enter training data');
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch('/api/admin/chatbot/training', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ training_data: newData.trim() }),
      });

      const data = await response.json();

      if (data.success) {
        showMessage('success', 'Training data added successfully! ✅');
        setNewData('');
        await loadTrainingData();
      } else {
        showMessage('error', data.error || 'Failed to add training data');
      }
    } catch (error) {
      console.error('Error adding training data:', error);
      showMessage('error', 'Error adding training data');
    } finally {
      setIsSaving(false);
    }
  };

  const resetTrainingData = async () => {
    if (!confirm('Are you sure you want to reset all custom training data? This cannot be undone.')) {
      return;
    }

    setIsSaving(true);
    try {
      const response = await fetch('/api/admin/chatbot/training', {
        method: 'DELETE',
        credentials: 'include',
      });

      const data = await response.json();

      if (data.success) {
        showMessage('success', 'Training data reset successfully! 🔄');
        await loadTrainingData();
      } else {
        showMessage('error', data.error || 'Failed to reset training data');
      }
    } catch (error) {
      console.error('Error resetting training data:', error);
      showMessage('error', 'Error resetting training data');
    } finally {
      setIsSaving(false);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-8 px-4">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-xl p-6 mb-6">
          <div className="flex items-center gap-4">
            <div className="bg-gradient-to-br from-blue-600 to-purple-600 p-4 rounded-xl">
              <Brain className="w-8 h-8 text-white" />
            </div>
            <div>
              <h1 className="text-3xl font-bold text-gray-900">AI Chatbot Training</h1>
              <p className="text-gray-600">Train the chatbot with custom medical knowledge</p>
            </div>
          </div>
        </div>

        {/* Message Alert */}
        {message && (
          <div
            className={`mb-6 p-4 rounded-xl flex items-center gap-3 ${
              message.type === 'success'
                ? 'bg-green-50 border border-green-200 text-green-800'
                : 'bg-red-50 border border-red-200 text-red-800'
            }`}
          >
            {message.type === 'success' ? (
              <CheckCircle className="w-5 h-5 flex-shrink-0" />
            ) : (
              <AlertCircle className="w-5 h-5 flex-shrink-0" />
            )}
            <span className="font-medium">{message.text}</span>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Add New Training Data */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <Plus className="w-6 h-6 text-blue-600" />
              <h2 className="text-xl font-bold text-gray-900">Add Training Data</h2>
            </div>

            <p className="text-sm text-gray-600 mb-4">
              Add custom medical knowledge, FAQs, or specific information to enhance the chatbot's responses.
            </p>

            <textarea
              value={newData}
              onChange={(e) => setNewData(e.target.value)}
              placeholder="Enter training data here...&#10;&#10;Example:&#10;Q: What is HbA1c?&#10;A: HbA1c is a blood test that measures your average blood sugar levels over the past 2-3 months. It's a key indicator for diabetes management.&#10;&#10;Normal Range: Below 5.7%&#10;Prediabetes: 5.7% - 6.4%&#10;Diabetes: 6.5% or higher"
              className="w-full h-64 px-4 py-3 border-2 border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none text-sm"
              disabled={isSaving}
            />

            <div className="flex gap-3 mt-4">
              <button
                onClick={addTrainingData}
                disabled={isSaving || !newData.trim()}
                className="flex-1 bg-gradient-to-r from-blue-600 to-blue-700 text-white px-6 py-3 rounded-xl font-semibold hover:from-blue-700 hover:to-blue-800 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 shadow-lg hover:shadow-xl"
              >
                {isSaving ? (
                  <>
                    <RefreshCw className="w-5 h-5 animate-spin" />
                    Adding...
                  </>
                ) : (
                  <>
                    <Save className="w-5 h-5" />
                    Add Training Data
                  </>
                )}
              </button>
            </div>

            {/* Training Tips */}
            <div className="mt-6 bg-blue-50 border border-blue-200 rounded-xl p-4">
              <h3 className="font-semibold text-blue-900 mb-2 flex items-center gap-2">
                <BookOpen className="w-4 h-4" />
                Training Tips
              </h3>
              <ul className="text-sm text-blue-800 space-y-1">
                <li>• Use Q&A format for better responses</li>
                <li>• Include medical terms and definitions</li>
                <li>• Add specific numbers and ranges</li>
                <li>• Keep information accurate and verified</li>
                <li>• Use clear, simple language</li>
              </ul>
            </div>
          </div>

          {/* Current Training Data */}
          <div className="bg-white rounded-2xl shadow-lg p-6">
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <BookOpen className="w-6 h-6 text-purple-600" />
                <h2 className="text-xl font-bold text-gray-900">Current Training Data</h2>
              </div>
              <button
                onClick={loadTrainingData}
                disabled={isLoading}
                className="text-purple-600 hover:text-purple-700 p-2 rounded-lg hover:bg-purple-50 transition-colors"
                title="Refresh"
              >
                <RefreshCw className={`w-5 h-5 ${isLoading ? 'animate-spin' : ''}`} />
              </button>
            </div>

            {lastUpdated && (
              <p className="text-sm text-gray-500 mb-3">
                Last updated: {new Date(lastUpdated).toLocaleString()}
              </p>
            )}

            <div className="bg-gray-50 border-2 border-gray-200 rounded-xl p-4 h-64 overflow-y-auto">
              {isLoading ? (
                <div className="flex items-center justify-center h-full">
                  <RefreshCw className="w-8 h-8 text-gray-400 animate-spin" />
                </div>
              ) : trainingData ? (
                <pre className="text-sm text-gray-700 whitespace-pre-wrap font-mono">
                  {trainingData}
                </pre>
              ) : (
                <div className="flex flex-col items-center justify-center h-full text-gray-400">
                  <BookOpen className="w-12 h-12 mb-2" />
                  <p className="text-sm">No custom training data added yet</p>
                </div>
              )}
            </div>

            <div className="mt-4">
              <button
                onClick={resetTrainingData}
                disabled={isSaving || !trainingData}
                className="w-full bg-red-50 text-red-600 px-6 py-3 rounded-xl font-semibold hover:bg-red-100 disabled:opacity-50 disabled:cursor-not-allowed transition-all flex items-center justify-center gap-2 border-2 border-red-200"
              >
                <Trash2 className="w-5 h-5" />
                Reset Training Data
              </button>
            </div>
          </div>
        </div>

        {/* Info Section */}
        <div className="mt-6 bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl shadow-xl p-6 text-white">
          <h3 className="text-xl font-bold mb-3 flex items-center gap-2">
            <Brain className="w-6 h-6" />
            How Auto-Training Works
          </h3>
          <div className="grid md:grid-cols-3 gap-4 text-sm">
            <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div className="font-semibold mb-2">📝 Add Knowledge</div>
              <p className="text-blue-100">
                Add custom medical information, FAQs, or specific health topics
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div className="font-semibold mb-2">🤖 AI Integration</div>
              <p className="text-blue-100">
                Training data is automatically integrated into the chatbot's knowledge base
              </p>
            </div>
            <div className="bg-white/10 rounded-xl p-4 backdrop-blur-sm">
              <div className="font-semibold mb-2">✨ Enhanced Responses</div>
              <p className="text-blue-100">
                Chatbot provides more accurate and specific answers using custom data
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
