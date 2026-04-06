// ─── ONBOARDING ───────────────────────────────────────
export type StepType = 'document_read' | 'task_complete' | 'video_watch' | 'form_fill';

export interface OnboardingStep {
  id: string;
  title: string;
  description: string;
  step_type: StepType;
  order: number;
  is_mandatory: boolean;
  is_completed: boolean;
  document_url: string | null;
}

export interface OnboardingJourney {
  template_title: string;
  total_steps: number;
  completed_steps: number;
  completion_percentage: number;
  steps: OnboardingStep[];
}

// ─── FORMATION ────────────────────────────────────────
export type Level = 'DISCOVERY' | 'BEGINNER' | 'INTERMEDIATE' | 'AUTONOMOUS' | 'PROJECT_READY';
export type LessonType = 'video' | 'pdf' | 'text' | 'exercise';

export interface Lesson {
  id: string;
  title: string;
  lesson_type: LessonType;
  order: number;
  duration_minutes: number;
  is_completed: boolean;
  content_url: string | null;
}

export interface Module {
  id: string;
  title: string;
  description: string;
  level: Level;
  order: number;
  is_locked: boolean;
  completion_percentage: number;
  lessons: Lesson[];
}

export interface LearningPath {
  id: string;
  title: string;
  description: string;
  modules: Module[];
  completion_percentage: number;
  is_enrolled: boolean;
}

// ─── EVALUATIONS ──────────────────────────────────────
export type QuestionType = 'MCQ' | 'TRUE_FALSE' | 'OPEN';

export interface Choice {
  id: string;
  text: string;
}

export interface Question {
  id: string;
  text: string;
  question_type: QuestionType;
  choices: Choice[];
}

export interface Quiz {
  id: string;
  title: string;
  pass_threshold: number;
  max_attempts: number;
  questions: Question[];
}

export interface QuizResult {
  attempt_id: string;
  score: number;
  passed: boolean;
  correct_answers: number;
  total_questions: number;
}

export interface SubmitQuizPayload {
  answers: { question_id: string; choice_ids?: string[]; text_answer?: string }[];
}

// ─── COMPÉTENCES ──────────────────────────────────────
export interface SkillDomain {
  id: string;
  name: string;
}

export interface Skill {
  id: string;
  name: string;
  domain: SkillDomain;
}

export interface UserSkill {
  skill: Skill;
  level: Level;
  is_validated: boolean;
  validated_by: string | null;
}

export interface SkillMatrix {
  skills: UserSkill[];
}

// ─── NOTIFICATIONS ────────────────────────────────────
export interface Notification {
  id: string;
  notification_type: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

// ─── DASHBOARD ────────────────────────────────────────
export type ValidationStatus =
  | 'ONBOARDING' | 'TRAINING' | 'EVALUATION'
  | 'CONSOLIDATION' | 'VALIDATED' | 'NOT_READY';

export interface LearnerDashboard {
  global_completion: number;
  active_modules: Module[];
  next_steps: OnboardingStep[];
  validated_skills_count: number;
  project_status: ValidationStatus;
  recent_notifications: Notification[];
}

export interface ManagerDashboardKPI {
  active_learners: number;
  avg_completion_rate: number;
  validated_learners: number;
  delayed_learners: number;
}

export interface LearnerSummary {
  user: { id: string; full_name: string; email: string; department: string };
  completion_percentage: number;
  quiz_avg_score: number;
  project_status: ValidationStatus;
  last_activity: string;
}

export interface ManagerDashboard {
  kpis: ManagerDashboardKPI;
  learners: LearnerSummary[];
}

