import { useState } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend, ReferenceLine, ScatterChart, Scatter, ZAxis } from 'recharts';
import { AlertTriangle, Brain, CheckCircle2, User, Activity, Calendar, Pill, Stethoscope, HelpCircle, Pencil, Check, X, Users } from 'lucide-react';
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

const restingTremorData = [
  { time: '0s',  rightArm: 4.2, leftArm: 0.4 },
  { time: '2s',  rightArm: 5.1, leftArm: 0.3 },
  { time: '4s',  rightArm: 4.8, leftArm: 0.5 },
  { time: '6s',  rightArm: 5.3, leftArm: 0.2 },
  { time: '8s',  rightArm: 4.6, leftArm: 0.4 },
  { time: '10s', rightArm: 5.0, leftArm: 0.3 },
];

// x = avg tapping frequency (Hz), y = voice pause (%)
const clusterData = {
  parkinsons: [
    { x: 1.9, y: 42 }, { x: 2.1, y: 38 }, { x: 2.3, y: 35 }, { x: 1.7, y: 44 },
    { x: 2.0, y: 40 }, { x: 1.8, y: 41 }, { x: 2.4, y: 36 }, { x: 2.2, y: 39 },
    { x: 1.6, y: 45 }, { x: 2.1, y: 43 }, { x: 1.9, y: 37 }, { x: 2.3, y: 33 },
    { x: 1.5, y: 46 }, { x: 2.0, y: 41 }, { x: 2.2, y: 34 },
  ],
  healthy: [
    { x: 4.2, y: 8 },  { x: 4.8, y: 6 },  { x: 5.1, y: 7 },  { x: 4.5, y: 9 },
    { x: 5.3, y: 5 },  { x: 4.0, y: 11 }, { x: 4.7, y: 7 },  { x: 5.0, y: 6 },
    { x: 4.3, y: 10 }, { x: 5.2, y: 8 },  { x: 4.6, y: 9 },  { x: 4.9, y: 6 },
    { x: 4.4, y: 12 }, { x: 5.1, y: 5 },  { x: 4.7, y: 8 },
  ],
  diabetes: [
    { x: 3.5, y: 14 }, { x: 3.8, y: 12 }, { x: 4.1, y: 11 }, { x: 3.2, y: 16 },
    { x: 4.3, y: 10 }, { x: 3.6, y: 15 }, { x: 3.9, y: 13 }, { x: 4.0, y: 12 },
    { x: 3.3, y: 17 }, { x: 4.2, y: 11 }, { x: 3.7, y: 14 },
  ],
  psychosis: [
    { x: 3.0, y: 22 }, { x: 3.5, y: 18 }, { x: 2.8, y: 25 }, { x: 3.2, y: 20 },
    { x: 4.0, y: 15 }, { x: 3.1, y: 24 }, { x: 2.7, y: 28 }, { x: 3.4, y: 19 },
    { x: 3.6, y: 17 }, { x: 2.9, y: 26 }, { x: 3.3, y: 21 },
  ],
  dip: [
    { x: 2.5, y: 29 }, { x: 2.8, y: 25 }, { x: 3.0, y: 22 }, { x: 2.3, y: 32 },
    { x: 3.2, y: 20 }, { x: 2.6, y: 29 }, { x: 2.9, y: 24 }, { x: 2.4, y: 31 },
    { x: 3.1, y: 21 }, { x: 2.7, y: 27 }, { x: 2.5, y: 33 },
  ],
  others: [
    { x: 2.0, y: 20 }, { x: 3.8, y: 30 }, { x: 4.5, y: 22 }, { x: 1.8, y: 15 },
    { x: 3.0, y: 35 }, { x: 5.0, y: 20 }, { x: 1.5, y: 30 }, { x: 4.2, y: 28 },
  ],
  patient: [{ x: 2.65, y: 34 }],
};

const clusterProximity = [
  { key: 'parkinsons', color: '#ef4444', pct: 82 },
  { key: 'dip',        color: '#f97316', pct: 58 },
  { key: 'psychosis',  color: '#8b5cf6', pct: 24 },
  { key: 'others',     color: '#94a3b8', pct: 20 },
  { key: 'diabetes',   color: '#f59e0b', pct: 12 },
  { key: 'healthy',    color: '#10b981', pct:  5 },
];

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

  const [isEditingNotes, setIsEditingNotes] = useState(false);
  const [savedNotes, setSavedNotes] = useState(pp.notesDefault);
  const [draftNotes, setDraftNotes] = useState(pp.notesDefault);

  const renderPatientDot = (props: any) => {
    const { cx, cy } = props;
    return (
      <g key={`patient-${cx}-${cy}`}>
        <circle cx={cx} cy={cy} r={16} fill="#0d9488" fillOpacity={0.12} />
        <circle cx={cx} cy={cy} r={8}  fill="#0d9488" stroke="white" strokeWidth={2.5} />
      </g>
    );
  };

  const handleSaveNotes = () => {
    setSavedNotes(draftNotes);
    setIsEditingNotes(false);
  };

  const handleCancelNotes = () => {
    setDraftNotes(savedNotes);
    setIsEditingNotes(false);
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

      {/* Population Benchmarking */}
      <div>
        <div className="mb-5">
          <h2 className="text-xl font-bold text-slate-800 flex items-center gap-2 mb-1">
            <Users className="w-5 h-5 text-teal-600" />
            {pp.benchmarkTitle}
          </h2>
          <p className="text-sm text-slate-500">{pp.benchmarkSubtitle}</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Scatter chart */}
          <div className="lg:col-span-2 bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            {/* Custom legend — flex-wrap so nothing overlaps */}
            <div className="flex flex-wrap gap-x-5 gap-y-2 mb-4">
              {(
                [
                  { key: 'parkinsons', color: '#ef4444' },
                  { key: 'dip',        color: '#f97316' },
                  { key: 'psychosis',  color: '#8b5cf6' },
                  { key: 'diabetes',   color: '#f59e0b' },
                  { key: 'healthy',    color: '#10b981' },
                  { key: 'others',     color: '#94a3b8' },
                ] as const
              ).map(({ key, color }) => (
                <div key={key} className="flex items-center gap-1.5">
                  <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: color }} />
                  <span className="text-xs text-slate-600">{pp.benchmarkClusters[key]}</span>
                </div>
              ))}
              <div className="flex items-center gap-1.5">
                <span className="relative flex w-3 h-3 shrink-0">
                  <span className="absolute inset-0 rounded-full bg-teal-500 opacity-30" />
                  <span className="relative m-auto w-2 h-2 rounded-full bg-teal-600" />
                </span>
                <span className="text-xs font-semibold text-teal-700">{pp.benchmarkClusters.patient}</span>
              </div>
            </div>

            <div className="h-[380px]">
              <ResponsiveContainer width="100%" height="100%">
                <ScatterChart margin={{ top: 10, right: 24, bottom: 36, left: 16 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
                  <XAxis
                    dataKey="x" type="number" name={pp.benchmarkXLabel}
                    domain={[1, 6]} unit=" Hz"
                    stroke="#64748b" fontSize={11} tickLine={false}
                    label={{ value: pp.benchmarkXLabel, position: 'insideBottom', offset: -22, fontSize: 11, fill: '#64748b' }}
                  />
                  <YAxis
                    dataKey="y" type="number" name={pp.benchmarkYLabel}
                    domain={[0, 50]} unit="%"
                    stroke="#64748b" fontSize={11} tickLine={false} axisLine={false}
                    label={{ value: pp.benchmarkYLabel, angle: -90, position: 'insideLeft', offset: 12, fontSize: 11, fill: '#64748b' }}
                  />
                  <ZAxis range={[48, 48]} />
                  <Tooltip
                    cursor={{ strokeDasharray: '3 3' }}
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)', fontSize: 12 }}
                    formatter={(value: number, name: string) => [
                      name === pp.benchmarkXLabel ? `${value} Hz` : `${value}%`,
                      name,
                    ]}
                  />
                  <Scatter name={pp.benchmarkClusters.parkinsons} data={clusterData.parkinsons} fill="#ef4444" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.dip}         data={clusterData.dip}        fill="#f97316" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.psychosis}   data={clusterData.psychosis}  fill="#8b5cf6" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.diabetes}    data={clusterData.diabetes}   fill="#f59e0b" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.healthy}     data={clusterData.healthy}    fill="#10b981" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.others}      data={clusterData.others}     fill="#94a3b8" fillOpacity={0.6} />
                  <Scatter name={pp.benchmarkClusters.patient}     data={clusterData.patient}    fill="#0d9488" shape={renderPatientDot} />
                </ScatterChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Cluster proximity panel */}
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col gap-5">
            <div>
              <h3 className="text-sm font-bold text-slate-700 mb-1">{pp.benchmarkProximityTitle}</h3>
              <p className="text-xs text-slate-500 leading-relaxed">{pp.benchmarkProximityDesc}</p>
            </div>

            <div className="space-y-3">
              {clusterProximity.map((cluster) => (
                <div key={cluster.key}>
                  <div className="flex items-center justify-between mb-1">
                    <div className="flex items-center gap-2">
                      <span className="w-2.5 h-2.5 rounded-full shrink-0" style={{ backgroundColor: cluster.color }} />
                      <span className="text-xs font-medium text-slate-700">
                        {pp.benchmarkClusters[cluster.key as keyof typeof pp.benchmarkClusters]}
                      </span>
                    </div>
                    <span className="text-xs font-bold" style={{ color: cluster.color }}>{cluster.pct}%</span>
                  </div>
                  <div className="h-2 bg-slate-100 rounded-full overflow-hidden">
                    <div
                      className="h-full rounded-full transition-all"
                      style={{ width: `${cluster.pct}%`, backgroundColor: cluster.color, opacity: 0.8 }}
                    />
                  </div>
                </div>
              ))}
            </div>

            <p className="text-xs text-slate-400 leading-relaxed border-t border-slate-100 pt-4 mt-auto">
              {pp.benchmarkNote}
            </p>
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
              <Activity className="w-5 h-5 text-indigo-600" />
              {pp.restingTremorsTitle}
            </h3>
            <p className="text-sm text-slate-500 mb-6">{pp.restingTremorsDesc}</p>
            <div className="h-[300px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={restingTremorData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="time" stroke="#64748b" fontSize={12} tickLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(v) => `${v} Hz`} domain={[0, 7]} />
                  <Tooltip
                    contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                    formatter={(value: number, name: string) => [`${value} Hz`, name]}
                  />
                  <Legend />
                  <ReferenceLine
                    y={0.8}
                    stroke="#10b981"
                    strokeDasharray="6 3"
                    strokeWidth={2}
                    label={{ value: pp.healthyAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#059669', fontWeight: 600 }}
                  />
                  <ReferenceLine
                    y={3.5}
                    stroke="#ef4444"
                    strokeDasharray="6 3"
                    strokeWidth={2}
                    label={{ value: pp.parkinsonsAvgLabel, position: 'insideTopRight', fontSize: 10, fill: '#dc2626', fontWeight: 600 }}
                  />
                  <Line type="monotone" name={pp.restingTremorsRightArm} dataKey="rightArm" stroke="#ef4444" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line type="monotone" name={pp.restingTremorsLeftArm}  dataKey="leftArm"  stroke="#10b981" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>

            {/* Asymmetry summary row */}
            <div className="mt-5 grid grid-cols-3 gap-3 text-center">
              <div className="bg-red-50 border border-red-100 rounded-lg p-3">
                <p className="text-xs text-slate-500 mb-1">{pp.restingTremorsRightArm}</p>
                <p className="text-lg font-bold text-red-600">4.2–5.3 Hz</p>
                <p className="text-xs text-red-500 mt-0.5">{pp.restingTremorsTremorDetected}</p>
              </div>
              <div className="bg-slate-50 border border-slate-200 rounded-lg p-3 flex flex-col items-center justify-center gap-1">
                <p className="text-xs text-slate-500">{pp.restingTremorsAsymmetryIndex}</p>
                <div className="w-full h-2 bg-slate-200 rounded-full overflow-hidden mt-1">
                  <div className="h-full rounded-full bg-gradient-to-r from-emerald-400 via-amber-400 to-red-500" style={{ width: '78%' }} />
                </div>
                <p className="text-sm font-bold text-red-600">78% — {pp.restingTremorsAsymmetryLevel}</p>
              </div>
              <div className="bg-emerald-50 border border-emerald-100 rounded-lg p-3">
                <p className="text-xs text-slate-500 mb-1">{pp.restingTremorsLeftArm}</p>
                <p className="text-lg font-bold text-emerald-600">~0.3 Hz</p>
                <p className="text-xs text-emerald-600 mt-0.5">{pp.restingTremorsNormal}</p>
              </div>
            </div>

            <div className="mt-5 p-4 bg-amber-50 rounded-lg border border-amber-100 flex gap-3">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <p className="text-sm text-amber-800 leading-relaxed">{pp.restingTremorsObservation}</p>
            </div>
          </div>
        </div>
      </div>

      {/* Doctor's Notes */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-4 border-b border-slate-100 bg-slate-50 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Pencil className="w-4 h-4 text-slate-500" />
            <h2 className="font-semibold text-slate-800">{pp.notesTitle}</h2>
          </div>
          {isEditingNotes ? (
            <div className="flex items-center gap-2">
              <button
                onClick={handleCancelNotes}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
              >
                <X className="w-3.5 h-3.5" />
                {pp.notesCancel}
              </button>
              <button
                onClick={handleSaveNotes}
                className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
              >
                <Check className="w-3.5 h-3.5" />
                {pp.notesSave}
              </button>
            </div>
          ) : (
            <button
              onClick={() => setIsEditingNotes(true)}
              className="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium text-slate-600 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors"
            >
              <Pencil className="w-3.5 h-3.5" />
              {pp.notesEdit}
            </button>
          )}
        </div>

        <div className="p-5">
          {isEditingNotes ? (
            <textarea
              value={draftNotes}
              onChange={(e) => setDraftNotes(e.target.value)}
              rows={6}
              placeholder={pp.notesPlaceholder}
              className="w-full text-sm text-slate-700 leading-relaxed resize-none rounded-lg border border-slate-200 p-3 focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent transition"
            />
          ) : (
            <div>
              <p className="text-xs text-slate-400 mb-3 flex items-center gap-1.5">
                <span className="font-medium text-slate-500">{pp.notesAuthor}</span>
                <span>·</span>
                <span>{pp.lastVisit} {pp.today}</span>
              </p>
              {savedNotes ? (
                <p className="text-sm text-slate-700 leading-relaxed whitespace-pre-wrap">{savedNotes}</p>
              ) : (
                <p className="text-sm text-slate-400 italic">{pp.notesPlaceholder}</p>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
