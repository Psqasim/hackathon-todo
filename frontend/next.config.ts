import type { NextConfig } from "next";

const nextConfig: NextConfig = {
  // Output standalone for Docker deployment optimization
  // This creates a minimal .next/standalone directory with only required dependencies
  // Reduces Docker image size by 70-80% compared to full node_modules
  output: 'standalone',
};

export default nextConfig;
