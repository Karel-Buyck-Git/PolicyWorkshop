import { Router } from 'express';
import { createOrder } from './orders.controller.js';

const router = Router();
router.post('/', createOrder);

export default router;
