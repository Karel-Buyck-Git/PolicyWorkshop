/**
 * ordersRoute.test.js
 * Unit / integration tests for POST /orders using Jest + Supertest.
 *
 * Install dev dependencies:
 *   npm install --save-dev jest supertest
 *
 * Run:
 *   npx jest ordersRoute.test.js
 */

const request = require('supertest');
const express = require('express');

// Mock the db module so tests don't need a real database
jest.mock('../db', () => ({
  orders: {
    create: jest.fn(),
  },
}));

const db = require('../db');
const ordersRouter = require('./ordersRoute');

// Build a minimal Express app for testing
function buildApp() {
  const app = express();
  app.use(express.json());
  app.use('/', ordersRouter);
  return app;
}

describe('POST /orders', () => {
  let app;

  beforeEach(() => {
    app = buildApp();
    jest.clearAllMocks();
  });

  // --- Happy path ---

  test('201: creates an order and returns it', async () => {
    const mockOrder = {
      id: 'order-123',
      customerId: 'cust-42',
      status: 'pending',
      createdAt: new Date().toISOString(),
      items: [{ id: 'item-1', productId: 'prod-7', quantity: 2 }],
    };
    db.orders.create.mockResolvedValue(mockOrder);

    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-42', items: [{ productId: 'prod-7', quantity: 2 }] });

    expect(res.status).toBe(201);
    expect(res.body).toEqual(mockOrder);
    expect(db.orders.create).toHaveBeenCalledWith({
      customerId: 'cust-42',
      items: [{ productId: 'prod-7', quantity: 2 }],
    });
  });

  // --- Validation failures ---

  test('400: missing customerId', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ items: [{ productId: 'prod-1', quantity: 1 }] });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/customerId/i);
    expect(db.orders.create).not.toHaveBeenCalled();
  });

  test('400: missing items', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1' });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/items/i);
  });

  test('400: items is not an array', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: 'not-an-array' });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/items must be an array/i);
  });

  test('400: items is an empty array', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: [] });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/not be empty/i);
  });

  test('400: item missing productId', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: [{ quantity: 3 }] });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/productId/i);
  });

  test('400: item quantity not a positive integer', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: [{ productId: 'prod-1', quantity: 0 }] });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/quantity/i);
  });

  test('400: item quantity is a float', async () => {
    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: [{ productId: 'prod-1', quantity: 1.5 }] });

    expect(res.status).toBe(400);
    expect(res.body.error).toMatch(/quantity/i);
  });

  // --- Server errors ---

  test('500: database error returns 500', async () => {
    db.orders.create.mockRejectedValue(new Error('DB connection failed'));

    const res = await request(app)
      .post('/orders')
      .send({ customerId: 'cust-1', items: [{ productId: 'prod-1', quantity: 1 }] });

    expect(res.status).toBe(500);
    expect(res.body.error).toMatch(/unexpected error/i);
  });
});
