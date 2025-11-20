import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useExam } from '../context/ExamContext'
import { Play, BookOpen, TrendingUp, Award } from 'lucide-react'

const Home = () => {
  const navigate = useNavigate()
  const { examTypes, loadExamTypes } = useExam()
  const [selectedType, setSelectedType] = useState('A')
  const [practiceMode, setPracticeMode] = useState(false)
  const [setNumber, setSetNumber] = useState(1)

  useEffect(() => {
    loadExamTypes()
  }, [])

  const handleStartExam = () => {
    navigate('/exam', { state: { examType: selectedType, practiceMode, setNumber } })
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="max-w-6xl w-full">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-6xl font-bold text-white mb-4 animate-pulse-slow">
            🚀 CKA 시험 시뮬레이터
          </h1>
          <p className="text-2xl text-white/90">
            Kubernetes Certified Administrator 완벽 대비
          </p>
        </div>

        {/* Main Card */}
        <div className="glassmorphism rounded-3xl p-8 shadow-2xl">
          <div className="grid md:grid-cols-2 gap-8">
            {/* Left: Type Selection */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">시험 타입 선택</h2>
              <div className="space-y-4">
                {examTypes.map((type) => (
                  <button
                    key={type.type}
                    onClick={() => setSelectedType(type.type)}
                    className={`w-full p-6 rounded-xl transition-all ${
                      selectedType === type.type
                        ? 'bg-white text-purple-600 shadow-xl scale-105'
                        : 'bg-white/10 text-white hover:bg-white/20'
                    }`}
                  >
                    <div className="flex justify-between items-start">
                      <div className="text-left">
                        <h3 className="text-xl font-bold mb-2">Type {type.type}</h3>
                        <p className="text-sm opacity-80">{type.description}</p>
                        <div className="flex gap-4 mt-3 text-sm">
                          <span>📝 {type.question_count}문제</span>
                          <span>⚡ {type.total_weight}점</span>
                        </div>
                      </div>
                      {selectedType === type.type && (
                        <Award className="w-8 h-8" />
                      )}
                    </div>
                  </button>
                ))}
              </div>

              {/* Set Number Selection */}
              <div className="mt-6">
                <label className="text-white font-bold block mb-3">
                  세트 번호 선택
                </label>
                <div className="flex gap-3">
                  {[1, 2, 3, 4, 5].map((num) => (
                    <button
                      key={num}
                      onClick={() => setSetNumber(num)}
                      className={`px-6 py-3 rounded-lg font-bold transition-all ${
                        setNumber === num
                          ? 'bg-white text-purple-600'
                          : 'bg-white/20 text-white hover:bg-white/30'
                      }`}
                    >
                      세트 {num}
                    </button>
                  ))}
                </div>
                <p className="text-white/70 text-sm mt-2">
                  같은 타입이라도 세트마다 다른 문제가 출제됩니다
                </p>
              </div>
            </div>

            {/* Right: Options & Start */}
            <div>
              <h2 className="text-2xl font-bold text-white mb-6">시험 옵션</h2>

              <div className="space-y-4">
                {/* Practice Mode */}
                <label className="flex items-center gap-3 p-4 bg-white/10 rounded-xl cursor-pointer hover:bg-white/20 transition-all">
                  <input
                    type="checkbox"
                    checked={practiceMode}
                    onChange={(e) => setPracticeMode(e.target.checked)}
                    className="w-5 h-5"
                  />
                  <div className="text-white">
                    <div className="font-bold">연습 모드</div>
                    <div className="text-sm opacity-80">타이머 없이 연습할 수 있습니다</div>
                  </div>
                </label>

                {/* Info Cards */}
                <div className="grid grid-cols-2 gap-4 mt-6">
                  <div className="bg-white/10 p-4 rounded-xl text-white">
                    <div className="text-3xl font-bold">2시간</div>
                    <div className="text-sm opacity-80">시험 시간</div>
                  </div>
                  <div className="bg-white/10 p-4 rounded-xl text-white">
                    <div className="text-3xl font-bold">66%</div>
                    <div className="text-sm opacity-80">합격 기준</div>
                  </div>
                </div>

                {/* Start Button */}
                <button
                  onClick={handleStartExam}
                  className="w-full mt-8 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold py-6 px-8 rounded-xl hover:shadow-2xl transform hover:scale-105 transition-all flex items-center justify-center gap-3 text-xl"
                >
                  <Play className="w-8 h-8" />
                  시험 시작
                </button>

                {/* Additional Buttons */}
                <div className="grid grid-cols-2 gap-4 mt-4">
                  <button
                    onClick={() => navigate('/statistics')}
                    className="bg-white/20 text-white font-bold py-4 px-6 rounded-xl hover:bg-white/30 transition-all flex items-center justify-center gap-2"
                  >
                    <TrendingUp className="w-5 h-5" />
                    통계
                  </button>
                  <button
                    className="bg-white/20 text-white font-bold py-4 px-6 rounded-xl hover:bg-white/30 transition-all flex items-center justify-center gap-2"
                  >
                    <BookOpen className="w-5 h-5" />
                    가이드
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Features */}
        <div className="grid md:grid-cols-3 gap-6 mt-8">
          {[
            { icon: '⚡', title: '실시간 채점', desc: '즉시 결과 확인' },
            { icon: '📊', title: '상세 통계', desc: '진행률 추적' },
            { icon: '📜', title: 'PDF 리포트', desc: '인증서 발급' }
          ].map((feature, idx) => (
            <div key={idx} className="glassmorphism p-6 rounded-xl text-center text-white">
              <div className="text-4xl mb-3">{feature.icon}</div>
              <div className="font-bold text-lg mb-2">{feature.title}</div>
              <div className="text-sm opacity-80">{feature.desc}</div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default Home
