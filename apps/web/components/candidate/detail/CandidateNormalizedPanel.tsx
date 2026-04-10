import type { CandidateDetailNormalizedProfileDto } from "@/lib/api/types";
import { Card } from "@/components/ui/Card";

type CandidateNormalizedPanelProps = {
  normalizedProfile: CandidateDetailNormalizedProfileDto;
};

function formatList(value: unknown) {
  if (!Array.isArray(value)) {
    return "";
  }
  return value
    .map((item) => (typeof item === "string" ? item.trim() : ""))
    .filter(Boolean)
    .join("、");
}

function DetailRow({ label, value }: { label: string; value: string | null | undefined }) {
  if (!value) {
    return null;
  }

  return (
    <div className="grid gap-1 sm:grid-cols-[120px_minmax(0,1fr)] sm:items-start">
      <p className="text-sm text-slate-500">{label}</p>
      <p className="text-sm leading-6 text-slate-700">{value}</p>
    </div>
  );
}

export function CandidateNormalizedPanel({ normalizedProfile }: CandidateNormalizedPanelProps) {
  const identity = normalizedProfile.identity;
  const profileSummary = normalizedProfile.profile_summary;
  const skillsRaw = formatList(normalizedProfile.skills.skills_raw);
  const skillsNormalized = formatList(normalizedProfile.skills.skills_normalized);
  const preferredLocations = formatList(normalizedProfile.employment_preferences.preferred_locations);
  const preferredWorkModes = formatList(normalizedProfile.employment_preferences.preferred_work_modes);
  const highlights = formatList(normalizedProfile.additional_information.uncategorized_highlights);
  const parserNotes = formatList(normalizedProfile.additional_information.parser_notes);

  return (
    <Card className="space-y-5">
      <div className="space-y-1">
        <h2 className="text-lg font-semibold tracking-tight text-slate-950">标准化信息</h2>
        <p className="text-sm leading-6 text-slate-600">把候选人信息整理成统一结构，便于后续查看和比对。</p>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">基础信息</p>
        <div className="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <DetailRow label="姓名" value={identity.full_name} />
          <DetailRow label="当前职位" value={identity.current_title} />
          <DetailRow label="当前公司" value={identity.current_company} />
          <DetailRow label="地点" value={identity.location_text} />
          <DetailRow label="邮箱" value={identity.email} />
          <DetailRow label="电话" value={identity.phone} />
          <DetailRow label="LinkedIn" value={identity.linkedin_url} />
        </div>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">职业概览</p>
        <div className="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <DetailRow label="原始摘要" value={profileSummary.professional_summary_raw} />
          <DetailRow label="标准摘要" value={profileSummary.professional_summary_normalized} />
          <DetailRow
            label="总经验"
            value={
              profileSummary.years_of_total_experience !== null
                ? `${profileSummary.years_of_total_experience} 年`
                : null
            }
          />
          <DetailRow
            label="相关经验"
            value={
              profileSummary.years_of_relevant_experience !== null
                ? `${profileSummary.years_of_relevant_experience} 年`
                : null
            }
          />
          <DetailRow label="级别" value={profileSummary.seniority_level} />
        </div>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">工作经历</p>
        {normalizedProfile.work_experiences.length > 0 ? (
          <div className="space-y-3">
            {normalizedProfile.work_experiences.map((experience, index) => (
              <div key={`experience-${index}`} className="rounded-2xl border border-slate-200 bg-white px-4 py-4">
                <p className="text-sm font-semibold text-slate-900">
                  {typeof experience.title === "string" && experience.title.trim()
                    ? experience.title
                    : "未命名经历"}
                </p>
                <p className="mt-1 text-sm text-slate-600">
                  {typeof experience.company_name === "string" ? experience.company_name : ""}
                </p>
                <p className="mt-1 text-sm leading-6 text-slate-600">
                  {typeof experience.description_normalized === "string"
                    ? experience.description_normalized
                    : typeof experience.description_raw === "string"
                      ? experience.description_raw
                      : "未提供经历说明。"}
                </p>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-sm leading-6 text-slate-600">未提取到工作经历。</p>
        )}
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">教育与技能</p>
        <div className="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <DetailRow
            label="教育经历"
            value={
              normalizedProfile.educations.length > 0
                ? normalizedProfile.educations
                    .map((education) => {
                      const school = typeof education.school_name === "string" ? education.school_name : "";
                      const degree = typeof education.degree === "string" ? education.degree : "";
                      const major = typeof education.major === "string" ? education.major : "";
                      return [school, degree, major].filter(Boolean).join(" · ");
                    })
                    .filter(Boolean)
                    .join("；")
                : null
            }
          />
          <DetailRow label="原始技能" value={skillsRaw || null} />
          <DetailRow label="标准技能" value={skillsNormalized || null} />
        </div>
      </div>

      <div className="space-y-3">
        <p className="text-sm font-medium text-slate-900">偏好与补充信息</p>
        <div className="space-y-2 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-4">
          <DetailRow
            label="工作授权"
            value={
              typeof normalizedProfile.employment_preferences.work_authorization === "string"
                ? normalizedProfile.employment_preferences.work_authorization
                : null
            }
          />
          <DetailRow label="偏好地点" value={preferredLocations || null} />
          <DetailRow label="偏好模式" value={preferredWorkModes || null} />
          <DetailRow
            label="申请问答"
            value={
              normalizedProfile.application_answers.length > 0
                ? normalizedProfile.application_answers
                    .map((item) => {
                      const question = typeof item.question_text === "string" ? item.question_text : "";
                      const answer = typeof item.answer_text === "string" ? item.answer_text : "";
                      return [question, answer].filter(Boolean).join("：");
                    })
                    .filter(Boolean)
                    .join("；")
                : null
            }
          />
          <DetailRow label="补充亮点" value={highlights || null} />
          <DetailRow label="解析备注" value={parserNotes || null} />
        </div>
      </div>
    </Card>
  );
}
