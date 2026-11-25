import type { Metadata, Viewport } from 'next';
import '@menu-it/design-tokens/index.css';
import './globals.css';
import { ThemeProvider } from '@menu-it/theme-engine';

export const metadata: Metadata = {
  title: {
    default: 'Menu-It',
    template: '%s | Menu-It',
  },
  description: 'A modern restaurant discovery and dining experience.',
  applicationName: 'Menu-It',
  appleWebApp: {
    capable: true,
    statusBarStyle: 'default',
    title: 'Menu-It',
  },
};

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  viewportFit: 'cover',
  themeColor: '#ffffff',
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider defaultMode="system">
          <main>{children}</main>
        </ThemeProvider>
      </body>
    </html>
  );
}
