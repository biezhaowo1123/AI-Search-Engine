'use client'

import { useState } from 'react'
import SearchBox from '@/components/SearchBox'
import SearchResults from '@/components/SearchResults'

interface SearchResult {
  title: string
  url: string
  snippet: string
  source?: string
  date?: string
  image?: string
}

interface SearchResponse {
  results: SearchResult[]
  ai_summary?: string
  cached: boolean
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [aiSummary, setAiSummary] = useState<string | undefined>(undefined)
  const [cached, setCached] = useState(false)
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (query: string) => {
    setLoading(true)
    setHasSearched(true)

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: 1, page_size: 20 })
      })

      if (response.ok) {
        const data: SearchResponse = await response.json()
        setResults(data.results || [])
        setAiSummary(data.ai_summary)
        setCached(data.cached)
      }
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-gray-50">
      <header className="bg-white border-b border-gray-200">
        <div className="max-w-6xl mx-auto px-4 py-4">
          <h1 className="text-2xl font-bold text-gray-900">
            <span className="text-blue-600">AI</span> 搜索引擎
          </h1>
        </div>
      </header>

      <div className="max-w-6xl mx-auto px-4 py-12">
        <div className="text-center mb-10">
          <h2 className="text-4xl font-bold text-gray-900 mb-3">
            智能搜索，精准答案
          </h2>
          <p className="text-lg text-gray-600">
            整合多个搜索源，AI 智能摘要
          </p>
        </div>

        <div className="flex justify-center mb-8">
          <SearchBox onSearch={handleSearch} loading={loading} />
        </div>

        {hasSearched && (
          <SearchResults
            results={results}
            aiSummary={aiSummary}
            cached={cached}
          />
        )}
      </div>

      <footer className="border-t border-gray-200 py-6 mt-auto">
        <div className="max-w-6xl mx-auto px-4 text-center text-sm text-gray-500">
          AI 搜索引擎 - 支持百度、Bing、搜狗、头条等多个搜索源
        </div>
      </footer>
    </main>
  )
}
