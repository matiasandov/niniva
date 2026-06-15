import { Activity, Brain, Clock, Mic, Plus, Users } from "lucide-react";
import { Link } from "react-router";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

export function Dashboard() {
  const { lang } = useLang();
  const t = useT(lang);
  const d = t.dashboard;

  const stats = [
    { title: d.todaySessions, value: "4", icon: Clock, color: "bg-blue-100 text-blue-700" },
    { title: d.totalPatients, value: "142", icon: Users, color: "bg-teal-100 text-teal-700" },
    { title: d.newInsights, value: "12", icon: Brain, color: "bg-purple-100 text-purple-700" },
    { title: d.testsCompleted, value: "38", icon: Activity, color: "bg-orange-100 text-orange-700" },
  ];

  const recentPatients = [
    { id: "1", name: "Arthur Pendelton", status: "Review Recommended", date: "2 hours ago" },
    { id: "2", name: "Martha Stewart", status: "Stable", date: "5 hours ago" },
    { id: "3", name: "John Doe", status: "Tests Pending", date: "Yesterday" },
  ];

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{d.welcome}</h1>
          <p className="text-slate-500">{d.subtitle}</p>
        </div>
        <Link
          to="/live"
          className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm"
        >
          <Plus className="w-5 h-5" />
          {d.startSession}
        </Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, idx) => (
          <div key={idx} className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
            <div className={`p-3 rounded-lg ${stat.color}`}>
              <stat.icon className="w-6 h-6" />
            </div>
            <div>
              <p className="text-sm font-medium text-slate-500">{stat.title}</p>
              <p className="text-2xl font-bold text-slate-900">{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="p-6 border-b border-slate-100 flex justify-between items-center">
            <h2 className="text-lg font-semibold text-slate-900">{d.recentSessions}</h2>
            <Link to="/patients" className="text-sm text-teal-600 hover:text-teal-700 font-medium">
              {d.viewAll}
            </Link>
          </div>
          <div className="divide-y divide-slate-100">
            {recentPatients.map((patient) => (
              <div key={patient.id} className="p-6 flex items-center justify-between hover:bg-slate-50 transition-colors">
                <div className="flex flex-col">
                  <span className="font-medium text-slate-900">{patient.name}</span>
                  <span className="text-sm text-slate-500">{patient.date}</span>
                </div>
                <div className="flex items-center gap-4">
                  <span className={`px-2.5 py-1 text-xs font-medium rounded-full ${
                    patient.status.includes("Review") ? "bg-amber-100 text-amber-800" :
                    patient.status.includes("Stable") ? "bg-emerald-100 text-emerald-800" :
                    "bg-slate-100 text-slate-800"
                  }`}>
                    {d.statuses[patient.status as keyof typeof d.statuses] ?? patient.status}
                  </span>
                  <Link to={`/patients/${patient.id}`} className="text-slate-400 hover:text-teal-600">
                    {d.view}
                  </Link>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-6">
          <h2 className="text-lg font-semibold text-slate-900 mb-4">{d.quickActions}</h2>
          <div className="space-y-3">
            <Link to="/live" className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-teal-500 hover:bg-teal-50 transition-all group">
              <div className="p-2 bg-slate-100 text-slate-600 rounded-md group-hover:bg-teal-100 group-hover:text-teal-700">
                <Mic className="w-5 h-5" />
              </div>
              <div className="flex-1 text-sm font-medium text-slate-700 group-hover:text-teal-800">
                {d.startAIRecording}
              </div>
            </Link>
            <Link to="/tests" className="flex items-center gap-3 p-3 rounded-lg border border-slate-200 hover:border-teal-500 hover:bg-teal-50 transition-all group">
              <div className="p-2 bg-slate-100 text-slate-600 rounded-md group-hover:bg-teal-100 group-hover:text-teal-700">
                <Activity className="w-5 h-5" />
              </div>
              <div className="flex-1 text-sm font-medium text-slate-700 group-hover:text-teal-800">
                {d.performMotorTests}
              </div>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
