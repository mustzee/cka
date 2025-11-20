import React, { useEffect, useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useExam } from '../context/ExamContext'
import { Clock, CheckCircle, XCircle } from 'lucide-react'

const ExamPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { startExam, gradeExam } = useExam()
  const [session, setSession] = useState(null)
  const [timeLeft, setTimeLeft] = useState(7200) // 2 hours
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const initExam = async () => {
      const { examType, practiceMode, setNumber } = location.state || {}
      if (!examType) {
        navigate('/')
        return
      }

      try {
        const data = await startExam(examType, practiceMode, setNumber)
        setSession(data)
      } catch (error) {
        console.error('Failed to start exam:', error)
        navigate('/')
      } finally {
        setLoading(false)
      }
    }

    initExam()
  }, [])

  useEffect(() => {
    if (!session || session.practice_mode) return

    const timer = setInterval(() => {
      setTimeLeft((prev) => {
        if (prev <= 0) {
          clearInterval(timer)
          handleFinishExam()
          return 0
        }
        return prev - 1
      })
    }, 1000)

    return () => clearInterval(timer)
  }, [session])

  const formatTime = (seconds) => {
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    const s = seconds % 60
    return `${String(h).padStart(2, '0')}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
  }

  const handleFinishExam = async () => {
    if (!session) return

    if (!confirm('시험을 종료하고 채점하시겠습니까?')) return

    setLoading(true)
    try {
      const results = await gradeExam(session.session_id, session.questions)
      navigate('/results', { state: { results, session } })
    } catch (error) {
      console.error('Grading failed:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl">로딩 중...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen p-8">
      {/* Timer */}
      {!session?.practice_mode && (
        <div className="fixed top-8 right-8 glassmorphism px-6 py-4 rounded-2xl shadow-xl z-50">
          <div className="flex items-center gap-3">
            <Clock className={`w-6 h-6 ${timeLeft < 600 ? 'text-red-400 animate-pulse' : 'text-white'}`} />
            <span className={`text-2xl font-bold ${timeLeft < 600 ? 'text-red-400' : 'text-white'}`}>
              {formatTime(timeLeft)}
            </span>
          </div>
        </div>
      )}

      {/* Main Content */}
      <div className="max-w-6xl mx-auto">
        <div className="glassmorphism rounded-3xl p-8 shadow-2xl">
          <div className="flex justify-between items-center mb-8">
            <div>
              <h1 className="text-3xl font-bold text-white mb-2">
                Type {session?.exam_type} - 세트 {session?.set_number || 1}
              </h1>
              <p className="text-white/80">
                {session?.practice_mode ? '연습 모드' : '실전 모드'} | {session?.questions?.length}문제
              </p>
            </div>
            <button
              onClick={handleFinishExam}
              className="bg-gradient-to-r from-red-500 to-pink-500 text-white font-bold py-3 px-8 rounded-xl hover:shadow-xl transition-all"
            >
              시험 종료
            </button>
          </div>

          {/* Questions List */}
          <div className="space-y-6">
            {session?.questions?.map((q, idx) => (
              <div key={idx} className="bg-white/10 rounded-xl p-6 border-l-4 border-blue-400">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-bold text-white">
                    {idx + 1}. {q.title}
                  </h3>
                  <div className="flex items-center gap-2">
                    <span className="bg-purple-500 text-white px-3 py-1 rounded-full text-sm">
                      {q.weight}점
                    </span>
                    <span className="bg-blue-500 text-white px-3 py-1 rounded-full text-sm">
                      {q.difficulty}
                    </span>
                  </div>
                </div>

                <div className="space-y-4 text-white/90">
                  <div>
                    <strong className="text-white">도메인:</strong> {q.domain}
                  </div>
                  <div>
                    <strong className="text-white">설명:</strong>
                    <pre className="mt-2 bg-black/30 p-4 rounded-lg whitespace-pre-wrap font-mono text-sm">
                      {q.description}
                    </pre>
                  </div>
                  <div>
                    <strong className="text-white">작업:</strong>
                    <pre className="mt-2 bg-black/30 p-4 rounded-lg whitespace-pre-wrap font-mono text-sm">
                      {q.task}
                    </pre>
                  </div>
                  {q.hints && q.hints.length > 0 && (
                    <div>
                      <strong className="text-white">힌트:</strong>
                      <ul className="mt-2 space-y-1">
                        {q.hints.map((hint, hintIdx) => (
                          <li key={hintIdx} className="ml-4">💡 {hint}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>

          {/* Instructions */}
          <div className="mt-8 bg-yellow-500/20 border-l-4 border-yellow-500 p-6 rounded-xl">
            <h4 className="text-yellow-300 font-bold mb-2">📝 중요 안내</h4>
            <ul className="text-white/90 space-y-2">
              <li>• 별도 터미널에서 kubectl 명령어를 사용하여 작업을 수행하세요</li>
              <li>• 각 문제는 독립적으로 채점됩니다</li>
              <li>• 시험 종료 버튼을 누르면 자동으로 채점됩니다</li>
              <li>• 합격 기준: 66% 이상</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ExamPage
