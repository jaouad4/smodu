import { Outlet } from "react-router-dom";

export default function AuthLayout() {
  return (
    <div className="min-h-screen bg-[#f7f6f2] flex items-center justify-center px-4">
      <Outlet />
    </div>
  );
}
