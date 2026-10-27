/**
 * API Client and Data Adapter for Instagram Demo Feed.
 * Supplies the 90-post extended demo feed with 3 images per post
 * and deterministic cursor-based pagination.
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const AUTH_TOKEN_KEY = 'ig_auth_token';
export const AUTH_USER_KEY = 'ig_auth_user';

export function getAuthToken() {
  try {
    return localStorage.getItem(AUTH_TOKEN_KEY);
  } catch {
    return null;
  }
}

export function getStoredUser() {
  try {
    const raw = localStorage.getItem(AUTH_USER_KEY);
    return raw ? JSON.parse(raw) : null;
  } catch {
    return null;
  }
}

export function setAuthSession(token, user) {
  try {
    if (token) {
      localStorage.setItem(AUTH_TOKEN_KEY, token);
    }
    if (user) {
      localStorage.setItem(AUTH_USER_KEY, JSON.stringify(user));
    }
  } catch (e) {
    console.error('Failed to save auth session:', e);
  }
}

export function clearAuthSession() {
  try {
    localStorage.removeItem(AUTH_TOKEN_KEY);
    localStorage.removeItem(AUTH_USER_KEY);
  } catch (e) {
    console.error('Failed to clear auth session:', e);
  }
}

export function getAuthHeaders() {
  const token = getAuthToken();
  const headers = { 'Accept': 'application/json' };
  if (token) {
    headers['Authorization'] = `Bearer ${token}`;
  }
  return headers;
}

/**
 * Signs in with handle and password.
 */
export async function loginApi({ handle, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      handle: handle.trim().toLowerCase(),
      password,
    }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const msg = data?.error?.message || data?.detail || `Sign in failed (${response.status})`;
    throw new Error(msg);
  }

  setAuthSession(data.accessToken, data.user);
  return data;
}

/**
 * Registers a new account.
 */
export async function registerApi({ handle, displayName, password }) {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    },
    body: JSON.stringify({
      handle: handle.trim().toLowerCase(),
      displayName: displayName.trim(),
      password,
    }),
  });

  const data = await response.json().catch(() => ({}));
  if (!response.ok) {
    const msg = data?.error?.message || data?.detail || `Sign up failed (${response.status})`;
    throw new Error(msg);
  }

  setAuthSession(data.accessToken, data.user);
  return data;
}

/**
 * Logs out and invalidates session token.
 */
export async function logoutApi() {
  const token = getAuthToken();
  if (token) {
    try {
      await fetch(`${API_BASE_URL}/auth/logout`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Accept': 'application/json',
        },
      });
    } catch (e) {
      console.warn('Logout API warning:', e);
    }
  }
  clearAuthSession();
}

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

  let category = item.category || 'Explore';
  const handle = (item.author?.handle || item.username || '').toLowerCase();
  const text = (item.text || item.caption || '').toLowerCase();
  if (handle === 'deepu' || text.includes('food') || text.includes('pasta') || text.includes('burger') || text.includes('ramen')) {
    category = 'Food';
  } else if (handle === 'sneha' || text.includes('flower') || text.includes('tulip') || text.includes('rose') || text.includes('peon')) {
    category = 'Flowers';
  } else if (handle === 'asha' || text.includes('book') || text.includes('study') || text.includes('read') || text.includes('library')) {
    category = 'Books & Study';
  } else if (handle === 'ani' || text.includes('music') || text.includes('guitar') || text.includes('piano') || text.includes('synth')) {
    category = 'Music';
  } else if (handle === 'virat' || text.includes('cricket') || text.includes('stadium') || text.includes('bat') || text.includes('pitch')) {
    category = 'Cricket';
  }

  return {
    ...item,
    id: item.id,
    kind: item.kind || 'original',
    text: item.text || item.caption || '',
    caption: item.caption || item.text || '',
    category: category,
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
    likerHandles: item.likerHandles || item.likers || [],
    comments: item.comments ?? item.replyCount ?? 0,
    replyCount: item.comments ?? item.replyCount ?? 0,
    repostCount: item.repostCount ?? 0,
    authorId: item.author?.id || item.authorId || item.userId || null,
    followedByViewer: Boolean(item.author?.followedByViewer ?? item.followedByViewer ?? false),
    likedByViewer: item.likedByViewer ?? false,
    repostedByViewer: Boolean(item.repostedByViewer ?? false),
    replyToId: item.replyToId || null,
    repostOfId: item.repostOfId || null,
    createdAt: item.createdAt,
    timeAgo: item.timeAgo || formatTimestamp(item.createdAt),
  };
}

/**
 * Sets or removes a repost on an original post via POST / DELETE on FastAPI backend.
 *
 * @param {string} postId - UUID of the original post.
 * @param {boolean} shouldRepost - True to repost (POST), false to undo (DELETE).
 * @returns {Promise<{ postId: string, repostedByViewer: boolean, repostCount: number }>}
 */
export async function toggleRepostApi(postId, shouldRepost) {
  const method = shouldRepost ? 'POST' : 'DELETE';
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/repost`, {
    method: method,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Repost action failed (${response.status})`);
  }

  return await response.json();
}

/**
 * Toggles follow state for a target user via PUT /users/{id}/follow or DELETE /users/{id}/follow.
 *
 * @param {string} userId - UUID of target user to follow/unfollow.
 * @param {boolean} shouldFollow - True to follow, false to unfollow.
 * @returns {Promise<{ userId: string, followedByViewer: boolean, followerCount: number }>}
 */
export async function toggleFollowApi(userId, shouldFollow) {
  const method = shouldFollow ? 'PUT' : 'DELETE';
  const response = await fetch(`${API_BASE_URL}/users/${userId}/follow`, {
    method: method,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Follow action failed (${response.status})`);
  }

  return await response.json();
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

export const formatRelativeTime = formatTimestamp;

/**
 * Fetches paginated feed from FastAPI backend /feed endpoint.
 *
 * @param {string|null} cursor - Opaque cursor token from previous page.
 * @param {number} limit - Number of items to fetch (1..50).
 * @returns {Promise<{ items: Array, nextCursor: string|null, hasMore: boolean, requestId: string|null }>}
 */
export async function fetchFeedFromApi(cursor = null, limit = 10) {
  const url = new URL(`${API_BASE_URL}/feed`);
  url.searchParams.set('limit', String(limit));
  if (cursor) {
    url.searchParams.set('cursor', cursor);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData?.error?.message || `Failed to fetch feed (${response.status})`;
    const err = new Error(message);
    err.requestId = response.headers.get('x-request-id') || errorData?.requestId;
    throw err;
  }

  const data = await response.json();
  const normalizedItems = (data.items || []).map(normalizePostItem);

  return {
    items: normalizedItems,
    nextCursor: data.nextCursor || null,
    hasMore: Boolean(data.hasMore),
    requestId: response.headers.get('x-request-id') || null,
  };
}

/**
 * Sets or removes a like on a post via desired-state PUT / DELETE on FastAPI backend.
 *
 * @param {string} postId - UUID of the post.
 * @param {boolean} shouldLike - True to like (PUT), false to unlike (DELETE).
 * @returns {Promise<{ postId: string, likedByViewer: boolean, likeCount: number }>}
 */
export async function toggleLikeApi(postId, shouldLike) {
  const method = shouldLike ? 'PUT' : 'DELETE';
  const response = await fetch(`${API_BASE_URL}/posts/${postId}/like`, {
    method: method,
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Like action failed (${response.status})`);
  }

  return await response.json();
}

/**
 * Fetches paginated direct replies for a given original post.
 *
 * @param {string} postId - UUID of the original post.
 * @param {string|null} cursor - Optional cursor for reply pagination.
 * @param {number} limit - Number of replies to fetch.
 * @returns {Promise<{ items: Array, nextCursor: string|null, hasMore: boolean }>}
 */
export async function fetchRepliesApi(postId, cursor = null, limit = 20) {
  const url = new URL(`${API_BASE_URL}/posts/${postId}/replies`);
  url.searchParams.set('limit', String(limit));
  if (cursor) {
    url.searchParams.set('cursor', cursor);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: {
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    return { items: [], nextCursor: null, hasMore: false };
  }

  const data = await response.json();
  return {
    items: (data.items || []).map(normalizePostItem),
    nextCursor: data.nextCursor || null,
    hasMore: Boolean(data.hasMore),
  };
}

/**
 * Creates a new reply (comment) attached to an existing post via POST /posts on FastAPI.
 *
 * @param {string} postId - UUID of the parent post.
 * @param {string} text - Comment text (1..280 chars).
 * @returns {Promise<Object>}
 */
export async function createReplyApi(postId, text) {
  const headers = {
    'Content-Type': 'application/json',
    ...getAuthHeaders(),
  };

  const response = await fetch(`${API_BASE_URL}/posts`, {
    method: 'POST',
    headers: headers,
    body: JSON.stringify({
      kind: 'reply',
      text: text,
      replyToId: postId,
    }),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Failed to post comment (${response.status})`);
  }

  const data = await response.json();
  return normalizePostItem(data.item);
}

/**
 * Fetches a single post detail by ID from FastAPI GET /posts/{id} endpoint.
 *
 * @param {string} postId - UUID of the post.
 * @returns {Promise<Object>}
 */
export async function fetchPostDetailApi(postId) {
  const response = await fetch(`${API_BASE_URL}/posts/${postId}`, {
    method: 'GET',
    headers: {
      ...getAuthHeaders(),
      'Accept': 'application/json',
    },
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData?.error?.message || `Failed to fetch post detail (${response.status})`);
  }

  const data = await response.json();
  return normalizePostItem(data.item);
}

/**
 * Fetches cursor-paginated notification inbox for current authenticated member.
 *
 * @param {string|null} cursor - Optional opaque pagination cursor token.
 * @param {number} limit - Page size (1..50).
 * @returns {Promise<{ items: Array, unreadCount: number, nextCursor: string|null, hasMore: boolean }>}
 */
export async function fetchNotificationsApi(cursor = null, limit = 20) {
  const url = new URL(`${API_BASE_URL}/notifications`);
  url.searchParams.set('limit', String(limit));
  if (cursor) {
    url.searchParams.set('cursor', cursor);
  }

  const response = await fetch(url.toString(), {
    method: 'GET',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    return { items: [], unreadCount: 0, nextCursor: null, hasMore: false };
  }

  const data = await response.json();
  return {
    items: data.items || [],
    unreadCount: data.unreadCount || 0,
    nextCursor: data.nextCursor || null,
    hasMore: Boolean(data.hasMore),
  };
}

/**
 * Marks all notifications as read for current authenticated member.
 *
 * @returns {Promise<{ markedCount: number, unreadCount: number }>}
 */
export async function markAllNotificationsReadApi() {
  const response = await fetch(`${API_BASE_URL}/notifications/read`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    return { markedCount: 0, unreadCount: 0 };
  }

  return await response.json();
}

/**
 * Marks single notification as read.
 *
 * @param {string} notificationId - UUID of the notification.
 * @returns {Promise<{ markedCount: number, unreadCount: number }>}
 */
export async function markSingleNotificationReadApi(notificationId) {
  const response = await fetch(`${API_BASE_URL}/notifications/${notificationId}/read`, {
    method: 'POST',
    headers: getAuthHeaders(),
  });

  if (!response.ok) {
    return { markedCount: 0, unreadCount: 0 };
  }

  return await response.json();
}

/**
 * Searches original posts across all profiles by caption, hashtags (#), author handle (@), display name, or bio.
 *
 * @param {string} query - Search string (e.g. '#waffles', 'waffles', '#cricket', 'flowers', 'gourmet', 'deepu').
 * @param {number} limit - Maximum number of posts to fetch (defaults to 60).
 * @returns {Promise<Array>} Normalized post items.
 */
export async function searchPostsApi(query, limit = 60) {
  if (!query || !query.trim()) return [];
  const cleanQ = query.trim();

  // FastAPI backend requires limit between 1 and 50 per request
  const fetchLimit = Math.min(Math.max(1, limit), 50);
  const url = new URL(`${API_BASE_URL}/search/posts`);
  url.searchParams.set('q', cleanQ);
  url.searchParams.set('limit', String(fetchLimit));

  try {
    const response = await fetch(url.toString(), {
      method: 'GET',
      headers: {
        ...getAuthHeaders(),
        'Accept': 'application/json',
      },
    });

    if (!response.ok) {
      console.warn(`Search API returned status ${response.status}`);
      return [];
    }

    const data = await response.json();
    let allItems = (data.items || []).map(normalizePostItem);

    // If caller requested more than 50 (e.g. 60) and more items exist, fetch second page
    if (limit > 50 && data.hasMore && data.nextCursor) {
      try {
        const page2Url = new URL(`${API_BASE_URL}/search/posts`);
        page2Url.searchParams.set('q', cleanQ);
        page2Url.searchParams.set('limit', String(Math.min(limit - 50, 50)));
        page2Url.searchParams.set('cursor', data.nextCursor);

        const res2 = await fetch(page2Url.toString(), {
          method: 'GET',
          headers: {
            ...getAuthHeaders(),
            'Accept': 'application/json',
          },
        });
        if (res2.ok) {
          const data2 = await res2.json();
          const items2 = (data2.items || []).map(normalizePostItem);
          allItems = [...allItems, ...items2];
        }
      } catch (err2) {
        console.warn('Failed to fetch subsequent search page:', err2);
      }
    }

    return allItems;
  } catch (err) {
    console.error('Search API request failed:', err);
    return [];
  }
}


