import React, { type HTMLAttributes } from 'react';
import './container.css';

export type ContainerSize = 'sm' | 'md' | 'lg' | 'xl' | 'full';

export interface ContainerProps extends HTMLAttributes<HTMLDivElement> {
  size?: ContainerSize;
}

export function Container({ size = 'xl', className, ...props }: ContainerProps) {
  const classes = ['ui-container', `ui-container--${size}`, className].filter(Boolean).join(' ');
  return <div className={classes} {...props} />;
}
