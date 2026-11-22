export function isApprovedMediaHost(url: string, approvedHosts: string[]): boolean {
  try {
    const parsed = new URL(url);
    return approvedHosts.some((host) => parsed.hostname === host || parsed.hostname.endsWith(`.${host}`));
  } catch {
    return false;
  }
}
