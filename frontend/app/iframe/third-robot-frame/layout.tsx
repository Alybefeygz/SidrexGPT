import "../../globals.css" // Ana CSS dosyası

export default function ThirdRobotFrameLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="tr">
      <body className="overflow-hidden">
        {children}
      </body>
    </html>
  )
} 