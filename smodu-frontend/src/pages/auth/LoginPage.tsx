import { useState, type FormEvent } from "react";
import { useNavigate } from "react-router-dom";
import { useAuth } from "../../hooks/useAuth";

export default function LoginPage() {
  const { login } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);
    try {
      await login(email, password);
      navigate("/dashboard");
    } catch {
      setError("Email ou mot de passe incorrect.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="w-full max-w-sm">
      {/* Logo */}
      <div className="mb-8 text-center">
        <span className="text-[#01696f] font-bold text-3xl tracking-tight">SMODU</span>
        <p className="mt-2 text-sm text-[#7a7974]">Plateforme d'onboarding Odoo ERP</p>
      </div>

      {/* Carte */}
      <div className="bg-white rounded-xl border border-[#dcd9d5] shadow-sm p-8">
        <h1 className="text-lg font-semibold text-[#28251d] mb-6">Connexion</h1>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-[#28251d] mb-1.5">
              Adresse email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
              placeholder="admin@smodu.ma"
              className="w-full rounded-lg border border-[#d4d1ca] bg-white px-3 py-2 text-sm text-[#28251d] placeholder:text-[#bab9b4] outline-none focus:border-[#01696f] focus:ring-2 focus:ring-[#cedcd8] transition-all"
            />
          </div>

          {/* Mot de passe */}
          <div>
            <label className="block text-sm font-medium text-[#28251d] mb-1.5">
              Mot de passe
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              autoComplete="current-password"
              placeholder="••••••••"
              className="w-full rounded-lg border border-[#d4d1ca] bg-white px-3 py-2 text-sm text-[#28251d] placeholder:text-[#bab9b4] outline-none focus:border-[#01696f] focus:ring-2 focus:ring-[#cedcd8] transition-all"
            />
          </div>

          {/* Erreur */}
          {error && (
            <p className="text-sm text-[#a12c7b] bg-[#e0ced7] rounded-lg px-3 py-2">
              {error}
            </p>
          )}

          {/* Bouton */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full rounded-lg bg-[#01696f] px-4 py-2.5 text-sm font-medium text-white hover:bg-[#0c4e54] disabled:opacity-60 transition-colors"
          >
            {isLoading ? "Connexion..." : "Se connecter"}
          </button>
        </form>
      </div>
    </div>
  );
}
