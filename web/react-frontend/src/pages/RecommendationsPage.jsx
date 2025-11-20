import React, { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Brain, TrendingUp, Target, BookOpen, ArrowRight, AlertCircle, CheckCircle2 } from 'lucide-react'

const RecommendationsPage = () => {
  const navigate = useNavigate()
  const [loading, setLoading] = useState(true)
  const [recommendations, setRecommendations] = useState([])
  const [analysis, setAnalysis] = useState(null)
  const [learningPath, setLearningPath] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [message, setMessage] = useState('')

  useEffect(() => {
    loadRecommendations()
  }, [])

  const loadRecommendations = async () => {
    try {
      setLoading(true)
      const response = await fetch('http://localhost:8000/api/recommendations?count=10')
      const data = await response.json()

      setRecommendations(data.recommendations || [])
      setAnalysis(data.analysis)
      setLearningPath(data.learning_path)
      setStrategy(data.strategy)
      setMessage(data.message)
    } catch (error) {
      console.error('Failed to load recommendations:', error)
      setMessage('추천 정보를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const getStrategyInfo = (strategy) => {
    const strategies = {
      foundation_building: {
        name: '기초 다지기',
        description: '기본 개념을 탄탄히 다지는 단계입니다',
        color: 'from-blue-500 to-cyan-500',
        icon: '📚'
      },
      skill_improvement: {
        name: '실력 향상',
        description: '중급 수준의 문제로 실력을 향상시키는 단계입니다',
        color: 'from-green-500 to-emerald-500',
        icon: '📈'
      },
      mastery: {
        name: '숙련도 향상',
        description: '고급 문제를 통해 숙련도를 높이는 단계입니다',
        color: 'from-purple-500 to-pink-500',
        icon: '🎯'
      },
      expert: {
        name: '전문가 레벨',
        description: '최고 난이도의 문제로 전문성을 키우는 단계입니다',
        color: 'from-orange-500 to-red-500',
        icon: '🏆'
      }
    }
    return strategies[strategy] || strategies.foundation_building
  }

  const getDifficultyColor = (difficulty) => {
    const colors = {
      easy: 'bg-green-500/20 text-green-300 border-green-500/30',
      medium: 'bg-yellow-500/20 text-yellow-300 border-yellow-500/30',
      hard: 'bg-red-500/20 text-red-300 border-red-500/30'
    }
    return colors[difficulty] || colors.medium
  }

  const getDifficultyLabel = (difficulty) => {
    const labels = {
      easy: '쉬움',
      medium: '보통',
      hard: '어려움'
    }
    return labels[difficulty] || '보통'
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-xl">분석 중...</div>
      </div>
    )
  }

  const strategyInfo = strategy ? getStrategyInfo(strategy) : null

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900 py-12 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <div className="flex items-center justify-center gap-3 mb-4">
            <Brain className="w-12 h-12 text-purple-400" />
            <h1 className="text-4xl font-bold text-white">AI 맞춤 문제 추천</h1>
          </div>
          <p className="text-gray-300 text-lg">{message}</p>
        </div>

        {/* Strategy Card */}
        {strategyInfo && (
          <div className={`mb-8 bg-gradient-to-r ${strategyInfo.color} rounded-2xl p-[2px]`}>
            <div className="bg-slate-900/90 backdrop-blur-xl rounded-2xl p-6">
              <div className="flex items-center gap-4">
                <span className="text-5xl">{strategyInfo.icon}</span>
                <div>
                  <h2 className="text-2xl font-bold text-white mb-2">
                    현재 학습 전략: {strategyInfo.name}
                  </h2>
                  <p className="text-gray-300">{strategyInfo.description}</p>
                </div>
              </div>
            </div>
          </div>
        )}

        {/* Weakness Analysis */}
        {analysis && (
          <div className="grid md:grid-cols-2 gap-6 mb-8">
            {/* Domain Weaknesses */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <AlertCircle className="w-6 h-6 text-red-400" />
                약점 도메인
              </h3>
              <div className="space-y-3">
                {Object.entries(analysis.domain_analysis)
                  .sort((a, b) => a[1].accuracy - b[1].accuracy)
                  .slice(0, 5)
                  .map(([domain, stats]) => (
                    <div key={domain} className="bg-black/30 rounded-lg p-3">
                      <div className="flex justify-between items-center mb-2">
                        <span className="text-white font-medium">{domain}</span>
                        <span className="text-gray-300">
                          {(stats.accuracy * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="w-full bg-gray-700 rounded-full h-2">
                        <div
                          className="bg-gradient-to-r from-red-500 to-orange-500 h-2 rounded-full transition-all"
                          style={{ width: `${stats.accuracy * 100}%` }}
                        />
                      </div>
                    </div>
                  ))}
              </div>
            </div>

            {/* Difficulty Analysis */}
            <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6">
              <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                <TrendingUp className="w-6 h-6 text-blue-400" />
                난이도별 성적
              </h3>
              <div className="space-y-3">
                {Object.entries(analysis.difficulty_analysis || {}).map(([difficulty, stats]) => (
                  <div key={difficulty} className="bg-black/30 rounded-lg p-3">
                    <div className="flex justify-between items-center mb-2">
                      <span className="text-white font-medium capitalize">
                        {getDifficultyLabel(difficulty)}
                      </span>
                      <span className="text-gray-300">
                        {(stats.accuracy * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-700 rounded-full h-2">
                      <div
                        className="bg-gradient-to-r from-blue-500 to-cyan-500 h-2 rounded-full transition-all"
                        style={{ width: `${stats.accuracy * 100}%` }}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Learning Path */}
        {learningPath && learningPath.steps && learningPath.steps.length > 0 && (
          <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6 mb-8">
            <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
              <Target className="w-6 h-6 text-green-400" />
              학습 로드맵
            </h3>
            <div className="space-y-4">
              {learningPath.steps.map((step, index) => (
                <div key={index} className="flex items-start gap-4">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold">
                    {index + 1}
                  </div>
                  <div className="flex-1 bg-black/30 rounded-lg p-4">
                    <h4 className="text-white font-semibold mb-1">{step.step}</h4>
                    <p className="text-gray-300 text-sm mb-2">{step.description}</p>
                    <div className="flex flex-wrap gap-2">
                      {step.focus_areas.map((area, i) => (
                        <span
                          key={i}
                          className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded-md text-xs"
                        >
                          {area}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Recommendations */}
        <div className="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 p-6">
          <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
            <BookOpen className="w-6 h-6 text-yellow-400" />
            추천 문제 ({recommendations.length}개)
          </h3>

          {recommendations.length === 0 ? (
            <p className="text-gray-400 text-center py-8">추천할 문제가 없습니다.</p>
          ) : (
            <div className="space-y-4">
              {recommendations.map((rec, index) => (
                <div
                  key={index}
                  className="bg-black/30 rounded-xl p-5 border border-white/10 hover:border-purple-500/50 transition-all"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <span className="text-white font-bold text-lg">
                          {rec.question?.id || `Q${index + 1}`}
                        </span>
                        <span
                          className={`px-3 py-1 rounded-full text-xs font-medium border ${getDifficultyColor(
                            rec.difficulty || rec.question?.difficulty
                          )}`}
                        >
                          {getDifficultyLabel(rec.difficulty || rec.question?.difficulty)}
                        </span>
                        <span className="px-3 py-1 bg-blue-500/20 text-blue-300 rounded-full text-xs font-medium">
                          {rec.question?.domain || '일반'}
                        </span>
                      </div>
                      <h4 className="text-white font-semibold mb-2">
                        {rec.question?.title || rec.question?.description?.split('\n')[0]}
                      </h4>
                      <p className="text-gray-400 text-sm mb-3">
                        {rec.reason}
                      </p>
                      {rec.question?.description && (
                        <p className="text-gray-300 text-sm line-clamp-2">
                          {rec.question.description}
                        </p>
                      )}
                    </div>
                    <div className="flex-shrink-0 ml-4">
                      <div className="text-right">
                        <div className="text-2xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
                          {(rec.priority * 100).toFixed(0)}
                        </div>
                        <div className="text-xs text-gray-400">우선순위</div>
                      </div>
                    </div>
                  </div>

                  {rec.question?.weight && (
                    <div className="flex items-center gap-2 text-sm text-gray-400">
                      <span>가중치: {rec.question.weight}%</span>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="mt-8 flex justify-center gap-4">
          <button
            onClick={() => navigate('/')}
            className="px-6 py-3 bg-white/10 backdrop-blur-xl rounded-xl border border-white/20 text-white font-medium hover:bg-white/20 transition-all"
          >
            홈으로
          </button>
          <button
            onClick={loadRecommendations}
            className="px-6 py-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-medium hover:from-purple-600 hover:to-pink-600 transition-all flex items-center gap-2"
          >
            <ArrowRight className="w-5 h-5" />
            새로고침
          </button>
        </div>
      </div>
    </div>
  )
}

export default RecommendationsPage
