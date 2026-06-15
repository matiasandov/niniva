import { useState, useEffect } from "react";
import { Mic, Square, AlertTriangle, Lightbulb, FileQuestion, ArrowRight, CheckCircle2, Brain } from "lucide-react";
import { clsx } from "clsx";
import { twMerge } from "tailwind-merge";
import { useLang } from "../context/LanguageContext";
import { useT } from "../i18n/translations";

function cn(...inputs: (string | undefined | null | false)[]) {
  return twMerge(clsx(inputs));
}

export function LiveSession() {
  const { lang } = useLang();
  const t = useT(lang);
  const ls = t.liveSession;

  const [isRecording, setIsRecording] = useState(false);
  const [sessionEnded, setSessionEnded] = useState(false);
  const [transcriptIndex, setTranscriptIndex] = useState(0);

  useEffect(() => {
    setIsRecording(false);
    setSessionEnded(false);
    setTranscriptIndex(0);
  }, [lang]);

  useEffect(() => {
    let interval: ReturnType<typeof setInterval>;
    if (isRecording && transcriptIndex < ls.transcriptLines.length) {
      interval = setInterval(() => {
        setTranscriptIndex(prev => prev + 1);
      }, 3000);
    } else if (transcriptIndex >= ls.transcriptLines.length && isRecording) {
      setIsRecording(false);
      setSessionEnded(true);
    }
    return () => clearInterval(interval);
  }, [isRecording, transcriptIndex, ls.transcriptLines.length]);

  const toggleRecording = () => {
    if (isRecording) {
      setIsRecording(false);
      setSessionEnded(true);
    } else {
      setIsRecording(true);
      setSessionEnded(false);
      setTranscriptIndex(0);
    }
  };

  return (
    <div className="flex flex-col h-[calc(100vh-2rem)] md:h-[calc(100vh-4rem)] max-w-5xl mx-auto">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">{ls.title}</h1>
          <p className="text-slate-500">{ls.subtitle}</p>
        </div>

        {!sessionEnded && (
          <button
            onClick={toggleRecording}
            className={cn(
              "flex items-center gap-2 px-6 py-3 rounded-full font-semibold text-white transition-all shadow-md",
              isRecording
                ? "bg-red-500 hover:bg-red-600 animate-pulse"
                : "bg-teal-600 hover:bg-teal-700"
            )}
          >
            {isRecording ? (
              <>
                <Square className="w-5 h-5 fill-current" />
                {ls.stopSession}
              </>
            ) : (
              <>
                <Mic className="w-5 h-5" />
                {ls.startRecording}
              </>
            )}
          </button>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 flex-1 min-h-0">
        {/* Transcript */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50 flex justify-between items-center">
            <h2 className="font-semibold text-slate-800 flex items-center gap-2">
              <Mic className={cn("w-4 h-4", isRecording ? "text-red-500 animate-pulse" : "text-slate-400")} />
              {ls.transcript}
            </h2>
            {isRecording && <span className="text-xs font-medium text-red-500 bg-red-50 px-2 py-1 rounded-full">{ls.recording}</span>}
          </div>
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {!isRecording && !sessionEnded && (
              <div className="h-full flex flex-col items-center justify-center text-slate-400 space-y-4">
                <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center">
                  <Mic className="w-8 h-8 text-slate-300" />
                </div>
                <p>{ls.clickToStart}</p>
              </div>
            )}

            {(isRecording || sessionEnded) && ls.transcriptLines.slice(0, transcriptIndex).map((line, idx) => {
              const isDoctor = idx % 2 === 0;
              return (
                <div key={idx} className={cn(
                  "flex flex-col max-w-[80%] rounded-2xl px-4 py-3",
                  isDoctor
                    ? "bg-teal-50 text-teal-900 self-end ml-auto rounded-br-sm"
                    : "bg-slate-100 text-slate-900 self-start mr-auto rounded-bl-sm"
                )}>
                  <span className="text-xs font-semibold mb-1 opacity-60">{line.speaker}</span>
                  <p className="text-sm leading-relaxed">{line.text}</p>
                </div>
              );
            })}
          </div>
        </div>

        {/* Domain Extraction */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm flex flex-col overflow-hidden">
          <div className="p-4 border-b border-slate-100 bg-slate-50">
            <h2 className="font-semibold text-slate-800">{ls.domainExtraction}</h2>
          </div>
          <div className="flex-1 overflow-y-auto p-4 space-y-2">
            {ls.domains.map((domain) => {
              let isActive = false;
              let isPopulated = false;
              if (domain.id === "motor" && transcriptIndex > 1) { isActive = true; isPopulated = true; }
              if (domain.id === "autonomic" && transcriptIndex > 3) { isActive = true; isPopulated = true; }
              if (domain.id === "cognitive" && transcriptIndex > 3) { isActive = true; isPopulated = true; }
              if (domain.id === "non-medical-drug" && transcriptIndex > 5) { isActive = true; isPopulated = true; }

              return (
                <div key={domain.id} className={cn(
                  "p-3 rounded-lg border text-sm transition-all duration-500",
                  isPopulated ? "border-teal-200 bg-teal-50/50" : "border-slate-100 bg-white",
                  isActive && isRecording ? "animate-pulse" : ""
                )}>
                  <div className="flex items-center justify-between">
                    <span className={cn("font-medium", isPopulated ? "text-teal-800" : "text-slate-500")}>
                      {domain.label}
                    </span>
                    {isPopulated && <CheckCircle2 className="w-4 h-4 text-teal-600" />}
                  </div>
                  {isPopulated && ls.domainDetails[domain.id] && (
                    <div className="mt-2 text-xs text-slate-600">
                      {ls.domainDetails[domain.id]}
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* Post-Session Insights */}
      {sessionEnded && (
        <div className="mt-6 bg-white rounded-xl border border-teal-200 shadow-sm overflow-hidden animate-in fade-in slide-in-from-bottom-4 duration-700">
          <div className="p-4 bg-teal-50 border-b border-teal-100 flex items-center gap-2">
            <Brain className="w-5 h-5 text-teal-600" />
            <h2 className="font-bold text-teal-900">{ls.aiAnalysis}</h2>
          </div>
          <div className="p-6 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-red-600 font-semibold border-b pb-2">
                <AlertTriangle className="w-4 h-4" />
                {ls.redFlags}
              </div>
              <ul className="text-sm text-slate-700 space-y-2 list-disc pl-4">
                {ls.redFlagItems.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-amber-600 font-semibold border-b pb-2">
                <Lightbulb className="w-4 h-4" />
                {ls.recommendations}
              </div>
              <ul className="text-sm text-slate-700 space-y-2 list-disc pl-4">
                {ls.recommendationItems.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-blue-600 font-semibold border-b pb-2">
                <FileQuestion className="w-4 h-4" />
                {ls.followUpQuestions}
              </div>
              <ul className="text-sm text-slate-700 space-y-2 list-disc pl-4">
                {ls.followUpItems.map((item, i) => <li key={i}>{item}</li>)}
              </ul>
            </div>
            <div className="space-y-3">
              <div className="flex items-center gap-2 text-teal-600 font-semibold border-b pb-2">
                <ArrowRight className="w-4 h-4" />
                {ls.nextSteps}
              </div>
              <div className="flex flex-col gap-2">
                <button className="w-full text-left text-sm px-3 py-2 bg-teal-50 hover:bg-teal-100 text-teal-800 rounded-lg transition-colors font-medium">
                  {ls.launchMotorTests}
                </button>
                <button className="w-full text-left text-sm px-3 py-2 bg-slate-50 hover:bg-slate-100 text-slate-700 rounded-lg transition-colors font-medium">
                  {ls.saveToRecord}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
