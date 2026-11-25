/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  transpilePackages: [
    '@menu-it/shared-types',
    '@menu-it/design-tokens',
    '@menu-it/theme-engine',
    '@menu-it/ui',
  ],
};

export default nextConfig;
