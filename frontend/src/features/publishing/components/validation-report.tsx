"use client";

import React from "react";
import { Diagnostic, ValidationReport } from "../types";

interface ValidationReportProps {
  report: ValidationReport;
}

export function ValidationReportView({ report }: ValidationReportProps) {
  const allDiagnostics: Diagnostic[] = [...report.errors, ...report.warnings];

  if (allDiagnostics.length === 0) {
    return (
      <div className="bg-green-50 border border-green-200 rounded-xl p-4 text-sm text-green-800">
        All publication criteria satisfied. Menu content, pricing, themes, and layouts are verified.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-gray-100 bg-gray-50">
        <h3 className="text-sm font-semibold text-gray-900">Pre-flight Validation Diagnostics</h3>
      </div>
      <ul className="divide-y divide-gray-100">
        {allDiagnostics.map((diag, idx) => (
          <li key={idx} className="p-4 flex items-start gap-3">
            <span
              className={`px-2 py-0.5 rounded text-xs font-semibold ${
                diag.severity === "ERROR"
                  ? "bg-red-100 text-red-800"
                  : "bg-yellow-100 text-yellow-800"
              }`}
            >
              {diag.severity}
            </span>
            <div className="flex-1">
              <p className="text-sm font-medium text-gray-900">{diag.message}</p>
              <div className="flex items-center gap-4 mt-1 text-xs text-gray-500">
                <span>Code: <code className="bg-gray-100 px-1 py-0.5 rounded">{diag.code}</code></span>
                <span>Path: <code className="bg-gray-100 px-1 py-0.5 rounded">{diag.path}</code></span>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
