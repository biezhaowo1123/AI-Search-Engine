import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'AI 搜索引擎 - 智能搜索 + AI 摘要',
  description: '整合多个搜索源，AI 智能摘要',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="zh">
      <body className="min-h-screen flex flex-col">{children}</body>
    </html>
  )
}
