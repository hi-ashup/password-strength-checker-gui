import React, { useState, useEffect } from 'react';
import './App.css';

const App = () => {
  const [password, setPassword] = useState('');
  const [analysis, setAnalysis] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [tips, setTips] = useState([]);
  const [suggestions, setSuggestions] = useState([]);
  const [copiedIndex, setCopiedIndex] = useState(null);
  const [loadingSuggestions, setLoadingSuggestions] = useState(false);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  // Fetch password tips on component mount
  useEffect(() => {
    const fetchTips = async () => {
      try {
        const response = await fetch(`${backendUrl}/api/password-tips`);
        const data = await response.json();
        setTips(data.tips);
      } catch (error) {
        console.error('Error fetching tips:', error);
      }
    };
    fetchTips();
  }, [backendUrl]);

  // Fetch password suggestions when password is weak or moderate
  useEffect(() => {
    const fetchSuggestions = async () => {
      if (analysis && (analysis.strength === 'weak' || analysis.strength === 'moderate')) {
        setLoadingSuggestions(true);
        try {
          const response = await fetch(`${backendUrl}/api/generate-passwords?count=3`);
          const data = await response.json();
          setSuggestions(data.suggestions || []);
        } catch (error) {
          console.error('Error fetching password suggestions:', error);
          setSuggestions([]);
        } finally {
          setLoadingSuggestions(false);
        }
      } else {
        setSuggestions([]);
      }
    };

    fetchSuggestions();
  }, [analysis, backendUrl]);

  // Copy password to clipboard
  const copyToClipboard = async (password, index) => {
    try {
      await navigator.clipboard.writeText(password);
      setCopiedIndex(index);
      
      // Reset the copied state after 2 seconds
      setTimeout(() => {
        setCopiedIndex(null);
      }, 2000);
    } catch (error) {
      console.error('Failed to copy password:', error);
      // Fallback for older browsers
      const textArea = document.createElement('textarea');
      textArea.value = password;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      
      setCopiedIndex(index);
      setTimeout(() => {
        setCopiedIndex(null);
      }, 2000);
    }
  };

  // Use suggested password
  const useSuggestedPassword = (suggestedPassword) => {
    setPassword(suggestedPassword);
  };

  // Analyze password with debouncing
  useEffect(() => {
    const analyzePassword = async () => {
      if (!password.trim()) {
        setAnalysis(null);
        return;
      }

      setIsLoading(true);
      try {
        const response = await fetch(`${backendUrl}/api/analyze-password`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ password }),
        });

        if (!response.ok) {
          throw new Error('Failed to analyze password');
        }

        const data = await response.json();
        setAnalysis(data);
      } catch (error) {
        console.error('Error analyzing password:', error);
        setAnalysis({
          strength: 'weak',
          score: 0,
          color: 'red',
          suggestions: ['Unable to analyze password. Please try again.'],
          criteria: {},
          message: 'Analysis failed'
        });
      } finally {
        setIsLoading(false);
      }
    };

    const debounceTimer = setTimeout(analyzePassword, 300);
    return () => clearTimeout(debounceTimer);
  }, [password, backendUrl]);

  const getStrengthColor = (strength) => {
    switch (strength) {
      case 'strong':
        return 'text-green-600';
      case 'moderate':
        return 'text-yellow-600';
      case 'weak':
        return 'text-red-600';
      default:
        return 'text-gray-600';
    }
  };

  const getProgressBarColor = (strength) => {
    switch (strength) {
      case 'strong':
        return 'bg-green-500';
      case 'moderate':
        return 'bg-yellow-500';
      case 'weak':
        return 'bg-red-500';
      default:
        return 'bg-gray-300';
    }
  };

  const getCriteriaIcon = (met) => {
    return met ? '✓' : '✗';
  };

  const getCriteriaColor = (met) => {
    return met ? 'text-green-600' : 'text-red-600';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-800 mb-4">
            🔒 Password Strength Checker
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Create strong, secure passwords that protect your accounts. Get real-time feedback and personalized suggestions.
          </p>
        </div>

        {/* Main Content */}
        <div className="grid lg:grid-cols-2 gap-8">
          {/* Password Input Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Test Your Password
            </h2>
            
            {/* Password Input */}
            <div className="mb-6">
              <label htmlFor="password" className="block text-sm font-medium text-gray-700 mb-2">
                Enter your password
              </label>
              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500 text-lg"
                  placeholder="Type your password here..."
                />
                <button
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3 text-gray-500 hover:text-gray-700"
                >
                  {showPassword ? '🙈' : '👁️'}
                </button>
              </div>
            </div>

            {/* Analysis Results */}
            {analysis && (
              <div className="space-y-6">
                {/* Strength Indicator */}
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-gray-700">Password Strength</span>
                    <span className={`text-sm font-bold ${getStrengthColor(analysis.strength)}`}>
                      {analysis.strength?.toUpperCase()} ({analysis.score}%)
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      className={`h-3 rounded-full transition-all duration-500 ${getProgressBarColor(analysis.strength)}`}
                      style={{ width: `${analysis.score}%` }}
                    ></div>
                  </div>
                </div>

                {/* Message */}
                <div className={`p-4 rounded-lg ${analysis.color === 'green' ? 'bg-green-50 border border-green-200' : 
                  analysis.color === 'yellow' ? 'bg-yellow-50 border border-yellow-200' : 
                  'bg-red-50 border border-red-200'}`}>
                  <p className={`font-medium ${getStrengthColor(analysis.strength)}`}>
                    {analysis.message}
                  </p>
                </div>

                {/* Criteria Checklist */}
                <div>
                  <h3 className="text-lg font-semibold text-gray-800 mb-3">Security Criteria</h3>
                  <div className="grid grid-cols-1 gap-2">
                    {analysis.criteria && Object.entries(analysis.criteria).map(([key, met]) => (
                      <div key={key} className="flex items-center space-x-2">
                        <span className={`text-lg ${getCriteriaColor(met)}`}>
                          {getCriteriaIcon(met)}
                        </span>
                        <span className="text-sm text-gray-700">
                          {key === 'length' ? 'At least 12 characters' :
                           key === 'uppercase' ? 'Uppercase letters (A-Z)' :
                           key === 'lowercase' ? 'Lowercase letters (a-z)' :
                           key === 'numbers' ? 'Numbers (0-9)' :
                           key === 'special' ? 'Special characters (!@#$%^&*)' :
                           key === 'no_common' ? 'Not a common password' :
                           key === 'no_patterns' ? 'No predictable patterns' : key}
                        </span>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Suggestions */}
                {analysis.suggestions && analysis.suggestions.length > 0 && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">Suggestions</h3>
                    <ul className="space-y-2">
                      {analysis.suggestions.map((suggestion, index) => (
                        <li key={index} className="flex items-start space-x-2">
                          <span className="text-indigo-500 mt-1">•</span>
                          <span className="text-sm text-gray-700">{suggestion}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Password Suggestions for Weak/Moderate Passwords */}
                {analysis && (analysis.strength === 'weak' || analysis.strength === 'moderate') && (
                  <div>
                    <h3 className="text-lg font-semibold text-gray-800 mb-3">
                      🔑 Try These Strong Passwords
                    </h3>
                    
                    {loadingSuggestions ? (
                      <div className="text-center py-4">
                        <div className="inline-block animate-spin rounded-full h-4 w-4 border-b-2 border-indigo-600"></div>
                        <p className="text-sm text-gray-600 mt-2">Generating suggestions...</p>
                      </div>
                    ) : (
                      <div className="space-y-3">
                        {suggestions.map((suggestion, index) => (
                          <div key={index} className="flex items-center justify-between p-3 bg-green-50 border border-green-200 rounded-lg">
                            <div className="flex-1">
                              <div className="font-mono text-sm text-gray-800 bg-white px-2 py-1 rounded border">
                                {suggestion.password}
                              </div>
                              <div className="text-xs text-green-600 mt-1">
                                Score: {suggestion.score}% • Length: {suggestion.length} chars
                              </div>
                            </div>
                            <div className="flex space-x-2 ml-4">
                              <button
                                onClick={() => copyToClipboard(suggestion.password, index)}
                                className={`px-3 py-1 text-xs font-medium rounded-md transition-all duration-200 ${
                                  copiedIndex === index
                                    ? 'bg-green-600 text-white'
                                    : 'bg-indigo-600 hover:bg-indigo-700 text-white'
                                }`}
                              >
                                {copiedIndex === index ? 'Copied ✓' : 'Copy'}
                              </button>
                              <button
                                onClick={() => useSuggestedPassword(suggestion.password)}
                                className="px-3 py-1 text-xs font-medium bg-gray-600 hover:bg-gray-700 text-white rounded-md transition-colors duration-200"
                              >
                                Use
                              </button>
                            </div>
                          </div>
                        ))}
                        
                        {suggestions.length === 0 && !loadingSuggestions && (
                          <div className="text-center py-4 text-gray-500">
                            <p className="text-sm">Unable to generate suggestions at the moment.</p>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Loading State */}
            {isLoading && (
              <div className="text-center py-4">
                <div className="inline-block animate-spin rounded-full h-6 w-6 border-b-2 border-indigo-600"></div>
                <p className="text-sm text-gray-600 mt-2">Analyzing password...</p>
              </div>
            )}
          </div>

          {/* Tips Section */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              💡 Password Security Tips
            </h2>
            <div className="space-y-3">
              {tips.map((tip, index) => (
                <div key={index} className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
                  <span className="text-indigo-500 font-bold">{index + 1}.</span>
                  <span className="text-sm text-gray-700">{tip}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="text-center mt-12">
          <p className="text-sm text-gray-500">
            Built with ❤️ using React and FastAPI | Keep your passwords secure!
          </p>
        </div>
      </div>
    </div>
  );
};

export default App;