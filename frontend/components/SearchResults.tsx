interface SearchResult {
  title: string
  url: string
  snippet: string
  source?: string
  date?: string
}

interface SearchResultsProps {
  results: SearchResult[]
  aiSummary?: string
  cached: boolean
}

export default function SearchResults({ results, aiSummary, cached }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="w-full max-w-3xl mt-8 text-center text-gray-500">
        未找到相关结果
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mt-8 space-y-6">
      {aiSummary && (
        <div className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2 py-0.5 bg-blue-600 text-white text-xs font-medium rounded-full">AI</span>
            <span className="text-sm font-medium text-blue-800">智能摘要</span>
            {cached && (
              <span className="text-xs text-blue-500">(缓存)</span>
            )}
          </div>
          <p className="text-gray-800 leading-relaxed">{aiSummary}</p>
        </div>
      )}

      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <span className="text-sm text-gray-500">找到 {results.length} 个结果</span>
        </div>
        
        {results.map((result, index) => (
          <div 
            key={index} 
            className="p-5 bg-white border border-gray-200 rounded-xl hover:shadow-lg hover:border-blue-200 transition-all duration-200"
          >
            <div className="flex items-start gap-3">
              <span className="flex-shrink-0 w-6 h-6 bg-gray-100 text-gray-500 text-xs font-medium rounded-full flex items-center justify-center mt-0.5">
                {index + 1}
              </span>
              <div className="flex-1 min-w-0">
                <a
                  href={result.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-lg text-blue-600 hover:text-blue-800 hover:underline font-medium line-clamp-2"
                >
                  {result.title}
                </a>
                
                <div className="flex items-center gap-3 mt-2 flex-wrap">
                  {result.source && (
                    <span className="px-2 py-0.5 bg-gray-100 text-gray-600 text-xs rounded">
                      {result.source}
                    </span>
                  )}
                  {result.date && (
                    <span className="text-xs text-gray-400">{result.date}</span>
                  )}
                </div>
                
                <p className="mt-2 text-gray-600 text-sm leading-relaxed line-clamp-3">
                  {result.snippet}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
