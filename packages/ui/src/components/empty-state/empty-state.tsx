import * as React from 'react';
import './empty-state.css';

export interface EmptyStateProps extends React.HTMLAttributes<HTMLDivElement> {
  icon?: React.ReactNode;
  title: string;
  description?: string;
  action?: React.ReactNode;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon,
  title,
  description,
  action,
  className = '',
  ...props
}) => {
  return (
    <div className={`menu-it-empty-state ${className}`} role="status" {...props}>
      {icon && <div className="menu-it-empty-state__icon">{icon}</div>}
      <h3 className="menu-it-empty-state__title">{title}</h3>
      {description && <p className="menu-it-empty-state__description">{description}</p>}
      {action && <div className="menu-it-empty-state__action">{action}</div>}
    </div>
  );
};
