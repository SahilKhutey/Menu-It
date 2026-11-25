import React, { type ImgHTMLAttributes } from 'react';
import './avatar.css';

export interface AvatarProps extends ImgHTMLAttributes<HTMLImageElement> {
  name: string;
  size?: 'sm' | 'md' | 'lg';
}

function getInitials(name: string): string {
  const parts = name.trim().split(/\s+/);
  if (parts.length === 0 || !parts[0]) return '?';
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase();
  const first = parts[0][0] ?? '';
  const second = parts[1]?.[0] ?? '';
  return `${first}${second}`.toUpperCase();
}

export function Avatar({ name, size = 'md', src, alt, className, ...props }: AvatarProps) {
  const [hasError, setHasError] = React.useState(!src);

  return (
    <div
      className={['ui-avatar', `ui-avatar--${size}`, className].filter(Boolean).join(' ')}
      aria-label={alt ?? name}
    >
      {src && !hasError ? (
        <img
          {...props}
          src={src}
          alt={alt ?? name}
          className="ui-avatar__img"
          onError={() => setHasError(true)}
        />
      ) : (
        <span className="ui-avatar__fallback" aria-hidden="true">
          {getInitials(name)}
        </span>
      )}
    </div>
  );
}
