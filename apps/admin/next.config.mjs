/** @type {import('next').NextConfig} */
const nextConfig = {
  ...(process.platform !== 'win32' || process.env.NEXT_OUTPUT_STANDALONE === 'true'
    ? { output: 'standalone' }
    : {}),
  reactStrictMode: true,
  transpilePackages: [
    '@menu-it/shared-types',
    '@menu-it/design-tokens',
    '@menu-it/theme-engine',
    '@menu-it/ui',
  ],
};

export default nextConfig;
