import type { Metadata, Viewport } from 'next';
import '@menu-it/design-tokens/index.css';
import './globals.css';
import { ThemeProvider } from '@menu-it/theme-engine';

export const metadata: Metadata = {
  title: {
    default: 'Menu-It Administration',
    template: '%s | Menu-It Admin',
  },
  description: 'Menu-It platform administration.',
  robots: {
    index: false,
    follow: false,
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
};

export default function AdminRootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider defaultMode="system">{children}</ThemeProvider>
      </body>
    </html>
  );
}
