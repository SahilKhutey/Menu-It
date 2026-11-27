import React, { type InputHTMLAttributes, useId } from 'react';
import './input.css';

export interface InputProps extends InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  hint?: string;
}

export function Input({ label, error, hint, id, className, disabled, ...props }: InputProps) {
  const reactGeneratedId = useId();
  const inputId = id ?? `field-${reactGeneratedId}`;
  const hintId = hint ? `${inputId}-hint` : undefined;
  const errorId = error ? `${inputId}-error` : undefined;
  const describedBy = [hintId, errorId].filter(Boolean).join(' ') || undefined;

  return (
    <div className={['ui-field', disabled ? 'ui-field--disabled' : ''].filter(Boolean).join(' ')}>
      {label && (
        <label className="ui-field__label" htmlFor={inputId}>
          {label}
        </label>
      )}
      <input
        {...props}
        id={inputId}
        disabled={disabled}
        className={['ui-input', error ? 'ui-input--error' : '', className]
          .filter(Boolean)
          .join(' ')}
        aria-invalid={error ? true : undefined}
        aria-describedby={describedBy}
      />
      {hint && !error && (
        <p className="ui-field__hint" id={hintId}>
          {hint}
        </p>
      )}
      {error && (
        <p className="ui-field__error" id={errorId} role="alert">
          {error}
        </p>
      )}
    </div>
  );
}
