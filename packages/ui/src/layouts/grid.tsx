import React, { type CSSProperties, type HTMLAttributes } from 'react';
import './grid.css';

export interface GridProps extends HTMLAttributes<HTMLDivElement> {
  minColumnWidth?: string;
  gap?: 'sm' | 'md' | 'lg';
}

export function Grid({
  minColumnWidth = '16rem',
  gap = 'md',
  style,
  className,
  ...props
}: GridProps) {
  const gridStyle: CSSProperties = {
    '--grid-min-width': minColumnWidth,
    ...style,
  } as CSSProperties;

  return (
    <div
      className={['ui-grid', `ui-grid--${gap}`, className].filter(Boolean).join(' ')}
      style={gridStyle}
      {...props}
    />
  );
}
