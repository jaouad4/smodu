import axios from "axios";

const BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

export const apiClient = axios.create({
  baseURL: `${BASE_URL}/api`,
  headers: { "Content-Type": "application/json" },
  timeout: 10000,
});

// ── Intercepteur requête : injecter le Bearer token ──────────────────
apiClient.interceptors.request.use((config) => {
  const raw = localStorage.getItem("smodu_tokens");
  if (raw) {
    try {
      const tokens = JSON.parse(raw);
      if (tokens?.access) {
        config.headers.Authorization = `Bearer ${tokens.access}`;
      }
    } catch {
      // token corrompu → on ignore
    }
  }
  return config;
});

// ── Intercepteur réponse : refresh auto sur 401 ───────────────────────
let isRefreshing = false;
let failedQueue: Array<{
  resolve: (token: string) => void;
  reject: (err: unknown) => void;
}> = [];

const processQueue = (error: unknown, token: string | null = null) => {
  failedQueue.forEach((p) => (error ? p.reject(error) : p.resolve(token!)));
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        }).then((token) => {
          originalRequest.headers.Authorization = `Bearer ${token}`;
          return apiClient(originalRequest);
        });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      try {
        const raw = localStorage.getItem("smodu_tokens");
        const tokens = raw ? JSON.parse(raw) : null;

        if (!tokens?.refresh) throw new Error("No refresh token");

        const { data } = await axios.post(`${BASE_URL}/api/auth/refresh/`, {
          refresh: tokens.refresh,
        });

        const newTokens = { ...tokens, access: data.access };
        localStorage.setItem("smodu_tokens", JSON.stringify(newTokens));

        processQueue(null, data.access);
        originalRequest.headers.Authorization = `Bearer ${data.access}`;
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        localStorage.removeItem("smodu_tokens");
        localStorage.removeItem("smodu_user");
        window.location.href = "/login";
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    return Promise.reject(error);
  }
);

// ── Helpers auth ──────────────────────────────────────────────────────
export const authApi = {
  login: (email: string, password: string) =>
    apiClient.post("/auth/login/", { email, password }),
  logout: (refresh: string) =>
    apiClient.post("/auth/logout/", { refresh }),
  me: () => apiClient.get("/auth/me/"),
};

export default apiClient;
