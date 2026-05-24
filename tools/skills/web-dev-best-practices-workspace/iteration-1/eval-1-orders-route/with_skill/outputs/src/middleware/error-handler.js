// Centralized error handler: operational errors get their own status; programmer errors become 500.
// Internal details are never leaked in production responses.
export function errorHandler(err, req, res, next) {
  if (err.isOperational) {
    const body = { error: err.message };
    if (err.fieldErrors) body.fieldErrors = err.fieldErrors;
    return res.status(err.statusCode).json(body);
  }
  console.error(err); // log programmer errors fully
  res.status(500).json({ error: 'An unexpected error occurred' });
}
