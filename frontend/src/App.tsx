import { BrowserRouter as Router, Routes, Route, Link, useLocation } from 'react-router-dom'
import DashboardPage from './pages/DashboardPage'
import TransactionsPage from './pages/TransactionsPage'
import CategoriesPage from './pages/CategoriesPage'

function Navigation() {
  const location = useLocation()
  
  const isActive = (path: string) => location.pathname === path
  
  const linkClass = (path: string) => 
    `px-3 py-2 rounded-md text-sm font-medium ${
      isActive(path)
        ? 'bg-blue-600 text-white'
        : 'text-gray-700 hover:bg-gray-100'
    }`
  
  return (
    <nav className="bg-white shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16 items-center">
          <Link to="/" className="text-2xl font-bold text-gray-900">
            Fin Analyzer
          </Link>
          <div className="flex gap-2">
            <Link to="/" className={linkClass('/')}>Dashboard</Link>
            <Link to="/transactions" className={linkClass('/transactions')}>Transactions</Link>
            <Link to="/categories" className={linkClass('/categories')}>Categories</Link>
            <Link to="/budgets" className={linkClass('/budgets')}>Budgets</Link>
            <Link to="/import" className={linkClass('/import')}>Import</Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

function DashboardPage() {
  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Welcome to Fin Analyzer</h2>
        <p className="text-gray-600">
          Your personal finance analyzer with AI-powered insights.
        </p>
        <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Import Data</h3>
            <p className="text-sm text-gray-600">Upload CSV files from your bank</p>
          </div>
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">AI Categorization</h3>
            <p className="text-sm text-gray-600">Automatic transaction categorization</p>
          </div>
          <div className="border rounded-lg p-4">
            <h3 className="font-semibold text-lg mb-2">Insights</h3>
            <p className="text-sm text-gray-600">Smart budgets and spending analysis</p>
          </div>
        </div>
      </div>
    </div>
  )
}

function App() {
  return (
    <Router>
      <div className="min-h-screen bg-gray-50">
        <Navigation />
        <main>
          <Routes>
            <Route path="/" element={<DashboardPage />} />
            <Route path="/transactions" element={<TransactionsPage />} />
            <Route path="/categories" element={<CategoriesPage />} />
            <Route path="/budgets" element={<div className="p-8 text-center">Budgets (Coming Soon)</div>} />
            <Route path="/import" element={<div className="p-8 text-center">Import (Coming Soon)</div>} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
