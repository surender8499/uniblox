import React, { useState, useEffect } from 'react';
import { useCart } from '../contexts/CartContext';
import api from '../services/api';
import { Box, Card, CardContent, Typography, Button, Grid } from '@mui/material';

function ProductList() {
  const [products, setProducts] = useState([]);
  const { addToCart } = useCart();

  useEffect(() => {
    api.getProducts()
      .then(response => setProducts(response.data))
      .catch(error => console.error('Error fetching products:', error));
  }, []);

  return (
    <Box sx={{ flexGrow: 1, padding: 3 }}>
      <Typography variant="h4" gutterBottom>Products</Typography>
      <Grid container spacing={3}>
        {products.map(product => (
          <Grid item key={product.id} xs={12} sm={6} md={4}>
            <Card>
              <CardContent>
                <Typography variant="h6">{product.name}</Typography>
                <Typography variant="body1">${product.price}</Typography>
                <Typography variant="body2" color="text.secondary">
                  {product.description}
                </Typography>
                <Button 
                  variant="contained" 
                  onClick={() => addToCart(product.id)}
                  sx={{ mt: 2 }}
                >
                  Add to Cart
                </Button>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
}

export default ProductList;