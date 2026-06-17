import { useState, useCallback } from 'react';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const initialValues = {
  email: '',
  password: '',
};

const initialErrors = {
  email: '',
  password: '',
};

const initialTouched = {
  email: false,
  password: false,
};

/**
 * Validates a single field and returns an error message string (empty string = valid).
 */
function validateField(name, value) {
  switch (name) {
    case 'email': {
      if (!value.trim()) return 'Email is required.';
      if (!EMAIL_REGEX.test(value.trim())) return 'Please enter a valid email address.';
      return '';
    }
    case 'password': {
      if (!value) return 'Password is required.';
      if (value.length < 8) return 'Password must be at least 8 characters.';
      return '';
    }
    default:
      return '';
  }
}

/**
 * Validates all fields and returns an errors object.
 */
function validateAll(values) {
  return Object.keys(values).reduce((acc, name) => {
    acc[name] = validateField(name, values[name]);
    return acc;
  }, {});
}

/**
 * useLoginForm
 *
 * A custom React hook that manages form state for a login form with
 * email and password fields, including basic validation.
 *
 * Returns:
 *   values      - current field values
 *   errors      - validation error messages per field (empty string = no error)
 *   touched     - whether each field has been interacted with
 *   isValid     - true when there are no validation errors
 *   isSubmitting - true while the onSubmit callback is in flight
 *   handleChange - onChange handler for inputs
 *   handleBlur  - onBlur handler for inputs (marks field as touched and validates)
 *   handleSubmit - form onSubmit handler
 *   reset       - resets form to initial state
 *
 * Usage:
 *   const { values, errors, touched, isValid, isSubmitting, handleChange, handleBlur, handleSubmit, reset } =
 *     useLoginForm({ onSubmit: async ({ email, password }) => { ... } });
 */
export function useLoginForm({ onSubmit } = {}) {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState(initialErrors);
  const [touched, setTouched] = useState(initialTouched);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const isValid = Object.values(errors).every((e) => e === '') &&
    Object.values(touched).every((t) => t === true);

  const handleChange = useCallback((event) => {
    const { name, value } = event.target;

    setValues((prev) => ({ ...prev, [name]: value }));

    // Re-validate the changed field if it has already been touched
    setTouched((prev) => {
      if (prev[name]) {
        setErrors((prevErrors) => ({
          ...prevErrors,
          [name]: validateField(name, value),
        }));
      }
      return prev;
    });
  }, []);

  const handleBlur = useCallback((event) => {
    const { name, value } = event.target;

    setTouched((prev) => ({ ...prev, [name]: true }));
    setErrors((prev) => ({ ...prev, [name]: validateField(name, value) }));
  }, []);

  const handleSubmit = useCallback(
    async (event) => {
      if (event && event.preventDefault) event.preventDefault();

      // Mark all fields as touched and validate everything
      const allTouched = Object.keys(values).reduce((acc, key) => {
        acc[key] = true;
        return acc;
      }, {});
      setTouched(allTouched);

      const allErrors = validateAll(values);
      setErrors(allErrors);

      const hasErrors = Object.values(allErrors).some((e) => e !== '');
      if (hasErrors) return;

      if (typeof onSubmit !== 'function') return;

      setIsSubmitting(true);
      try {
        await onSubmit({ email: values.email.trim(), password: values.password });
      } finally {
        setIsSubmitting(false);
      }
    },
    [values, onSubmit]
  );

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors(initialErrors);
    setTouched(initialTouched);
    setIsSubmitting(false);
  }, []);

  return {
    values,
    errors,
    touched,
    isValid,
    isSubmitting,
    handleChange,
    handleBlur,
    handleSubmit,
    reset,
  };
}

export default useLoginForm;
