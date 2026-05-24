// Repository: database interaction only — no business logic.
import { db } from '../db/connection.js';
import { randomUUID } from 'crypto';

export async function createOrder({ customerId, items, total }) {
  return db.transaction(async (trx) => {
    const [order] = await trx('orders')
      .insert({ id: randomUUID(), customer_id: customerId, total, created_at: new Date() })
      .returning('*');

    const lineItems = items.map((item) => ({
      id: randomUUID(),
      order_id: order.id,
      product_id: item.productId,
      quantity: item.quantity,
      unit_price: item.unitPrice,
    }));
    await trx('order_items').insert(lineItems);

    return { ...order, items: lineItems };
  });
}
