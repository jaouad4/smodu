export type UserRole =
  | "ADMIN"
  | "HR"
  | "MANAGER"
  | "TRAINER"
  | "ODOO_REF"
  | "LEARNER";

export interface UserProfile {
  bio: string;
  phone: string;
  start_date: string | null;
  contract_type: string;
  project_status: string;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: UserRole;
  department: string;
  avatar: string | null;
  is_active: boolean;
  date_joined: string;
  profile: UserProfile | null;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginResponse extends AuthTokens {
  user: User;
}

export interface AuthState {
  user: User | null;
  tokens: AuthTokens | null;
  isAuthenticated: boolean;
  isLoading: boolean;
}
