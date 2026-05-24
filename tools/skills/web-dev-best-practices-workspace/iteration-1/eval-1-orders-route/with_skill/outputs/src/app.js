import express from 'express';
import ordersRouter from './orders/orders.router.js';
import { errorHandler } from './middleware/error-handler.js';

const app = express();
app.use(express.json());
app.use('/orders', ordersRouter);
app.use(errorHandler); // must be last
export default app;
