/**
 * Image helper utilities for responsive images.
 */

/**
 * Helper to build responsive srcset strings for image URLs that support width parameters.
 * @param {string} url - Base image URL
 * @returns {string} - Formatted srcset string
 */
export function getResponsiveSrcSet(url) {
  if (!url) return '';
  if (url.includes('unsplash.com')) {
    const baseUrl = url.split('&w=')[0].split('?')[0];
    return `${baseUrl}?auto=format&fit=crop&w=400&q=80 400w, ${baseUrl}?auto=format&fit=crop&w=800&q=80 800w, ${baseUrl}?auto=format&fit=crop&w=1200&q=80 1200w`;
  }
  return `${url} 1x`;
}
