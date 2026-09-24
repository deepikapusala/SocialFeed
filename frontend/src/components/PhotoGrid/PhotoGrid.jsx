import React, { useEffect, useRef } from 'react';
import { PhotoCard } from '../PhotoCard/PhotoCard';
import './PhotoGrid.css';

/**
 * PhotoGrid component renders the explore grid using a responsive uniform CSS Grid layout.
 * Maps through Instagram posts and displays their 4:5 preview thumbnails.
 *
 * Uses an Intersection Observer on a sentinel element at the bottom of the grid
 * to trigger infinite scroll — loading the next batch from the backend API.
 */
export function PhotoGrid({ posts, onSelectPost, onToggleFollow, onLoadMore, hasMore, loading }) {
  const sentinelRef = useRef(null);

  // Intersection Observer: when the sentinel div scrolls into view, fetch more posts
  useEffect(() => {
    const sentinel = sentinelRef.current;
    if (!sentinel) return;

    const observer = new IntersectionObserver(
      (entries) => {
        // If the sentinel is visible and we have more posts to load, trigger fetch
        if (entries[0].isIntersecting && hasMore && !loading) {
          onLoadMore();
        }
      },
      {
        // Start loading a bit before the user reaches the very bottom
        rootMargin: '200px',
      }
    );

    observer.observe(sentinel);

    return () => {
      observer.disconnect();
    };
  }, [hasMore, loading, onLoadMore]);

  return (
    <main className="explore-main">
      <section className="photo-grid" aria-label="Instagram explore post grid">
        {posts.map((post, index) => (
          <PhotoCard
            key={post.id}
            post={post}
            index={index}
            onSelectPost={onSelectPost}
            onToggleFollow={onToggleFollow}
          />
        ))}
      </section>

      {/* Sentinel element — Intersection Observer watches this */}
      <div ref={sentinelRef} className="photo-grid__sentinel" aria-hidden="true" />

      {/* Loading spinner while fetching next batch */}
      {loading && (
        <div className="photo-grid__loading" aria-label="Loading more posts">
          <div className="photo-grid__spinner" />
          <span className="photo-grid__loading-text">Loading...</span>
        </div>
      )}

      {/* End-of-feed message when all posts are loaded */}
      {!hasMore && posts.length > 0 && (
        <div className="photo-grid__end">
          <span className="photo-grid__end-icon">✨</span>
          <p className="photo-grid__end-text">You're all caught up</p>
        </div>
      )}
    </main>
  );
}
