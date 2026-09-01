import React, { useState, useEffect, useCallback } from 'react';
import { TopBar } from './components/TopBar/TopBar';
import { PhotoGrid } from './components/PhotoGrid/PhotoGrid';
import { PhotoViewer } from './components/PhotoViewer/PhotoViewer';
import { posts as INITIAL_POSTS } from './data/photos';
import './App.css';

/**
 * Backend API base URL.
 */
const API_BASE = 'http://localhost:8000';

/**
 * Root Application component.
 * - Simple & instant tag search (e.g. #art, #nature, #wanderlust).
 * - Simple light/dark mode toggle (Baby Pink 🌸 vs Absolute Pure Black 🌙).
 */
export function App() {
  // Start with INITIAL_POSTS so all posts are immediately available for search
  const [posts, setPosts] = useState(INITIAL_POSTS);
  const [selectedPost, setSelectedPost] = useState(null);
  const [cursor, setCursor] = useState(0);
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
   * Fetch a batch of posts from backend API.
   */
  const fetchPosts = useCallback(async () => {
    if (loading || !hasMore) return;

    setLoading(true);
    setError(null);

    try {
      const response = await fetch(`${API_BASE}/feed?cursor=${cursor}&limit=12`);
      if (!response.ok) throw new Error(`API error: ${response.status}`);

      const data = await response.json();
      if (cursor === 0) {
        setPosts(data.posts);
      } else {
        setPosts((prev) => [...prev, ...data.posts]);
      }
      setCursor(data.next_cursor);
      setHasMore(data.has_more);
    } catch (err) {
      console.error('Backend connection notice (using local dataset):', err);
    } finally {
      setLoading(false);
    }
  }, [cursor, loading, hasMore]);

  // Initial load on page mount
  useEffect(() => {
    fetchPosts();
  }, []);

  // -------------------------------------------------------------
  // Clean hashtag & category search filter
  // -------------------------------------------------------------
  const cleanQuery = searchQuery.trim().toLowerCase();
  const searchWord = cleanQuery.replace('#', '');
  const searchTag = '#' + searchWord;

  const filteredPosts = cleanQuery
    ? posts.filter((post) => {
        const caption = (post.caption || '').toLowerCase();
        const category = (post.category || '').toLowerCase();
        const username = (post.username || '').toLowerCase();
        const captionWords = caption.split(/\s+/);

        // 1. Tag matches in caption (e.g. "#art")
        const hasTag = captionWords.includes(searchTag) || caption.includes(searchTag);

        // 2. Category or username matches (e.g. "art" or "atelier_canvas")
        const hasCategory = category === searchWord || category.includes(searchWord);
        const hasUsername = username.includes(searchWord);

        // 3. Exact word in caption matches
        const hasWord = captionWords.some(
          (w) => w.replace(/[.,!?:;\"'()#]/g, '') === searchWord
        );

        return hasTag || hasCategory || hasWord || hasUsername;
      })
    : posts;

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

      {/* Message when no posts match search */}
      {cleanQuery && filteredPosts.length === 0 && (
        <div className="app__empty-search">
          <span className="app__empty-icon">🔍</span>
          <p className="app__empty-title">No posts found for "{searchQuery}"</p>
          <p className="app__empty-desc">
            Try searching for <em>#art, #nature, #coffee, #travel, #food, #ocean</em>...
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
      <PhotoGrid
        posts={filteredPosts}
        onSelectPost={(post) => setSelectedPost(post)}
        onLoadMore={fetchPosts}
        hasMore={cleanQuery ? false : hasMore}
        loading={loading}
      />

      {/* Carousel Modal Viewer */}
      {selectedPost && (
        <PhotoViewer
          post={selectedPost}
          onClose={() => setSelectedPost(null)}
        />
      )}
    </div>
  );
}

export default App;
