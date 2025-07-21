import "../globals.css"

export default function EmbedLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <body className="bg-transparent pointer-events-none" style={{ margin: 0, padding: 0, background: 'transparent' }}>
        {children}
      </body>
    </html>
  )
}