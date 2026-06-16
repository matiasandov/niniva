import { Link } from "react-router";
import { Search, UserPlus, Filter, FileText } from "lucide-react";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

const Badge = ({ children, variant = "default" }: { children: React.ReactNode, variant?: "default" | "red" | "yellow" | "purple" | "slate" }) => {
  const styles = {
    default: "bg-slate-100 text-slate-700 border-slate-200",
    slate: "bg-slate-100 text-slate-700 border-slate-200",
    red: "bg-rose-50 text-rose-700 border-rose-200",
    yellow: "bg-amber-50 text-amber-700 border-amber-200",
    purple: "bg-purple-50 text-purple-700 border-purple-200"
  };
  return (
    <span className={`px-2 py-0.5 text-[11px] font-medium rounded-md border ${styles[variant]} whitespace-nowrap`}>
      {children}
    </span>
  );
};

export function PatientList() {
  const { lang } = useLang();
  const t = useT(lang);
  const p = t.patients;

  const patients = [
    {
      id: "1", name: "Arthur Pendelton", age: "68", sex: "M",
      dipRisk: [{ label: "Haloperidol", risk: "high" }], 
      exposures: [], 
      fallsOrthostatic: ["Orthostatic drop >30 mmHg"], 
      autonomic: ["Constipation", "nOH"], 
      symmetry: { label: "Asymmetric (Right)", flag: false }, 
      tremor: { label: "Resting", flag: false }, 
      lastVisit: "Today", status: "Review Recommended" 
    },
    { 
      id: "2", name: "Martha Stewart", age: "72", sex: "F",
      dipRisk: [], 
      exposures: ["Pesticides (Paraquat)"], 
      fallsOrthostatic: [], 
      autonomic: ["Urinary retention"], 
      symmetry: { label: "Symmetric Onset", flag: true }, 
      tremor: { label: "Action/Kinetic", flag: true }, 
      lastVisit: "5 hours ago", status: "Stable" 
    },
    { 
      id: "3", name: "John Doe", age: "55", sex: "M",
      dipRisk: [{ label: "Metoclopramide", risk: "high" }, { label: "Lithium", risk: "moderate" }], 
      exposures: ["Heavy metals (Mn)"], 
      fallsOrthostatic: ["Early backward falls"], 
      autonomic: [], 
      symmetry: { label: "Asymmetric", flag: false }, 
      tremor: { label: "None", flag: false }, 
      lastVisit: "Yesterday", status: "Tests Pending" 
    },
    { 
      id: "4", name: "Eleanor Rigby", age: "81", sex: "F",
      dipRisk: [], 
      exposures: [], 
      fallsOrthostatic: [], 
      autonomic: ["Constipation"], 
      symmetry: { label: "Asymmetric (Left)", flag: false }, 
      tremor: { label: "Resting (Unilateral)", flag: false }, 
      lastVisit: "Oct 12, 2023", status: "Stable" 
    },
    { 
      id: "5", name: "Robert California", age: "62", sex: "M",
      dipRisk: [{ label: "Quetiapine", risk: "moderate" }], 
      exposures: ["Cocaine"], 
      fallsOrthostatic: [], 
      autonomic: ["Severe ED (Early)"], 
      symmetry: { label: "Symmetric", flag: true }, 
      tremor: { label: "Resting", flag: false }, 
      lastVisit: "Sep 28, 2023", status: "Review Recommended" 
    },
    { 
      id: "6", name: "Evelyn Harper", age: "74", sex: "F",
      dipRisk: [{ label: "Valproate", risk: "moderate" }], 
      exposures: [], 
      fallsOrthostatic: ["Orthostatic drops"], 
      autonomic: ["nOH (Severe)"], 
      symmetry: { label: "Asymmetric (Right)", flag: false }, 
      tremor: { label: "Resting", flag: false }, 
      lastVisit: "Nov 02, 2023", status: "Tests Pending" 
    },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{p.title}</h1>
          <p className="text-slate-500">{p.subtitle}</p>
        </div>
        <button className="inline-flex items-center justify-center gap-2 px-4 py-2 bg-teal-600 text-white rounded-lg font-medium hover:bg-teal-700 transition-colors shadow-sm">
          <UserPlus className="w-5 h-5" />
          {p.addPatient}
        </button>
      </div>

      <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col">
        <div className="p-4 border-b border-slate-100 flex flex-col sm:flex-row gap-4 justify-between items-center bg-slate-50 rounded-t-xl">
          <div className="relative w-full sm:max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
            <input
              type="text"
              placeholder={p.searchPlaceholder}
              className="w-full pl-9 pr-4 py-2 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-teal-500 focus:border-transparent bg-white shadow-sm"
            />
          </div>
          <button className="flex items-center gap-2 px-4 py-2 border border-slate-200 bg-white rounded-lg text-sm font-medium text-slate-700 hover:bg-slate-50 transition-colors shadow-sm">
            <Filter className="w-4 h-4" />
            {p.filter}
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left border-collapse min-w-[1200px]">
            <thead>
              <tr className="bg-slate-50/80 text-slate-500 text-xs uppercase tracking-wider border-b border-slate-200">
                <th className="px-5 py-4 font-semibold">{p.colName}</th>
                <th className="px-4 py-4 font-semibold">{p.colAge}</th>
                <th className="px-4 py-4 font-semibold">{p.colSex}</th>
                <th className="px-4 py-4 font-semibold">{p.colDIPRisk}</th>
                <th className="px-4 py-4 font-semibold">{p.colExposures}</th>
                <th className="px-4 py-4 font-semibold">{p.colFallsOrthostatic}</th>
                <th className="px-4 py-4 font-semibold">{p.colAutonomic}</th>
                <th className="px-4 py-4 font-semibold">{p.colSymmetry}</th>
                <th className="px-4 py-4 font-semibold">{p.colTremor}</th>
                <th className="px-4 py-4 font-semibold">{p.colStatus}</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {patients.map((patient) => (
                <tr key={patient.id} className="hover:bg-slate-50/50 transition-colors group">
                  <td className="px-5 py-4">
                    <div className="flex items-center gap-4">
                      <div className="flex items-center gap-3 w-48">
                        <div className="w-9 h-9 rounded-full bg-teal-100 text-teal-700 flex items-center justify-center font-bold text-sm shadow-inner shrink-0">
                          {patient.name.split(' ').map(n => n[0]).join('')}
                        </div>
                        <div className="flex flex-col">
                          <span className="font-semibold text-slate-900 truncate">{patient.name}</span>
                          <span className="text-xs text-slate-400">ID: {patient.id.padStart(5, '0')}</span>
                        </div>
                      </div>
                      <Link
                        to={`/patients/${patient.id}`}
                        className="inline-flex items-center justify-center gap-1.5 px-3 py-1.5 text-xs font-medium text-teal-600 bg-teal-50 rounded-lg hover:bg-teal-100 transition-colors focus:ring-2 focus:ring-teal-500 focus:outline-none whitespace-nowrap focus-visible:opacity-100"
                      >
                        <FileText className="w-3.5 h-3.5" />
                        {p.viewRecord}
                      </Link>
                    </div>
                  </td>
                  <td className="px-4 py-4 text-slate-600 text-sm font-medium">{patient.age}</td>
                  <td className="px-4 py-4 text-slate-600 text-sm font-medium">{patient.sex}</td>
                  
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {patient.dipRisk.length > 0 ? (
                        patient.dipRisk.map((risk, i) => (
                          <Badge key={i} variant={risk.risk === "high" ? "red" : "yellow"}>
                            {risk.label}
                          </Badge>
                        ))
                      ) : (
                        <span className="text-slate-300 text-sm">—</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {patient.exposures.length > 0 ? (
                        patient.exposures.map((exp, i) => (
                          <Badge key={i} variant="purple">{exp}</Badge>
                        ))
                      ) : (
                        <span className="text-slate-300 text-sm">—</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {patient.fallsOrthostatic.length > 0 ? (
                        patient.fallsOrthostatic.map((item, i) => (
                          <Badge key={i} variant={item.toLowerCase().includes("early") ? "red" : "yellow"}>{item}</Badge>
                        ))
                      ) : (
                        <span className="text-slate-300 text-sm">—</span>
                      )}
                    </div>
                  </td>
                  
                  <td className="px-4 py-4">
                    <div className="flex flex-wrap gap-1.5">
                      {patient.autonomic.length > 0 ? (
                        patient.autonomic.map((item, i) => (
                          <Badge key={i} variant={item.toLowerCase().includes("severe") || item.toLowerCase().includes("retention") ? "red" : "yellow"}>{item}</Badge>
                        ))
                      ) : (
                        <span className="text-slate-300 text-sm">—</span>
                      )}
                    </div>
                  </td>

                  <td className="px-4 py-4">
                    <Badge variant={patient.symmetry.flag ? "red" : "slate"}>
                      {patient.symmetry.label}
                    </Badge>
                  </td>

                  <td className="px-4 py-4">
                    <Badge variant={patient.tremor.flag ? "yellow" : "slate"}>
                      {patient.tremor.label}
                    </Badge>
                  </td>
                  
                  <td className="px-4 py-4">
                    <span className={`px-2.5 py-1 text-xs font-medium rounded-full inline-flex items-center ${
                      patient.status.includes("Review") ? "bg-amber-100 text-amber-800" :
                      patient.status.includes("Stable") ? "bg-emerald-100 text-emerald-800" :
                      "bg-slate-100 text-slate-800"
                    }`}>
                      {p.statuses[patient.status as keyof typeof p.statuses] ?? patient.status}
                    </span>
                    <div className="text-[10px] text-slate-400 mt-1">{patient.lastVisit}</div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
