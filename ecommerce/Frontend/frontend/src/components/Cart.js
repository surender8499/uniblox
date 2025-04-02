import React from 'react';
import { useCart } from '../contexts/CartContext';
import { Box, Typography, List, ListItem, ListItemText, Divider, Button, TextField } from '@mui/material';

function Cart() {
  const { cart, loading, checkout } = useCart();
  const [discountCode, setDiscountCode] = React.useState('');
  const [checkoutMessage, setCheckoutMessage] = React.useState(null);

  const handleCheckout = async () => {
    try {
      const order = await checkout(discountCode);
      setCheckoutMessage(`Order #${order.id} placed successfully! Total: $${order.final_amount}`);
    } catch (error) {
      setCheckoutMessage(error.response?.data?.error || 'Checkout failed');
    }
  };

  if (loading) return <Typography>Loading cart...</Typography>;
  if (!cart) return <Typography>Your cart is empty</Typography>;

  return (
    <Box sx={{ padding: 3 }}>
      <Typography variant="h4" gutterBottom>Your Cart</Typography>
      <List>
        {cart.items.map(item => (
          <React.Fragment key={item.id}>
            <ListItem>
              <ListItemText
                primary={item.product.name}
                secondary={`Quantity: ${item.quantity} - $${item.subtotal}`}
              />
            </ListItem>
            <Divider />
          </React.Fragment>
        ))}
      </List>
      <Typography variant="h6" sx={{ mt: 2 }}>
        Total: ${cart.total}
      </Typography>
      
      <Box sx={{ mt: 3 }}>
        <TextField
          label="Discount Code"
          value={discountCode}
          onChange={(e) => setDiscountCode(e.target.value)}
          sx={{ mr: 2 }}
        />
        <Button 
          variant="contained" 
          color="primary" 
          onClick={handleCheckout}
        >
          Checkout
        </Button>
      </Box>
      
      {checkoutMessage && (
        <Typography color={checkoutMessage.includes('success') ? 'success.main' : 'error.main'} sx={{ mt: 2 }}>
          {checkoutMessage}
        </Typography>
      )}
    </Box>
  );
}

export default Cart;