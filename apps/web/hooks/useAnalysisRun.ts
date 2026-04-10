"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { createAnalysisRunEventSource } from "@/lib/api/analysis-runs";
import type {
  AnalysisRunCompletedEventDto,
  AnalysisRunConnectedEventDto,
  AnalysisRunFailedEventDto,
  AnalysisRunProgressEventDto,
  AnalysisRunStartResponseDto,
} from "@/lib/api/types";

type AnalysisRunState = "idle" | "starting" | "running" | "completed" | "failed";

type UseAnalysisRunOptions = {
  onCompleted: (event: AnalysisRunCompletedEventDto) => void;
};

type StartRunFn = () => Promise<AnalysisRunStartResponseDto>;

function parseEventPayload<T>(event: MessageEvent<string>) {
  return JSON.parse(event.data) as T;
}

export function useAnalysisRun({ onCompleted }: UseAnalysisRunOptions) {
  const eventSourceRef = useRef<EventSource | null>(null);
  const isTerminalRef = useRef(false);
  const [state, setState] = useState<AnalysisRunState>("idle");
  const [runId, setRunId] = useState<string | null>(null);
  const [currentStage, setCurrentStage] = useState("");
  const [currentAiStep, setCurrentAiStep] = useState(0);
  const [totalAiSteps, setTotalAiSteps] = useState(0);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const close = useCallback(() => {
    eventSourceRef.current?.close();
    eventSourceRef.current = null;
  }, []);

  useEffect(() => close, [close]);

  const start = useCallback(
    async (startRun: StartRunFn) => {
      close();
      setState("starting");
      isTerminalRef.current = false;
      setErrorMessage(null);
      setCurrentAiStep(0);
      setCurrentStage("正在启动分析任务");

      const run = await startRun();
      setRunId(run.run_id);
      setTotalAiSteps(run.total_ai_steps);

      const eventSource = createAnalysisRunEventSource(run.run_id);
      eventSourceRef.current = eventSource;

      eventSource.addEventListener("connected", (event) => {
        const payload = parseEventPayload<AnalysisRunConnectedEventDto>(event as MessageEvent<string>);
        setState(payload.status === "completed" ? "completed" : payload.status === "failed" ? "failed" : "running");
        setCurrentStage(payload.current_stage);
        setCurrentAiStep(payload.current_ai_step);
        setTotalAiSteps(payload.total_ai_steps);
      });

      eventSource.addEventListener("progress", (event) => {
        const payload = parseEventPayload<AnalysisRunProgressEventDto>(event as MessageEvent<string>);
        setState("running");
        setCurrentStage(payload.message || payload.current_stage);
        setCurrentAiStep(payload.current_ai_step);
        setTotalAiSteps(payload.total_ai_steps);
      });

      eventSource.addEventListener("completed", (event) => {
        const payload = parseEventPayload<AnalysisRunCompletedEventDto>(event as MessageEvent<string>);
        isTerminalRef.current = true;
        setState("completed");
        setCurrentStage("分析完成");
        close();
        onCompleted(payload);
      });

      eventSource.addEventListener("failed", (event) => {
        const payload = parseEventPayload<AnalysisRunFailedEventDto>(event as MessageEvent<string>);
        isTerminalRef.current = true;
        setState("failed");
        setCurrentStage("分析失败");
        setErrorMessage(payload.message);
        close();
      });

      eventSource.onerror = () => {
        if (isTerminalRef.current) {
          return;
        }
        setState("failed");
        setCurrentStage("分析连接中断");
        setErrorMessage("分析连接中断，请稍后重试。");
        close();
      };
    },
    [close, onCompleted],
  );

  return {
    state,
    runId,
    currentStage,
    currentAiStep,
    totalAiSteps,
    errorMessage,
    isRunning: state === "starting" || state === "running",
    start,
    resetError: () => setErrorMessage(null),
    close,
  };
}
