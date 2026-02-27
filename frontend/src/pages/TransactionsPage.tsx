import { useState, useEffect } from 'react'
import axios from 'axios'
import { format } from 'date-fns'

interface Transaction {
  id: number
  date: string
  amount: number
  description: string
  merchant: string | null
  category_id: number | null
  is_categorized: boolean
  notes: string | null
}

interface Filters {
  search: string
  startDate: string
  endDate: string
  minAmount: string
  maxAmount: string
  isCategorized: string
}

function TransactionsPage() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [filters, setFilters] = useState<Filters>({
    search: '',
    startDate: '',
    endDate: '',
    minAmount: '',
    maxAmount: '',
    isCategorized: 'all',
  })
  const [sortBy, setSortBy] = useState('date')
  const [sortOrder, setSortOrder] = useState('desc')

  useEffect(() => {
    fetchTransactions()
  }, [sortBy, sortOrder])

  const fetchTransactions = async () => {
    setLoading(true)
    try {
      const params = new URLSearchParams()
      
      if (filters.search) params.append('search', filters.search)
      if (filters.startDate) params.append('start_date', filters.startDate)
      if (filters.endDate) params.append('end_date', filters.endDate)
      if (filters.minAmount) params.append('min_amount', filters.minAmount)
      if (filters.maxAmount) params.append('max_amount', filters.maxAmount)
      if (filters.isCategorized !== 'all') {
        params.append('is_categorized', filters.isCategorized)
      }
      
      params.append('sort_by', sortBy)
      params.append('sort_order', sortOrder)
      params.append('limit', '100')

      const response = await axios.get(`/api/transactions?${params.toString()}`)
      setTransactions(response.data)
    } catch (error) {
      console.error('Failed to fetch transactions:', error)
    } finally {
      setLoading(false)
    }
  }

  const handleFilterChange = (key: keyof Filters, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }))
  }

  const handleApplyFilters = () => {
    fetchTransactions()
  }

  const handleSort = (field: string) => {
    if (sortBy === field) {
      setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')
    } else {
      setSortBy(field)
      setSortOrder('desc')
    }
  }

  const formatCurrency = (amount: number) => {
    const formatted = new Intl.NumberFormat('he-IL', {
      style: 'currency',
      currency: 'ILS',
    }).format(Math.abs(amount))
    
    return amount >= 0 ? `+${formatted}` : `-${formatted}`
  }

  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'dd/MM/yyyy')
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Transactions</h1>
          <p className="text-gray-600 mt-2">View and manage your financial transactions</p>
        </div>

        {/* Filters */}
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-lg font-semibold mb-4">Filters</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <input
              type="text"
              placeholder="Search description or merchant..."
              value={filters.search}
              onChange={(e) => handleFilterChange('search', e.target.value)}
              className="border rounded px-3 py-2"
            />
            
            <div className="flex gap-2">
              <input
                type="date"
                placeholder="Start date"
                value={filters.startDate}
                onChange={(e) => handleFilterChange('startDate', e.target.value)}
                className="border rounded px-3 py-2 flex-1"
              />
              <input
                type="date"
                placeholder="End date"
                value={filters.endDate}
                onChange={(e) => handleFilterChange('endDate', e.target.value)}
                className="border rounded px-3 py-2 flex-1"
              />
            </div>
            
            <div className="flex gap-2">
              <input
                type="number"
                placeholder="Min amount"
                value={filters.minAmount}
                onChange={(e) => handleFilterChange('minAmount', e.target.value)}
                className="border rounded px-3 py-2 flex-1"
              />
              <input
                type="number"
                placeholder="Max amount"
                value={filters.maxAmount}
                onChange={(e) => handleFilterChange('maxAmount', e.target.value)}
                className="border rounded px-3 py-2 flex-1"
              />
            </div>
            
            <select
              value={filters.isCategorized}
              onChange={(e) => handleFilterChange('isCategorized', e.target.value)}
              className="border rounded px-3 py-2"
            >
              <option value="all">All transactions</option>
              <option value="true">Categorized only</option>
              <option value="false">Uncategorized only</option>
            </select>
            
            <button
              onClick={handleApplyFilters}
              className="bg-blue-600 text-white rounded px-4 py-2 hover:bg-blue-700"
            >
              Apply Filters
            </button>
          </div>
        </div>

        {/* Transaction List */}
        <div className="bg-white rounded-lg shadow overflow-hidden">
          {loading ? (
            <div className="p-8 text-center text-gray-500">Loading...</div>
          ) : transactions.length === 0 ? (
            <div className="p-8 text-center text-gray-500">
              No transactions found. Try adjusting your filters.
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th
                      onClick={() => handleSort('date')}
                      className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    >
                      Date {sortBy === 'date' && (sortOrder === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Description
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Merchant
                    </th>
                    <th
                      onClick={() => handleSort('amount')}
                      className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                    >
                      Amount {sortBy === 'amount' && (sortOrder === 'asc' ? '↑' : '↓')}
                    </th>
                    <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Category
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {transactions.map((transaction) => (
                    <tr key={transaction.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {formatDate(transaction.date)}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-900">
                        {transaction.description}
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {transaction.merchant || '-'}
                      </td>
                      <td className={`px-6 py-4 whitespace-nowrap text-sm text-right font-medium ${
                        transaction.amount >= 0 ? 'text-green-600' : 'text-red-600'
                      }`}>
                        {formatCurrency(transaction.amount)}
                      </td>
                      <td className="px-6 py-4 text-center">
                        {transaction.is_categorized ? (
                          <span className="px-2 py-1 text-xs rounded-full bg-green-100 text-green-800">
                            Categorized
                          </span>
                        ) : (
                          <span className="px-2 py-1 text-xs rounded-full bg-yellow-100 text-yellow-800">
                            Uncategorized
                          </span>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Pagination info */}
        {!loading && transactions.length > 0 && (
          <div className="mt-4 text-sm text-gray-600 text-center">
            Showing {transactions.length} transactions
          </div>
        )}
      </div>
    </div>
  )
}

export default TransactionsPage
