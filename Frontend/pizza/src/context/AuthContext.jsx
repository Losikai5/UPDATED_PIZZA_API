/* eslint-disable react-refresh/only-export-components -- provider, context and hook intentionally co-located */
import { useContext, createContext, useState, useEffect } from "react";
import { jwtDecode } from "jwt-decode";

export const AuthContext = createContext();

// Decode the stored access token into a lightweight user object.
// The backend nests identity under a "user" claim and adds exp/jti/refresh
// (see src/auth/utils.py -> create_access_token).
function userFromToken(token) {
    if (!token) return null;
    try {
        const decoded = jwtDecode(token);
        const claims = decoded.user || {};
        // Reject expired tokens up front so we don't show a logged-in UI.
        if (decoded.exp && decoded.exp * 1000 < Date.now()) return null;
        return { uid: claims.uid, email: claims.email, role: claims.role };
    } catch {
        return null;
    }
}

export function ProviderContext({ children }) {
    const [user, setUser] = useState(() =>
        userFromToken(localStorage.getItem("access_token"))
    );

    // Keep auth state in sync if the token changes in another tab.
    useEffect(() => {
        function sync() {
            setUser(userFromToken(localStorage.getItem("access_token")));
        }
        window.addEventListener("storage", sync);
        return () => window.removeEventListener("storage", sync);
    }, []);

    function login(accessToken, refreshToken) {
        localStorage.setItem("access_token", accessToken);
        localStorage.setItem("refresh_token", refreshToken);
        setUser(userFromToken(accessToken));
    }

    function logout() {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        setUser(null);
    }

    const values = {
        user,
        role: user?.role ?? null,
        isAuthenticated: !!user,
        isAdmin: user?.role === "Admin",
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={values}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    return useContext(AuthContext);
}
