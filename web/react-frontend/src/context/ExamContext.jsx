import React, { createContext, useContext, useState, useEffect } from 'react'
import axios from 'axios'

const ExamContext = createContext()

export const useExam = () => {
  const context = useContext(ExamContext)
  if (!context) {
    throw new Error('useExam must be used within ExamProvider')
  }
  return context
}

export const ExamProvider = ({ children }) => {
  const [examTypes, setExamTypes] = useState([])
  const [currentSession, setCurrentSession] = useState(null)
  const [results, setResults] = useState(null)
  const [ws, setWs] = useState(null)

  // WebSocket 연결
  useEffect(() => {
    if (currentSession) {
      const websocket = new WebSocket(`ws://localhost:8000/ws/${currentSession.session_id}`)

      websocket.onmessage = (event) => {
        const data = JSON.parse(event.data)
        console.log('WebSocket message:', data)
        // 실시간 업데이트 처리
      }

      websocket.onerror = (error) => {
        console.error('WebSocket error:', error)
      }

      setWs(websocket)

      return () => {
        if (websocket) {
          websocket.close()
        }
      }
    }
  }, [currentSession])

  // 문제 타입 로드
  const loadExamTypes = async () => {
    try {
      const response = await axios.get('/api/questions/types')
      setExamTypes(response.data)
    } catch (error) {
      console.error('Failed to load exam types:', error)
    }
  }

  // 시험 시작
  const startExam = async (examType, practiceMode = false, setNumber = 1) => {
    try {
      const response = await axios.post('/api/exam/start', {
        exam_type: examType,
        practice_mode: practiceMode,
        set_number: setNumber
      })
      setCurrentSession(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to start exam:', error)
      throw error
    }
  }

  // 시험 채점
  const gradeExam = async (sessionId, questions) => {
    try {
      const response = await axios.post('/api/exam/grade', {
        session_id: sessionId,
        questions: questions
      })
      setResults(response.data)
      return response.data
    } catch (error) {
      console.error('Failed to grade exam:', error)
      throw error
    }
  }

  // PDF 리포트 다운로드
  const downloadPDFReport = async (sessionId) => {
    try {
      const response = await axios.get(`/api/exam/report/pdf/${sessionId}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `cka_exam_${sessionId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download PDF:', error)
      throw error
    }
  }

  // 인증서 다운로드
  const downloadCertificate = async (sessionId) => {
    try {
      const response = await axios.get(`/api/exam/certificate/${sessionId}`, {
        responseType: 'blob'
      })
      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', `cka_certificate_${sessionId}.pdf`)
      document.body.appendChild(link)
      link.click()
      link.remove()
    } catch (error) {
      console.error('Failed to download certificate:', error)
      throw error
    }
  }

  const value = {
    examTypes,
    currentSession,
    results,
    loadExamTypes,
    startExam,
    gradeExam,
    downloadPDFReport,
    downloadCertificate,
    setCurrentSession,
    setResults
  }

  return <ExamContext.Provider value={value}>{children}</ExamContext.Provider>
}
