import React, { type HTMLAttributes, type ReactNode } from 'react';
import './card.css';

export interface CardProps extends HTMLAttributes<HTMLDivElement> {
  children: ReactNode;
  padding?: 'none' | 'sm' | 'md' | 'lg';
  variant?: 'default' | 'muted' | 'outline';
}

export function Card({
  children,
  padding = 'md',
  variant = 'default',
  className,
  ...props
}: CardProps) {
  return (
    <div
      {...props}
      className={['ui-card', `ui-card--p-${padding}`, `ui-card--${variant}`, className]
        .filter(Boolean)
        .join(' ')}
    >
      {children}
    </div>
  );
}

export function CardHeader({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={['ui-card__header', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}

export function CardTitle({ children, className, ...props }: HTMLAttributes<HTMLHeadingElement>) {
  return (
    <h3 className={['ui-card__title', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </h3>
  );
}

export function CardContent({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={['ui-card__content', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}
