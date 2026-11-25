'use client';

import React, { useEffect, useId, useRef, type HTMLAttributes, type ReactNode } from 'react';
import './dialog.css';

export interface DialogProps {
  open: boolean;
  onClose: () => void;
  title: string;
  description?: string;
  children: ReactNode;
  className?: string;
}

export function Dialog({ open, onClose, title, description, children, className }: DialogProps) {
  const titleId = useId();
  const descId = useId();
  const dialogRef = useRef<HTMLDivElement>(null);

  // Close on Escape key
  useEffect(() => {
    if (!open) return;
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [open, onClose]);

  // Trap focus & lock background scrolling
  useEffect(() => {
    if (!open) return;
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    dialogRef.current?.focus();
    return () => {
      document.body.style.overflow = originalOverflow;
    };
  }, [open]);

  if (!open) return null;

  return (
    <div
      className="ui-dialog-backdrop"
      onClick={(e) => {
        if (e.target === e.currentTarget) {
          onClose();
        }
      }}
    >
      <div
        ref={dialogRef}
        role="dialog"
        aria-modal="true"
        aria-labelledby={titleId}
        aria-describedby={description ? descId : undefined}
        tabIndex={-1}
        className={['ui-dialog', className].filter(Boolean).join(' ')}
      >
        <div className="ui-dialog__header">
          <div className="ui-dialog__titles">
            <h2 id={titleId} className="ui-dialog__title">
              {title}
            </h2>
            {description && (
              <p id={descId} className="ui-dialog__description">
                {description}
              </p>
            )}
          </div>
          <button
            type="button"
            className="ui-dialog__close"
            onClick={onClose}
            aria-label="Close dialog"
          >
            ×
          </button>
        </div>
        <div className="ui-dialog__body">{children}</div>
      </div>
    </div>
  );
}

export function DialogFooter({ children, className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div className={['ui-dialog__footer', className].filter(Boolean).join(' ')} {...props}>
      {children}
    </div>
  );
}
