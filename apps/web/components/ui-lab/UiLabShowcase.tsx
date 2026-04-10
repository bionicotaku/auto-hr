"use client";

import { useState } from "react";

import { cn } from "@/lib/utils/cn";

type ThemeMode = "light" | "dark";

type Metric = {
  label: string;
  value: string;
  hint: string;
  tone: "mint" | "blue" | "amber";
};

type CandidateRow = {
  name: string;
  role: string;
  status: string;
  fit: string;
  signal: "strong" | "review" | "risk";
};

type CompareRow = {
  title: string;
  leftLabel: string;
  leftValue: number;
  rightLabel: string;
  rightValue: number;
};

type QueueItem = {
  title: string;
  note: string;
  status: "Ready" | "Review" | "Blocked";
};

const metricCards: Metric[] = [
  {
    label: "Qualified Profiles",
    value: "64",
    hint: "较上周 +9，当前适合优先推进",
    tone: "mint",
  },
  {
    label: "Manager Review Load",
    value: "18",
    hint: "5 条需要同日处理",
    tone: "blue",
  },
  {
    label: "Risk Flags",
    value: "06",
    hint: "2 条缺关键证据",
    tone: "amber",
  },
];

const candidateRows: CandidateRow[] = [
  {
    name: "Lina Chen",
    role: "Senior Product Recruiter",
    status: "面试推进",
    fit: "技能匹配度高，流程设计与沟通信号稳定",
    signal: "strong",
  },
  {
    name: "Marcus Hall",
    role: "Talent Operations Lead",
    status: "待复核",
    fit: "履历完整，但跨区域协作证据还不够扎实",
    signal: "review",
  },
  {
    name: "Anika Patel",
    role: "People Analytics Manager",
    status: "风险提示",
    fit: "分析能力突出，但岗位相关性与材料完整度偏弱",
    signal: "risk",
  },
];

const compareRows: CompareRow[] = [
  {
    title: "Evidence depth",
    leftLabel: "Profile A",
    leftValue: 84,
    rightLabel: "Profile B",
    rightValue: 61,
  },
  {
    title: "Role relevance",
    leftLabel: "Profile A",
    leftValue: 72,
    rightLabel: "Profile B",
    rightValue: 79,
  },
  {
    title: "Communication readiness",
    leftLabel: "Profile A",
    leftValue: 88,
    rightLabel: "Profile B",
    rightValue: 68,
  },
];

const actionQueue: QueueItem[] = [
  {
    title: "Send shortlist note",
    note: "当前候选人证据更完整，适合优先进入经理确认。",
    status: "Ready",
  },
  {
    title: "Verify domain transfer",
    note: "经验迁移可能成立，但仍需人工补读项目上下文。",
    status: "Review",
  },
  {
    title: "Request revised packet",
    note: "现有材料不足以支撑推荐结论，需要补更多证明。",
    status: "Blocked",
  },
];

const heatMatrix = [
  [0.82, 0.67, 0.35, 0.51],
  [0.73, 0.8, 0.46, 0.64],
  [0.58, 0.75, 0.72, 0.39],
];

const heatColumns = ["Evidence", "Fit", "Responsiveness", "Clarity"];
const heatRows = ["Initial read", "Manager pass", "Draft quality"];
const tabs = ["Overview", "Compare", "Signals", "Queue"];

export function UiLabShowcase() {
  const [theme, setTheme] = useState<ThemeMode>("light");

  const isDark = theme === "dark";

  return (
    <main
      className={cn(
        "relative min-h-screen overflow-hidden px-4 py-5 sm:px-6 lg:px-8",
        isDark
          ? "bg-[radial-gradient(circle_at_top_left,#15314b_0%,#091522_42%,#020617_100%)] text-slate-100"
          : "bg-[radial-gradient(circle_at_top_left,#f5fbff_0%,#f7fcf9_38%,#fffdf6_100%)] text-slate-900",
      )}
    >
      <BackgroundOrbs isDark={isDark} />

      <div className="relative mx-auto flex w-full max-w-7xl flex-col gap-6 pb-14">
        <header
          className={glassPanelClass(
            isDark,
            "sticky top-4 z-20 grid gap-4 px-5 py-4 sm:px-6 lg:grid-cols-[1fr_auto_auto] lg:items-center",
          )}
        >
          <div className="flex items-center gap-3">
            <div
              className={cn(
                "flex h-11 w-11 items-center justify-center rounded-2xl border",
                isDark
                  ? "border-cyan-300/20 bg-cyan-300/10 text-cyan-200"
                  : "border-white/80 bg-white/88 text-slate-900",
              )}
            >
              <SparkIcon className="h-5 w-5" />
            </div>
            <div>
              <p className={eyebrowClass(isDark)}>UI Laboratory</p>
              <h1 className="text-lg font-semibold">Decision Support Glass Preview</h1>
            </div>
          </div>

          <nav className="flex flex-wrap gap-2">
            {tabs.map((tab, index) => (
              <button
                key={tab}
                className={cn(
                  "cursor-pointer rounded-full px-3 py-2 text-sm font-medium transition-colors duration-200 ease-out motion-reduce:transition-none",
                  index === 0
                    ? isDark
                      ? "bg-cyan-200 text-slate-950"
                      : "bg-slate-950 text-white shadow-[0_8px_24px_rgba(15,23,42,0.12)]"
                    : isDark
                      ? "text-slate-300 hover:bg-white/8"
                      : "text-slate-600 hover:bg-white",
                )}
                type="button"
              >
                {tab}
              </button>
            ))}
          </nav>

          <div className="flex items-center gap-2">
            <span className={cn("text-sm", isDark ? "text-slate-400" : "text-slate-500")}>
              Theme
            </span>
            <div
              className={cn(
                "inline-flex rounded-full border p-1",
                isDark ? "border-white/10 bg-white/5" : "border-slate-200 bg-white/85",
              )}
            >
              {(["light", "dark"] as ThemeMode[]).map((mode) => {
                const active = theme === mode;

                return (
                  <button
                    key={mode}
                    className={cn(
                      "cursor-pointer rounded-full px-3 py-1.5 text-sm font-medium capitalize transition-colors duration-200 ease-out motion-reduce:transition-none",
                      active
                        ? isDark
                          ? "bg-cyan-200 text-slate-950"
                          : "bg-slate-950 text-white"
                        : isDark
                          ? "text-slate-300 hover:bg-white/8"
                          : "text-slate-600 hover:bg-slate-100",
                    )}
                    onClick={() => setTheme(mode)}
                    type="button"
                  >
                    {mode}
                  </button>
                );
              })}
            </div>
          </div>
        </header>

        <section className="grid gap-6 xl:grid-cols-[1.06fr_0.94fr]">
          <section className={glassPanelClass(isDark, "overflow-hidden px-6 py-6 sm:px-8 sm:py-8")}>
            <div className="grid gap-8 xl:grid-cols-[1.02fr_0.98fr]">
              <div className="flex flex-col gap-6">
                <BadgeLabel isDark={isDark}>Light-first / modern / comparison-first</BadgeLabel>

                <div className="space-y-4">
                  <h2 className="max-w-2xl text-4xl font-semibold leading-tight sm:text-5xl">
                    为招聘后处理设计的一套更清晰的判断界面。
                  </h2>
                  <p className={cn("max-w-2xl text-base leading-7 sm:text-lg", subtleTextClass(isDark))}>
                    合并后的方案不再做沉浸式 workspace，也不走杂志式长叙事，而是聚焦三个问题：
                    谁值得推进、哪里需要补证据、下一步动作是什么。视觉保持明亮的玻璃层次，
                    但结构更贴近当前系统真实的信息组织方式。
                  </p>
                </div>

                <div className="grid gap-3 sm:grid-cols-3">
                  {metricCards.map((metric) => (
                    <MetricCard isDark={isDark} key={metric.label} metric={metric} />
                  ))}
                </div>

                <div className="flex flex-wrap gap-3">
                  <button
                    className={cn(
                      "cursor-pointer rounded-full px-5 py-3 text-sm font-semibold transition-colors duration-200 ease-out motion-reduce:transition-none",
                      isDark
                        ? "bg-cyan-200 text-slate-950 hover:bg-cyan-100"
                        : "bg-slate-950 text-white hover:bg-slate-800",
                    )}
                    type="button"
                  >
                    Open Decision Flow
                  </button>
                  <button
                    className={cn(
                      "cursor-pointer rounded-full border px-5 py-3 text-sm font-medium transition-colors duration-200 ease-out motion-reduce:transition-none",
                      isDark
                        ? "border-white/12 bg-white/6 text-slate-100 hover:bg-white/10"
                        : "border-white/80 bg-white/80 text-slate-900 hover:bg-white",
                    )}
                    type="button"
                  >
                    Review Compare Blocks
                  </button>
                </div>
              </div>

              <div className="grid gap-4">
                <div className={surfaceCardClass(isDark, "relative overflow-hidden p-5")}>
                  <div
                    className={cn(
                      "absolute inset-x-8 top-0 h-24 rounded-full blur-3xl",
                      isDark ? "bg-cyan-300/18" : "bg-cyan-200/55",
                    )}
                  />
                  <div className="relative space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <p className={eyebrowClass(isDark)}>Decision Map</p>
                        <h3 className="text-xl font-semibold">Three-layer reading order</h3>
                      </div>
                      <DecisionIcon className={iconClass(isDark)} />
                    </div>

                    {[
                      ["1. Compare signal strength", "先并排读差异，再决定是否继续深挖。"],
                      ["2. Inspect evidence gaps", "把不确定性单独抬出来，不埋在摘要里。"],
                      ["3. Commit next action", "每一块都收束成可执行动作。"],
                    ].map(([title, detail]) => (
                      <div
                        className={cn(
                          "rounded-[24px] border px-4 py-4",
                          isDark
                            ? "border-white/10 bg-slate-950/42"
                            : "border-white/85 bg-white/84",
                        )}
                        key={title}
                      >
                        <p className="text-sm font-medium">{title}</p>
                        <p className={cn("mt-1 text-sm leading-6", subtleTextClass(isDark))}>{detail}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="grid gap-4 sm:grid-cols-2">
                  <MiniInsightCard
                    isDark={isDark}
                    title="Candidate review"
                    detail="列表模块保留高可读的 glass rows，适合未来映射回岗位详情 Candidate 列表。"
                    tone="blue"
                  />
                  <MiniInsightCard
                    isDark={isDark}
                    title="Action queue"
                    detail="把推荐结论、复核需求和动作状态拆开，而不是只给一个标签。"
                    tone="mint"
                  />
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-6">
            <div className={glassPanelClass(isDark, "px-5 py-5")}>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className={eyebrowClass(isDark)}>Direct comparison</p>
                  <h3 className="text-2xl font-semibold">Side-by-side decision bars</h3>
                </div>
                <CompareIcon className={iconClass(isDark)} />
              </div>

              <div className="space-y-4">
                {compareRows.map((row) => (
                  <div className={surfaceCardClass(isDark, "p-4")} key={row.title}>
                    <div className="mb-3 flex items-center justify-between">
                      <p className="text-sm font-medium">{row.title}</p>
                      <span className={cn("text-xs font-semibold", subtleTextClass(isDark))}>
                        Comparison
                      </span>
                    </div>
                    <div className="grid gap-3">
                      <BarRow
                        isDark={isDark}
                        label={row.leftLabel}
                        tone="mint"
                        value={row.leftValue}
                      />
                      <BarRow
                        isDark={isDark}
                        label={row.rightLabel}
                        tone="blue"
                        value={row.rightValue}
                      />
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className={glassPanelClass(isDark, "px-5 py-5")}>
              <div className="mb-4 flex items-center justify-between">
                <div>
                  <p className={eyebrowClass(isDark)}>Evidence density</p>
                  <h3 className="text-2xl font-semibold">Matrix snapshot</h3>
                </div>
                <MatrixIcon className={iconClass(isDark)} />
              </div>

              <div className="overflow-hidden rounded-[28px] border border-white/55">
                <div
                  className={cn(
                    "grid grid-cols-[120px_repeat(4,minmax(0,1fr))] gap-px",
                    isDark ? "bg-white/10" : "bg-slate-200/90",
                  )}
                >
                  <div className={cn("px-3 py-3 text-xs font-semibold", headerCellClass(isDark))} />
                  {heatColumns.map((column) => (
                    <div
                      className={cn("px-3 py-3 text-center text-xs font-semibold", headerCellClass(isDark))}
                      key={column}
                    >
                      {column}
                    </div>
                  ))}
                  {heatMatrix.map((row, rowIndex) => (
                    <HeatRow
                      isDark={isDark}
                      key={heatRows[rowIndex]}
                      label={heatRows[rowIndex]}
                      values={row}
                    />
                  ))}
                </div>
              </div>
            </div>
          </section>
        </section>

        <section className={glassPanelClass(isDark, "px-6 py-6")}>
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className={eyebrowClass(isDark)}>Candidate list</p>
              <h3 className="text-2xl font-semibold">Candidate signal table</h3>
            </div>
            <div className="flex flex-wrap gap-2">
              <BadgeTone isDark={isDark} tone="mint">
                Preserved module
              </BadgeTone>
              <BadgeTone isDark={isDark} tone="blue">
                Primary review surface
              </BadgeTone>
            </div>
          </div>

          <div className="overflow-hidden rounded-[28px] border border-white/50">
            <div
              className={cn(
                "grid grid-cols-[1.1fr_1fr_0.8fr_1.4fr] gap-4 px-5 py-4 text-xs font-semibold uppercase tracking-[0.24em]",
                isDark ? "bg-white/6 text-slate-400" : "bg-white/70 text-slate-500",
              )}
            >
              <span>Candidate</span>
              <span>Role</span>
              <span>Status</span>
              <span>Signal</span>
            </div>

            {candidateRows.map((row) => (
              <div
                className={cn(
                  "grid grid-cols-1 gap-4 border-t px-5 py-4 transition-colors duration-200 ease-out md:grid-cols-[1.1fr_1fr_0.8fr_1.4fr] motion-reduce:transition-none",
                  isDark
                    ? "border-white/8 bg-white/4 hover:bg-white/7"
                    : "border-white/65 bg-white/65 hover:bg-white/82",
                )}
                key={row.name}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={cn(
                      "flex h-11 w-11 items-center justify-center rounded-2xl text-sm font-semibold",
                      row.signal === "strong"
                        ? isDark
                          ? "bg-emerald-300/14 text-emerald-200"
                          : "bg-emerald-100 text-emerald-700"
                        : row.signal === "review"
                          ? isDark
                            ? "bg-sky-300/14 text-sky-200"
                            : "bg-sky-100 text-sky-700"
                          : isDark
                            ? "bg-amber-300/14 text-amber-200"
                            : "bg-amber-100 text-amber-700",
                    )}
                  >
                    {row.name.slice(0, 2).toUpperCase()}
                  </div>
                  <div>
                    <p className="font-medium">{row.name}</p>
                    <p className={subtleTextClass(isDark)}>Portfolio / resume packet</p>
                  </div>
                </div>
                <div className="flex items-center text-sm">{row.role}</div>
                <div className="flex items-center">
                  <BadgeTone
                    isDark={isDark}
                    tone={
                      row.signal === "strong"
                        ? "mint"
                        : row.signal === "review"
                          ? "blue"
                          : "amber"
                    }
                  >
                    {row.status}
                  </BadgeTone>
                </div>
                <div className={cn("text-sm leading-6", subtleTextClass(isDark))}>{row.fit}</div>
              </div>
            ))}
          </div>
        </section>

        <section className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
          <section className={glassPanelClass(isDark, "px-5 py-5")}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className={eyebrowClass(isDark)}>Recommended next actions</p>
                <h3 className="text-2xl font-semibold">Operational queue</h3>
              </div>
              <QueueIcon className={iconClass(isDark)} />
            </div>

            <div className="space-y-3">
              {actionQueue.map((item) => (
                <div
                  className={cn(
                    "rounded-[26px] border p-4 transition-colors duration-200 ease-out motion-reduce:transition-none",
                    surfaceShellClass(isDark),
                    isDark ? "hover:bg-white/8" : "hover:bg-white",
                  )}
                  key={item.title}
                >
                  <div className="mb-3 flex items-center justify-between gap-3">
                    <p className="text-sm font-medium">{item.title}</p>
                    <BadgeTone
                      isDark={isDark}
                      tone={
                        item.status === "Ready"
                          ? "mint"
                          : item.status === "Review"
                            ? "blue"
                            : "amber"
                      }
                    >
                      {item.status}
                    </BadgeTone>
                  </div>
                  <p className={cn("text-sm leading-6", subtleTextClass(isDark))}>{item.note}</p>
                </div>
              ))}
            </div>
          </section>

          <section className={glassPanelClass(isDark, "px-5 py-5")}>
            <div className="mb-4 flex items-center justify-between">
              <div>
                <p className={eyebrowClass(isDark)}>Component strip</p>
                <h3 className="text-2xl font-semibold">Decision-oriented widgets</h3>
              </div>
            </div>

            <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
              <div className="grid gap-4">
                <div className={surfaceCardClass(isDark, "p-4")}>
                  <div className="mb-3 flex items-center justify-between">
                    <p className={eyebrowClass(isDark)}>Priority chips</p>
                    <ChipIcon className={iconClass(isDark)} />
                  </div>
                  <div className="flex flex-wrap gap-2">
                    {["High signal", "Needs context", "Reply soon", "Missing proof"].map(
                      (chip, index) => (
                        <button
                          className={cn(
                            "cursor-pointer rounded-full px-3 py-2 text-sm font-medium transition-colors duration-200 ease-out motion-reduce:transition-none",
                            index === 0
                              ? isDark
                                ? "bg-cyan-200 text-slate-950"
                                : "bg-slate-950 text-white"
                              : isDark
                                ? "bg-white/8 text-slate-300 hover:bg-white/10"
                                : "bg-white/86 text-slate-600 hover:bg-white",
                          )}
                          key={chip}
                          type="button"
                        >
                          {chip}
                        </button>
                      ),
                    )}
                  </div>
                </div>

                <div className={surfaceCardClass(isDark, "p-4")}>
                  <div className="mb-3 flex items-center justify-between">
                    <p className={eyebrowClass(isDark)}>Decision note</p>
                    <NoteIcon className={iconClass(isDark)} />
                  </div>
                  <div
                    className={cn(
                      "rounded-[22px] border px-4 py-4 text-sm leading-7",
                      isDark
                        ? "border-white/10 bg-slate-950/44 text-slate-300"
                        : "border-white/90 bg-white/86 text-slate-600",
                    )}
                  >
                    Candidate A should move forward first. The evidence is broader, the response
                    quality is stronger, and the remaining uncertainty is smaller than the current
                    review burden.
                  </div>
                </div>
              </div>

              <div className={surfaceCardClass(isDark, "p-4")}>
                <div className="mb-4 flex items-center justify-between">
                  <div>
                    <p className={eyebrowClass(isDark)}>Relative spread</p>
                    <h4 className="text-lg font-semibold">Ranked horizontal bars</h4>
                  </div>
                  <RankIcon className={iconClass(isDark)} />
                </div>

                <div className="space-y-4">
                  {[
                    { label: "Communication quality", value: 88, tone: "mint" as const },
                    { label: "Role fit confidence", value: 76, tone: "blue" as const },
                    { label: "Evidence completeness", value: 69, tone: "blue" as const },
                    { label: "Follow-up urgency", value: 41, tone: "amber" as const },
                  ].map(({ label, value, tone }) => (
                    <BarRow isDark={isDark} key={label} label={label} tone={tone} value={value} />
                  ))}
                </div>
              </div>
            </div>
          </section>
        </section>
      </div>
    </main>
  );
}

function BackgroundOrbs({ isDark }: { isDark: boolean }) {
  return (
    <div aria-hidden="true" className="pointer-events-none absolute inset-0 overflow-hidden">
      <div
        className={cn(
          "absolute -left-24 top-0 h-72 w-72 rounded-full blur-3xl",
          isDark ? "bg-cyan-400/14" : "bg-sky-200/45",
        )}
      />
      <div
        className={cn(
          "absolute right-[-2.5rem] top-24 h-80 w-80 rounded-full blur-3xl",
          isDark ? "bg-emerald-400/14" : "bg-emerald-200/45",
        )}
      />
      <div
        className={cn(
          "absolute bottom-[-6rem] left-1/3 h-96 w-96 rounded-full blur-3xl",
          isDark ? "bg-indigo-400/10" : "bg-amber-200/35",
        )}
      />
    </div>
  );
}

function BadgeLabel({
  children,
  isDark,
}: {
  children: string;
  isDark: boolean;
}) {
  return (
    <span
      className={cn(
        "inline-flex w-fit items-center rounded-full border px-3 py-1.5 text-xs font-semibold uppercase tracking-[0.24em]",
        isDark
          ? "border-white/10 bg-white/6 text-slate-300"
          : "border-white/85 bg-white/88 text-slate-500",
      )}
    >
      {children}
    </span>
  );
}

function MetricCard({ isDark, metric }: { isDark: boolean; metric: Metric }) {
  return (
    <div className={surfaceCardClass(isDark, "p-4")}>
      <div className="mb-4 flex items-center justify-between">
        <p className={eyebrowClass(isDark)}>{metric.label}</p>
        <BadgeTone isDark={isDark} tone={metric.tone}>
          Live
        </BadgeTone>
      </div>
      <div className="space-y-1">
        <p className="text-3xl font-semibold">{metric.value}</p>
        <p className={cn("text-sm", subtleTextClass(isDark))}>{metric.hint}</p>
      </div>
    </div>
  );
}

function MiniInsightCard({
  detail,
  isDark,
  title,
  tone,
}: {
  detail: string;
  isDark: boolean;
  title: string;
  tone: "mint" | "blue";
}) {
  return (
    <div className={surfaceCardClass(isDark, "p-4")}>
      <div className="mb-3 flex items-center justify-between">
        <span className={eyebrowClass(isDark)}>{title}</span>
        <BadgeTone isDark={isDark} tone={tone}>
          Preview
        </BadgeTone>
      </div>
      <p className={cn("text-sm leading-6", subtleTextClass(isDark))}>{detail}</p>
    </div>
  );
}

function BadgeTone({
  children,
  isDark,
  tone,
}: {
  children: string;
  isDark: boolean;
  tone: "mint" | "blue" | "amber";
}) {
  const toneClass =
    tone === "mint"
      ? isDark
        ? "bg-emerald-300/12 text-emerald-200"
        : "bg-emerald-100 text-emerald-700"
      : tone === "blue"
        ? isDark
          ? "bg-sky-300/12 text-sky-200"
          : "bg-sky-100 text-sky-700"
        : isDark
          ? "bg-amber-300/14 text-amber-200"
          : "bg-amber-100 text-amber-700";

  return (
    <span className={cn("rounded-full px-3 py-1 text-xs font-semibold", toneClass)}>{children}</span>
  );
}

function BarRow({
  isDark,
  label,
  tone,
  value,
}: {
  isDark: boolean;
  label: string;
  tone: "mint" | "blue" | "amber";
  value: number;
}) {
  const barColor =
    tone === "mint"
      ? isDark
        ? "from-emerald-400 to-cyan-300"
        : "from-emerald-400 to-teal-300"
      : tone === "blue"
        ? isDark
          ? "from-sky-400 to-cyan-300"
          : "from-sky-400 to-indigo-300"
        : isDark
          ? "from-amber-300 to-orange-300"
          : "from-amber-300 to-rose-300";

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{label}</span>
        <span className={cn("text-xs font-semibold", subtleTextClass(isDark))}>{value}%</span>
      </div>
      <div className={cn("h-2 overflow-hidden rounded-full", isDark ? "bg-white/8" : "bg-slate-200/80")}>
        <div className={cn("h-full rounded-full bg-linear-to-r", barColor)} style={{ width: `${value}%` }} />
      </div>
    </div>
  );
}

function HeatRow({
  isDark,
  label,
  values,
}: {
  isDark: boolean;
  label: string;
  values: number[];
}) {
  return (
    <>
      <div className={cn("px-3 py-4 text-xs font-semibold", headerCellClass(isDark))}>{label}</div>
      {values.map((value, index) => (
        <div
          className={cn(
            "flex items-center justify-center px-3 py-4 text-sm font-medium",
            isDark ? "bg-slate-950/46 text-slate-100" : "bg-white/84 text-slate-700",
          )}
          key={`${label}-${index}`}
          style={{
            boxShadow: `inset 0 0 0 999px rgba(${isDark ? "34,211,238" : "14,165,233"}, ${value * (isDark ? 0.22 : 0.14)})`,
          }}
        >
          {Math.round(value * 100)}
        </div>
      ))}
    </>
  );
}

function glassPanelClass(isDark: boolean, className?: string) {
  return cn(
    "rounded-[32px] border backdrop-blur-2xl",
    isDark
      ? "border-white/10 bg-white/6 shadow-[0_24px_80px_rgba(2,6,23,0.42)]"
      : "border-white/80 bg-white/62 shadow-[0_24px_80px_rgba(15,23,42,0.10)]",
    className,
  );
}

function surfaceCardClass(isDark: boolean, className?: string) {
  return cn(
    "rounded-[28px] border backdrop-blur-xl transition-transform duration-300 ease-out hover:-translate-y-1 motion-reduce:transform-none motion-reduce:transition-none motion-reduce:hover:translate-y-0",
    surfaceShellClass(isDark),
    className,
  );
}

function surfaceShellClass(isDark: boolean) {
  return isDark
    ? "border-white/10 bg-slate-950/34 shadow-[0_18px_48px_rgba(2,6,23,0.36)]"
    : "border-white/88 bg-white/78 shadow-[0_18px_48px_rgba(15,23,42,0.08)]";
}

function eyebrowClass(isDark: boolean) {
  return cn(
    "text-xs font-semibold uppercase tracking-[0.24em]",
    isDark ? "text-slate-400" : "text-slate-500",
  );
}

function subtleTextClass(isDark: boolean) {
  return isDark ? "text-slate-300" : "text-slate-600";
}

function iconClass(isDark: boolean) {
  return cn("h-4 w-4", isDark ? "text-slate-400" : "text-slate-500");
}

function headerCellClass(isDark: boolean) {
  return isDark ? "bg-slate-950/60 text-slate-300" : "bg-white/88 text-slate-500";
}

function SparkIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path
        d="M12 3l1.9 4.6L18.5 9l-4.6 1.4L12 15l-1.9-4.6L5.5 9l4.6-1.4L12 3zm6 11l.9 2.1L21 17l-2.1.9L18 20l-.9-2.1L15 17l2.1-.9L18 14zM6 14l1.2 2.8L10 18l-2.8 1.2L6 22l-1.2-2.8L2 18l2.8-1.2L6 14z"
        fill="currentColor"
      />
    </svg>
  );
}

function DecisionIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M5 5h14v4H5V5zm0 6h8v4H5v-4zm10 0h4v8h-4v-8zm-10 6h8v2H5v-2z" fill="currentColor" />
    </svg>
  );
}

function CompareIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M4 6h7v12H4V6zm9 4h7v8h-7v-8z" fill="currentColor" />
    </svg>
  );
}

function MatrixIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path
        d="M4 4h5v5H4V4zm0 7h5v5H4v-5zm7-7h5v5h-5V4zm0 7h5v5h-5v-5zm7-7h2v12h-2V4z"
        fill="currentColor"
      />
    </svg>
  );
}

function QueueIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M5 6h14v2H5V6zm0 5h14v2H5v-2zm0 5h10v2H5v-2z" fill="currentColor" />
    </svg>
  );
}

function ChipIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M7 7h10v4H7V7zm-2 6h14v4H5v-4z" fill="currentColor" />
    </svg>
  );
}

function NoteIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M6 4h12v16H6V4zm3 4v2h6V8H9zm0 4v2h6v-2H9z" fill="currentColor" />
    </svg>
  );
}

function RankIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24">
      <path d="M5 17h14v2H5v-2zm0-4h10v2H5v-2zm0-4h7v2H5V9z" fill="currentColor" />
    </svg>
  );
}
