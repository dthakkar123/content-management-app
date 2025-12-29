import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { Toaster } from 'react-hot-toast';
import HomePage from './pages/HomePage';
import ContentDetailPage from './pages/ContentDetailPage';

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        {/* Toast notifications */}
        <Toaster
          position="top-right"
          toastOptions={{
            duration: 4000,
            style: {
              background: '#363636',
              color: '#fff',
            },
            success: {
              duration: 3000,
              iconTheme: {
                primary: '#10b981',
                secondary: '#fff',
              },
            },
            error: {
              duration: 5000,
              iconTheme: {
                primary: '#ef4444',
                secondary: '#fff',
              },
            },
          }}
        />

        {/* Main content */}
        <main>
          <Routes>
            <Route path="/" element={<HomePage />} />
            <Route path="/content/:id" element={<ContentDetailPage />} />
          </Routes>
        </main>

        {/* Footer */}
        <footer className="bg-white border-t border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <p className="text-center text-gray-500 text-sm">
              Content Management & Summarization App - Powered by Claude AI
            </p>
          </div>
        </footer>
      </div>
    </Router>
  );
}

export default App;
