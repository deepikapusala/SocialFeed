/**
 * API Client and Data Adapter for Instagram Demo Feed.
 * Supplies the 90-post extended demo feed with 3 images per post
 * and deterministic cursor-based pagination.
 */

import { getExtendedDemoFeedPage } from '../data/extendedFeed';

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

/**
 * Normalizes a PostItem into a UI-friendly post object.
 * Ensures every post preserves its exact 3-image media array.
 */
export function normalizePostItem(item) {
  if (!item) return null;

  const mediaList = Array.isArray(item.media) ? item.media : [];
  const images = mediaList.length > 0
    ? mediaList.map((m) => m.largeUrl || m.smallUrl).filter(Boolean)
    : (Array.isArray(item.images) ? item.images : (item.imageUrl ? [item.imageUrl] : []));

  const defaultAvatar = 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80';
  const avatarUrl = item.author?.avatar?.smallUrl || item.author?.avatar?.largeUrl || item.userAvatar || defaultAvatar;

  return {
    ...item,
    id: item.id,
    kind: item.kind || 'original',
    text: item.text || item.caption || '',
    caption: item.caption || item.text || '',
    category: item.category || 'Explore',
    username: item.author?.handle || item.username || 'user',
    displayName: item.author?.displayName || item.displayName || item.author?.handle || 'User',
    userAvatar: avatarUrl,
    author: item.author || null,
    media: mediaList,
    images: images,
    imageUrl: images.length > 0 ? images[0] : null,
    hasMedia: images.length > 0,
    alt: mediaList[0]?.altText || item.alt || item.text || 'Instagram post',
    likes: item.likeCount ?? item.likes ?? 0,
    likeCount: item.likeCount ?? item.likes ?? 0,
    replyCount: item.replyCount ?? 0,
    likedByViewer: item.likedByViewer ?? false,
    createdAt: item.createdAt,
    timeAgo: item.timeAgo || formatTimestamp(item.createdAt),
  };
}

/**
 * Formats an ISO 8601 UTC timestamp into a human-readable relative time or date string.
 */
export function formatTimestamp(isoString) {
  if (!isoString) return 'recently';
  try {
    const date = new Date(isoString);
    if (isNaN(date.getTime())) return 'recently';

    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffSecs = Math.floor(diffMs / 1000);
    const diffMins = Math.floor(diffSecs / 60);
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffDays > 30) {
      return date.toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' });
    }
    if (diffDays > 0) return `${diffDays}d ago`;
    if (diffHours > 0) return `${diffHours}h ago`;
    if (diffMins > 0) return `${diffMins}m ago`;
    return 'just now';
  } catch {
    return 'recently';
  }
}

/**
 * Fetches paginated feed containing 90 original posts, each with 3 media items.
 *
 * @param {string|null} cursor - Opaque cursor token from previous page.
 * @param {number} limit - Number of items to fetch (1..50).
 * @returns {Promise<{ items: Array, nextCursor: string|null, hasMore: boolean, requestId: string|null }>}
 */
export async function fetchFeedFromApi(cursor = null, limit = 10) {
  // Small simulated latency (50ms) for authentic smooth network pagination feel
  await new Promise((resolve) => setTimeout(resolve, 50));

  const page = getExtendedDemoFeedPage(cursor, limit);
  const normalizedItems = (page.items || []).map(normalizePostItem);

  return {
    items: normalizedItems,
    nextCursor: page.nextCursor,
    hasMore: page.hasMore,
    requestId: `demo-req-${Date.now()}`,
  };
}
