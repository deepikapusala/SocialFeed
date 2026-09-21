import React, { useState, useEffect } from 'react';
import { getResponsiveSrcSet } from '../../utils/images';
import './PhotoCard.css';

/**
 * PhotoCard component renders an individual post preview within the explore grid.
 * Displays the first image of the post formatted to a 4:5 aspect ratio container
 * with a multi-photo carousel badge if applicable, or a clean typography card
 * if the post has no media attachments.
 */
export function PhotoCard({ post, index, onSelectPost }) {
  const images = Array.isArray(post.images)
    ? post.images
    : (post.imageUrl ? [post.imageUrl] : []);
  const hasImages = images.length > 0;
  const firstImage = hasImages ? images[0] : null;
  const isCarousel = images.length > 1;
  const srcSet = firstImage ? getResponsiveSrcSet(firstImage) : '';

  return (
    <article className={`photo-card ${!hasImages ? 'photo-card--text' : ''}`}>
      <button
        type="button"
        className="photo-card__button"
        onClick={() => onSelectPost(post, index)}
        aria-label={`View post by ${post.username || 'user'}: ${post.caption || post.text || 'Post'}`}
      >
        {hasImages ? (
          <>
            <img
              className="photo-card__image"
              src={firstImage}
              srcSet={srcSet}
              sizes="(max-width: 600px) 100vw, (max-width: 1024px) 50vw, 360px"
              alt={post.caption || post.alt || 'Instagram photo'}
              loading="lazy"
              decoding="async"
            />

            {isCarousel && (
              <span
                className="photo-card__carousel-badge"
                aria-label="Multiple photos"
                title="Multiple photos"
              >
                <svg viewBox="0 0 24 24" width="16" height="16" fill="currentColor">
                  <path d="M19 2H8a2 2 0 0 0-2 2v12a2 2 0 0 0 2 2h11a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2zm0 14H8V4h11v12zM4 6H2v14a2 2 0 0 0 2 2h14v-2H4V6z"/>
                </svg>
              </span>
            )}

            <span className="photo-card__overlay" aria-hidden="true">
              <span className="photo-card__overlay-stat">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
                {post.likeCount ?? post.likes ?? 0}
              </span>
              <span className="photo-card__overlay-stat">
                <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
                {post.replyCount ?? 0}
              </span>
            </span>
          </>
        ) : (
          <div className="photo-card__text-content">
            <div className="photo-card__text-header">
              <img
                className="photo-card__text-avatar"
                src={post.userAvatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=80&q=80'}
                alt={post.username || 'user'}
              />
              <div className="photo-card__text-user">
                <span className="photo-card__text-username">@{post.username || 'user'}</span>
                <span className="photo-card__text-time">{post.timeAgo || 'recently'}</span>
              </div>
            </div>
            <p className="photo-card__text-body">
              {post.caption || post.text || 'Original post'}
            </p>
            <div className="photo-card__text-footer">
              <span className="photo-card__stat-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
                  <path d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
                {post.likeCount ?? post.likes ?? 0}
              </span>
              <span className="photo-card__stat-item">
                <svg viewBox="0 0 24 24" width="15" height="15" fill="currentColor">
                  <path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
                </svg>
                {post.replyCount ?? 0}
              </span>
            </div>
            <span className="photo-card__overlay" aria-hidden="true" />
          </div>
        )}
      </button>
    </article>
  );
}
