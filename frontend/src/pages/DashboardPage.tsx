import { useState, useEffect } from 'react'
import axios from 'axios'
import { PieChart, Pie, Cell, BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

interface OverviewStats {
  total_income: number
  total_expenses: number
  net_amount: number
  transaction_count: number
  categorized_percentage: number
}

interface CategorySpending {
  name: string
  amount: number
  color: string
  icon: string
}

interface MonthlyTrend {
  month_name: string
  income: number
  expenses: number
  net: number
}

function DashboardPage() {
  const [overview, setOverview] = useState<OverviewStats | null>(null)
  const [categorySpending, setCategorySpending] = useState<CategorySpending[]>([])
  const [monthlyTrend, setMonthlyTrend] = useState<MonthlyTrend[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    fetchDashboardData()
  }, [])

  const fetchDashboardData = async () => {
    setLoading(true)
    try {
      // Fetch last 30 days by default
      const endDate = new Date()
      const startDate = new Date()
      startDate.setDate(startDate.getDate() - 30)

      const [overviewRes, categoryRes, trendRes] = await Promise.all([
        axios.get('/api/dashboard/overview', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString()
          }
        }),
        axios.get('/api/dashboard/spending-by-category', {
          params: {
            start_date: startDate.toISOString(),
            end_date: endDate.toISOString(),
            limit: 8
          }
        }),
        axios.get('/api/dashboard/income-vs-expenses', {
          params: { months: 6 }
        })
      ])

      setOverview(overviewRes.data)
      setCategorySpending(categoryRes.data)
      setMonthlyTrend(trendRes.data)
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error)
    } finally {
      setLoading(false)
    }
  }

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount)
  }

  const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#EC4899', '#06B6D4', '#F97316']

  if (loading) {
    return <div className="p-8 text-center">Loading dashboard...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-2">Your financial overview for the last 30 days</p>
        </div>

        {/* Overview Cards */}
        {overview && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Total Income</div>
              <div className="text-2xl font-bold text-green-600">
                {formatCurrency(overview.total_income)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Total Expenses</div>
              <div className="text-2xl font-bold text-red-600">
                {formatCurrency(overview.total_expenses)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Net Amount</div>
              <div className={`text-2xl font-bold ${overview.net_amount >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {formatCurrency(overview.net_amount)}
              </div>
            </div>

            <div className="bg-white rounded-lg shadow p-6">
              <div className="text-sm text-gray-600 mb-2">Transactions</div>
              <div className="text-2xl font-bold text-gray-900">
                {overview.transaction_count}
              </div>
              <div className="text-xs text-gray-500 mt-1">
                {overview.categorized_percentage.toFixed(0)}% categorized
              </div>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Spending by Category - Pie Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Spending by Category</h2>
            {categorySpending.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={categorySpending}
                    dataKey="amount"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={100}
                    label={(entry) => `${entry.name}: ${formatCurrency(entry.amount)}`}
                  >
                    {categorySpending.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color || COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                </PieChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-12">No spending data available</div>
            )}
          </div>

          {/* Top Categories - Bar Chart */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold mb-4">Top Spending Categories</h2>
            {categorySpending.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={categorySpending} layout="horizontal">
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis type="number" tickFormatter={(value) => formatCurrency(value)} />
                  <YAxis dataKey="name" type="category" width={100} />
                  <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  <Bar dataKey="amount" fill="#3B82F6" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="text-center text-gray-500 py-12">No data available</div>
            )}
          </div>
        </div>

        {/* Income vs Expenses Trend */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-lg font-semibold mb-4">Income vs Expenses (Last 6 Months)</h2>
          {monthlyTrend.length > 0 ? (
            <ResponsiveContainer width="100%" height={350}>
              <LineChart data={monthlyTrend}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="month_name" />
                <YAxis tickFormatter={(value) => formatCurrency(value)} />
                <Tooltip formatter={(value: number) => formatCurrency(value)} />
                <Legend />
                <Line type="monotone" dataKey="income" stroke="#10B981" strokeWidth={2} name="Income" />
                <Line type="monotone" dataKey="expenses" stroke="#EF4444" strokeWidth={2} name="Expenses" />
                <Line type="monotone" dataKey="net" stroke="#3B82F6" strokeWidth={2} name="Net" strokeDasharray="5 5" />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <div className="text-center text-gray-500 py-12">No trend data available</div>
          )}
        </div>

        {/* Quick Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
          {categorySpending.slice(0, 3).map((cat, index) => (
            <div key={index} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center justify-between mb-2">
                <span className="text-3xl">{cat.icon || '📊'}</span>
                <span className="text-sm text-gray-500">#{index + 1}</span>
              </div>
              <div className="text-lg font-semibold text-gray-900 mb-1">{cat.name}</div>
              <div className="text-2xl font-bold" style={{ color: cat.color || '#3B82F6' }}>
                {formatCurrency(cat.amount)}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default DashboardPage
