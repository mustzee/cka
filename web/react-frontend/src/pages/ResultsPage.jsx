import React from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { useExam } from '../context/ExamContext'
import { Trophy, Download, Home, TrendingUp, CheckCircle, XCircle } from 'lucide-react'

const ResultsPage = () => {
  const location = useLocation()
  const navigate = useNavigate()
  const { downloadPDFReport, downloadCertificate } = useExam()
  const { results, session } = location.state || {}

  if (!results) {
    navigate('/')
    return null
  }

  const passed = results.passed
  const percentage = results.percentage.toFixed(1)

  const handleDownloadPDF = async () => {
    try {
      await downloadPDFReport(session.session_id)
    } catch (error) {
      alert('PDF 다운로드 실패')
    }
  }

  const handleDownloadCertificate = async () => {
    if (!passed) {
      alert('합격한 경우에만 인증서를 발급받을 수 있습니다')
      return
    }

    try {
      await downloadCertificate(session.session_id)
    } catch (error) {
      alert('인증서 다운로드 실패')
    }
  }

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="text-8xl mb-4">
            {passed ? '🎉' : '😔'}
          </div>
          <h1 className={`text-5xl font-bold mb-4 ${passed ? 'text-green-400' : 'text-red-400'}`}>
            {passed ? '합격!' : '불합격'}
          </h1>
          <p className="text-white text-2xl">
            Type {session?.exam_type} - 세트 {session?.set_number || 1}
          </p>
        </div>

        {/* Score Card */}
        <div className="glassmorphism rounded-3xl p-8 shadow-2xl mb-8">
          {/* Progress Bar */}
          <div className="mb-8">
            <div className="flex justify-between text-white mb-2">
              <span className="font-bold">점수</span>
              <span className="text-2xl font-bold">{percentage}%</span>
            </div>
            <div className="h-8 bg-gray-700 rounded-full overflow-hidden">
              <div
                className={`h-full transition-all duration-1000 flex items-center justify-center text-white font-bold ${
                  passed ? 'bg-gradient-to-r from-green-400 to-blue-500' : 'bg-gradient-to-r from-red-400 to-orange-500'
                }`}
                style={{ width: `${Math.min(percentage, 100)}%` }}
              >
                {percentage}%
              </div>
            </div>
            <div className="flex justify-between text-white/70 text-sm mt-2">
              <span>0%</span>
              <span className="text-yellow-400 font-bold">합격선: 66%</span>
              <span>100%</span>
            </div>
          </div>

          {/* Stats Grid */}
          <div className="grid grid-cols-4 gap-4 mb-8">
            <div className="bg-white/10 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-white mb-2">
                {results.total_score.toFixed(1)}
              </div>
              <div className="text-white/70">획득 점수</div>
            </div>
            <div className="bg-white/10 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-white mb-2">
                {results.total_weight}
              </div>
              <div className="text-white/70">총점</div>
            </div>
            <div className="bg-white/10 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-green-400 mb-2">
                {results.results.filter(r => r.passed).length}
              </div>
              <div className="text-white/70">정답</div>
            </div>
            <div className="bg-white/10 rounded-xl p-6 text-center">
              <div className="text-4xl font-bold text-red-400 mb-2">
                {results.results.filter(r => !r.passed).length}
              </div>
              <div className="text-white/70">오답</div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <button
              onClick={() => navigate('/')}
              className="bg-white/20 hover:bg-white/30 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <Home className="w-5 h-5" />
              홈
            </button>
            <button
              onClick={() => navigate('/statistics')}
              className="bg-white/20 hover:bg-white/30 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <TrendingUp className="w-5 h-5" />
              통계
            </button>
            <button
              onClick={handleDownloadPDF}
              className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-2"
            >
              <Download className="w-5 h-5" />
              PDF
            </button>
            <button
              onClick={handleDownloadCertificate}
              disabled={!passed}
              className={`${
                passed
                  ? 'bg-gradient-to-r from-yellow-400 to-orange-500 hover:shadow-xl'
                  : 'bg-gray-500 cursor-not-allowed opacity-50'
              } text-white font-bold py-4 px-6 rounded-xl transition-all flex items-center justify-center gap-2`}
            >
              <Trophy className="w-5 h-5" />
              인증서
            </button>
          </div>
        </div>

        {/* Results Details */}
        <div className="glassmorphism rounded-3xl p-8 shadow-2xl">
          <h2 className="text-2xl font-bold text-white mb-6">문제별 결과</h2>
          <div className="space-y-4">
            {results.results.map((result, idx) => (
              <div
                key={idx}
                className={`rounded-xl p-6 border-l-4 ${
                  result.passed
                    ? 'bg-green-500/20 border-green-500'
                    : 'bg-red-500/20 border-red-500'
                }`}
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-start gap-3">
                    {result.passed ? (
                      <CheckCircle className="w-6 h-6 text-green-400 flex-shrink-0 mt-1" />
                    ) : (
                      <XCircle className="w-6 h-6 text-red-400 flex-shrink-0 mt-1" />
                    )}
                    <div>
                      <h3 className="text-xl font-bold text-white mb-2">
                        {idx + 1}. {result.title}
                      </h3>
                      <div className="text-white/80 text-sm">
                        점수: {result.score.toFixed(1)}/{result.weight} |
                        체크: {result.passed_checks}/{result.total_checks}
                      </div>
                    </div>
                  </div>
                </div>

                {!result.passed && result.details && (
                  <div className="mt-4 bg-black/30 p-4 rounded-lg">
                    <strong className="text-red-300 block mb-2">오답 상세:</strong>
                    <div className="space-y-1">
                      {result.details
                        .filter(d => !d.passed)
                        .map((detail, detailIdx) => (
                          <div key={detailIdx} className="text-white/90 text-sm">
                            ❌ {detail.check}: {detail.message}
                          </div>
                        ))}
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}

export default ResultsPage
