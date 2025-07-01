import type { Metadata } from "next";
import "./globals.css";
import ClientWrapper from "./ClientWrapper";

export const metadata: Metadata = {
  title: "Sidrex",
  description: "Sidrex GPT Platform",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="tr">
      <body suppressHydrationWarning>
        <ClientWrapper>
          {children}
        </ClientWrapper>
      </body>
    </html>
  );
}
