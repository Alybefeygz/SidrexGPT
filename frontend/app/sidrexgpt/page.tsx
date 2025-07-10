"use client"

import Link from "next/link"
import { Navbar } from "@/components/Navbar"
import RobotManager from "@/components/robots/RobotManager"

export default function ContactPage() {
  return (
    <div className="min-h-screen bg-white">
      <Navbar currentPage="sidrexgpts" />

      {/* Breadcrumb */}
      <div className="bg-gray-50 py-3">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="text-sm">
            <Link href="/" className="text-gray-500 hover:text-gray-700">
              Ana Sayfa
            </Link>
            <span className="mx-2 text-gray-400">{">"}</span>
            <span className="text-gray-900">SidrexGPT's</span>
          </nav>
        </div>
      </div>

      {/* Robot Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
        <RobotManager />
      </div>
    </div>
  )
}
