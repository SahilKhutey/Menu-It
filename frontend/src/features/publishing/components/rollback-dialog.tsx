"use client";

import React, { useState } from "react";
import { PublicationSummary } from "../types";

interface RollbackDialogProps {
  isOpen: boolean;
  targetPublication: PublicationSummary | null;
  onConfirm: (reason: string) => Promise<void>;
  onClose: () => void;
}

export function RollbackDialog({
  isOpen,
  targetPublication,
  onConfirm,
  onClose,
}: RollbackDialogProps) {
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen || !targetPublication) return null;

  const handleRollback = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await onConfirm(reason);
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to rollback publication");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-100 animate-in fade-in zoom-in-95 duration-150">
        <h3 className="text-lg font-bold text-gray-900">Rollback to Version {targetPublication.version_number}</h3>
        <p className="text-sm text-gray-500 mt-1">
          This will immediately reactivate historical snapshot <strong>v{targetPublication.version_number}</strong> for public visitors.
        </p>

        <div className="my-4 p-3 bg-amber-50 border border-amber-200 rounded-lg text-xs text-amber-900">
          <p className="font-semibold">⚠️ Non-Destructive Activation</p>
          <p className="mt-0.5">
            Rollback does not rewrite history or delete subsequent publications. It shifts the active publication pointer and logs an immutable audit event.
          </p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Rollback Reason (Mandatory for audit trail)
          </label>
          <input
            type="text"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g., Reverting temporary promotional pricing"
            className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-amber-500 focus:outline-none"
          />
        </div>

        <div className="flex justify-end gap-3 pt-2">
          <button
            onClick={onClose}
            disabled={isSubmitting}
            className="px-4 py-2 text-sm font-medium text-gray-700 hover:bg-gray-100 rounded-lg transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={handleRollback}
            disabled={isSubmitting || !reason.trim()}
            className="px-5 py-2 text-sm font-medium text-white bg-amber-600 hover:bg-amber-700 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors"
          >
            {isSubmitting ? "Restoring..." : `Reactivate v${targetPublication.version_number}`}
          </button>
        </div>
      </div>
    </div>
  );
}
