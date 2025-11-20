import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line, PieChart, Pie, Cell } from 'recharts'
import { Home, TrendingUp, Award } from 'lucide-react'

const COLORS = ['#8884d8', '#82ca9d', '#ffc658', '#ff8042', '#8dd1e1']

const StatisticsPage = () => {
  const navigate = useNavigate()
  const [stats, setStats] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStatistics()
  }, [])

  const loadStatistics = async () => {
    try {
      const response = await axios.get('/api/statistics')
      setStats(response.data)
    } catch (error) {
      console.error('Failed to load statistics:', error)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-white text-2xl">통계를 불러오는 중...</div>
      </div>
    )
  }

  const typeData = stats?.by_type
    ? Object.entries(stats.by_type).map(([type, data]) => ({
        name: `Type ${type}`,
        total: data.total,
        passed: data.passed,
        failed: data.failed,
        avg: data.avg_percentage
      }))
    : []

  return (
    <div className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="flex justify-between items-center mb-8">
          <div>
            <h1 className="text-4xl font-bold text-white mb-2">📊 통계 대시보드</h1>
            <p className="text-white/80">전체 시험 기록 및 성과 분석</p>
          </div>
          <button
            onClick={() => navigate('/')}
            className="bg-white/20 hover:bg-white/30 text-white font-bold py-3 px-6 rounded-xl transition-all flex items-center gap-2"
          >
            <Home className="w-5 h-5" />
            홈으로
          </button>
        </div>

        {/* Overview Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="glassmorphism rounded-2xl p-6 text-center">
            <div className="text-5xl font-bold text-white mb-2">{stats?.total_exams || 0}</div>
            <div className="text-white/80">총 시험 횟수</div>
          </div>
          <div className="glassmorphism rounded-2xl p-6 text-center">
            <div className="text-5xl font-bold text-green-400 mb-2">{stats?.passed || 0}</div>
            <div className="text-white/80">합격 횟수</div>
          </div>
          <div className="glassmorphism rounded-2xl p-6 text-center">
            <div className="text-5xl font-bold text-red-400 mb-2">{stats?.failed || 0}</div>
            <div className="text-white/80">불합격 횟수</div>
          </div>
          <div className="glassmorphism rounded-2xl p-6 text-center">
            <div className="text-5xl font-bold text-yellow-400 mb-2">
              {stats?.pass_rate?.toFixed(1) || 0}%
            </div>
            <div className="text-white/80">합격률</div>
          </div>
        </div>

        {/* Charts Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
          {/* Type Statistics Bar Chart */}
          <div className="glassmorphism rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">타입별 통계</h3>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Bar dataKey="passed" fill="#82ca9d" name="합격" />
                <Bar dataKey="failed" fill="#ff8042" name="불합격" />
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Average Score Line Chart */}
          <div className="glassmorphism rounded-2xl p-6">
            <h3 className="text-xl font-bold text-white mb-6">타입별 평균 점수</h3>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={typeData}>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
                <XAxis dataKey="name" stroke="#fff" />
                <YAxis stroke="#fff" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: 'rgba(0,0,0,0.8)',
                    border: '1px solid rgba(255,255,255,0.2)',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line
                  type="monotone"
                  dataKey="avg"
                  stroke="#8884d8"
                  strokeWidth={3}
                  name="평균 점수 (%)"
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Detailed Type Statistics */}
        <div className="glassmorphism rounded-2xl p-8">
          <h3 className="text-2xl font-bold text-white mb-6">상세 통계</h3>
          <div className="grid gap-4">
            {Object.entries(stats?.by_type || {}).map(([type, data]) => (
              <div key={type} className="bg-white/10 rounded-xl p-6">
                <div className="flex items-center justify-between mb-4">
                  <h4 className="text-xl font-bold text-white">Type {type}</h4>
                  <div className="flex gap-4">
                    <span className="bg-purple-500 px-4 py-2 rounded-lg text-white font-bold">
                      총 {data.total}회
                    </span>
                  </div>
                </div>
                <div className="grid grid-cols-3 gap-4">
                  <div className="text-center">
                    <div className="text-3xl font-bold text-green-400 mb-1">
                      {data.passed}
                    </div>
                    <div className="text-white/70">합격</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-red-400 mb-1">
                      {data.failed}
                    </div>
                    <div className="text-white/70">불합격</div>
                  </div>
                  <div className="text-center">
                    <div className="text-3xl font-bold text-yellow-400 mb-1">
                      {data.avg_percentage.toFixed(1)}%
                    </div>
                    <div className="text-white/70">평균 점수</div>
                  </div>
                </div>
                {/* Progress Bar */}
                <div className="mt-4">
                  <div className="h-3 bg-gray-700 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-green-400 to-blue-500"
                      style={{ width: `${data.avg_percentage}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Motivational Message */}
        <div className="mt-8 glassmorphism rounded-2xl p-8 text-center">
          <div className="text-6xl mb-4">🚀</div>
          <h3 className="text-2xl font-bold text-white mb-2">계속 도전하세요!</h3>
          <p className="text-white/80">
            합격률 {stats?.pass_rate?.toFixed(1)}% | 평균 점수 {stats?.avg_percentage?.toFixed(1)}%
          </p>
          <button
            onClick={() => navigate('/')}
            className="mt-6 bg-gradient-to-r from-green-400 to-blue-500 text-white font-bold py-4 px-8 rounded-xl hover:shadow-2xl transform hover:scale-105 transition-all flex items-center justify-center gap-2 mx-auto"
          >
            <Award className="w-6 h-6" />
            새 시험 시작하기
          </button>
        </div>
      </div>
    </div>
  )
}

export default StatisticsPage
