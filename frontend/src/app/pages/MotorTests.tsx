import { useState } from "react";
import { Camera, Mic, Activity, Play, ChevronRight } from "lucide-react";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

const TEST_ICONS: Record<string, React.ElementType> = {
  "finger-tapping": Camera,
  "voice-pause": Mic,
  "resting-tremors": Activity,
};

export function MotorTests() {
  const { lang } = useLang();
  const t = useT(lang);
  const mt = t.motorTests;

  const [activeTestId, setActiveTestId] = useState<string | null>(null);
  const [testState, setTestState] = useState<"idle" | "running" | "completed">("idle");
  const [progress, setProgress] = useState(0);

  const DURATIONS: Record<string, number> = {
    "finger-tapping": 10,
    "voice-pause": 15,
    "resting-tremors": 20,
  };

  const startTest = (testId: string) => {
    setTestState("running");
    setProgress(0);

    const durationMs = (DURATIONS[testId] ?? 10) * 1000;
    const intervalMs = 100;
    const step = 100 / (durationMs / intervalMs);

    const interval = setInterval(() => {
      setProgress(p => {
        if (p >= 100) {
          clearInterval(interval);
          setTestState("completed");
          return 100;
        }
        return p + step;
      });
    }, intervalMs);
  };

  const activeTest = mt.tests.find(t => t.id === activeTestId);
  const ActiveIcon = activeTestId ? TEST_ICONS[activeTestId] : null;

  return (
    <div className="flex flex-col h-full max-w-5xl mx-auto items-center justify-center py-8">
      <div className="text-center mb-8">
        <h1 className="text-2xl font-bold text-slate-900 mb-2">{mt.title}</h1>
        <p className="text-slate-500 max-w-md">{mt.subtitle}</p>
      </div>

      {/* Mock Smartphone */}
      <div className="relative w-full max-w-[375px] h-[750px] bg-slate-900 rounded-[3rem] p-4 shadow-2xl border-[8px] border-slate-800 flex flex-col">
        <div className="absolute top-0 inset-x-0 h-6 flex justify-center">
          <div className="w-32 h-6 bg-slate-800 rounded-b-3xl"></div>
        </div>

        <div className="flex-1 bg-white rounded-[2rem] overflow-hidden flex flex-col relative">
          <div className="pt-10 pb-4 px-6 bg-teal-600 text-white shadow-sm z-10">
            <h2 className="text-lg font-semibold">{mt.mobileHeader}</h2>
            <p className="text-teal-100 text-xs">{mt.patient}: Arthur Pendelton</p>
          </div>

          <div className="flex-1 overflow-y-auto bg-slate-50 relative">
            {!activeTestId ? (
              <div className="p-4 space-y-4">
                <div className="mb-6">
                  <h3 className="text-sm font-semibold text-slate-500 uppercase tracking-wider mb-2">
                    {mt.availableTests}
                  </h3>
                  <div className="space-y-3">
                    {mt.tests.map(test => {
                      const Icon = TEST_ICONS[test.id];
                      return (
                        <button
                          key={test.id}
                          onClick={() => { setActiveTestId(test.id); setTestState("idle"); }}
                          className="w-full text-left bg-white p-4 rounded-xl border border-slate-200 shadow-sm hover:border-teal-500 hover:shadow-md transition-all group flex items-center justify-between"
                        >
                          <div className="flex items-center gap-4">
                            <div className="w-10 h-10 rounded-full bg-teal-50 flex items-center justify-center text-teal-600 group-hover:bg-teal-600 group-hover:text-white transition-colors">
                              <Icon className="w-5 h-5" />
                            </div>
                            <div>
                              <div className="font-semibold text-slate-900 text-sm">{test.title}</div>
                              <div className="text-xs text-slate-500 mt-0.5 max-w-[200px] truncate">{test.description}</div>
                            </div>
                          </div>
                          <ChevronRight className="w-5 h-5 text-slate-400 group-hover:text-teal-600" />
                        </button>
                      );
                    })}
                  </div>
                </div>
              </div>
            ) : (
              <div className="absolute inset-0 flex flex-col bg-slate-900 text-white">
                <div className="p-4 flex items-center gap-3 bg-black/40">
                  <button
                    onClick={() => { setActiveTestId(null); setTestState("idle"); }}
                    className="text-white/70 hover:text-white"
                  >
                    {mt.back}
                  </button>
                  <h3 className="font-medium text-sm flex-1 truncate">{activeTest?.title}</h3>
                </div>

                <div className="flex-1 flex flex-col items-center justify-center p-6 text-center">
                  {testState === "idle" && (
                    <>
                      <div className="w-24 h-24 rounded-full bg-white/10 flex items-center justify-center mb-6">
                        {ActiveIcon && <ActiveIcon className="w-12 h-12 text-teal-400" />}
                      </div>
                      <p className="text-sm text-white/80 mb-8">{activeTest?.description}</p>
                      <button
                        onClick={() => startTest(activeTestId)}
                        className="w-full py-4 bg-teal-500 hover:bg-teal-400 rounded-full font-bold text-lg shadow-lg shadow-teal-500/30 flex items-center justify-center gap-2 transition-colors"
                      >
                        <Play className="w-6 h-6 fill-current" />
                        {mt.startTest}
                      </button>
                    </>
                  )}

                  {testState === "running" && (
                    <>
                      <div className="relative w-48 h-48 mb-8">
                        <div className="absolute inset-0 border-4 border-white/20 rounded-full"></div>
                        <svg className="absolute inset-0 transform -rotate-90 w-full h-full" viewBox="0 0 100 100">
                          <circle
                            cx="50" cy="50" r="48"
                            fill="none"
                            stroke="currentColor"
                            strokeWidth="4"
                            className="text-teal-400"
                            strokeDasharray={`${progress * 3.01} 301`}
                          />
                        </svg>
                        <div className="absolute inset-0 flex flex-col items-center justify-center">
                          {ActiveIcon && <ActiveIcon className="w-12 h-12 text-teal-400 animate-pulse mb-2" />}
                          <span className="text-xl font-bold">{Math.round(progress)}%</span>
                        </div>
                      </div>
                      <p className="text-sm text-white/80 animate-pulse">{mt.capturing}</p>
                    </>
                  )}

                  {testState === "completed" && (
                    <div className="animate-in zoom-in duration-500">
                      <div className="w-24 h-24 rounded-full bg-teal-500 flex items-center justify-center mb-6 mx-auto">
                        <svg className="w-12 h-12 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M5 13l4 4L19 7" />
                        </svg>
                      </div>
                      <h4 className="text-xl font-bold mb-2">{mt.testComplete}</h4>
                      <p className="text-sm text-white/70 mb-8">{mt.testCompleteSubtitle}</p>
                      <div className="bg-white/10 rounded-xl p-4 mb-8 w-full text-left">
                        <div className="text-xs text-white/50 uppercase mb-2">{mt.preliminaryResults}</div>
                        {activeTestId && mt.results[activeTestId] && (
                          <div className="space-y-2">
                            {mt.results[activeTestId].map((row, i) => (
                              <div key={i} className="flex justify-between">
                                <span className="text-white/80">{row.label}</span>
                                <span className={`font-bold ${row.highlight ? "text-amber-400" : ""}`}>{row.value}</span>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                      <button
                        onClick={() => { setActiveTestId(null); setTestState("idle"); }}
                        className="w-full py-3 bg-white text-slate-900 rounded-full font-bold shadow-lg"
                      >
                        {mt.done}
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>

          <div className="h-6 bg-white flex justify-center items-center pb-2">
            <div className="w-32 h-1 bg-slate-300 rounded-full"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
