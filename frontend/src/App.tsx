import { useState } from 'react'

function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <h1 className="text-2xl font-bold text-gray-900">Fin Analyzer</h1>
            <div className="flex gap-4">
              <a href="#" className="text-gray-700 hover:text-gray-900">Dashboard</a>
              <a href="#" className="text-gray-700 hover:text-gray-900">Transactions</a>
              <a href="#" className="text-gray-700 hover:text-gray-900">Budgets</a>
              <a href="#" className="text-gray-700 hover:text-gray-900">Import</a>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
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
      </main>
    </div>
  )
}

export default App
