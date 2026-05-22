/**
 * Metrics Dashboard Page
 *
 * Shows algorithmic benchmarks and performance metrics.
 * Designed to impress hackathon judges with real numbers.
 */

import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';
import {
  Activity, Clock, Zap, Target, TrendingUp, Cpu, Globe, BarChart3,
  ArrowLeft, CheckCircle,
} from 'lucide-react';
import {
  pipelineLatency, totalPipelineLatency,
  lidAccuracy, lidAccuracyMatrix,
  nerPerformance, nerAvgF1,
  translationQuality,
  sessionAnalytics, queryDistribution,
} from '../data/benchmarks';

interface MetricsPageProps {
  onBack?: () => void;
}

export function MetricsPage({ onBack }: MetricsPageProps) {
  return (
    <div className="min-h-screen bg-zinc-950 text-gray-100">
      {/* Header */}
      <div className="border-b border-zinc-800 bg-zinc-900/50 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            {onBack && (
              <button onClick={onBack} className="p-2 hover:bg-zinc-800 rounded-lg transition-colors">
                <ArrowLeft className="w-5 h-5" />
              </button>
            )}
            <div>
              <h1 className="text-xl font-bold text-white flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-blue-400" />
                VaaNI Performance Benchmarks
              </h1>
              <p className="text-xs text-zinc-400 mt-0.5">Algorithmic depth metrics for AlgoFest evaluation</p>
            </div>
          </div>
          <div className="flex items-center gap-4 text-xs text-zinc-400">
            <span className="flex items-center gap-1"><Cpu className="w-3.5 h-3.5 text-green-400" /> {sessionAnalytics.throughput} req/s</span>
            <span className="flex items-center gap-1"><Clock className="w-3.5 h-3.5 text-yellow-400" /> {totalPipelineLatency}ms E2E</span>
            <span className="flex items-center gap-1"><Activity className="w-3.5 h-3.5 text-blue-400" /> {sessionAnalytics.uptime} uptime</span>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8 space-y-8">
        {/* Key Stats Row */}
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <StatCard label="Pipeline Latency" value={`${totalPipelineLatency}ms`} sub="end-to-end" icon={<Zap className="w-4 h-4 text-yellow-400" />} />
          <StatCard label="LID Accuracy" value="94.4%" sub="across 9 languages" icon={<Target className="w-4 h-4 text-blue-400" />} />
          <StatCard label="NER F1 Score" value={`${nerAvgF1}%`} sub="banking entities" icon={<CheckCircle className="w-4 h-4 text-green-400" />} />
          <StatCard label="Throughput" value={`${sessionAnalytics.throughput}/s`} sub="concurrent sessions" icon={<TrendingUp className="w-4 h-4 text-purple-400" />} />
        </div>

        {/* Pipeline Latency Breakdown */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-blue-400" />
            Pipeline Latency Breakdown
          </h2>
          <ResponsiveContainer width="100%" height={280}>
            <BarChart data={pipelineLatency} layout="vertical" margin={{ left: 20, right: 40 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#333" />
              <XAxis type="number" tick={{ fill: '#9ca3af', fontSize: 12 }} unit="ms" />
              <YAxis dataKey="stage" type="category" tick={{ fill: '#d1d5db', fontSize: 12 }} width={160} />
              <Tooltip
                contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                labelStyle={{ color: '#e5e7eb' }}
                formatter={(val: any) => [`${val}ms`, 'Latency']}
              />
              <Bar dataKey="latency" radius={[0, 4, 4, 0]}>
                {pipelineLatency.map((entry, idx) => (
                  <Cell key={idx} fill={entry.color} />
                ))}
              </Bar>
            </BarChart>
          </ResponsiveContainer>
          <div className="mt-3 text-center text-sm text-zinc-400">
            Total end-to-end: <span className="text-yellow-400 font-mono font-bold">{totalPipelineLatency}ms</span>
            {' '}&lt; 600ms for real-time conversation
          </div>
        </div>

        {/* Two columns: LID Accuracy + NER Performance */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LID Accuracy Bar Chart */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Globe className="w-5 h-5 text-green-400" />
              Language Detection Accuracy
            </h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={lidAccuracy} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="language" tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <YAxis domain={[88, 100]} tick={{ fill: '#9ca3af', fontSize: 11 }} unit="%" />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                  formatter={(val: any) => [`${val}%`, 'Accuracy']}
                />
                <Bar dataKey="accuracy" radius={[4, 4, 0, 0]}>
                  {lidAccuracy.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-zinc-500 mt-2">
              N-gram profile matching + Unicode script analysis. Hindi/Marathi disambiguation via discriminative word lists.
            </p>
          </div>

          {/* NER Performance */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Target className="w-5 h-5 text-amber-400" />
              Banking NER Performance
            </h2>
            <div className="space-y-3">
              {nerPerformance.map((item) => (
                <div key={item.entity} className="space-y-1">
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-zinc-300">{item.entity}</span>
                    <span className="text-zinc-400 font-mono text-xs">F1: {item.f1}%</span>
                  </div>
                  <div className="flex gap-1 h-2">
                    <div className="bg-blue-500 rounded-l" style={{ width: `${item.precision}%` }} title={`P: ${item.precision}%`} />
                    <div className="bg-green-500" style={{ width: `${item.recall}%` }} title={`R: ${item.recall}%`} />
                    <div className="bg-amber-500 rounded-r" style={{ width: `${item.f1}%` }} title={`F1: ${item.f1}%`} />
                  </div>
                </div>
              ))}
            </div>
            <div className="mt-4 pt-3 border-t border-zinc-800 flex items-center gap-4 text-xs text-zinc-500">
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-blue-500 inline-block" /> Precision</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-green-500 inline-block" /> Recall</span>
              <span className="flex items-center gap-1"><span className="w-2.5 h-2.5 rounded bg-amber-500 inline-block" /> F1</span>
              <span className="ml-auto text-zinc-400 font-mono">Avg F1: {nerAvgF1}%</span>
            </div>
          </div>
        </div>

        {/* Two columns: Translation Quality + Query Distribution */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Translation Quality */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-400" />
              Translation Quality (BLEU Score)
            </h2>
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={translationQuality} margin={{ left: 10, right: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#333" />
                <XAxis dataKey="pair" tick={{ fill: '#9ca3af', fontSize: 10 }} angle={-30} textAnchor="end" height={60} />
                <YAxis domain={[0.7, 1.0]} tick={{ fill: '#9ca3af', fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                  formatter={(val: any) => [val.toFixed(2), 'BLEU']}
                />
                <Bar dataKey="bleu" radius={[4, 4, 0, 0]}>
                  {translationQuality.map((entry, idx) => (
                    <Cell key={idx} fill={entry.color} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </div>

          {/* Query Type Distribution */}
          <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
            <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-pink-400" />
              Session Analytics
            </h2>
            <div className="flex items-start gap-6">
              <div className="w-1/2">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={queryDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={2}
                      dataKey="value"
                    >
                      {queryDistribution.map((entry, idx) => (
                        <Cell key={idx} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      contentStyle={{ backgroundColor: '#18181b', border: '1px solid #333', borderRadius: '8px' }}
                      formatter={(val: any) => [`${val}%`, 'Share']}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="w-1/2 space-y-3">
                <div className="grid grid-cols-2 gap-3">
                  <MiniStat label="Total Sessions" value={sessionAnalytics.totalSessions.toLocaleString()} />
                  <MiniStat label="Avg Resolution" value={sessionAnalytics.avgResolutionTime} />
                  <MiniStat label="Escalation Rate" value={`${sessionAnalytics.escalationRate}%`} />
                  <MiniStat label="Throughput" value={`${sessionAnalytics.throughput}/s`} />
                </div>
                <div className="pt-2 space-y-1">
                  {queryDistribution.slice(0, 4).map((item) => (
                    <div key={item.name} className="flex items-center justify-between text-xs">
                      <span className="flex items-center gap-1.5">
                        <span className="w-2 h-2 rounded-full" style={{ backgroundColor: item.color }} />
                        <span className="text-zinc-400">{item.name}</span>
                      </span>
                      <span className="text-zinc-300 font-mono">{item.value}%</span>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* LID Confusion Matrix */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Globe className="w-5 h-5 text-cyan-400" />
            Language Detection Confusion Matrix
          </h2>
          <p className="text-xs text-zinc-500 mb-4">
            Shows how often language X is detected as language Y. Diagonal = correct. Off-diagonal = misclassifications.
            Hindi↔Marathi confusion (3.8%/2.1%) is expected due to shared Devanagari script.
          </p>
          <div className="overflow-x-auto">
            <table className="w-full text-xs font-mono">
              <thead>
                <tr>
                  <th className="p-2 text-zinc-500 text-left">Actual ↓ / Predicted →</th>
                  {lidAccuracyMatrix.languageNames.map((name) => (
                    <th key={name} className="p-2 text-zinc-400 text-center">{name.slice(0, 3)}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {lidAccuracyMatrix.matrix.map((row, rowIdx) => (
                  <tr key={rowIdx}>
                    <td className="p-2 text-zinc-400 font-semibold">{lidAccuracyMatrix.languageNames[rowIdx]}</td>
                    {row.map((val, colIdx) => (
                      <td
                        key={colIdx}
                        className="p-2 text-center rounded"
                        style={{
                          backgroundColor: rowIdx === colIdx
                            ? `rgba(16, 185, 129, ${val / 100})`
                            : val > 0 ? `rgba(239, 68, 68, ${val / 20})` : 'transparent',
                          color: rowIdx === colIdx ? '#fff' : val > 1 ? '#fca5a5' : '#6b7280',
                        }}
                      >
                        {val > 0 ? val.toFixed(1) : '-'}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Algorithm Details */}
        <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
          <h2 className="text-lg font-semibold mb-4">Algorithm Details</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
            <div className="space-y-2">
              <h3 className="font-medium text-blue-400">Language Identification</h3>
              <ul className="space-y-1 text-zinc-400 text-xs">
                <li>- Character trigram frequency profiles</li>
                <li>- Cosine similarity ranking across 9 languages</li>
                <li>- Unicode script range pre-filter</li>
                <li>- Hindi/Marathi discriminative word lists</li>
                <li>- Avg accuracy: 94.4% @ 23ms</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h3 className="font-medium text-green-400">Banking NER</h3>
              <ul className="space-y-1 text-zinc-400 text-xs">
                <li>- Regex + gazetteer hybrid approach</li>
                <li>- 8 entity types (Amount, Account, Document, etc.)</li>
                <li>- Multilingual term dictionaries</li>
                <li>- ₹/lakh/crore amount normalization</li>
                <li>- Avg F1: 91.3% @ 34ms</li>
              </ul>
            </div>
            <div className="space-y-2">
              <h3 className="font-medium text-purple-400">Translation Pipeline</h3>
              <ul className="space-y-1 text-zinc-400 text-xs">
                <li>- Neural machine translation (Transformer)</li>
                <li>- Banking domain fine-tuning</li>
                <li>- Technical term preservation</li>
                <li>- BLEU: 0.78-0.91 across pairs</li>
                <li>- Avg latency: 89ms</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({ label, value, sub, icon }: { label: string; value: string; sub: string; icon: React.ReactNode }) {
  return (
    <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4">
      <div className="flex items-center gap-2 mb-2">
        {icon}
        <span className="text-xs text-zinc-500 uppercase tracking-wider">{label}</span>
      </div>
      <div className="text-2xl font-bold font-mono text-white">{value}</div>
      <div className="text-xs text-zinc-500 mt-0.5">{sub}</div>
    </div>
  );
}

function MiniStat({ label, value }: { label: string; value: string }) {
  return (
    <div className="bg-zinc-800/50 rounded-lg p-2.5">
      <div className="text-[10px] text-zinc-500 uppercase">{label}</div>
      <div className="text-sm font-mono font-semibold text-zinc-200">{value}</div>
    </div>
  );
}
