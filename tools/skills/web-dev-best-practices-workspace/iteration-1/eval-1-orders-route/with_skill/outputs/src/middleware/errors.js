export class AppError extends Error {
  constructor(message, statusCode) {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = true;
  }
}
export class ValidationError extends AppError {
  constructor(fieldErrors) {
    super('Validation failed', 400);
    this.fieldErrors = fieldErrors;
  }
}
export class NotFoundError extends AppError {
  constructor(resource) {
    super(`${resource} not found`, 404);
  }
}
