// Validation lives at the HTTP boundary — nothing downstream ever sees unvalidated input.
import { z } from 'zod';

export const createOrderSchema = z.object({
  customerId: z.string().uuid('customerId must be a valid UUID'),
  items: z
    .array(
      z.object({
        productId: z.string().uuid('productId must be a valid UUID'),
        quantity: z.number().int().positive('quantity must be a positive integer'),
        unitPrice: z.number().positive('unitPrice must be a positive number'),
      })
    )
    .min(1, 'orders must contain at least one item'),
});
