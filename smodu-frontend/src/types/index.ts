// Onboarding
export type StepType = 'document_read' | 'video_watch' | 'task_complete' | 'form_fill';

export interface OnboardingStep {
  id: number;
  title: string;
  description: string;
  step_type: StepType;
  is_mandatory: boolean;
  is_completed: boolean;
  document_url?: string;
}

export interface OnboardingJourney {
  id: number;
  template_title: string;
  steps: OnboardingStep[];
  completed_steps: number;
  total_steps: number;
  completion_percentage: number;
}

// Formation
export type Level = 'DISCOVERY' | 'BEGINNER' | 'INTERMEDIATE' | 'AUTONOMOUS' | 'PROJECT_READY';
export type LessonType = 'video' | 'pdf' | 'text' | 'exercise';

export interface Lesson {
  id: number;
  title: string;
  lesson_type: LessonType;
  duration_minutes: number;
  is_completed: boolean;
}

export interface Module {
  id: number;
  title: string;
  description: string;
  level: Level;
  is_locked: boolean;
  completion_percentage: number;
  lessons?: Lesson[];
}

export interface LearningPath {
  id: number;
  title: string;
  description: string;
  modules: Module[];
}

// Evaluations
export type QuestionType = 'MCQ' | 'SINGLE_CHOICE';

export interface QuizChoice {
  id: number;
  text: string;
}

export interface QuizQuestion {
  id: number;
  text: string;
  question_type: QuestionType;
  choices: QuizChoice[];
}

export interface Quiz {
  id: number;
  title: string;
  questions: QuizQuestion[];
  pass_threshold: number;
}

export interface SubmitAnswerPayload {
  question_id: number;
  choice_ids: number[];
}

export interface QuizAttempt {
  id: number;
  quiz_id: number;
  score: number;
  attempted_at: string;
}

export interface QuizResult {
  passed: boolean;
  score: number;
  feedback?: Array<{
    question: string;
    correct: boolean;
    explanation: string;
  }>;
}

// Competences
export interface SkillDomain {
  id: number;
  name: string;
}

export interface Skill {
  id: number;
  name: string;
  domain: SkillDomain;
}

export interface UserSkill {
  skill: Skill;
  level: Level;
  is_validated: boolean;
  validated_by?: string;
}

export interface SkillMatrix {
  id: number;
  skills: UserSkill[];
}
