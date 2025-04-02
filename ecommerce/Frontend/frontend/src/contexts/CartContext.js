import React, { createContext, useContext, useState, useEffect } from 'react';
import api from '../services/api';

const CartContext = createContext();

export function CartProvider({ children }) {
  const [cart, setCart] = useState(null);
  const [loading, setLoading] = useState(true);
  const userId = 'user1'; // Simplified user identification

  const fetchCart = async () => {
    try {
      const response = await api.getCart(userId);
      setCart(response.data);
    } catch (error) {
      console.error('Error fetching cart:', error);
    } finally {
      setLoading(false);
    }
  };

  const addToCart = async (productId) => {
    try {
      await api.addToCart(userId, productId);
      await fetchCart();
    } catch (error) {
      console.error('Error adding to cart:', error);
    }
  };

  const checkout = async (discountCode) => {
    try {
      const response = await api.checkout(userId, discountCode);
      await fetchCart(); // Refresh cart after checkout
      return response.data;
    } catch (error) {
      console.error('Error during checkout:', error);
      throw error;
    }
  };

  useEffect(() => {
    fetchCart();
  }, []);

  return (
    <CartContext.Provider value={{ cart, loading, addToCart, checkout }}>
      {children}
    </CartContext.Provider>
  );
}

export function useCart() {
  return useContext(CartContext);
}