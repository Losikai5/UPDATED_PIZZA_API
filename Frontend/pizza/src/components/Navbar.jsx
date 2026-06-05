import { useEffect, useState } from "react";
import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { useCart } from "../context/CartContext";
import { logout as logoutRequest } from "../services/auth";
import PizzaMark from "./PizzaMark";

export default function Navbar() {
  const { isAuthenticated, isAdmin, user, logout } = useAuth();
  const { cartItems } = useCart();
  const navigate = useNavigate();
  const [menuOpen, setMenuOpen] = useState(false);

  const cartCount = cartItems.reduce((sum, i) => sum + (i.quantity || 1), 0);

  const closeMenu = () => setMenuOpen(false);

  // Lock body scroll while the mobile drawer is open.
  useEffect(() => {
    document.body.style.overflow = menuOpen ? "hidden" : "";
    return () => {
      document.body.style.overflow = "";
    };
  }, [menuOpen]);

  async function handleLogout() {
    try {
      await logoutRequest();
    } catch {
      // Even if the server call fails, clear the local session below.
    }
    logout();
    navigate("/login");
  }

  const tickerItems = [
    "Wood-Fired Daily",
    "Hand-Tossed Dough",
    "30-Minute Delivery",
    "Fresh Basil & Mozzarella",
    "Order Online",
  ];

  const navLinks = (
    <>
      <NavLink to="/menu" className="nav-link">Menu</NavLink>

      {isAuthenticated && (
        <>
          <NavLink to="/orders" className="nav-link">Orders</NavLink>
          <NavLink to="/reviews" className="nav-link">Reviews</NavLink>
          <NavLink to="/cart" className="nav-link cart-pill">
            Cart
            {cartCount > 0 && (
              <span className="cart-count" aria-label={`${cartCount} items in cart`}>
                {cartCount}
              </span>
            )}
          </NavLink>
        </>
      )}

      {isAdmin && (
        <>
          <NavLink to="/admin/menu" className="nav-link">Manage Menu</NavLink>
          <NavLink to="/admin/orders" className="nav-link">All Orders</NavLink>
          <NavLink to="/admin/reviews" className="nav-link">All Reviews</NavLink>
          <NavLink to="/admin/addresses" className="nav-link">Addresses</NavLink>
        </>
      )}
    </>
  );

  return (
    <>
      <div className="ticker" aria-hidden="true">
        <div className="ticker-track">
          {[...tickerItems, ...tickerItems].map((t, i) => (
            <span key={i}>{t}</span>
          ))}
        </div>
      </div>
      <nav className="nav">
        <NavLink to={isAuthenticated ? "/dashboard" : "/login"} className="brand">
          <span className="seal"><PizzaMark size={26} title="Losika Pizza" /></span> Losika Pizza
        </NavLink>

        {/* Desktop navigation */}
        <div className="nav-links nav-links-desktop">
          {navLinks}
          {isAuthenticated ? (
            <div className="row" style={{ marginLeft: 8 }}>
              <span className="muted nav-email">{user?.email}</span>
              <button className="btn btn-outline btn-sm" onClick={handleLogout}>Logout</button>
            </div>
          ) : (
            <>
              <NavLink to="/login" className="nav-link">Login</NavLink>
              <NavLink to="/signup" className="btn btn-primary btn-sm" style={{ marginLeft: 6 }}>
                Sign up
              </NavLink>
            </>
          )}
        </div>

        {/* Mobile hamburger toggle */}
        <button
          type="button"
          className={`nav-toggle ${menuOpen ? "is-open" : ""}`}
          aria-label={menuOpen ? "Close menu" : "Open menu"}
          aria-expanded={menuOpen}
          aria-controls="mobile-menu"
          onClick={() => setMenuOpen((v) => !v)}
        >
          <span className="nav-toggle-bar" />
          <span className="nav-toggle-bar" />
          <span className="nav-toggle-bar" />
        </button>
      </nav>

      {/* Mobile drawer */}
      <div
        className={`nav-scrim ${menuOpen ? "is-open" : ""}`}
        onClick={() => setMenuOpen(false)}
        aria-hidden="true"
      />
      <div id="mobile-menu" className={`mobile-menu ${menuOpen ? "is-open" : ""}`}>
        {/* Any tap inside (nav link or logout) dismisses the drawer. */}
        <div className="nav-links-mobile" onClick={closeMenu}>
          {navLinks}
          <hr className="divider" />
          {isAuthenticated ? (
            <>
              <span className="muted nav-email">{user?.email}</span>
              <button className="btn btn-outline btn-block" onClick={handleLogout}>Logout</button>
            </>
          ) : (
            <>
              <NavLink to="/login" className="btn btn-outline btn-block">Login</NavLink>
              <NavLink to="/signup" className="btn btn-primary btn-block">Sign up</NavLink>
            </>
          )}
        </div>
      </div>
    </>
  );
}
