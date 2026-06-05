// AdminRoute.jsx
import { Navigate } from "react-router-dom";
import { jwtDecode } from "jwt-decode";

// Safely read the role out of the stored access token. The backend nests
// identity under a "user" claim (see auth/utils.create_access_token).
function readRole(token) {
  if (!token) return null;
  try {
    return jwtDecode(token).user?.role ?? null;
  } catch {
    return null;
  }
}

export default function AdminRoute({ children }) {
  const role = readRole(localStorage.getItem("access_token"));

  if (role === null) {
    return <Navigate to="/login" replace />;
  }
  if (role !== "Admin") {
    return <Navigate to="/" replace />; // logged in but not an admin
  }
  return children;
}
