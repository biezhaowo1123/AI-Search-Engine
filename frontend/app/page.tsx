'use client'

import { useState } from 'react'
import SearchBox from '@/components/SearchBox'
import SearchResults from '@/components/SearchResults'
import Pagination from '@/components/Pagination'

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

const PAGE_SIZE = 20

export default function Home() {
  const [results, setResults] = useState<SearchResult[]>([])
  const [allResults, setAllResults] = useState<SearchResult[]>([])
  const [aiSummary, setAiSummary] = useState<string | undefined>(undefined)
  const [cached, setCached] = useState(false)
  const [loading, setLoading] = useState(false)
  const [hasSearched, setHasSearched] = useState(false)
  const [summaryLoading, setSummaryLoading] = useState(false)
  const [currentPage, setCurrentPage] = useState(1)
  const [currentQuery, setCurrentQuery] = useState('')

  const handleSearch = async (query: string) => {
    setLoading(true)
    setHasSearched(true)
    setAiSummary(undefined)
    setResults([])
    setAllResults([])
    setCurrentPage(1)
    setCurrentQuery(query)

    let searchResults: SearchResult[] = []

    try {
      const response = await fetch('/api/search', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query, page: 1, page_size: 100 })
      })

      if (response.ok) {
        const data: SearchResponse = await response.json()
        searchResults = data.results || []
        setAllResults(searchResults)
        setResults(searchResults.slice(0, PAGE_SIZE))
        setCached(data.cached)
        if (data.ai_summary) {
          setAiSummary(data.ai_summary)
        }
      }
    } catch (error) {
      console.error('Search error:', error)
      setResults([])
    } finally {
      setLoading(false)
    }

    if (!cached && searchResults.length > 0) {
      setSummaryLoading(true)
      try {
        const snippets = searchResults
          .filter(r => r.snippet && r.snippet.trim().length > 10)
          .map(r => r.snippet)
          .slice(0, 10)

        const response = await fetch('/api/search/ai-summary', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ query, snippets })
        })

        const reader = response.body?.getReader()
        const decoder = new TextDecoder()
        let fullSummary = ''

        if (reader) {
          while (true) {
            const { done, value } = await reader.read()
            if (done) break

            const chunk = decoder.decode(value)
            const lines = chunk.split('\n')

            for (const line of lines) {
              if (line.startsWith('data: ')) {
                try {
                  const data = JSON.parse(line.slice(6))
                  if (data.type === 'chunk') {
                    fullSummary += data.content
                    setAiSummary(fullSummary)
                  } else if (data.type === 'done') {
                    break
                  }
                } catch (e) {
                  console.error('Parse error:', e)
                }
              }
            }
          }
        }
      } catch (error) {
        console.error('Summary error:', error)
      } finally {
        setSummaryLoading(false)
      }
    }
  }

  const handlePageChange = (page: number) => {
    setCurrentPage(page)
    const start = (page - 1) * PAGE_SIZE
    const end = start + PAGE_SIZE
    setResults(allResults.slice(start, end))
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  return (
    <main className="min-h-screen bg-white">
      <header className="border-b border-gray-100">
        <div className="max-w-4xl mx-auto px-4 py-3 flex items-center justify-between">
          <h1 className="text-xl font-bold">
            <span className="text-blue-600">AI</span> 搜索
          </h1>
          <span className="text-sm text-gray-500">支持多个搜索源</span>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-4 py-6">
        <div className="mb-6">
          <SearchBox onSearch={handleSearch} loading={loading} />
        </div>

        {hasSearched && (
          <>
            <SearchResults
              results={results}
              aiSummary={aiSummary}
              cached={cached}
              summaryLoading={summaryLoading}
            />
            <Pagination
              currentPage={currentPage}
              totalResults={allResults.length}
              pageSize={PAGE_SIZE}
              onPageChange={handlePageChange}
            />
          </>
        )}
      </div>
    </main>
  )
}