"use client";

import React, { useCallback, useEffect, useState } from "react";
import {
  getPublicationReadiness,
  listPublications,
  publishMenu,
  rollbackPublication,
  validateMenuDraft,
} from "@/features/publishing/services/publishing-service";
import {
  PublicationSummary,
  ValidationReport,
} from "@/features/publishing/types";
import { ReadinessPanel } from "@/features/publishing/components/readiness-panel";
import { ValidationReportView } from "@/features/publishing/components/validation-report";
import { VersionHistoryTable } from "@/features/publishing/components/version-history-table";
import { PublishDialog } from "@/features/publishing/components/publish-dialog";
import { RollbackDialog } from "@/features/publishing/components/rollback-dialog";

export default function PublishingPage({ params }: { params: { menuId: string } }) {
  const { menuId } = params;

  const [isLoading, setIsLoading] = useState(true);
  const [report, setReport] = useState<ValidationReport | null>(null);
  const [publications, setPublications] = useState<PublicationSummary[]>([]);
  const [isPublishOpen, setIsPublishOpen] = useState(false);
  const [rollbackTarget, setRollbackTarget] = useState<PublicationSummary | null>(null);

  const loadData = useCallback(async () => {
    setIsLoading(true);
    try {
      const [validationData, pubList] = await Promise.all([
        validateMenuDraft(menuId, 1),
        listPublications(menuId),
      ]);
      setReport(validationData);
      setPublications(pubList);
    } catch (err) {
      console.error("Error loading publishing data:", err);
    } finally {
      setIsLoading(false);
    }
  }, [menuId]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const activePub = publications.find((p) => p.status === "ACTIVE");
  const isReady = report?.result === "PASSED" || report?.result === "WARNING";

  const handlePublishConfirm = async (reason: string) => {
    await publishMenu(menuId, {
      draft_revision: 1,
      expected_active_publication_id: activePub?.id || null,
      reason,
    });
    await loadData();
  };

  const handleRollbackConfirm = async (reason: string) => {
    if (!rollbackTarget) return;
    await rollbackPublication(menuId, rollbackTarget.id, {
      target_publication_id: rollbackTarget.id,
      expected_active_publication_id: activePub?.id || null,
      reason,
    });
    await loadData();
  };

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-8">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Menu Publishing & Version Control</h1>
        <p className="text-sm text-gray-500 mt-1">
          Manage publication readiness, generate immutable snapshots, and control public releases.
        </p>
      </div>

      <ReadinessPanel
        ready={isReady}
        activeVersion={activePub ? activePub.version_number : null}
        report={report}
        onValidate={loadData}
        onOpenPublish={() => setIsPublishOpen(true)}
        isLoading={isLoading}
      />

      {report && <ValidationReportView report={report} />}

      <VersionHistoryTable
        publications={publications}
        onOpenRollback={(pub) => setRollbackTarget(pub)}
        isLoading={isLoading}
      />

      <PublishDialog
        isOpen={isPublishOpen}
        menuTitle="Menu"
        draftRevision={1}
        currentActiveVersion={activePub ? activePub.version_number : null}
        onConfirm={handlePublishConfirm}
        onClose={() => setIsPublishOpen(false)}
      />

      <RollbackDialog
        isOpen={Boolean(rollbackTarget)}
        targetPublication={rollbackTarget}
        onConfirm={handleRollbackConfirm}
        onClose={() => setRollbackTarget(null)}
      />
    </div>
  );
}
