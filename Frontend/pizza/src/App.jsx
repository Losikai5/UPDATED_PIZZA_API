import { BrowserRouter, Routes, Route } from "react-router-dom";
import { ProviderContext } from "./context/AuthContext";
import { CartProvider } from "./context/CartContext";

// Auth pages
import LoginPage from "./pages/auth/LoginPage";
import SignupPage from "./pages/auth/SignupPage";

// Customer pages
import MenuPage from "./pages/customer/MenuPage";
import CartPage from "./pages/customer/CartPage";
import OrdersPage from "./pages/customer/OrdersPage";
import ReviewsPage from "./pages/customer/ReviewsPage";

// Admin pages
import AdminMenuPage from "./pages/admin/AdminMenuPage";
import AdminOrdersPage from "./pages/admin/AdminOrdersPage";
import AdminReviewsPage from "./pages/admin/AdminReviewsPage";
import AddressesPage from "./pages/admin/AddressesPage";

// Dashboard
import Dashboard from "./pages/Dashboard";

// Route guards
import ProtectedRoute from "./components/ProtectedRoute";
import AdminRoute from "./components/AdminRoute";

export default function App() {
  return (
    <ProviderContext>
      <CartProvider>
        <BrowserRouter>
          <Routes>
            {/* Public routes */}
            <Route path="/login" element={<LoginPage />} />
            <Route path="/signup" element={<SignupPage />} />
            <Route path="/menu" element={<MenuPage />} />

            {/* Customer protected routes */}
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/cart" element={<ProtectedRoute><CartPage /></ProtectedRoute>} />
            <Route path="/orders" element={<ProtectedRoute><OrdersPage /></ProtectedRoute>} />
            <Route path="/reviews" element={<ProtectedRoute><ReviewsPage /></ProtectedRoute>} />

            {/* Admin protected routes */}
            <Route path="/admin/menu" element={<AdminRoute><AdminMenuPage /></AdminRoute>} />
            <Route path="/admin/orders" element={<AdminRoute><AdminOrdersPage /></AdminRoute>} />
            <Route path="/admin/reviews" element={<AdminRoute><AdminReviewsPage /></AdminRoute>} />
            <Route path="/admin/addresses" element={<AdminRoute><AddressesPage /></AdminRoute>} />

            {/* Default route */}
            <Route path="/" element={<LoginPage />} />
          </Routes>
        </BrowserRouter>
      </CartProvider>
    </ProviderContext>
  );
}