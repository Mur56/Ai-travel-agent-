import React from 'react';
import './Loading.css';

interface LoadingProps {
  size?: 'small' | 'medium' | 'large';
  color?: string;
  className?: string;
  message?: string;
}

const Loading: React.FC<LoadingProps> = ({
  size = 'medium',
  color = 'currentColor',
  className = '',
  message
}) => {
  const sizeMap = {
    small: 16,
    medium: 24,
    large: 32
  };

  return (
    <div className={`loading-container ${className}`}>
      <svg
        className="loading-spinner"
        width={sizeMap[size]}
        height={sizeMap[size]}
        viewBox="0 0 24 24"
        fill="none"
        stroke={color}
        strokeWidth="2"
      >
        <circle
          className="loading-circle"
          cx="12"
          cy="12"
          r="10"
          strokeDasharray="42"
          strokeLinecap="round"
        />
      </svg>
      {message && <span className="loading-message">{message}</span>}
    </div>
  );
};

export default Loading;