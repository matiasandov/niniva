import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, ReferenceLine } from 'recharts';
import { AlertTriangle, Brain, CheckCircle2, User, Activity, Calendar, Pill, Stethoscope, HelpCircle, Camera, Loader2 } from 'lucide-react';
import { useParams, Link } from 'react-router';
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

const fingerTappingData = [
  { time: '0s', freq: 3.5, amplitude: 100 },
  { time: '2s', freq: 3.2, amplitude: 95 },
  { time: '4s', freq: 2.8, amplitude: 80 },
  { time: '6s', freq: 2.4, amplitude: 65 },
  { time: '8s', freq: 2.2, amplitude: 50 },
  { time: '10s', freq: 1.8, amplitude: 40 },
];

const voicePauseValues = [15, 28, 34];

type TremorState = 'idle' | 'recording' | 'analyzing' | 'done';

const confidenceColors: Record<string, string> = {
  High: 'bg-red-100 text-red-700',
  Moderate: 'bg-amber-100 text-amber-700',
  Low: 'bg-slate-100 text-slate-600',
  Alto: 'bg-red-100 text-red-700',
  Moderado: 'bg-amber-100 text-amber-700',
  Bajo: 'bg-slate-100 text-slate-600',
};

export function PatientProfile() {
  const { id } = useParams();
  const { lang } = useLang();
  const t = useT(lang);
  const pp = t.patientProfile;

  const [tremorState, setTremorState] = useState<TremorState>('idle');

  const launchTremorTest = () => {
    setTremorState('recording');
    setTimeout(() => {
      setTremorState('analyzing');
      setTimeout(() => {
        setTremorState('done');
      }, 2800);
    }, 3500);
  };

  const voicePauseData = pp.voicePauseCategories.map((category, i) => ({
    category,
    pausePercent: voicePauseValues[i],
  }));

  return (
    <div className="space-y-6 pb-12 max-w-6xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
        <div className="flex items-center gap-4">
          <div className="w-16 h-16 bg-teal-100 text-teal-700 rounded-full flex items-center justify-center font-bold text-2xl">
            AP
          </div>
          <div>
            <h1 className="text-2xl font-bold text-slate-900">Arthur Pendelton</h1>
            <div className="flex items-center gap-4 text-sm text-slate-500 mt-1">
              <span className="flex items-center gap-1"><User className="w-4 h-4" /> 68 {pp.age}</span>
              <span className="flex items-center gap-1"><Calendar className="w-4 h-4" /> {pp.lastVisit} {pp.today}</span>
              <span className="bg-amber-100 text-amber-800 px-2 py-0.5 rounded-full font-medium text-xs">{pp.reviewRequired}</span>
            </div>
          </div>
        </div>
        <div className="flex gap-2">
          <Link to="/live" className="px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-colors">
            {pp.startSession}
          </Link>
          <Link to="/tests" className="px-4 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors">
            {pp.runTests}
          </Link>
        </div>
      </div>

      {/* AI Interpretation + Collected Domain Data */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-teal-200 shadow-sm overflow-hidden">
          <div className="p-4 bg-teal-50 border-b border-teal-100 flex items-center gap-2">
            <Brain className="w-5 h-5 text-teal-700" />
            <h2 className="font-bold text-teal-900">{pp.aiInterpretation}</h2>
          </div>
          <div className="p-5 space-y-4">
            <p className="text-sm text-slate-700 leading-relaxed">{pp.aiSummary}</p>
            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">{pp.redFlagsDetected}</h3>
              <ul className="space-y-2">
                {pp.redFlags.map((flag, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                    <AlertTriangle className="w-4 h-4 text-red-500 shrink-0 mt-0.5" />
                    {flag}
                  </li>
                ))}
              </ul>
            </div>
            <div className="pt-4 border-t border-slate-100">
              <h3 className="text-xs font-bold text-slate-500 uppercase tracking-wider mb-3">{pp.recommendationsTitle}</h3>
              <ul className="space-y-2">
                {pp.recommendationsList.map((rec, i) => (
                  <li key={i} className="flex items-start gap-2 text-sm text-slate-700">
                    <CheckCircle2 className="w-4 h-4 text-teal-500 shrink-0 mt-0.5" />
                    {rec}
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50">
            <h2 className="font-semibold text-slate-800">{pp.collectedDomainData}</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {pp.domainData.map((item, i) => (
              <div key={i} className="p-4 flex flex-col gap-1">
                <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">{item.domain}</span>
                <span className="text-sm text-slate-900">{item.val}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Medications | Confirmed Diagnoses | Differential Diagnoses */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Medications */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
            <Pill className="w-4 h-4 text-teal-600" />
            <h2 className="font-semibold text-slate-800">{pp.medicationsTitle}</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {pp.medications.map((med, i) => (
              <div key={i} className="p-4 flex flex-col gap-1">
                <span className="text-sm font-medium text-slate-900">{med.name}</span>
                <span className="text-xs text-slate-500">{med.dose}</span>
                {med.note && (
                  <span className="mt-1 inline-flex items-center gap-1 text-xs text-amber-700 bg-amber-50 border border-amber-100 rounded px-2 py-0.5 w-fit">
                    <AlertTriangle className="w-3 h-3" />
                    {med.note}
                  </span>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Confirmed Diagnoses */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
            <Stethoscope className="w-4 h-4 text-teal-600" />
            <h2 className="font-semibold text-slate-800">{pp.confirmedDxTitle}</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {pp.confirmedDx.map((dx, i) => (
              <div key={i} className="p-4 flex flex-col gap-1.5">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium text-slate-900">{dx.name}</span>
                  <span className="shrink-0 text-xs bg-teal-50 text-teal-700 border border-teal-100 rounded px-2 py-0.5">{dx.status}</span>
                </div>
                <span className="text-xs text-slate-500">{pp.sinceLabel} {dx.since}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Differential Diagnoses */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center gap-2">
            <HelpCircle className="w-4 h-4 text-purple-600" />
            <h2 className="font-semibold text-slate-800">{pp.differentialDxTitle}</h2>
          </div>
          <div className="divide-y divide-slate-100">
            {pp.differentialDx.map((dx, i) => (
              <div key={i} className="p-4 flex flex-col gap-1.5">
                <div className="flex items-start justify-between gap-2">
                  <span className="text-sm font-medium text-slate-900 leading-snug">{dx.name}</span>
                  <span className={`shrink-0 text-xs rounded px-2 py-0.5 font-medium ${confidenceColors[dx.confidence] ?? 'bg-slate-100 text-slate-600'}`}>
                    {dx.confidence}
                  </span>
                </div>
                <span className="text-xs text-slate-500 leading-relaxed">{dx.rationale}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Motor Tests Results & Analytics */}
      <div>
        <div className="mb-5">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-1">
            <Activity className="w-5 h-5 text-teal-600" />
            {pp.motorTestsSectionTitle}
          </h2>
          <p className="text-sm text-slate-500">{pp.motorTestsSectionSubtitle}</p>
        </div>

        {/* Threshold legend */}
        <div className="flex items-center gap-6 mb-5 px-1">
          <div className="flex items-center gap-2">
            <svg width="28" height="10"><line x1="0" y1="5" x2="28" y2="5" stroke="#10b981" strokeWidth="2" strokeDasharray="5 3" /></svg>
            <span className="text-xs font-medium text-slate-600">{pp.healthyAvgLabel}</span>
          </div>
          <div className="flex items-center gap-2">
            <svg width="28" height="10"><line x1="0" y1="5" x2="28" y2="5" stroke="#ef4444" strokeWidth="2" strokeDasharray="5 3" /></svg>
            <span className="text-xs font-medium text-slate-600">{pp.parkinsonsAvgLabel}</span>
          </div>
        </div>

        <div className="space-y-6">
          {/* Finger Tapping Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-teal-600" />
              {pp.fingerTappingTitle}
            </h3>
            <p className="text-sm text-slate-500 mb-6">{pp.fingerTappingDesc}</p>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={fingerTappingData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis yAxisId="left" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis yAxisId="right" orientation="right" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <Tooltip contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Legend />
                  <ReferenceLine yAxisId="left" y={4.3} stroke="#10b981" strokeDasharray="6 3" strokeWidth={2}
                    label={{ value: pp.healthyAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#059669', fontWeight: 600 }} />
                  <ReferenceLine yAxisId="left" y={2.5} stroke="#ef4444" strokeDasharray="6 3" strokeWidth={2}
                    label={{ value: pp.parkinsonsAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#dc2626', fontWeight: 600 }} />
                  <Line yAxisId="left" type="monotone" name={pp.freqLabel} dataKey="freq" stroke="#0d9488" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line yAxisId="right" type="monotone" name={pp.ampLabel} dataKey="amplitude" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-5 p-4 bg-amber-50 rounded-lg border border-amber-100 flex gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800 leading-relaxed">{pp.fingerTappingObservation}</p>
            </div>
          </div>

          {/* Voice Pause Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-600" />
              {pp.voicePauseTitle}
            </h3>
            <p className="text-sm text-slate-500 mb-6">{pp.voicePauseDesc}</p>
            <div className="h-[260px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={voicePauseData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }} barSize={40}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="category" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                  <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <ReferenceLine y={10} stroke="#10b981" strokeDasharray="6 3" strokeWidth={2}
                    label={{ value: pp.healthyAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#059669', fontWeight: 600 }} />
                  <ReferenceLine y={32} stroke="#ef4444" strokeDasharray="6 3" strokeWidth={2}
                    label={{ value: pp.parkinsonsAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#dc2626', fontWeight: 600 }} />
                  <Bar dataKey="pausePercent" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
            <div className="mt-5 p-4 bg-amber-50 rounded-lg border border-amber-100 flex gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800 leading-relaxed">{pp.voicePauseObservation}</p>
            </div>
          </div>

          {/* Resting Tremors Card */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h3 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Camera className="w-5 h-5 text-indigo-600" />
              {pp.restingTremorsTitle}
            </h3>
            <p className="text-sm text-slate-500 mb-6">{pp.restingTremorsDesc}</p>

            {/* Idle state */}
            {tremorState === 'idle' && (
              <div className="flex flex-col items-center justify-center h-[220px] bg-slate-900 rounded-xl border border-slate-700 gap-5">
                <Camera className="w-14 h-14 text-slate-600" />
                <button
                  onClick={launchTremorTest}
                  className="px-5 py-2.5 bg-indigo-600 text-white rounded-lg font-medium hover:bg-indigo-700 transition-colors flex items-center gap-2 text-sm"
                >
                  <Camera className="w-4 h-4" />
                  {pp.restingTremorsLaunch}
                </button>
              </div>
            )}

            {/* Recording state */}
            {tremorState === 'recording' && (
              <div className="relative h-[220px] bg-slate-900 rounded-xl border border-slate-700 overflow-hidden flex flex-col items-center justify-center gap-4">
                {/* subtle grid */}
                <div className="absolute inset-0 opacity-[0.06]"
                  style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
                {/* REC badge */}
                <div className="absolute top-3 right-3 flex items-center gap-1.5 bg-black/50 px-2.5 py-1 rounded-full">
                  <span className="w-2 h-2 bg-red-500 rounded-full animate-pulse" />
                  <span className="text-xs text-white font-bold tracking-wider">REC</span>
                </div>
                {/* Person silhouette */}
                <svg width="90" height="100" viewBox="0 0 90 100" fill="none" className="opacity-25">
                  <circle cx="45" cy="13" r="11" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="45" y1="24" x2="45" y2="60" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="45" y1="34" x2="18" y2="55" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="45" y1="34" x2="72" y2="55" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="45" y1="60" x2="28" y2="72" stroke="#94a3b8" strokeWidth="2" />
                  <line x1="45" y1="60" x2="62" y2="72" stroke="#94a3b8" strokeWidth="2" />
                  <circle cx="18" cy="57" r="4" stroke="#94a3b8" strokeWidth="1.5" />
                  <circle cx="72" cy="57" r="4" stroke="#94a3b8" strokeWidth="1.5" />
                </svg>
                <p className="text-xs text-slate-400 text-center">{pp.restingTremorsRecording}</p>
              </div>
            )}

            {/* Analyzing state */}
            {tremorState === 'analyzing' && (
              <div className="relative h-[220px] bg-slate-900 rounded-xl border border-slate-700 overflow-hidden flex flex-col items-center justify-center gap-4">
                <div className="absolute inset-0 opacity-[0.06]"
                  style={{ backgroundImage: 'linear-gradient(rgba(255,255,255,1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,1) 1px, transparent 1px)', backgroundSize: '32px 32px' }} />
                {/* CV corner brackets */}
                <div className="absolute top-5 left-5 w-7 h-7 border-t-2 border-l-2 border-emerald-400 animate-pulse" />
                <div className="absolute top-5 right-5 w-7 h-7 border-t-2 border-r-2 border-emerald-400 animate-pulse" />
                <div className="absolute bottom-5 left-5 w-7 h-7 border-b-2 border-l-2 border-emerald-400 animate-pulse" />
                <div className="absolute bottom-5 right-5 w-7 h-7 border-b-2 border-r-2 border-emerald-400 animate-pulse" />
                {/* Keypoint dots simulating arm detection */}
                <div className="absolute" style={{ top: '55%', left: '26%' }}>
                  <span className="w-2.5 h-2.5 bg-emerald-400 rounded-full animate-ping block" />
                </div>
                <div className="absolute" style={{ top: '55%', right: '26%' }}>
                  <span className="w-2.5 h-2.5 bg-red-400 rounded-full animate-ping block" />
                </div>
                <div className="absolute" style={{ top: '38%', left: '38%' }}>
                  <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-ping block" />
                </div>
                <div className="absolute" style={{ top: '38%', right: '38%' }}>
                  <span className="w-1.5 h-1.5 bg-red-400 rounded-full animate-ping block" />
                </div>
                <Loader2 className="w-6 h-6 text-emerald-400 animate-spin" />
                <p className="text-xs text-slate-300 text-center">{pp.restingTremorsAnalyzing}</p>
              </div>
            )}

            {/* Done state — results */}
            {tremorState === 'done' && (
              <div className="space-y-4">
                {/* Arm comparison */}
                <div className="grid grid-cols-2 gap-4">
                  {/* Left arm — normal */}
                  <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-4 flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-700">{pp.restingTremorsLeftArm}</span>
                      <span className="flex items-center gap-1 text-xs font-semibold text-emerald-700 bg-emerald-100 px-2 py-0.5 rounded-full">
                        <CheckCircle2 className="w-3.5 h-3.5" />
                        {pp.restingTremorsNormal}
                      </span>
                    </div>
                    <div className="space-y-2 text-xs text-slate-600">
                      <div className="flex justify-between"><span>Frequency</span><span className="font-medium">~0.3 Hz</span></div>
                      <div className="flex justify-between"><span>Amplitude</span><span className="font-medium">Low</span></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs text-slate-500 mb-1"><span>Signal</span><span>8%</span></div>
                      <div className="h-2 bg-emerald-200 rounded-full overflow-hidden">
                        <div className="h-full bg-emerald-500 rounded-full" style={{ width: '8%' }} />
                      </div>
                    </div>
                  </div>

                  {/* Right arm — tremor */}
                  <div className="rounded-xl border border-red-200 bg-red-50 p-4 flex flex-col gap-3">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-bold text-slate-700">{pp.restingTremorsRightArm}</span>
                      <span className="flex items-center gap-1 text-xs font-semibold text-red-700 bg-red-100 px-2 py-0.5 rounded-full">
                        <AlertTriangle className="w-3.5 h-3.5" />
                        {pp.restingTremorsTremorDetected}
                      </span>
                    </div>
                    <div className="space-y-2 text-xs text-slate-600">
                      <div className="flex justify-between"><span>Frequency</span><span className="font-medium text-red-700">4–6 Hz</span></div>
                      <div className="flex justify-between"><span>Amplitude</span><span className="font-medium text-red-700">Elevated</span></div>
                    </div>
                    <div>
                      <div className="flex justify-between text-xs text-slate-500 mb-1"><span>Signal</span><span className="text-red-600 font-medium">78%</span></div>
                      <div className="h-2 bg-red-200 rounded-full overflow-hidden">
                        <div className="h-full bg-red-500 rounded-full" style={{ width: '78%' }} />
                      </div>
                    </div>
                  </div>
                </div>

                {/* Asymmetry Index */}
                <div className="bg-slate-50 border border-slate-200 rounded-xl p-4 space-y-2">
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-bold text-slate-700">{pp.restingTremorsAsymmetryIndex}</span>
                    <span className="text-sm font-bold text-red-700">78% — {pp.restingTremorsAsymmetryLevel}</span>
                  </div>
                  <div className="h-3 bg-slate-200 rounded-full overflow-hidden">
                    <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-red-500" style={{ width: '78%' }} />
                  </div>
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Symmetric</span>
                    <span>Highly Asymmetric</span>
                  </div>
                </div>

                <button
                  onClick={() => setTremorState('idle')}
                  className="text-xs text-indigo-600 hover:text-indigo-800 font-medium flex items-center gap-1 transition-colors"
                >
                  <Camera className="w-3.5 h-3.5" />
                  {pp.restingTremorsRerun}
                </button>
              </div>
            )}

            <div className="mt-5 p-4 bg-amber-50 rounded-lg border border-amber-100 flex gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800 leading-relaxed">{pp.restingTremorsObservation}</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
