import React from 'react'
import { Link } from 'react-router-dom'

function Navbar() {
  return (
    <nav className="bg-white shadow">
      <div className="container mx-auto px-4 py-4 flex items-center justify-between">
        <Link to="/" className="flex items-center space-x-2">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <span className="text-white font-bold">BA</span>
          </div>
          <span className="text-xl font-bold text-gray-900">Browser Agent</span>
        </Link>
        
        <div className="flex items-center space-x-6">
          <Link to="/" className="text-gray-600 hover:text-gray-900 font-medium">
            Dashboard
          </Link>
          <a
            href="http://localhost:8000/docs"
            target="_blank"
            rel="noopener noreferrer"
            className="text-gray-600 hover:text-gray-900 font-medium"
          >
            API Docs
          </a>
        </div>
      </div>
    </nav>
  )
}

export default Navbar
