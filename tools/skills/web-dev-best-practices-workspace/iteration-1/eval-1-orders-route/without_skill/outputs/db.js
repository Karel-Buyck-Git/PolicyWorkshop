/**
 * db.js — lightweight database abstraction layer
 *
 * Replace the implementation of `db.orders.create` with your actual
 * database driver (e.g. pg, mysql2, mongoose, Prisma, Sequelize, etc.).
 *
 * The interface expected by ordersRoute.js:
 *
 *   db.orders.create({ customerId, items }) => Promise<Order>
 *
 * where Order is the saved record including at minimum:
 *   { id, customerId, items, status, createdAt }
 */

// Example using a hypothetical ORM / query-builder pattern.
// Swap this out for your real DB client.

const { Pool } = require('pg'); // example: node-postgres

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
});

const db = {
  orders: {
    /**
     * Persist a new order and return the complete saved record.
     * @param {{ customerId: string|number, items: Array }} orderData
     * @returns {Promise<Object>} The created order row/document
     */
    async create({ customerId, items }) {
      const client = await pool.connect();
      try {
        await client.query('BEGIN');

        // Insert the order header
        const orderResult = await client.query(
          `INSERT INTO orders (customer_id, status, created_at)
           VALUES ($1, 'pending', NOW())
           RETURNING id, customer_id AS "customerId", status, created_at AS "createdAt"`,
          [customerId]
        );
        const order = orderResult.rows[0];

        // Insert line items
        const savedItems = [];
        for (const item of items) {
          const itemResult = await client.query(
            `INSERT INTO order_items (order_id, product_id, quantity)
             VALUES ($1, $2, $3)
             RETURNING id, product_id AS "productId", quantity`,
            [order.id, item.productId, item.quantity]
          );
          savedItems.push(itemResult.rows[0]);
        }

        await client.query('COMMIT');

        return { ...order, items: savedItems };
      } catch (err) {
        await client.query('ROLLBACK');
        throw err;
      } finally {
        client.release();
      }
    },
  },
};

module.exports = db;
