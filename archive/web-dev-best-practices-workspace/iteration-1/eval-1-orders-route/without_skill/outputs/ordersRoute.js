const express = require('express');
const router = express.Router();
const db = require('../db');

/**
 * POST /orders
 * Creates a new order.
 *
 * Request body:
 *   - customerId {string|number} (required) — ID of the customer placing the order
 *   - items      {Array}         (required) — non-empty array of order line items
 *
 * Each item must have:
 *   - productId {string|number} (required)
 *   - quantity  {number}        (required, positive integer)
 *
 * Responses:
 *   201 Created  — order saved successfully, returns the created order object
 *   400 Bad Request — validation failed, returns { error: string }
 *   500 Internal Server Error — unexpected error
 */
router.post('/orders', async (req, res) => {
  try {
    const { customerId, items } = req.body;

    // --- Validation ---
    const errors = [];

    if (customerId === undefined || customerId === null || customerId === '') {
      errors.push('customerId is required.');
    }

    if (!Array.isArray(items)) {
      errors.push('items must be an array.');
    } else if (items.length === 0) {
      errors.push('items array must not be empty.');
    } else {
      items.forEach((item, index) => {
        if (item.productId === undefined || item.productId === null || item.productId === '') {
          errors.push(`items[${index}].productId is required.`);
        }
        if (
          item.quantity === undefined ||
          !Number.isInteger(item.quantity) ||
          item.quantity < 1
        ) {
          errors.push(`items[${index}].quantity must be a positive integer.`);
        }
      });
    }

    if (errors.length > 0) {
      return res.status(400).json({ error: errors.join(' ') });
    }

    // --- Persist to database ---
    const order = await db.orders.create({ customerId, items });

    return res.status(201).json(order);
  } catch (err) {
    console.error('POST /orders error:', err);
    return res.status(500).json({ error: 'An unexpected error occurred. Please try again later.' });
  }
});

module.exports = router;
