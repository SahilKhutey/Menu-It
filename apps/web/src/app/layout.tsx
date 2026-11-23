import type { Metadata, Viewport } from 'next';
import './globals.css';

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
    <html lang="en">
      <body>
        <main>{children}</main>
      </body>
    </html>
  );
}
