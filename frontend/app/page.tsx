'use client'

import { useState } from 'react'
import SearchBox from '@/components/SearchBox'
import SearchResults from '@/components/SearchResults'

interface SearchResult {
  title: string
  url: string
  snippet: string
  date?: string
}

interface SearchResponse {
  results: SearchResult[]
  ai_summary?: string
  cached: boolean
}

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [aiSummary, setAiSummary] = useState<string | undefined>()
  const [cached, setCached] = useState(false)
  const [loading, setLoading] = useState(false)
  const [searched, setSearched] = useState(false)

  const handleSearch = async (query: string) => {
    setLoading(true)
    setSearched(true)

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: 1, page_size: 20 })
      })

      if (response.ok) {
        const data: SearchResponse = await response.json()
        setResults(data.results)
        setAiSummary(data.ai_summary)
        setCached(data.cached)
      }
    } catch (error) {
      console.error('Search error:', error)
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen flex flex-col items-center pt-20 px-4">
      <h1 className="text-4xl font-bold text-gray-900 mb-2">AI 搜索引擎</h1>
      <p className="text-gray-600 mb-8">智能搜索 + AI 摘要</p>

      <SearchBox onSearch={handleSearch} loading={loading} />

      {searched && (
        <SearchResults
          results={results}
          aiSummary={aiSummary}
          cached={cached}
        />
      )}
    </main>
  )
}
