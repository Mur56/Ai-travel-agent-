import React from 'react';
import './Input.css';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  icon?: React.ReactNode;
  helperText?: string;
  variant?: 'default' | 'filled' | 'outlined';
}

const Input = React.forwardRef<HTMLInputElement, InputProps>((
  {
    label,
    error,
    icon,
    helperText,
    variant = 'default',
    className = '',
    disabled,
    ...props
  },
  ref
) => {
  const inputId = React.useId();
  
  return (
    <div className={`input-wrapper ${className}`}>
      {label && (
        <label 
          htmlFor={inputId}
          className="input-label"
        >
          {label}
        </label>
      )}
      
      <div className={`input-container input-${variant} ${error ? 'has-error' : ''} ${disabled ? 'disabled' : ''}`}>
        {icon && <span className="input-icon">{icon}</span>}
        <input
          ref={ref}
          id={inputId}
          className={`input-field ${icon ? 'has-icon' : ''}`}
          disabled={disabled}
          {...props}
        />
      </div>

      {(error || helperText) && (
        <span className={`input-message ${error ? 'error' : 'helper'}`}>
          {error || helperText}
        </span>
      )}
    </div>
  );
});

Input.displayName = 'Input';

export default Input;