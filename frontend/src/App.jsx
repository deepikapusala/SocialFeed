import React, { useState, useEffect, useCallback } from 'react';
import { TopBar } from './components/TopBar/TopBar';
import { PhotoGrid } from './components/PhotoGrid/PhotoGrid';
import { PhotoViewer } from './components/PhotoViewer/PhotoViewer';
import { fetchFeedFromApi } from './utils/api';
import './App.css';

/**
 * Root Application component.
 * Consumes the Stage A FastAPI /feed endpoint with opaque cursor pagination.
 */
export function App() {
  const [posts, setPosts] = useState([]);
  const [selectedPost, setSelectedPost] = useState(null);
  const [cursor, setCursor] = useState(null);
  const [hasMore, setHasMore] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Search query state
  const [searchQuery, setSearchQuery] = useState('');

  // Theme state: 'dark' (pure black) vs 'light' (baby pink)
  const [theme, setTheme] = useState(() => {
    return localStorage.getItem('app-theme') || 'dark';
  });

  // Apply theme to document
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    localStorage.setItem('app-theme', theme);
  }, [theme]);

  const handleToggleTheme = () => {
    setTheme((prev) => (prev === 'dark' ? 'light' : 'dark'));
  };

  /**
   * Fetch a batch of posts from FastAPI backend API.
   */
  const loadPosts = useCallback(async (isInitial = false) => {
    if (loading) return;
    const currentCursor = isInitial ? null : cursor;
    if (!isInitial && !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const result = await fetchFeedFromApi(currentCursor, 10);
      setPosts((prev) => {
        if (isInitial || currentCursor === null) {
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
  }, [cursor, hasMore, loading]);

  // Initial load on page mount
  useEffect(() => {
    loadPosts(true);
  }, []);

  const handleRetry = () => {
    loadPosts(posts.length === 0);
  };

  // -------------------------------------------------------------
  // Search filter: Supports '#art', 'art', username, & category
  // -------------------------------------------------------------
  const cleanQuery = searchQuery.trim().toLowerCase();
  const rawTerm = cleanQuery.replace(/^#+/, ''); // Strips leading '#' if present
  const hashtagTerm = '#' + rawTerm;             // Ensures '#art' format for tag matching

  const filteredPosts = cleanQuery
    ? posts.filter((post) => {
        const caption = (post.caption || post.text || '').toLowerCase();
        const category = (post.category || '').toLowerCase();
        const username = (post.username || post.author?.handle || '').toLowerCase();
        const displayName = (post.displayName || post.author?.displayName || '').toLowerCase();

        // 1. Match hashtag (e.g. searching '#art' or 'art' matches '#art' in caption)
        const matchesHashtag = caption.includes(hashtagTerm);

        // 2. Match category (e.g. 'Art', 'Nature', 'Coffee')
        const matchesCategory = category.includes(rawTerm);

        // 3. Match username or display name (e.g. 'yosemite_wanderer', 'atelier_canvas')
        const matchesUser = username.includes(rawTerm) || displayName.includes(rawTerm);

        // 4. Match general caption words
        const matchesCaption = caption.includes(cleanQuery) || caption.includes(rawTerm);

        return matchesHashtag || matchesCategory || matchesUser || matchesCaption;
      })
    : posts;

  const handleUpdatePost = useCallback((postId, updates) => {
    setPosts((prev) =>
      prev.map((p) => (p.id === postId ? { ...p, ...updates } : p))
    );
    setSelectedPost((prev) => (prev && prev.id === postId ? { ...prev, ...updates } : prev));
  }, []);

  return (
    <div className="app">
      {/* Top Header Bar: Search on Left/Center, Theme Toggle on Right/Center */}
      <TopBar
        searchQuery={searchQuery}
        onSearchChange={setSearchQuery}
        onClearSearch={() => setSearchQuery('')}
        theme={theme}
        onToggleTheme={handleToggleTheme}
      />

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
      {cleanQuery && filteredPosts.length === 0 && !loading && (
        <div className="app__empty-search">
          <p className="app__empty-title">No posts found for "{searchQuery}"</p>
          <p className="app__empty-subtitle">
            Try searching by tag, caption keyword, or handle...
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
          onSelectPost={(post) => setSelectedPost(post)}
          onLoadMore={() => loadPosts(false)}
          hasMore={cleanQuery ? false : hasMore}
          loading={loading}
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

      {/* Carousel Modal Viewer */}
      {selectedPost && (
        <PhotoViewer
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
          onUpdatePost={handleUpdatePost}
        />
      )}
    </div>
  );
}

export default App;
