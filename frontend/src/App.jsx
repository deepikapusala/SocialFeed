import React, { useState, useEffect, useCallback } from 'react';
import { TopBar } from './components/TopBar/TopBar';
import { PhotoGrid } from './components/PhotoGrid/PhotoGrid';
import { PhotoViewer } from './components/PhotoViewer/PhotoViewer';
import { AuthModal } from './components/AuthModal/AuthModal';
import { EditProfileModal } from './components/EditProfileModal/EditProfileModal';
import { CreatePostModal } from './components/CreatePostModal/CreatePostModal';
import { SuggestedProfiles } from './components/SuggestedProfiles/SuggestedProfiles';
import {
  fetchFeedFromApi,
  toggleFollowApi,
  fetchPostDetailApi,
  getStoredUser,
  logoutApi,
  searchPostsApi,
} from './utils/api';
import './App.css';

/**
 * Helper to extract post ID from URL path /p/:postId
 */
function getPostIdFromUrl() {
  const match = window.location.pathname.match(/^\/p\/([^/]+)/);
  return match ? match[1] : null;
}

/**
 * Root Application component.
 * Consumes the Stage A FastAPI /feed endpoint with opaque cursor pagination
 * and supports deep linking / URL routing (/p/:postId).
 */
export function App() {
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Authentication state
  const [currentUser, setCurrentUser] = useState(() => getStoredUser());
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isEditProfileModalOpen, setIsEditProfileModalOpen] = useState(false);
  const [isCreatePostModalOpen, setIsCreatePostModalOpen] = useState(false);

  // Search query & results state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState(null);
  const [isSearching, setIsSearching] = useState(false);

  // Map of followed author handles for synced UI
  const [followingMap, setFollowingMap] = useState({});

  // Theme state: 'dark' (pure black) vs 'light' (baby pink)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('app-theme') || 'dark';
  });

  // Synchronize followingMap from incoming posts
  useEffect(() => {
    if (currentUser) {
      const initialMap = {};
      posts.forEach((p) => {
        const handle = (p.username || p.author?.handle)?.toLowerCase();
        if (handle && p.followedByViewer !== undefined) {
          initialMap[handle] = p.followedByViewer;
        }
      });
      setFollowingMap((prev) => ({ ...initialMap, ...prev }));
    } else {
      setFollowingMap({});
    }
  }, [currentUser, posts]);

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  /**
   * Handle selecting a post and updating URL to /p/:postId.
   * Gracefully handles:
   * - Full post objects from clicking photo cards in feed
   * - Post IDs or notification items from clicking notifications or URL deep links
   * - Automatically resolves comments/replies to their parent post
   * - Enriches post with liker actor handle when clicked from like notification
   */
  const handleSelectPost = useCallback(async (postOrId, context = {}) => {
    if (!postOrId) return;

    let targetId = typeof postOrId === 'string' ? postOrId : postOrId.id;
    let postObj = typeof postOrId === 'object' ? { ...postOrId } : null;

    // If given post is a reply stub, resolve to parent post ID
    if (postObj?.kind === 'reply' && postObj.replyToId) {
      targetId = postObj.replyToId;
      postObj = null;
    }

    // 1. Look for existing full post in feed state
    let matchedPost = posts.find((p) => p.id === targetId);

    // 2. If not found or if the post is incomplete (missing images/media or author), fetch from backend
    if (!matchedPost || !matchedPost.images || matchedPost.images.length === 0 || !matchedPost.author) {
      try {
        const fetched = await fetchPostDetailApi(targetId);
        if (fetched) {
          // If fetched post is a reply, load its parent post
          if (fetched.kind === 'reply' && fetched.replyToId) {
            matchedPost = await fetchPostDetailApi(fetched.replyToId);
          } else {
            matchedPost = fetched;
          }
        }
      } catch (err) {
        console.warn('Could not fetch post detail:', err);
      }
    }

    const finalPost = matchedPost || postObj;
    if (finalPost) {
      // Enrich with liker information if this came from a like notification
      if (context.eventType === 'like' && context.actor?.handle) {
        const existingLikers = finalPost.likerHandles || [];
        if (!existingLikers.includes(context.actor.handle)) {
          finalPost.likerHandles = [context.actor.handle, ...existingLikers];
        }
        finalPost.topLiker = context.actor;
      }
      setSelectedPost(finalPost);

      const targetUrl = `/p/${finalPost.id}`;
      if (window.location.pathname !== targetUrl) {
        window.history.pushState({ postId: finalPost.id }, '', targetUrl);
      }
    }
  }, [posts]);

  /**
   * Handle closing post modal and reverting URL to /
   */
  const handleClosePost = useCallback(() => {
    setSelectedPost(null);
    if (window.location.pathname !== '/') {
      window.history.pushState({}, '', '/');
    }
  }, []);

  // Listen for browser Back / Forward buttons (popstate event)
  useEffect(() => {
    const handlePopState = async () => {
      const urlPostId = getPostIdFromUrl();
      if (urlPostId) {
        const matched = posts.find((p) => p.id === urlPostId);
        if (matched) {
          setSelectedPost(matched);
        } else {
          try {
            const detail = await fetchPostDetailApi(urlPostId);
            setSelectedPost(detail);
          } catch (err) {
            console.error('Failed to fetch post detail from URL:', err);
            setSelectedPost(null);
          }
        }
      } else {
        setSelectedPost(null);
      }
    };

    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, [posts]);

  /**
   * On initial page load: check if direct URL contains /p/:postId
   */
  useEffect(() => {
    const urlPostId = getPostIdFromUrl();
    if (urlPostId) {
      fetchPostDetailApi(urlPostId)
        .then((detail) => setSelectedPost(detail))
        .catch((err) => console.error('Failed to load initial post from URL:', err));
    }
  }, []);


  /**
   * Toggle follow state for an author across all posts and sidebar synchronously.
   */
  const handleToggleFollow = useCallback(async ({ authorId, authorHandle, shouldFollow }) => {
    // 0. If user is not logged in (default page), redirect to sign in / sign up!
    if (!currentUser) {
      setIsAuthModalOpen(true);
      return;
    }

    // 1. Update followingMap immediately
    if (authorHandle) {
      setFollowingMap((prev) => ({
        ...prev,
        [authorHandle.toLowerCase()]: shouldFollow,
      }));
    }

    // 2. Optimistic UI update across all posts authored by this user
    setPosts((prev) =>
      prev.map((p) => {
        const matchesId = authorId && (p.authorId === authorId || p.author?.id === authorId);
        const matchesHandle = authorHandle && (
          p.username?.toLowerCase() === authorHandle.toLowerCase() ||
          p.author?.handle?.toLowerCase() === authorHandle.toLowerCase()
        );
        if (matchesId || matchesHandle) {
          return {
            ...p,
            followedByViewer: shouldFollow,
            author: p.author ? { ...p.author, followedByViewer: shouldFollow } : p.author,
          };
        }
        return p;
      })
    );

    setSelectedPost((prev) => {
      if (!prev) return null;
      const matchesId = authorId && (prev.authorId === authorId || prev.author?.id === authorId);
      const matchesHandle = authorHandle && (
        prev.username?.toLowerCase() === authorHandle.toLowerCase() ||
        prev.author?.handle?.toLowerCase() === authorHandle.toLowerCase()
      );
      if (matchesId || matchesHandle) {
        return {
          ...prev,
          followedByViewer: shouldFollow,
          author: prev.author ? { ...prev.author, followedByViewer: shouldFollow } : prev.author,
        };
      }
      return prev;
    });

    // 3. Call backend API if authorId is available
    if (authorId) {
      try {
        await toggleFollowApi(authorId, shouldFollow);
      } catch (err) {
        console.error('Failed to toggle follow on server:', err);
        // Revert optimistic update on error
        if (authorHandle) {
          setFollowingMap((prev) => ({
            ...prev,
            [authorHandle.toLowerCase()]: !shouldFollow,
          }));
        }
        setPosts((prev) =>
          prev.map((p) => {
            const matchesId = p.authorId === authorId || p.author?.id === authorId;
            if (matchesId) {
              return {
                ...p,
                followedByViewer: !shouldFollow,
                author: p.author ? { ...p.author, followedByViewer: !shouldFollow } : p.author,
              };
            }
            return p;
          })
        );
      }
    }
  }, [currentUser]);

  /**
   * Fetch a batch of posts from FastAPI backend API.
   * If reset is true, ignores previous cursor and starts from page 1.
   */
  const fetchFeedBatch = useCallback(async (reset = false, targetCursor = null) => {
    setLoading(true);
    setError(null);

    try {
      const activeCursor = reset ? null : targetCursor;
      const result = await fetchFeedFromApi(activeCursor, 10);
      setPosts((prev) => {
        if (reset || activeCursor === null) {
          return result.items;
        }
        // Deduplicate incoming items by id
        const existingIds = new Set(prev.map((p) => p.id));
        const newItems = result.items.filter((item) => !existingIds.has(item.id));
        return [...prev, ...newItems];
      });
      setCursor(result.nextCursor);
      setHasMore(result.hasMore);
    } catch (err) {
      console.error('FastAPI Backend connection error:', err);
      setError({
        code: err.code || 'CONNECTION_ERROR',
        message: err.message || 'Unable to connect to the backend server.',
        requestId: err.requestId || null,
      });
    } finally {
      setLoading(false);
    }
  }, []);

  const loadPosts = useCallback((isInitial = false) => {
    if (loading) return;
    if (!isInitial && !hasMore) return;
    fetchFeedBatch(isInitial, isInitial ? null : cursor);
  }, [loading, hasMore, cursor, fetchFeedBatch]);

  // Initial load on page mount
  useEffect(() => {
    fetchFeedBatch(true, null);
  }, [fetchFeedBatch]);

  /**
   * Authentication handlers
   */
  const handleAuthSuccess = useCallback((user) => {
    setCurrentUser(user);
    setIsAuthModalOpen(false);
    // Reload feed immediately to display following feed for authenticated user
    fetchFeedBatch(true, null);
  }, [fetchFeedBatch]);

  const handleLogout = useCallback(async () => {
    await logoutApi();
    setCurrentUser(null);
    // Reload feed immediately to restore default public explore feed
    fetchFeedBatch(true, null);
  }, [fetchFeedBatch]);

  const handleRetry = () => {
    fetchFeedBatch(posts.length === 0, cursor);
  };

  // -------------------------------------------------------------
  // -------------------------------------------------------------
  // Live global search: queries backend across all 60 posts from all 5 profiles
  // Supports captions, hashtags (#), usernames (@handle, name), and bio keywords!
  // Works identically everywhere: default guest page + when logged in as any profile.
  // -------------------------------------------------------------
  useEffect(() => {
    const trimmed = searchQuery.trim();
    if (!trimmed) {
      setSearchResults(null);
      setIsSearching(false);
      return;
    }

    // If query is 1 character, do fast local filter on loaded posts
    if (trimmed.length < 2) {
      const lower = trimmed.toLowerCase();
      const localMatches = posts.filter((p) => {
        const caption = (p.caption || p.text || '').toLowerCase();
        const handle = (p.username || p.author?.handle || '').toLowerCase();
        const name = (p.author?.displayName || p.displayName || '').toLowerCase();
        const bio = (p.author?.bio || '').toLowerCase();
        return (
          caption.includes(lower) ||
          handle.includes(lower) ||
          name.includes(lower) ||
          bio.includes(lower)
        );
      });
      setSearchResults(localMatches);
      setIsSearching(false);
      return;
    }

    setIsSearching(true);
    const timer = setTimeout(async () => {
      try {
        const results = await searchPostsApi(trimmed, 60);
        setSearchResults(results);
      } catch (err) {
        console.warn('Live search error:', err);
        setSearchResults([]);
      } finally {
        setIsSearching(false);
      }
    }, 150);

    return () => clearTimeout(timer);
  }, [searchQuery, posts]);

  const isSearchActive = Boolean(searchQuery.trim());
  const filteredPosts = isSearchActive
    ? (searchResults !== null ? searchResults : [])
    : posts;

  const handleProfileUpdated = useCallback((updatedUser) => {
    setCurrentUser((prev) => ({
      ...prev,
      ...updatedUser,
    }));

    // Update feed posts authored by this user
    setPosts((prev) =>
      prev.map((p) => {
        const authorId = p.authorId || p.author?.id;
        if (authorId === updatedUser.id) {
          return {
            ...p,
            username: updatedUser.handle,
            displayName: updatedUser.displayName,
            author: p.author
              ? {
                  ...p.author,
                  handle: updatedUser.handle,
                  displayName: updatedUser.displayName,
                  bio: updatedUser.bio,
                }
              : p.author,
          };
        }
        return p;
      })
    );
  }, []);

  const handleUpdatePost = useCallback((postId, updates) => {
    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, ...updates } : p))
    );
    setSelectedPost((prev) => (prev && prev.id === postId ? { ...prev, ...updates } : prev));
  }, []);

  const handlePostCreated = useCallback((newPost) => {
    if (!newPost) return;
    setPosts((prev) => [newPost, ...prev]);
    setSearchQuery('');
  }, []);

  return (
    <div className="app">
      {/* Top Header Bar: Search on Left, Auth in Middle, Theme Toggle on Right */}
      <TopBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onClearSearch={() => setSearchQuery('')}
        theme={theme}
        onToggleTheme={handleToggleTheme}
        currentUser={currentUser}
        onOpenAuth={() => setIsAuthModalOpen(true)}
        onOpenEditProfile={() => setIsEditProfileModalOpen(true)}
        onOpenCreatePost={() => setIsCreatePostModalOpen(true)}
        onLogout={handleLogout}
        onSelectPost={handleSelectPost}
      />

      {/* Feed confirmation banner when logged in */}
      {currentUser && (
        <div className="app__feed-banner" role="status">
          <span>
            Logged in as <strong>@{currentUser.handle}</strong>
          </span>
        </div>
      )}

      <div className="app__content-layout">
        <main className="app__feed-column">
          {/* Primary Error Banner when initial feed load fails */}
          {error && posts.length === 0 && (
            <div className="app__error" role="alert">
              <p>{error.message}</p>
              {error.requestId && (
                <p className="app__error-detail">Request ID: {error.requestId}</p>
              )}
              <button type="button" className="app__retry-btn" onClick={handleRetry}>
                Retry
              </button>
            </div>
          )}

          {/* Message when no posts match search */}
          {isSearchActive && filteredPosts.length === 0 && !isSearching && !loading && (
            <div className="app__empty-search">
              <p className="app__empty-title">No posts found for "{searchQuery}"</p>
              <p className="app__empty-subtitle">
                Try searching any word from caption, username (@deepu, @sneha, etc.), or bio (e.g. gourmet, flora, books, cricket, acoustic)...
              </p>
              <button
                type="button"
                className="app__clear-search-btn"
                onClick={() => setSearchQuery('')}
              >
                Show All Posts
              </button>
            </div>
          )}

          {/* Main Post Grid */}
          {(!error || posts.length > 0) && (
            <PhotoGrid
              posts={filteredPosts}
              onSelectPost={handleSelectPost}
              onToggleFollow={handleToggleFollow}
              onLoadMore={() => loadPosts(false)}
              hasMore={isSearchActive ? false : hasMore}
              loading={loading}
              onSelectAuthor={(handle) => setSearchQuery(`@${handle}`)}
            />
          )}

          {/* Secondary Error Banner when subsequent page fails to load */}
          {error && posts.length > 0 && (
            <div className="app__error" role="alert">
              <p>{error.message}</p>
              {error.requestId && (
                <p className="app__error-detail">Request ID: {error.requestId}</p>
              )}
              <button type="button" className="app__retry-btn" onClick={handleRetry}>
                Retry Loading Next Page
              </button>
            </div>
          )}
        </main>

        <aside className="app__sidebar-column">
          <SuggestedProfiles
            currentUser={currentUser}
            onOpenAuth={() => setIsAuthModalOpen(true)}
            onToggleFollow={handleToggleFollow}
            followingMap={followingMap}
            onSelectProfile={(handle) => setSearchQuery(`@${handle}`)}
          />
        </aside>
      </div>

      {/* Carousel Modal Viewer */}
      {selectedPost && (
        <PhotoViewer
          post={selectedPost}
          onClose={handleClosePost}
          onUpdatePost={handleUpdatePost}
          onToggleFollow={handleToggleFollow}
          currentUser={currentUser}
          onOpenAuth={() => setIsAuthModalOpen(true)}
        />
      )}

      {/* Sign In / Sign Up Modal */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthSuccess={handleAuthSuccess}
      />

      {/* Edit Profile Modal */}
      <EditProfileModal
        isOpen={isEditProfileModalOpen}
        onClose={() => setIsEditProfileModalOpen(false)}
        currentUser={currentUser}
        onProfileUpdated={handleProfileUpdated}
      />

      {/* Create Post Modal */}
      <CreatePostModal
        isOpen={isCreatePostModalOpen}
        onClose={() => setIsCreatePostModalOpen(false)}
        currentUser={currentUser}
        onPostCreated={handlePostCreated}
      />
    </div>
  );
}

export default App;
