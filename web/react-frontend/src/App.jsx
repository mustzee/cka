import React, { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import ExamPage from './pages/ExamPage'
import ResultsPage from './pages/ResultsPage'
import StatisticsPage from './pages/StatisticsPage'
import { ExamProvider } from './context/ExamContext'

function App() {
  return (
    <Router>
      <ExamProvider>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/exam" element={<ExamPage />} />
            <Route path="/results" element={<ResultsPage />} />
            <Route path="/statistics" element={<StatisticsPage />} />
          </Routes>
        </div>
      </ExamProvider>
    </Router>
  )
}

export default App
