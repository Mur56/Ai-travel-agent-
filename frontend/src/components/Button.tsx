import React from 'react';
import './Button.css';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'outline';
  size?: 'small' | 'medium' | 'large';
  isLoading?: boolean;
  icon?: React.ReactNode;
  fullWidth?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'medium',
  isLoading = false,
  icon,
  className = '',
  disabled,
  fullWidth = false,
  ...props
}) => {
  return (
    <button
      className={`button button-${variant} button-${size} ${isLoading ? 'loading' : ''} ${fullWidth ? 'full-width' : ''} ${className}`}
      disabled={isLoading || disabled}
      aria-busy={isLoading}
      {...props}
    >
      {isLoading ? (
        <span className="loading-spinner" aria-label="Loading" />
      ) : (
        <>
          {icon && <span className="button-icon">{icon}</span>}
          {children}
        </>
      )}
    </button>
  );
};

export default Button;