import React from 'react';
import { getResponsiveSrcSet } from '../../data/photos';
import './PhotoCard.css';

/**
 * PhotoCard component renders an individual post preview within the explore grid.
 * Displays the first image of the post formatted to a 4:5 aspect ratio container
 * with an authentic multi-photo carousel badge if applicable.
 */
export function PhotoCard({ post, index, onSelectPost }) {
  const firstImage = post.images && post.images.length > 0 ? post.images[0] : post.imageUrl;
  const srcSet = getResponsiveSrcSet(firstImage);

  return (
    <article className="photo-card">
      <button
        type="button"
        className="photo-card__button"
        onClick={() => onSelectPost(post, index)}
        aria-label={`View post by ${post.username || 'user'}: ${post.caption || 'Photo'}`}
      >
        <img
          className="photo-card__image"
          src={firstImage}
          srcSet={srcSet}
          sizes="(max-width: 600px) 100vw, (max-width: 1024px) 50vw, 360px"
          alt={post.caption || post.alt || 'Instagram photo'}
          loading="lazy"
          decoding="async"
        />

        <span className="photo-card__overlay" aria-hidden="true" />
      </button>
    </article>
  );
}
