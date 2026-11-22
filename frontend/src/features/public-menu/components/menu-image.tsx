"use client";

import React, { useState } from "react";

interface MenuImageProps {
  src: string;
  alt: string;
  width?: number;
  height?: number;
  priority?: boolean;
  className?: string;
}

export function MenuImage({
  src,
  alt,
  width = 400,
  height = 300,
  priority = false,
  className = "menu-image",
}: MenuImageProps) {
  const [hasError, setHasError] = useState(false);

  if (hasError || !src) {
    return (
      <div
        className={`${className} menu-image--fallback flex items-center justify-center bg-zinc-100 text-zinc-400`}
        style={{ width: "100%", height: height ? `${height}px` : "200px" }}
        role="img"
        aria-label={alt || "Image unavailable"}
      >
        <span className="text-xs">No Photo</span>
      </div>
    );
  }

  return (
    <img
      src={src}
      alt={alt || "Menu presentation"}
      width={width}
      height={height}
      loading={priority ? "eager" : "lazy"}
      onError={() => setHasError(true)}
      className={`${className} object-cover w-full h-auto`}
      style={{ aspectRatio: `${width} / ${height}` }}
    />
  );
}
