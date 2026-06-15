import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar, Legend } from 'recharts';
import { AlertTriangle, Brain, CheckCircle2, User, Activity, Calendar } from 'lucide-react';
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

export function PatientProfile() {
  const { id } = useParams();
  const { lang } = useLang();
  const t = useT(lang);
  const pp = t.patientProfile;

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

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Column */}
        <div className="lg:col-span-2 space-y-6">
          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-teal-600" />
              {pp.fingerTappingTitle}
            </h2>
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
                  <Line yAxisId="left" type="monotone" name={pp.freqLabel} dataKey="freq" stroke="#0d9488" strokeWidth={3} dot={{ r: 4 }} activeDot={{ r: 6 }} />
                  <Line yAxisId="right" type="monotone" name={pp.ampLabel} dataKey="amplitude" stroke="#f59e0b" strokeWidth={3} dot={{ r: 4 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm">
            <h2 className="text-lg font-bold text-slate-900 mb-4 flex items-center gap-2">
              <Activity className="w-5 h-5 text-purple-600" />
              {pp.voicePauseTitle}
            </h2>
            <p className="text-sm text-slate-500 mb-6">{pp.voicePauseDesc}</p>
            <div className="h-[250px] w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={voicePauseData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }} barSize={40}>
                  <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                  <XAxis dataKey="category" stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} />
                  <YAxis stroke="#64748b" fontSize={12} tickLine={false} axisLine={false} tickFormatter={(val) => `${val}%`} />
                  <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '8px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                  <Bar dataKey="pausePercent" fill="#8b5cf6" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        {/* Right Column */}
        <div className="space-y-6">
          <div className="bg-white rounded-xl border border-teal-200 shadow-sm overflow-hidden">
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
      </div>
    </div>
  );
}
