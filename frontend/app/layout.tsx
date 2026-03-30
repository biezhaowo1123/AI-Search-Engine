import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI 搜索引擎',
  description: '智能搜索 + AI 摘要',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className="min-h-screen bg-white">{children}</body>
    </html>
  )
}
