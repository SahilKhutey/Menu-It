/**
 * Platform notification types and in-app models (FCD-09 WP-10).
 */

export type NotificationChannel = 'email' | 'in_app';

export type NotificationStatus =
  'pending' | 'accepted' | 'sent' | 'delivered' | 'failed' | 'cancelled';

export interface InAppNotification {
  id: string;
  type: string;
  title: string;
  body: string;
  read_at: string | null;
  created_at: string;
}
