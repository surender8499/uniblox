import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { AppBar, Toolbar, Typography, Button, Container } from '@mui/material';
import ProductList from './components/ProductList';
import Cart from './components/Cart';
import AdminPanel from './components/AdminPanel';
import { CartProvider } from './contexts/CartContext';

function App() {
  return (
    <CartProvider>
      <Router>
        <AppBar position="static">
          <Toolbar>
            <Typography variant="h6" component="div" sx={{ flexGrow: 1 }}>
              Ecommerce Store
            </Typography>
            <Button color="inherit" component={Link} to="/">Products</Button>
            <Button color="inherit" component={Link} to="/cart">Cart</Button>
            <Button color="inherit" component={Link} to="/admin">Admin</Button>
          </Toolbar>
        </AppBar>
        
        <Container maxWidth="lg" sx={{ mt: 4 }}>
          <Routes>
            <Route path="/" element={<ProductList />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/admin" element={<AdminPanel />} />
          </Routes>
        </Container>
      </Router>
    </CartProvider>
  );
}

export default App;