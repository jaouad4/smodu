import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import { authApi } from "../api/client";
import type { AuthState, AuthTokens, LoginResponse, User, UserRole } from "../types/auth";

interface AuthContextValue extends AuthState {
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  hasRole: (...roles: UserRole[]) => boolean;
}

export const AuthContext = createContext<AuthContextValue | null>(null);

const TOKENS_KEY = "smodu_tokens";
const USER_KEY = "smodu_user";

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    try {
      const raw = localStorage.getItem(USER_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const [tokens, setTokens] = useState<AuthTokens | null>(() => {
    try {
      const raw = localStorage.getItem(TOKENS_KEY);
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState(true);

  // ── Vérifier la validité du token au montage ────────────────────
  useEffect(() => {
    const verifyToken = async () => {
      if (!tokens?.access) {
        setIsLoading(false);
        return;
      }
      try {
        const { data } = await authApi.me();
        setUser(data);
        localStorage.setItem(USER_KEY, JSON.stringify(data));
      } catch {
        setUser(null);
        setTokens(null);
        localStorage.removeItem(TOKENS_KEY);
        localStorage.removeItem(USER_KEY);
      } finally {
        setIsLoading(false);
      }
    };
    verifyToken();
  }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const login = useCallback(async (email: string, password: string) => {
    const { data } = await authApi.login(email, password);
    const response = data as LoginResponse;

    const newTokens: AuthTokens = {
      access: response.access,
      refresh: response.refresh,
    };

    setTokens(newTokens);
    setUser(response.user);
    localStorage.setItem(TOKENS_KEY, JSON.stringify(newTokens));
    localStorage.setItem(USER_KEY, JSON.stringify(response.user));
  }, []);

  const logout = useCallback(async () => {
    try {
      if (tokens?.refresh) {
        await authApi.logout(tokens.refresh);
      }
    } finally {
      setUser(null);
      setTokens(null);
      localStorage.removeItem(TOKENS_KEY);
      localStorage.removeItem(USER_KEY);
    }
  }, [tokens]);

  const hasRole = useCallback(
    (...roles: UserRole[]) => !!user && roles.includes(user.role),
    [user]
  );

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      tokens,
      isAuthenticated: !!user && !!tokens,
      isLoading,
      login,
      logout,
      hasRole,
    }),
    [user, tokens, isLoading, login, logout, hasRole]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
