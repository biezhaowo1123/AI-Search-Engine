'use client'

import { useState, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import remarkGfm from 'remark-gfm'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter'
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism'

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
  summaryLoading?: boolean
}

const SOURCE_COLORS: Record<string, string> = {
  '百度': 'text-red-500',
  'Bing搜索': 'text-blue-500',
  '搜狗': 'text-orange-500',
  '头条': 'text-red-600',
  'CSDN': 'text-yellow-600',
}

function SourceIcon({ source }: { source?: string }) {
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return <div className="w-14 h-14 bg-gray-100 rounded-lg" />
  }

  const iconMap: Record<string, string> = {
    '百度': 'B',
    'Bing搜索': 'Bi',
    '搜狗': 'S',
    '头条': 'T',
    'CSDN': 'C',
  }

  return (
    <div className="w-14 h-14 bg-gray-100 rounded-lg flex items-center justify-center">
      <span className="text-lg font-bold text-gray-500">
        {iconMap[source || ''] || '?'}
      </span>
    </div>
  )
}

function CopyButton({ code }: { code: string }) {
  const [copied, setCopied] = useState(false)

  const handleCopy = async () => {
    await navigator.clipboard.writeText(code)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <button
      onClick={handleCopy}
      className="absolute top-2 right-2 px-2 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded transition-colors"
    >
      {copied ? '已复制' : '复制'}
    </button>
  )
}

function MarkdownWithCode({ content }: { content: string }) {
  return (
    <ReactMarkdown
      remarkPlugins={[remarkGfm]}
      components={{
        code({ className, children, ...props }) {
          const match = /language-(\w+)/.exec(className || '')
          const code = String(children).replace(/\n$/, '')

          if (match) {
            return (
              <div className="relative">
                <SyntaxHighlighter
                  style={oneDark}
                  language={match[1]}
                  PreTag="div"
                  customStyle={{
                    margin: '0.5em 0',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                  }}
                >
                  {code}
                </SyntaxHighlighter>
                <CopyButton code={code} />
              </div>
            )
          }

          return (
            <code className="px-1.5 py-0.5 bg-gray-100 text-red-600 rounded text-sm font-mono" {...props}>
              {children}
            </code>
          )
        },
        a({ href, children }) {
          return (
            <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-600 hover:underline">
              {children}
            </a>
          )
        },
      }}
    >
      {content}
    </ReactMarkdown>
  )
}

export default function SearchResults({ results, aiSummary, cached, summaryLoading }: SearchResultsProps) {
  if (results.length === 0) {
    return (
      <div className="w-full mt-8 text-center py-12">
        <p className="text-gray-500 text-lg">未找到相关结果</p>
      </div>
    )
  }

  return (
    <div className="w-full mt-6">
      {(aiSummary || summaryLoading) && (
        <div className="mb-8 p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
          <div className="flex items-center gap-2 mb-3">
            <span className="px-2.5 py-1 bg-blue-600 text-white text-xs font-bold rounded">AI</span>
            <span className="text-sm font-medium text-gray-700">智能摘要</span>
            {cached && (
              <span className="text-xs text-gray-400 bg-gray-100 px-2 py-0.5 rounded">缓存</span>
            )}
            {summaryLoading && !aiSummary && (
              <span className="text-xs text-gray-400">生成中...</span>
            )}
          </div>
          {aiSummary ? (
            <MarkdownWithCode content={aiSummary} />
          ) : (
            <div className="animate-pulse space-y-2">
              <div className="h-4 bg-gray-200 rounded w-3/4"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          )}
        </div>
      )}

      <div className="space-y-3">
        {results.map((result, index) => {
          const colorClass = SOURCE_COLORS[result.source || ''] || 'text-gray-500'

          return (
            <div key={index} className="bg-white p-4 rounded-lg border border-gray-100 hover:border-gray-300 hover:shadow-sm transition-all">
              <div className="flex gap-4">
                {result.image ? (
                  <img
                    src={result.image}
                    alt=""
                    className="w-20 h-20 object-cover rounded-lg border border-gray-200 flex-shrink-0"
                    loading="lazy"
                  />
                ) : (
                  <SourceIcon source={result.source} />
                )}

                <div className="flex-1 min-w-0">
                  <a
                    href={result.url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-lg text-blue-600 hover:text-blue-800 hover:underline font-medium"
                  >
                    {result.title}
                  </a>

                  <div className="flex items-center gap-3 mt-1 text-sm">
                    <span className={`font-medium ${colorClass}`}>
                      {result.source}
                    </span>
                    <span className="text-gray-400">•</span>
                    <a
                      href={result.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-green-600 hover:text-green-800 truncate max-w-lg"
                    >
                      {result.url}
                    </a>
                  </div>

                  {result.snippet && (
                    <p className="mt-2 text-gray-600 text-sm leading-relaxed">
                      {result.snippet}
                    </p>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}