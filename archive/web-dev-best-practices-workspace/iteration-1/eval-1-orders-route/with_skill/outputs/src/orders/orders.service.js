// Service: business rules only — no HTTP objects, no raw SQL.
import { createOrder } from './orders.repository.js';

export function calculateOrderTotal(items) {
  return items.reduce((sum, item) => sum + item.quantity * item.unitPrice, 0);
}

export async function placeOrder({ customerId, items }) {
  const total = calculateOrderTotal(items);
  return createOrder({ customerId, items, total });
}
