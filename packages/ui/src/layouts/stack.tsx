import React, { type HTMLAttributes } from 'react';
import './stack.css';

export interface StackProps extends HTMLAttributes<HTMLDivElement> {
  gap?: 'none' | 'xs' | 'sm' | 'md' | 'lg' | 'xl';
  align?: 'start' | 'center' | 'end' | 'stretch';
  direction?: 'vertical' | 'horizontal';
  wrap?: boolean;
}

export function Stack({
  gap = 'md',
  align = 'stretch',
  direction = 'vertical',
  wrap = false,
  className,
  ...props
}: StackProps) {
  const classes = [
    'ui-stack',
    `ui-stack--${direction}`,
    `ui-stack--gap-${gap}`,
    `ui-stack--align-${align}`,
    wrap ? 'ui-stack--wrap' : '',
    className,
  ]
    .filter(Boolean)
    .join(' ');

  return <div className={classes} {...props} />;
}
