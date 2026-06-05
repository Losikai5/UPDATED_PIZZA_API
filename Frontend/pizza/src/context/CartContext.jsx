/* eslint-disable react-refresh/only-export-components -- provider, context and hook intentionally co-located */
import { useState, createContext, useContext, useCallback, useEffect } from "react";
import { get_cart } from "../services/cart";

export const CartContext = createContext();

export function CartProvider({ children }) {
    // Server-backed cart state. `cart` holds the full CartRead payload
    // ({ uid, items, total }); `cartItems` is exposed for convenience.
    const [cart, setCart] = useState(null);

    // Pull the latest cart from the backend. Only attempt it when a session
    // exists so public pages (login/signup) don't trigger 401 -> redirect.
    const refreshCart = useCallback(async () => {
        if (!localStorage.getItem("access_token")) {
            setCart(null);
            return null;
        }
        try {
            const data = await get_cart();
            setCart(data);
            return data;
        } catch {
            return null;
        }
    }, []);

    function clearCartState() {
        setCart(null);
    }

    // Hydrate once on load if the user is already signed in.
    useEffect(() => {
        (async () => { await refreshCart(); })();
    }, [refreshCart]);

    const values = {
        cart,
        cartItems: cart?.items ?? [],
        cartTotal: cart?.total ?? 0,
        refreshCart,
        clearCartState,
    };

    return (
        <CartContext.Provider value={values}>
            {children}
        </CartContext.Provider>
    );
}

export function useCart() {
    return useContext(CartContext);
}
