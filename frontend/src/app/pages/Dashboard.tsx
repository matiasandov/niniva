import { AlertCircle, AlertTriangle, ArrowRight, Bell, Brain, CalendarDays, CheckCircle2, Clock, Plus, Smartphone, Users, UserPlus } from "lucide-react";
import { Link } from "react-router";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

type Urgency   = 'urgent' | 'review' | 'pending';
type TestResult = 'flagged' | 'borderline' | 'normal';
type Severity  = 'high' | 'medium' | 'low';

const urgencyConfig: Record<Urgency, { badge: string; border: string; dot: string }> = {
  urgent:  { badge: 'bg-red-100 text-red-700',    border: 'border-l-red-500',    dot: 'bg-red-500' },
  review:  { badge: 'bg-amber-100 text-amber-800', border: 'border-l-amber-400',  dot: 'bg-amber-500' },
  pending: { badge: 'bg-slate-100 text-slate-600', border: 'border-l-slate-300',  dot: 'bg-slate-400' },
};

const resultConfig: Record<TestResult, { badge: string; dot: string }> = {
  flagged:    { badge: 'bg-red-100 text-red-700',      dot: 'bg-red-500' },
  borderline: { badge: 'bg-amber-100 text-amber-800',  dot: 'bg-amber-400' },
  normal:     { badge: 'bg-emerald-100 text-emerald-700', dot: 'bg-emerald-500' },
};

const severityIcon: Record<Severity, { Icon: typeof AlertCircle; color: string; bg: string }> = {
  high:   { Icon: AlertCircle,   color: 'text-red-500',    bg: 'bg-red-50 border-red-100' },
  medium: { Icon: AlertTriangle, color: 'text-amber-500',  bg: 'bg-amber-50 border-amber-100' },
  low:    { Icon: CheckCircle2,  color: 'text-teal-500',   bg: 'bg-teal-50 border-teal-100' },
};

const priorityPatients = [
  { id: '1', name: 'Arthur Pendelton', age: 68, avatar: 'AP', urgency: 'urgent' as Urgency,
    condition: "Parkinson's — Early Stage",
    alert: 'Resting tremor ↑ 5.3 Hz · sequence effect confirmed across sessions',
    timeAgo: '2h ago' },
  { id: '5', name: 'Margaret Liu', age: 72, avatar: 'ML', urgency: 'urgent' as Urgency,
    condition: 'Drug-Induced Parkinsonism',
    alert: 'Voice pause 38% — exceeds PD average threshold',
    timeAgo: '4h ago' },
  { id: '3', name: 'Carlos Ruiz', age: 61, avatar: 'CR', urgency: 'review' as Urgency,
    condition: 'Essential Tremor',
    alert: 'Tapping frequency declining — avg. 2.1 Hz over last 3 tests',
    timeAgo: 'Yesterday' },
  { id: '7', name: 'Elena Torres', age: 55, avatar: 'ET', urgency: 'pending' as Urgency,
    condition: 'Under evaluation',
    alert: 'Remote test submission overdue · 3 days',
    timeAgo: '3d ago' },
];

const remoteActivity = [
  { id: '5',  name: 'Margaret Liu',  test: 'Finger Tapping',   timeAgo: '35 min ago', result: 'flagged'    as TestResult, detail: 'Avg. 2.1 Hz — below PD threshold' },
  { id: '6',  name: 'John Roe',      test: 'Voice Pause',      timeAgo: '2h ago',     result: 'borderline' as TestResult, detail: '28% pause — approaching threshold' },
  { id: '8',  name: 'Elena Torres',  test: 'Resting Tremors',  timeAgo: '4h ago',     result: 'normal'     as TestResult, detail: 'Asymmetry 12% — within normal range' },
  { id: '9',  name: 'Robert Chang',  test: 'Finger Tapping',   timeAgo: '5h ago',     result: 'normal'     as TestResult, detail: 'Avg. 4.1 Hz — healthy range' },
  { id: '10', name: 'Maria Santos',  test: 'Voice Pause',      timeAgo: '6h ago',     result: 'flagged'    as TestResult, detail: '41% pause — significantly elevated' },
];

const todaySchedule = [
  { id: '1',  name: 'Arthur Pendelton', time: '9:00 AM',  type: 'Follow-up Session',   done: false },
  { id: '5',  name: 'Margaret Liu',     time: '11:00 AM', type: 'Motor Tests Review',   done: false },
  { id: '3',  name: 'Carlos Ruiz',      time: '2:00 PM',  type: 'New Evaluation',       done: false },
  { id: '11', name: 'Helen Park',       time: '4:30 PM',  type: 'Routine Check-in',     done: false },
];

const populationBreakdown = [
  { condition: "Parkinson's Disease",    count: 48, color: '#ef4444', bg: 'bg-red-500' },
  { condition: 'Essential Tremor',       count: 31, color: '#f97316', bg: 'bg-orange-500' },
  { condition: 'Drug-Induced Parkins.',  count: 22, color: '#8b5cf6', bg: 'bg-violet-500' },
  { condition: 'Other Neurological',     count: 41, color: '#94a3b8', bg: 'bg-slate-400' },
];
const populationTotal = populationBreakdown.reduce((s, g) => s + g.count, 0);

const aiInsights = [
  { id: '1',  name: 'Arthur Pendelton', severity: 'high'   as Severity, timeAgo: 'Today, 8:42 AM',
    text: 'Progressive sequence effect across 3 consecutive sessions. Consistent with early PD motor signature. Recommend expedited DaTscan.' },
  { id: '5',  name: 'Margaret Liu',     severity: 'high'   as Severity, timeAgo: 'Today, 7:15 AM',
    text: 'Voice pause increased 12% since last visit. Possible hypophonia progression. Consider urgent medication review.' },
  { id: '6',  name: 'John Roe',         severity: 'medium' as Severity, timeAgo: 'Yesterday',
    text: 'Right arm asymmetry trending upward over 6 remote sessions. Gradual motor decline — no immediate action required but monitor closely.' },
  { id: '3',  name: 'Carlos Ruiz',      severity: 'low'    as Severity, timeAgo: '2 days ago',
    text: 'Motor scores stable across last 4 evaluations. Current treatment protocol appears effective. Continue standard monitoring schedule.' },
];

export function Dashboard() {
  const { lang } = useLang();
  const t = useT(lang);
  const d = t.dashboard;

  const kpiStats = [
    { title: d.patientsUnderCare,     value: '142', sub: `+3 ${d.thisMonth}`,     subColor: 'text-emerald-600', icon: Users,       iconBg: 'bg-teal-100 text-teal-700' },
    { title: d.pendingReviewLabel,    value: '8',   sub: `2 ${d.urgentCount}`,    subColor: 'text-red-500',     icon: AlertCircle, iconBg: 'bg-amber-100 text-amber-700' },
    { title: d.remoteTestsTodayLabel, value: '5',   sub: `3 ${d.flaggedCount}`,   subColor: 'text-amber-600',   icon: Smartphone,  iconBg: 'bg-blue-100 text-blue-700' },
    { title: d.aiAlertsLabel,         value: '12',  sub: `5 ${d.newCount}`,       subColor: 'text-purple-600',  icon: Brain,       iconBg: 'bg-purple-100 text-purple-700' },
  ];

  const urgencyLabel: Record<Urgency, string> = {
    urgent: d.urgentBadge, review: d.reviewBadge, pending: d.pendingBadge,
  };
  const resultLabel: Record<TestResult, string> = {
    flagged: d.flaggedBadge, borderline: d.borderlineBadge, normal: d.normalBadge,
  };
  const severityLabel: Record<Severity, string> = {
    high: d.highSeverity, medium: d.mediumSeverity, low: d.lowSeverity,
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">

      {/* ── Header ─────────────────────────────────────────────────── */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{d.welcome}</h1>
          <p className="text-slate-500 text-sm mt-0.5">{d.subtitle}</p>
        </div>
        <div className="flex items-center gap-2">
          <Link
            to="/patients"
            className="inline-flex items-center gap-2 px-4 py-2 bg-white border border-slate-200 text-slate-700 rounded-lg font-medium hover:bg-slate-50 transition-colors text-sm"
          >
            <UserPlus className="w-4 h-4" />
            {d.addPatient}
          </Link>
          <Link
            to="/live"
            className="inline-flex items-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm text-sm"
          >
            <Plus className="w-4 h-4" />
            {d.startSession}
          </Link>
        </div>
      </div>

      {/* ── AI Clinical Insights ─────────────────────────────────── */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div>
            <h2 className="text-lg font-bold text-slate-800 flex items-center gap-2">
              <Bell className="w-5 h-5 text-purple-600" />
              {d.aiInsightsTitle}
            </h2>
            <p className="text-sm text-slate-500">{d.aiInsightsSubtitle}</p>
          </div>
          <span className="text-xs text-slate-400 flex items-center gap-1">
            <Clock className="w-3.5 h-3.5" /> Updated just now
          </span>
        </div>
        <div className="flex items-center gap-2 bg-amber-50 border border-amber-200 rounded-lg px-4 py-2.5 mb-4">
          <AlertTriangle className="w-4 h-4 text-amber-500 shrink-0" />
          <p className="text-xs text-amber-800">{d.aiDisclaimer}</p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {aiInsights.map((insight) => {
            const { Icon, color, bg } = severityIcon[insight.severity];
            return (
              <div key={insight.id} className={`rounded-xl border p-5 flex gap-4 ${bg}`}>
                <Icon className={`w-5 h-5 shrink-0 mt-0.5 ${color}`} />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center justify-between gap-2 mb-1">
                    <span className="text-sm font-semibold text-slate-900">{insight.name}</span>
                    <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full shrink-0 ${severityIcon[insight.severity].bg.replace('50', '100').replace('border-', '')} ${color}`}>
                      {severityLabel[insight.severity]}
                    </span>
                  </div>
                  <p className="text-sm text-slate-700 leading-relaxed">{insight.text}</p>
                  <div className="flex items-center justify-between mt-3">
                    <span className="text-xs text-slate-400">{insight.timeAgo}</span>
                    <Link to={`/patients/${insight.id}`} className="text-xs font-medium text-teal-600 hover:text-teal-800 flex items-center gap-0.5 transition-colors">
                      {d.viewProfile} <ArrowRight className="w-3 h-3" />
                    </Link>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* ── KPI Stats ──────────────────────────────────────────────── */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        {kpiStats.map((stat, i) => (
          <div key={i} className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className={`p-3 rounded-lg shrink-0 ${stat.iconBg}`}>
              <stat.icon className="w-5 h-5" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-medium text-slate-500 truncate">{stat.title}</p>
              <p className="text-2xl font-bold text-slate-900 leading-tight">{stat.value}</p>
              <p className={`text-xs font-medium mt-0.5 ${stat.subColor}`}>{stat.sub}</p>
            </div>
          </div>
        ))}
      </div>

      {/* ── Patient Population Strip ─────────────────────────────── */}
      <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-4">
        <div className="flex items-center justify-between mb-3">
          <span className="text-sm font-semibold text-slate-700">{d.populationTitle}</span>
          <span className="text-xs text-slate-400">{populationTotal} patients total</span>
        </div>
        <div className="flex h-3 rounded-full overflow-hidden gap-0.5">
          {populationBreakdown.map((g) => (
            <div
              key={g.condition}
              className={`${g.bg} rounded-full`}
              style={{ width: `${(g.count / populationTotal) * 100}%` }}
              title={`${g.condition}: ${g.count}`}
            />
          ))}
        </div>
        <div className="flex flex-wrap gap-x-5 gap-y-1.5 mt-3">
          {populationBreakdown.map((g) => (
            <div key={g.condition} className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: g.color }} />
              <span className="text-xs text-slate-600">{g.condition}</span>
              <span className="text-xs font-semibold text-slate-900">{g.count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* ── Main Grid ────────────────────────────────────────────── */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">

        {/* Left column */}
        <div className="lg:col-span-2 space-y-6">

          {/* Priority Review Queue */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-slate-900 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 text-red-500" />
                  {d.priorityQueueTitle}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">{d.priorityQueueSubtitle}</p>
              </div>
              <Link to="/patients" className="text-xs text-teal-600 hover:text-teal-700 font-medium flex items-center gap-1">
                {d.viewAll} <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="divide-y divide-slate-100">
              {priorityPatients.map((p) => {
                const cfg = urgencyConfig[p.urgency];
                return (
                  <div key={p.id} className={`flex items-center gap-4 px-5 py-4 border-l-4 hover:bg-slate-50 transition-colors ${cfg.border}`}>
                    <div className="w-9 h-9 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center text-xs font-bold shrink-0">
                      {p.avatar}
                    </div>
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-0.5">
                        <span className="text-sm font-semibold text-slate-900">{p.name}</span>
                        <span className="text-xs text-slate-400">{p.age}y</span>
                        <span className={`text-xs font-medium px-1.5 py-0.5 rounded-full ${cfg.badge}`}>
                          {urgencyLabel[p.urgency]}
                        </span>
                      </div>
                      <p className="text-xs text-slate-500 truncate">{p.condition}</p>
                      <p className="text-xs text-slate-700 mt-0.5 truncate">{p.alert}</p>
                    </div>
                    <div className="flex flex-col items-end gap-2 shrink-0">
                      <span className="text-xs text-slate-400">{p.timeAgo}</span>
                      <Link to={`/patients/${p.id}`} className="text-xs text-teal-600 hover:text-teal-800 font-medium flex items-center gap-0.5">
                        {d.viewProfile} <ArrowRight className="w-3 h-3" />
                      </Link>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>

          {/* Remote Test Activity */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex items-center justify-between">
              <div>
                <h2 className="font-semibold text-slate-900 flex items-center gap-2">
                  <Smartphone className="w-4 h-4 text-blue-500" />
                  {d.remoteActivityTitle}
                </h2>
                <p className="text-xs text-slate-500 mt-0.5">{d.remoteActivitySubtitle}</p>
              </div>
              <span className="flex items-center gap-1.5 text-xs font-medium text-emerald-700 bg-emerald-50 border border-emerald-200 px-2 py-1 rounded-full">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                {d.liveLabel}
              </span>
            </div>
            <div className="divide-y divide-slate-100">
              {remoteActivity.map((entry) => {
                const cfg = resultConfig[entry.result];
                return (
                  <div key={`${entry.id}-${entry.test}`} className="flex items-center gap-4 px-5 py-3.5 hover:bg-slate-50 transition-colors">
                    <span className={`w-2 h-2 rounded-full shrink-0 ${cfg.dot}`} />
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-sm font-medium text-slate-900">{entry.name}</span>
                        <span className="text-xs text-slate-400">·</span>
                        <span className="text-xs text-slate-500">{entry.test}</span>
                      </div>
                      <p className="text-xs text-slate-500 mt-0.5 truncate">{entry.detail}</p>
                    </div>
                    <div className="flex items-center gap-3 shrink-0">
                      <span className={`text-xs font-medium px-2 py-0.5 rounded-full ${cfg.badge}`}>
                        {resultLabel[entry.result]}
                      </span>
                      <span className="text-xs text-slate-400 w-16 text-right">{entry.timeAgo}</span>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

        {/* Right column */}
        <div className="space-y-6">

          {/* Today's Schedule */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
            <div className="p-5 border-b border-slate-100 flex items-center gap-2">
              <CalendarDays className="w-4 h-4 text-teal-600" />
              <h2 className="font-semibold text-slate-900">{d.scheduleTitle}</h2>
            </div>
            <div className="divide-y divide-slate-100">
              {todaySchedule.map((appt) => (
                <div key={appt.id} className="px-5 py-3.5 flex items-center gap-3 hover:bg-slate-50 transition-colors">
                  <div className="text-center shrink-0 w-14">
                    <span className="text-xs font-bold text-teal-600 block leading-tight">{appt.time.split(' ')[0]}</span>
                    <span className="text-xs text-slate-400">{appt.time.split(' ')[1]}</span>
                  </div>
                  <div className="w-px h-8 bg-slate-200 shrink-0" />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-slate-900 truncate">{appt.name}</p>
                    <p className="text-xs text-slate-500">{appt.type}</p>
                  </div>
                  <Link to={`/patients/${appt.id}`}>
                    <ArrowRight className="w-4 h-4 text-slate-300 hover:text-teal-600 transition-colors" />
                  </Link>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
            <h2 className="font-semibold text-slate-900 mb-3">{d.quickActions}</h2>
            <div className="space-y-2">
              <Link to="/live" className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-teal-400 hover:bg-teal-50 transition-all group">
                <div className="p-1.5 bg-slate-100 rounded-md group-hover:bg-teal-100 group-hover:text-teal-700 text-slate-600 transition-colors">
                  <Brain className="w-4 h-4" />
                </div>
                <span className="text-sm font-medium text-slate-700 group-hover:text-teal-800 transition-colors">{d.startAIRecording}</span>
              </Link>
              <Link to="/tests" className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-teal-400 hover:bg-teal-50 transition-all group">
                <div className="p-1.5 bg-slate-100 rounded-md group-hover:bg-teal-100 group-hover:text-teal-700 text-slate-600 transition-colors">
                  <Smartphone className="w-4 h-4" />
                </div>
                <span className="text-sm font-medium text-slate-700 group-hover:text-teal-800 transition-colors">{d.performMotorTests}</span>
              </Link>
              <Link to="/patients" className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-teal-400 hover:bg-teal-50 transition-all group">
                <div className="p-1.5 bg-slate-100 rounded-md group-hover:bg-teal-100 group-hover:text-teal-700 text-slate-600 transition-colors">
                  <Users className="w-4 h-4" />
                </div>
                <span className="text-sm font-medium text-slate-700 group-hover:text-teal-800 transition-colors">{d.patientsUnderCare}</span>
              </Link>
            </div>
          </div>
        </div>
      </div>


    </div>
  );
}
