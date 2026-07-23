import { useState, useCallback } from 'react';

// Validation rules are kept separate so they can be tested independently
// and extended without touching hook logic.
function validateEmail(email) {
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email.trim()) return 'Email is required';
  if (!emailPattern.test(email)) return 'Enter a valid email address';
  return null;
}

function validatePassword(password) {
  if (!password) return 'Password is required';
  if (password.length < 8) return 'Password must be at least 8 characters';
  return null;
}

const INITIAL_VALUES = { email: '', password: '' };
const INITIAL_ERRORS = { email: null, password: null };
const INITIAL_TOUCHED = { email: false, password: false };

/**
 * Manages form state for a login form with email and password fields.
 *
 * Validates fields on blur (after the user has interacted with them) and
 * re-validates on every change once a field has been touched, so users get
 * timely feedback without being scolded before they've started typing.
 *
 * @param {object}   [options]
 * @param {function} [options.onSubmit] - Called with { email, password } when
 *   the form passes validation. Receives a plain object, not a SyntheticEvent.
 *
 * @returns {{
 *   values:      { email: string, password: string },
 *   errors:      { email: string|null, password: string|null },
 *   touched:     { email: boolean, password: boolean },
 *   isSubmitting: boolean,
 *   handleChange: (e: React.ChangeEvent<HTMLInputElement>) => void,
 *   handleBlur:   (e: React.FocusEvent<HTMLInputElement>)  => void,
 *   handleSubmit: (e: React.FormEvent<HTMLFormElement>)    => Promise<void>,
 *   resetForm:    () => void,
 * }}
 */
export function useLoginForm({ onSubmit } = {}) {
  const [values, setValues] = useState(INITIAL_VALUES);
  const [errors, setErrors] = useState(INITIAL_ERRORS);
  const [touched, setTouched] = useState(INITIAL_TOUCHED);
  const [isSubmitting, setIsSubmitting] = useState(false);

  // Returns a full error map for the current field values.
  const validateAll = useCallback((currentValues) => ({
    email:    validateEmail(currentValues.email),
    password: validatePassword(currentValues.password),
  }), []);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;

    setValues((prev) => {
      const next = { ...prev, [name]: value };

      // Re-validate immediately once a field has been touched so the user
      // sees errors resolve as they correct their input.
      setErrors((prevErrors) => {
        if (!touched[name]) return prevErrors;
        return { ...prevErrors, [name]: validateAll(next)[name] };
      });

      return next;
    });
  }, [touched, validateAll]);

  const handleBlur = useCallback((e) => {
    const { name, value } = e.target;

    setTouched((prev) => ({ ...prev, [name]: true }));

    // Validate only the blurred field to avoid showing errors the user
    // hasn't reached yet.
    const fieldValidators = { email: validateEmail, password: validatePassword };
    const fieldError = fieldValidators[name]?.(value) ?? null;
    setErrors((prev) => ({ ...prev, [name]: fieldError }));
  }, []);

  const handleSubmit = useCallback(async (e) => {
    e.preventDefault();

    // Mark every field as touched so all errors become visible on submit.
    setTouched({ email: true, password: true });

    const validationErrors = validateAll(values);
    setErrors(validationErrors);

    const hasErrors = Object.values(validationErrors).some(Boolean);
    if (hasErrors || !onSubmit) return;

    setIsSubmitting(true);
    try {
      await onSubmit({ email: values.email, password: values.password });
    } finally {
      // Always clear the submitting flag, even if onSubmit throws, so the
      // form doesn't become permanently locked on a network error.
      setIsSubmitting(false);
    }
  }, [values, validateAll, onSubmit]);

  const resetForm = useCallback(() => {
    setValues(INITIAL_VALUES);
    setErrors(INITIAL_ERRORS);
    setTouched(INITIAL_TOUCHED);
    setIsSubmitting(false);
  }, []);

  return {
    values,
    errors,
    touched,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    resetForm,
  };
}
