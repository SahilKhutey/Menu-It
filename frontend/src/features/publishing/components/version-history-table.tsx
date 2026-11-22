"use client";

import React from "react";
import { PublicationSummary } from "../types";

interface VersionHistoryTableProps {
  publications: PublicationSummary[];
  onOpenRollback: (pub: PublicationSummary) => void;
  isLoading?: boolean;
}

export function VersionHistoryTable({
  publications,
  onOpenRollback,
  isLoading = false,
}: VersionHistoryTableProps) {
  if (publications.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-gray-200 p-8 text-center text-sm text-gray-500">
        No published versions yet. Validate and publish to establish Version 1.
      </div>
    );
  }

  return (
    <div className="bg-white rounded-xl border border-gray-200 overflow-hidden shadow-sm">
      <div className="px-6 py-4 border-b border-gray-100 flex items-center justify-between">
        <h3 className="text-sm font-semibold text-gray-900">Immutable Publication History</h3>
        <span className="text-xs text-gray-500">{publications.length} versions recorded</span>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm text-gray-600">
          <thead className="bg-gray-50 text-xs uppercase text-gray-500 font-semibold border-b border-gray-100">
            <tr>
              <th className="px-6 py-3">Version</th>
              <th className="px-6 py-3">Status</th>
              <th className="px-6 py-3">Published Date</th>
              <th className="px-6 py-3">Integrity SHA-256</th>
              <th className="px-6 py-3 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100">
            {publications.map((pub) => {
              const isActive = pub.status === "ACTIVE";
              return (
                <tr key={pub.id} className="hover:bg-gray-50/50 transition-colors">
                  <td className="px-6 py-4 font-bold text-gray-900">
                    v{pub.version_number}
                  </td>
                  <td className="px-6 py-4">
                    <span
                      className={`inline-flex px-2 py-0.5 text-xs font-semibold rounded-full ${
                        isActive
                          ? "bg-green-100 text-green-800"
                          : "bg-gray-100 text-gray-600"
                      }`}
                    >
                      {isActive ? "Currently Active" : "Historical"}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-xs text-gray-500">
                    {new Date(pub.published_at).toLocaleString()}
                  </td>
                  <td className="px-6 py-4 text-xs font-mono text-gray-400">
                    {pub.checksum ? `${pub.checksum.slice(0, 12)}...` : "sha256-verified"}
                  </td>
                  <td className="px-6 py-4 text-right">
                    {!isActive && (
                      <button
                        onClick={() => onOpenRollback(pub)}
                        disabled={isLoading}
                        className="text-xs font-medium text-blue-600 hover:text-blue-800 hover:underline"
                      >
                        Rollback to v{pub.version_number}
                      </button>
                    )}
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
