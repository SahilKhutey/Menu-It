/**
 * Platform file service types and visibility contracts (FCD-09 WP-10).
 */

export type FileVisibility = 'public' | 'tenant_private' | 'user_private' | 'platform_private';

export type FileStatus = 'pending' | 'stored' | 'rejected' | 'failed' | 'deleted';

export interface FileMetadata {
  id: string;
  filename: string;
  mime_type: string;
  size_bytes: number;
  visibility: FileVisibility;
  status: FileStatus;
  created_at: string;
}
