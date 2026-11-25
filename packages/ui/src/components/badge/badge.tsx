import React, { type HTMLAttributes, type ReactNode } from 'react';
import './badge.css';

export type BadgeVariant =
  'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'outline';
export type BadgeSize = 'sm' | 'md';

export interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  children: ReactNode;
  variant?: BadgeVariant;
  size?: BadgeSize;
}

export function Badge({
  children,
  variant = 'default',
  size = 'md',
  className,
  ...props
}: BadgeProps) {
  return (
    <span
      className={['ui-badge', `ui-badge--${variant}`, `ui-badge--${size}`, className]
        .filter(Boolean)
        .join(' ')}
      {...props}
    >
      {children}
    </span>
  );
}
