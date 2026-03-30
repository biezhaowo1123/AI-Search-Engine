interface SearchResult {
  title: string
  url: string
  snippet: string
  source?: string
  date?: string
  image?: string
}

interface SearchResultsProps {
  results: SearchResult[]
  aiSummary?: string
  cached: boolean
}

const SOURCE_COLORS: Record<string, string> = {
  '百度': 'bg-red-100 text-red-700',
  'Bing搜索': 'bg-blue-100 text-blue-700',
  '搜狗': 'bg-orange-100 text-orange-700',
  '头条': 'bg-red-50 text-red-600',
  'CSDN': 'bg-yellow-100 text-yellow-700',
}

export default function SearchResults({ results, aiSummary, cached }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="w-full max-w-4xl mt-8 text-center py-12">
        <div className="text-6xl mb-4">🔍</div>
        <p className="text-gray-500 text-lg">未找到相关结果</p>
      </div>
    )
  }

  return (
    <div className="w-full max-w-4xl mt-8 space-y-6">
      {aiSummary && (
        <div className="p-5 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl shadow-sm">
          <div className="flex items-center gap-2 mb-2">
            <span className="px-2.5 py-1 bg-blue-600 text-white text-xs font-bold rounded-full">AI</span>
            <span className="text-sm font-semibold text-blue-800">智能摘要</span>
            {cached && (
              <span className="text-xs text-blue-500 bg-blue-100 px-2 py-0.5 rounded-full">缓存</span>
            )}
          </div>
          <p className="text-gray-800 leading-relaxed text-lg">{aiSummary}</p>
        </div>
      )}

      <div className="bg-white rounded-xl border border-gray-200 shadow-sm overflow-hidden">
        <div className="px-5 py-3 bg-gray-50 border-b border-gray-200 flex items-center justify-between">
          <span className="text-sm text-gray-600">
            共找到 <span className="font-bold text-gray-900">{results.length}</span> 个结果
          </span>
        </div>

        <div className="divide-y divide-gray-100">
          {results.map((result, index) => {
            const colorClass = SOURCE_COLORS[result.source || ''] || 'bg-gray-100 text-gray-600'
            
            return (
              <div 
                key={index} 
                className="p-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex gap-4">
                  {result.image ? (
                    <div className="flex-shrink-0">
                      <img 
                        src={result.image} 
                        alt=""
                        className="w-20 h-20 object-cover rounded-lg border border-gray-200"
                        onError={(e) => {
                          (e.target as HTMLImageElement).style.display = 'none'
                        }}
                      />
                    </div>
                  ) : (
                    <div className="flex-shrink-0 w-20 h-20 bg-gray-100 rounded-lg border border-gray-200 flex items-center justify-center">
                      <span className="text-3xl">
                        {result.source === '百度' && '🔍'}
                        {result.source === 'Bing搜索' && '🌐'}
                        {result.source === '搜狗' && '🦊'}
                        {result.source === '头条' && '📰'}
                        {result.source === 'CSDN' && '💻'}
                        {!result.source && '📄'}
                      </span>
                    </div>
                  )}
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-start justify-between gap-2">
                      <a
                        href={result.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-lg text-blue-600 hover:text-blue-800 hover:underline font-medium line-clamp-2 flex-1"
                      >
                        {result.title}
                      </a>
                    </div>
                    
                    <div className="flex items-center gap-2 mt-1 flex-wrap">
                      <span className={`px-2 py-0.5 text-xs font-medium rounded-full ${colorClass}`}>
                        {result.source}
                      </span>
                      {result.date && (
                        <span className="text-xs text-gray-400">{result.date}</span>
                      )}
                    </div>
                    
                    <p className="mt-2 text-gray-600 text-sm line-clamp-2 leading-relaxed">
                      {result.snippet}
                    </p>
                  </div>
                </div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
