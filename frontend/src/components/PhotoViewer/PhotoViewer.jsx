import React, { useState, useEffect, useRef } from 'react';
import { getResponsiveSrcSet } from '../../utils/images';
import { toggleLikeApi, toggleRepostApi, fetchRepliesApi, createReplyApi } from '../../utils/api';
import './PhotoViewer.css';

/**
 * PhotoViewer modal renders an authentic Instagram post modal with an in-post multi-image carousel.
 * Allows swiping, clicking arrows, or using keyboard arrows to navigate through the images
 * belonging to the selected post. If the post has no media, renders the post cleanly without
 * an image stage.
 */
export function PhotoViewer({ post, onClose, onUpdatePost, onToggleFollow }) {
  const images = Array.isArray(post.images)
    ? post.images
    : (post.imageUrl ? [post.imageUrl] : []);
  const totalImages = images.length;
  const hasMedia = totalImages > 0;

  const authorId = post.authorId || post.author?.id;
  const authorHandle = post.username || post.author?.handle || 'user';
  const isSelf = authorId === 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa' || authorHandle.toLowerCase() === 'asha';
  const isFollowing = Boolean(post.followedByViewer || post.author?.followedByViewer);

  const handleFollowClick = (e) => {
    e.stopPropagation();
    e.preventDefault();
    if (onToggleFollow) {
      onToggleFollow({
        authorId,
        authorHandle,
        shouldFollow: !isFollowing,
      });
    }
  };

  const [currentImageIndex, setCurrentImageIndex] = useState(0);
  const [isLiked, setIsLiked] = useState(Boolean(post.likedByViewer));
  const [isReposted, setIsReposted] = useState(Boolean(post.repostedByViewer));
  const [isSaved, setIsSaved] = useState(false);
  const [comments, setComments] = useState([]);
  const [commentInput, setCommentInput] = useState('');

  const commentInputRef = useRef(null);
  const touchStartXRef = useRef(null);
  const touchStartYRef = useRef(null);

  // Reset state and fetch direct replies whenever a different post opens
  useEffect(() => {
    setCurrentImageIndex(0);
    setIsLiked(Boolean(post.likedByViewer));
    setIsReposted(Boolean(post.repostedByViewer));
    setIsSaved(false);
    setComments([]);
    setCommentInput('');

    // Fetch seeded replies for this post
    if (post.id) {
      fetchRepliesApi(post.id)
        .then((res) => {
          if (res?.items?.length > 0) {
            const replyList = res.items.map((r) => ({
              id: r.id,
              username: r.username || 'user',
              text: r.text || r.caption || '',
            }));
            setComments(replyList);
          }
        })
        .catch(() => {});
    }
  }, [post.id, post.likedByViewer]);

  // Carousel navigation handlers
  const handlePrevImage = () => {
    if (currentImageIndex > 0) {
      setCurrentImageIndex((prev) => prev - 1);
    }
  };

  const handleNextImage = () => {
    if (currentImageIndex < totalImages - 1) {
      setCurrentImageIndex((prev) => prev + 1);
    }
  };

  const handleDotClick = (index) => {
    setCurrentImageIndex(index);
  };

  // Keyboard navigation & body scroll locking
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      } else if (e.key === 'ArrowLeft' && hasMedia) {
        handlePrevImage();
      } else if (e.key === 'ArrowRight' && hasMedia) {
        handleNextImage();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    const originalOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';

    return () => {
      window.removeEventListener('keydown', handleKeyDown);
      document.body.style.overflow = originalOverflow;
    };
  }, [currentImageIndex, totalImages, hasMedia, onClose]);

  // Touch Swipe Handlers for mobile
  const handleTouchStart = (e) => {
    touchStartXRef.current = e.touches[0].clientX;
    touchStartYRef.current = e.touches[0].clientY;
  };

  const handleTouchEnd = (e) => {
    if (touchStartXRef.current === null || touchStartYRef.current === null) return;
    const deltaX = e.changedTouches[0].clientX - touchStartXRef.current;
    const deltaY = e.changedTouches[0].clientY - touchStartYRef.current;

    // Trigger when horizontal swipe exceeds 35px
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 35) {
      if (deltaX > 0) {
        handlePrevImage(); // Swipe right -> previous image
      } else {
        handleNextImage(); // Swipe left -> next image
      }
    }
    touchStartXRef.current = null;
    touchStartYRef.current = null;
  };

  const handleToggleLike = async () => {
    const nextLiked = !isLiked;
    setIsLiked(nextLiked); // Optimistic UI update

    try {
      const res = await toggleLikeApi(post.id, nextLiked);
      if (onUpdatePost) {
        onUpdatePost(post.id, {
          likedByViewer: res.likedByViewer,
          likeCount: res.likeCount,
        });
      }
    } catch (err) {
      console.error('Failed to update like on server:', err);
      setIsLiked(!nextLiked); // Revert on failure
    }
  };

  const handleToggleRepost = async () => {
    const nextReposted = !isReposted;
    setIsReposted(nextReposted); // Optimistic UI update

    try {
      const res = await toggleRepostApi(post.id, nextReposted);
      if (onUpdatePost) {
        onUpdatePost(post.id, {
          repostedByViewer: res.repostedByViewer,
          repostCount: res.repostCount,
        });
      }
    } catch (err) {
      console.error('Failed to update repost on server:', err);
      setIsReposted(!nextReposted); // Revert on failure
    }
  };

  const handleToggleSave = () => {
    setIsSaved((prev) => !prev);
  };

  const handleFocusComment = () => {
    if (commentInputRef.current) {
      commentInputRef.current.focus();
    }
  };

  const handleAddComment = async (e) => {
    e.preventDefault();
    const text = commentInput.trim();
    if (!text) return;

    // Optimistic comment in UI
    const tempId = `temp-${Date.now()}`;
    const optimisticComment = {
      id: tempId,
      username: 'asha',
      text: text,
    };
    setComments((prev) => [...prev, optimisticComment]);
    setCommentInput('');

    try {
      const savedReply = await createReplyApi(post.id, text);
      // Replace optimistic comment with authoritative saved row from PostgreSQL
      setComments((prev) =>
        prev.map((c) =>
          c.id === tempId
            ? { id: savedReply.id, username: savedReply.username || 'asha', text: savedReply.text }
            : c
        )
      );
      if (onUpdatePost) {
        onUpdatePost(post.id, {
          replyCount: (post.replyCount || 0) + 1,
        });
      }
    } catch (err) {
      console.error('Failed to save comment to backend:', err);
      setComments((prev) => prev.filter((c) => c.id !== tempId));
      alert(`Could not post comment: ${err.message}`);
    }
  };

  const currentImageUrl = hasMedia ? images[currentImageIndex] : null;
  const srcSet = currentImageUrl ? getResponsiveSrcSet(currentImageUrl) : '';
  const initialLikes = post.likeCount ?? post.likes ?? 0;
  const wasInitiallyLiked = Boolean(post.likedByViewer);
  const currentLikes = initialLikes + (isLiked ? (wasInitiallyLiked ? 0 : 1) : (wasInitiallyLiked ? -1 : 0));

  const initialReposts = post.repostCount ?? 0;
  const wasInitiallyReposted = Boolean(post.repostedByViewer);
  const currentReposts = initialReposts + (isReposted ? (wasInitiallyReposted ? 0 : 1) : (wasInitiallyReposted ? -1 : 0));

  return (
    <div
      className="post-modal"
      role="dialog"
      aria-modal="true"
      aria-label={`Post by ${post.username || 'user'}`}
    >
      {/* Darkened Backdrop */}
      <div
        className="post-modal__backdrop"
        onClick={onClose}
        aria-hidden="true"
      />

      {/* Centered Post Card Modal */}
      <article className={`post-modal__card ${!hasMedia ? 'post-modal__card--no-media' : ''}`}>
        {/* Post Header */}
        <header className="post-modal__header">
          <div className="post-modal__user-info">
            <img
              className="post-modal__avatar"
              src={post.userAvatar || 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=120&q=80'}
              alt={authorHandle}
            />
            <div className="post-modal__user-meta">
              <span className="post-modal__username">@{authorHandle}</span>
              {post.category && (
                <span className="post-modal__category">• {post.category}</span>
              )}
            </div>
            {!isSelf && (
              <button
                type="button"
                className={`ig-follow-btn ${isFollowing ? 'ig-follow-btn--following' : ''}`}
                onClick={handleFollowClick}
                style={{ marginLeft: '12px' }}
                aria-label={isFollowing ? `Unfollow ${authorHandle}` : `Follow ${authorHandle}`}
              >
                {isFollowing ? 'Following' : 'Follow'}
              </button>
            )}
          </div>
          <button
            type="button"
            className="post-modal__close-btn"
            onClick={onClose}
            aria-label="Close post modal"
          >
            &times;
          </button>
        </header>

        {/* Media Carousel Stage with Swipe Support (Rendered only when post has media) */}
        {hasMedia && (
          <div
            className="post-modal__media"
            onTouchStart={handleTouchStart}
            onTouchEnd={handleTouchEnd}
          >
            {/* Carousel Image Counter Pill (e.g. 1 / 3) */}
            {totalImages > 1 && (
              <span
                className="post-modal__image-counter"
                aria-label={`Image ${currentImageIndex + 1} of ${totalImages}`}
              >
                {currentImageIndex + 1} / {totalImages}
              </span>
            )}

            {/* Left / Previous Arrow inside carousel */}
            {totalImages > 1 && currentImageIndex > 0 && (
              <button
                type="button"
                className="post-modal__carousel-arrow post-modal__carousel-arrow--prev"
                onClick={handlePrevImage}
                aria-label="Previous image"
              >
                &#8249;
              </button>
            )}

            {/* Right / Next Arrow inside carousel */}
            {totalImages > 1 && currentImageIndex < totalImages - 1 && (
              <button
                type="button"
                className="post-modal__carousel-arrow post-modal__carousel-arrow--next"
                onClick={handleNextImage}
                aria-label="Next image"
              >
                &#8250;
              </button>
            )}

            {/* Current Carousel Image */}
            <img
              key={`${post.id}-${currentImageIndex}`}
              className="post-modal__image"
              src={currentImageUrl}
              srcSet={srcSet}
              sizes="(max-width: 600px) 100vw, (max-width: 1024px) 600px, 700px"
              alt={`${post.caption || post.text || 'Instagram photo'} (image ${currentImageIndex + 1} of ${totalImages})`}
            />
          </div>
        )}

        {/* Action Buttons & Carousel Dots */}
        <div className="post-modal__actions">
          <div className="post-modal__actions-left">
            <button
              type="button"
              className={`post-modal__action-btn post-modal__action-btn--like ${isLiked ? 'is-liked' : ''}`}
              onClick={handleToggleLike}
              aria-label={isLiked ? 'Unlike photo' : 'Like photo'}
            >
              {isLiked ? (
                <svg className="icon-heart-filled" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="#ef4444" d="M12 21.35l-1.45-1.32C5.4 15.36 2 12.28 2 8.5 2 5.42 4.42 3 7.5 3c1.74 0 3.41.81 4.5 2.09C13.09 3.81 14.76 3 16.5 3 19.58 3 22 5.42 22 8.5c0 3.78-3.4 6.86-8.55 11.54L12 21.35z"/>
                </svg>
              ) : (
                <svg className="icon-heart-outline" viewBox="0 0 24 24" width="24" height="24">
                  <path fill="currentColor" d="M16.5 3c-1.74 0-3.41.81-4.5 2.09C10.91 3.81 9.24 3 7.5 3 4.42 3 2 5.42 2 8.5c0 3.78 3.4 6.86 8.55 11.54L12 21.35l1.45-1.32C18.6 15.36 22 12.28 22 8.5 22 5.42 19.58 3 16.5 3zm-4.4 15.55l-.1.1-.1-.1C7.14 14.24 4 11.39 4 8.5 4 6.5 5.5 5 7.5 5c1.54 0 3.04.99 3.57 2.36h1.87C13.46 5.99 14.96 5 16.5 5c2 0 3.5 1.5 3.5 3.5 0 2.89-3.14 5.74-7.9 10.05z"/>
                </svg>
              )}
            </button>

            <button
              type="button"
              className="post-modal__action-btn"
              onClick={handleFocusComment}
              aria-label="Comment on post"
            >
              <svg viewBox="0 0 24 24" width="24" height="24">
                <path fill="currentColor" d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/>
              </svg>
            </button>

            {/* Repost Action Button (Exact Instagram Curved Loop Icon) */}
            <button
              type="button"
              className={`post-modal__action-btn post-modal__action-btn--repost ${isReposted ? 'is-reposted' : ''}`}
              onClick={handleToggleRepost}
              aria-label={isReposted ? 'Undo repost' : 'Repost post'}
              title={isReposted ? 'Undo Repost' : 'Repost'}
            >
              <svg className="icon-repost" viewBox="0 0 24 24" width="22" height="22" fill="none" stroke={isReposted ? "#10b981" : "currentColor"} strokeWidth="2.3" strokeLinecap="round" strokeLinejoin="round">
                <path d="M17 2l4 4-4 4" />
                <path d="M3 11V9a4 4 0 0 1 4-4h14" />
                <path d="M7 22l-4-4 4-4" />
                <path d="M21 13v2a4 4 0 0 1-4 4H3" />
              </svg>
            </button>
          </div>

          {/* Carousel Pagination Dots Indicator (● ○ ○ ○) */}
          {totalImages > 1 && (
            <div className="post-modal__dots" aria-label="Carousel pagination dots">
              {images.map((_, dotIdx) => (
                <button
                  key={dotIdx}
                  type="button"
                  className={`post-modal__dot ${dotIdx === currentImageIndex ? 'post-modal__dot--active' : ''}`}
                  onClick={() => handleDotClick(dotIdx)}
                  aria-label={`Go to image ${dotIdx + 1} of ${totalImages}`}
                />
              ))}
            </div>
          )}

          <div className="post-modal__actions-right">
            <button
              type="button"
              className={`post-modal__action-btn post-modal__action-btn--save ${isSaved ? 'is-saved' : ''}`}
              onClick={handleToggleSave}
              aria-label={isSaved ? 'Remove from saved' : 'Save post'}
            >
              {isSaved ? (
                <svg viewBox="0 0 24 24" width="24" height="24" fill="var(--color-accent)" aria-hidden="true">
                  <path fill="var(--color-accent)" d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2z"/>
                </svg>
              ) : (
                <svg viewBox="0 0 24 24" width="24" height="24">
                  <path fill="currentColor" d="M17 3H7c-1.1 0-1.99.9-1.99 2L5 21l7-3 7 3V5c0-1.1-.9-2-2-2zm0 15l-5-2.18L7 18V5h10v13z"/>
                </svg>
              )}
            </button>
          </div>
        </div>

        {/* Post Details (Likes, Reposts, Caption, Comments, Time) */}
        <div className="post-modal__body">
          <p className="post-modal__likes">
            <strong>{currentLikes.toLocaleString()} {currentLikes === 1 ? 'like' : 'likes'}</strong>
            {currentReposts > 0 && (
              <span className="post-modal__reposts-count" style={{ marginLeft: '12px', color: 'var(--color-text-secondary)' }}>
                • <strong>{currentReposts.toLocaleString()} {currentReposts === 1 ? 'repost' : 'reposts'}</strong>
              </span>
            )}
          </p>

          <p className="post-modal__caption">
            <strong className="post-modal__caption-username">{post.username || 'instagram_user'} </strong>
            <span className="post-modal__caption-text">{post.caption || post.text || ''}</span>
          </p>

          {/* User Comments List */}
          {comments.length > 0 && (
            <div className="post-modal__comments-list">
              {comments.map((c) => (
                <p key={c.id} className="post-modal__comment-item">
                  <strong>{c.username}</strong> <span>{c.text}</span>
                </p>
              ))}
            </div>
          )}

          <time className="post-modal__timestamp">
            {post.timeAgo || 'recently'}
          </time>
        </div>

        {/* Add Comment Bar */}
        <form className="post-modal__comment-form" onSubmit={handleAddComment}>
          <input
            ref={commentInputRef}
            type="text"
            className="post-modal__comment-input"
            placeholder="Add a comment..."
            value={commentInput}
            onChange={(e) => setCommentInput(e.target.value)}
          />
          <button
            type="submit"
            className="post-modal__comment-submit"
            disabled={!commentInput.trim()}
          >
            Post
          </button>
        </form>
      </article>
    </div>
  );
}
