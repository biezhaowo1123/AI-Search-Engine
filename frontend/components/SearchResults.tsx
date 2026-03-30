interface SearchResult {
  title: string
  url: string
  snippet: string
  date?: string
}

interface SearchResultsProps {
  results: SearchResult[]
  aiSummary?: string
  cached: boolean
}

export default function SearchResults({ results, aiSummary, cached }: SearchResultsProps) {
  if (results.length === 0) {
    return null
  }

  return (
    <div className="w-full max-w-3xl mt-8">
      {aiSummary && (
        <div className="mb-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
          <h3 className="text-sm font-medium text-blue-800 mb-2">AI 摘要</h3>
          <p className="text-blue-900">{aiSummary}</p>
          {cached && (
            <span className="text-xs text-blue-600 mt-2 inline-block">（缓存）</span>
          )}
        </div>
      )}

      <div className="space-y-4">
        {results.map((result, index) => (
          <div key={index} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
            <a
              href={result.url}
              target="_blank"
              rel="noopener noreferrer"
              className="text-lg text-blue-600 hover:text-blue-800 hover:underline"
            >
              {result.title}
            </a>
            {result.date && (
              <span className="ml-2 text-xs text-gray-500">{result.date}</span>
            )}
            <p className="mt-1 text-gray-600 text-sm">{result.snippet}</p>
          </div>
        ))}
      </div>
    </div>
  )
}
