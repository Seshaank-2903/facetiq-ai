import React, { useState, useEffect } from 'react';
import Header from './components/Header';
import Sidebar from './components/Sidebar';
import AnalyzeView from './components/AnalyzeView';
import CatalogView from './components/CatalogView';
import SafetyView from './components/SafetyView';
import BenchmarkView from './components/BenchmarkView';
import HistoryView from './components/HistoryView';
import SettingsView from './components/SettingsView';

export default function App() {
  const [theme, setTheme] = useState('light');
  const [activeTab, setActiveTab] = useState('analyze');
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [history, setHistory] = useState([]);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [systemInfo, setSystemInfo] = useState(null);
  const [apiStatus, setApiStatus] = useState(false);

  // Apply theme attribute to root
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Fetch System info on mount
  useEffect(() => {
    fetch('http://127.0.0.1:8000/api/system')
      .then(res => res.json())
      .then(data => {
        setSystemInfo(data);
        setApiStatus(true);
      })
      .catch(err => {
        console.error('API Connection Error:', err);
        setApiStatus(false);
      });
  }, []);

  const toggleTheme = () => {
    setTheme(prev => (prev === 'dark' ? 'light' : 'dark'));
  };

  const handleRunAnalysis = (conversationText) => {
    setIsAnalyzing(true);
    fetch('http://127.0.0.1:8000/api/analyze', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ conversation: conversationText })
    })
      .then(res => res.json())
      .then(data => {
        setCurrentAnalysis(data);
        setIsAnalyzing(false);

        // Add to history log
        const historyItem = {
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          snippet: conversationText.slice(0, 60) + '...',
          full_text: conversationText,
          result: data
        };
        setHistory(prev => [historyItem, ...prev]);
      })
      .catch(err => {
        console.error('Analysis error:', err);
        setIsAnalyzing(false);
        alert('Failed to connect to backend server at http://127.0.0.1:8000');
      });
  };

  const handleLoadHistoryItem = (item) => {
    setCurrentAnalysis(item.result);
    setActiveTab('analyze');
  };

  return (
    <div className="app-container">
      {/* Left Sidebar Shell */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        systemInfo={systemInfo}
      />

      {/* Main Workspace Area */}
      <div className="main-content">
        {/* Header Bar */}
        <Header
          theme={theme}
          toggleTheme={toggleTheme}
          apiStatus={apiStatus}
        />

        {/* Content Body */}
        <main className="content-body">
          {activeTab === 'analyze' && (
            <AnalyzeView
              currentAnalysis={currentAnalysis}
              onRunAnalysis={handleRunAnalysis}
              history={history}
              isAnalyzing={isAnalyzing}
            />
          )}

          {activeTab === 'catalog' && <CatalogView />}

          {activeTab === 'safety' && <SafetyView />}

          {activeTab === 'benchmark' && <BenchmarkView />}

          {activeTab === 'history' && (
            <HistoryView
              history={history}
              onLoadHistoryItem={handleLoadHistoryItem}
            />
          )}

          {activeTab === 'settings' && (
            <SettingsView systemInfo={systemInfo} />
          )}
        </main>
      </div>
    </div>
  );
}
