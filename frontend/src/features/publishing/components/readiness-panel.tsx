"use client";

import React from "react";
import { ValidationReport } from "../types";

interface ReadinessPanelProps {
  ready: boolean;
  activeVersion: number | null;
  report: ValidationReport | null;
  onValidate: () => void;
  onOpenPublish: () => void;
  isLoading?: boolean;
}

export function ReadinessPanel({
  ready,
  activeVersion,
  report,
  onValidate,
  onOpenPublish,
  isLoading = false,
}: ReadinessPanelProps) {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-6 shadow-sm">
      <div className="flex items-center justify-between border-b border-gray-100 pb-4 mb-4">
        <div>
          <span className="text-xs font-semibold tracking-wider text-gray-500 uppercase">
            Publication Status
          </span>
          <div className="flex items-center gap-3 mt-1">
            <span
              className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                activeVersion ? "bg-green-100 text-green-800" : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {activeVersion ? `Published · v${activeVersion}` : "Unpublished Draft"}
            </span>
            <span className="text-sm text-gray-600">
              Readiness:{" "}
              <strong className={ready ? "text-green-600" : "text-red-600"}>
                {ready ? "Ready to Publish" : "Action Required"}
              </strong>
            </span>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={onValidate}
            disabled={isLoading}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-50 hover:bg-gray-100 border border-gray-300 rounded-lg transition-colors"
          >
            Re-validate Draft
          </button>
          <button
            onClick={onOpenPublish}
            disabled={!ready || isLoading}
            className="px-5 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed rounded-lg shadow-sm transition-colors"
          >
            Publish New Version
          </button>
        </div>
      </div>

      {report && (
        <div className="grid grid-cols-3 gap-4 pt-2">
          <div className="p-3 bg-gray-50 rounded-lg">
            <span className="text-xs text-gray-500 font-medium">Validation Result</span>
            <p className="text-base font-bold text-gray-900 mt-0.5">{report.result}</p>
          </div>
          <div className="p-3 bg-red-50 rounded-lg">
            <span className="text-xs text-red-600 font-medium">Blocking Errors</span>
            <p className="text-base font-bold text-red-700 mt-0.5">{report.errors.length}</p>
          </div>
          <div className="p-3 bg-yellow-50 rounded-lg">
            <span className="text-xs text-yellow-600 font-medium">Warnings</span>
            <p className="text-base font-bold text-yellow-700 mt-0.5">{report.warnings.length}</p>
          </div>
        </div>
      )}
    </div>
  );
}
