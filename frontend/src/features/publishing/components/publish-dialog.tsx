"use client";

import React, { useState } from "react";

interface PublishDialogProps {
  isOpen: boolean;
  menuTitle: string;
  draftRevision: number;
  currentActiveVersion: number | null;
  onConfirm: (reason: string) => Promise<void>;
  onClose: () => void;
}

export function PublishDialog({
  isOpen,
  menuTitle,
  draftRevision,
  currentActiveVersion,
  onConfirm,
  onClose,
}: PublishDialogProps) {
  const [reason, setReason] = useState("");
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (!isOpen) return null;

  const handlePublish = async () => {
    setIsSubmitting(true);
    setError(null);
    try {
      await onConfirm(reason);
      onClose();
    } catch (err: any) {
      setError(err?.message || "Failed to publish menu");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 backdrop-blur-sm p-4">
      <div className="bg-white rounded-2xl max-w-md w-full p-6 shadow-xl border border-gray-100 animate-in fade-in zoom-in-95 duration-150">
        <h3 className="text-lg font-bold text-gray-900">Publish Menu Version</h3>
        <p className="text-sm text-gray-500 mt-1">
          You are about to publish an immutable snapshot of <strong>{menuTitle}</strong>.
        </p>

        <div className="my-4 p-3 bg-blue-50 border border-blue-100 rounded-lg text-xs text-blue-900 space-y-1">
          <p>• <strong>Draft revision:</strong> #{draftRevision}</p>
          <p>• <strong>Current active version:</strong> {currentActiveVersion ? `v${currentActiveVersion}` : "None"}</p>
          <p>• <strong>New public version:</strong> {currentActiveVersion ? `v${currentActiveVersion + 1}` : "v1"}</p>
        </div>

        {error && (
          <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 text-xs rounded-lg">
            {error}
          </div>
        )}

        <div className="mb-4">
          <label className="block text-xs font-semibold text-gray-700 mb-1">
            Publication Note / Change Log (Optional)
          </label>
          <textarea
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="e.g., Seasonal price adjustments and autumn tasting dishes added"
            className="w-full text-sm border border-gray-300 rounded-lg p-2 focus:ring-2 focus:ring-blue-500 focus:outline-none"
            rows={3}
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
            onClick={handlePublish}
            disabled={isSubmitting}
            className="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-sm transition-colors"
          >
            {isSubmitting ? "Publishing..." : "Confirm & Publish"}
          </button>
        </div>
      </div>
    </div>
  );
}
