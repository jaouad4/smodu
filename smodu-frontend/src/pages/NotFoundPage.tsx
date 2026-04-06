import { Link } from "react-router-dom";

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-[#f7f6f2] flex flex-col items-center justify-center text-center px-4">
      <p className="text-6xl font-bold text-[#01696f]">404</p>
      <h1 className="mt-4 text-xl font-semibold text-[#28251d]">Page introuvable</h1>
      <p className="mt-2 text-sm text-[#7a7974]">Cette page n'existe pas ou a été déplacée.</p>
      <Link to="/dashboard" className="mt-6 text-sm text-[#01696f] hover:underline">
        Retour au dashboard →
      </Link>
    </div>
  );
}
