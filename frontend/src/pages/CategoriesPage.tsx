import { useState, useEffect } from 'react'
import axios from 'axios'

interface Category {
  id: number
  name: string
  category_type: string
  icon: string | null
  color: string | null
  is_system: boolean
  parent_id?: number | null
}

interface CategoryTree extends Category {
  subcategories: Category[]
}

function CategoriesPage() {
  const [categories, setCategories] = useState<CategoryTree[]>([])
  const [rules, setRules] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [showAddCategory, setShowAddCategory] = useState(false)
  const [showAddRule, setShowAddRule] = useState(false)
  const [editingCategory, setEditingCategory] = useState<Category | null>(null)

  // Form states
  const [newCategory, setNewCategory] = useState({
    name: '',
    category_type: 'expense',
    icon: '',
    color: '#3B82F6',
    parent_id: null as number | null
  })

  const [newRule, setNewRule] = useState({
    category_id: 0,
    rule_type: 'keyword',
    pattern: '',
    priority: 50
  })

  useEffect(() => {
    fetchCategories()
    fetchRules()
  }, [])

  const fetchCategories = async () => {
    try {
      const response = await axios.get('/api/categories/tree')
      setCategories(response.data)
    } catch (error) {
      console.error('Failed to fetch categories:', error)
    } finally {
      setLoading(false)
    }
  }

  const fetchRules = async () => {
    try {
      const response = await axios.get('/api/categorization/rules')
      setRules(response.data)
    } catch (error) {
      console.error('Failed to fetch rules:', error)
    }
  }

  const handleAddCategory = async () => {
    try {
      await axios.post('/api/categories', newCategory)
      setNewCategory({ name: '', category_type: 'expense', icon: '', color: '#3B82F6', parent_id: null })
      setShowAddCategory(false)
      fetchCategories()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create category')
    }
  }

  const handleUpdateCategory = async () => {
    if (!editingCategory) return
    
    try {
      await axios.patch(`/api/categories/${editingCategory.id}`, {
        icon: editingCategory.icon,
        color: editingCategory.color,
      })
      setEditingCategory(null)
      fetchCategories()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update category')
    }
  }

  const handleDeleteCategory = async (id: number) => {
    if (!confirm('Are you sure you want to delete this category?')) return
    
    try {
      await axios.delete(`/api/categories/${id}`)
      fetchCategories()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete category')
    }
  }

  const handleAddRule = async () => {
    try {
      await axios.post('/api/categorization/rules', newRule)
      setNewRule({ category_id: 0, rule_type: 'keyword', pattern: '', priority: 50 })
      setShowAddRule(false)
      fetchRules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to create rule')
    }
  }

  const handleDeleteRule = async (id: number) => {
    if (!confirm('Delete this rule?')) return
    
    try {
      await axios.delete(`/api/categorization/rules/${id}`)
      fetchRules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to delete rule')
    }
  }

  const handleToggleRule = async (rule: any) => {
    try {
      await axios.patch(`/api/categorization/rules/${rule.id}`, {
        is_active: !rule.is_active
      })
      fetchRules()
    } catch (error: any) {
      alert(error.response?.data?.detail || 'Failed to update rule')
    }
  }

  const getAllCategories = (): Category[] => {
    const all: Category[] = []
    categories.forEach(parent => {
      all.push(parent)
      all.push(...parent.subcategories)
    })
    return all
  }

  if (loading) {
    return <div className="p-8 text-center">Loading...</div>
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Categories & Rules</h1>
          <p className="text-gray-600 mt-2">Manage transaction categories and auto-categorization rules</p>
        </div>

        {/* Categories Section */}
        <div className="bg-white rounded-lg shadow mb-8">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Categories</h2>
            <button
              onClick={() => setShowAddCategory(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + Add Category
            </button>
          </div>

          <div className="p-6">
            {categories.map(parent => (
              <div key={parent.id} className="mb-6">
                <div className="flex items-center justify-between bg-gray-50 px-4 py-3 rounded-lg">
                  <div className="flex items-center gap-3">
                    <span className="text-2xl">{parent.icon || '📁'}</span>
                    <div>
                      <span className="font-semibold text-lg">{parent.name}</span>
                      {parent.is_system && (
                        <span className="ml-2 text-xs bg-gray-200 px-2 py-1 rounded">System</span>
                      )}
                    </div>
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => setEditingCategory(parent)}
                      className="text-blue-600 hover:text-blue-800 text-sm"
                    >
                      Edit
                    </button>
                    {!parent.is_system && (
                      <button
                        onClick={() => handleDeleteCategory(parent.id)}
                        className="text-red-600 hover:text-red-800 text-sm"
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </div>

                {/* Subcategories */}
                {parent.subcategories.length > 0 && (
                  <div className="ml-12 mt-2 space-y-2">
                    {parent.subcategories.map(sub => (
                      <div key={sub.id} className="flex items-center justify-between px-4 py-2 hover:bg-gray-50 rounded">
                        <div className="flex items-center gap-2">
                          <span>{sub.icon || '📄'}</span>
                          <span>{sub.name}</span>
                        </div>
                        <div className="flex gap-2">
                          <button
                            onClick={() => setEditingCategory(sub)}
                            className="text-blue-600 hover:text-blue-800 text-sm"
                          >
                            Edit
                          </button>
                          {!sub.is_system && (
                            <button
                              onClick={() => handleDeleteCategory(sub.id)}
                              className="text-red-600 hover:text-red-800 text-sm"
                            >
                              Delete
                            </button>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Rules Section */}
        <div className="bg-white rounded-lg shadow">
          <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Categorization Rules</h2>
            <button
              onClick={() => setShowAddRule(true)}
              className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            >
              + Add Rule
            </button>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Pattern</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Category</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Priority</th>
                  <th className="px-6 py-3 text-center text-xs font-medium text-gray-500 uppercase">Status</th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {rules.map(rule => {
                  const category = getAllCategories().find(c => c.id === rule.category_id)
                  return (
                    <tr key={rule.id}>
                      <td className="px-6 py-4 text-sm font-mono">{rule.pattern}</td>
                      <td className="px-6 py-4 text-sm">
                        <span className="px-2 py-1 rounded-full bg-gray-100 text-xs">
                          {rule.rule_type}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-sm">{category?.name || 'Unknown'}</td>
                      <td className="px-6 py-4 text-sm text-center">{rule.priority}</td>
                      <td className="px-6 py-4 text-center">
                        <button
                          onClick={() => handleToggleRule(rule)}
                          className={`px-3 py-1 rounded-full text-xs ${
                            rule.is_active
                              ? 'bg-green-100 text-green-800'
                              : 'bg-gray-100 text-gray-600'
                          }`}
                        >
                          {rule.is_active ? 'Active' : 'Inactive'}
                        </button>
                      </td>
                      <td className="px-6 py-4 text-right">
                        <button
                          onClick={() => handleDeleteRule(rule.id)}
                          className="text-red-600 hover:text-red-800 text-sm"
                        >
                          Delete
                        </button>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Add Category Modal */}
        {showAddCategory && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Add New Category</h3>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Category name"
                  value={newCategory.name}
                  onChange={(e) => setNewCategory({...newCategory, name: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
                <select
                  value={newCategory.category_type}
                  onChange={(e) => setNewCategory({...newCategory, category_type: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="expense">Expense</option>
                  <option value="income">Income</option>
                </select>
                <input
                  type="text"
                  placeholder="Icon (emoji)"
                  value={newCategory.icon}
                  onChange={(e) => setNewCategory({...newCategory, icon: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
                <input
                  type="color"
                  value={newCategory.color}
                  onChange={(e) => setNewCategory({...newCategory, color: e.target.value})}
                  className="w-full h-10 border rounded"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setShowAddCategory(false)}
                    className="px-4 py-2 border rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddCategory}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Edit Category Modal */}
        {editingCategory && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Edit Category</h3>
              <div className="space-y-4">
                <input
                  type="text"
                  placeholder="Icon (emoji)"
                  value={editingCategory.icon || ''}
                  onChange={(e) => setEditingCategory({...editingCategory, icon: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
                <input
                  type="color"
                  value={editingCategory.color || '#3B82F6'}
                  onChange={(e) => setEditingCategory({...editingCategory, color: e.target.value})}
                  className="w-full h-10 border rounded"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setEditingCategory(null)}
                    className="px-4 py-2 border rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleUpdateCategory}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Save
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Add Rule Modal */}
        {showAddRule && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 w-full max-w-md">
              <h3 className="text-lg font-semibold mb-4">Add Categorization Rule</h3>
              <div className="space-y-4">
                <select
                  value={newRule.category_id}
                  onChange={(e) => setNewRule({...newRule, category_id: parseInt(e.target.value)})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value={0}>Select category...</option>
                  {getAllCategories().map(cat => (
                    <option key={cat.id} value={cat.id}>{cat.name}</option>
                  ))}
                </select>
                <select
                  value={newRule.rule_type}
                  onChange={(e) => setNewRule({...newRule, rule_type: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                >
                  <option value="keyword">Keyword</option>
                  <option value="regex">Regex</option>
                  <option value="merchant">Merchant</option>
                </select>
                <input
                  type="text"
                  placeholder="Pattern (e.g., 'שופרסל' or 'amazon')"
                  value={newRule.pattern}
                  onChange={(e) => setNewRule({...newRule, pattern: e.target.value})}
                  className="w-full border rounded px-3 py-2"
                />
                <input
                  type="number"
                  placeholder="Priority (0-100)"
                  value={newRule.priority}
                  onChange={(e) => setNewRule({...newRule, priority: parseInt(e.target.value)})}
                  className="w-full border rounded px-3 py-2"
                />
                <div className="flex gap-2 justify-end">
                  <button
                    onClick={() => setShowAddRule(false)}
                    className="px-4 py-2 border rounded hover:bg-gray-50"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={handleAddRule}
                    className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
                  >
                    Add
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}

export default CategoriesPage
