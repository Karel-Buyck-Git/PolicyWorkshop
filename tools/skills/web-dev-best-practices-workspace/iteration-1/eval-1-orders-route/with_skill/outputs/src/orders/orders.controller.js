// Controller: HTTP concerns only — parse, validate, respond. No business logic here.
import { createOrderSchema } from './orders.schema.js';
import { placeOrder } from './orders.service.js';
import { ValidationError } from '../middleware/errors.js';

export async function createOrder(req, res, next) {
  const result = createOrderSchema.safeParse(req.body);
  if (!result.success) {
    return next(new ValidationError(result.error.flatten().fieldErrors));
  }
  try {
    const order = await placeOrder(result.data);
    res.status(201).json(order);
  } catch (err) {
    next(err);
  }
}
