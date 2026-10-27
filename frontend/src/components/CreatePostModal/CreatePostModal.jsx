import React, { useState, useRef, useEffect } from 'react';
import { createOriginalPostApi, resolveImageUrlApi } from '../../utils/api';
import './CreatePostModal.css';

/**
 * Curated Unsplash photo presets in standard format (?auto=format&fit=crop&w=1080&q=80).
 */
const UNSPLASH_PRESETS = [
  { label: '🍝 Pasta', url: 'https://images.unsplash.com/photo-1551183053-bf91a1d81141?auto=format&fit=crop&w=1080&q=80' },
  { label: '🌸 Flora', url: 'https://images.unsplash.com/photo-1520763185298-1b434c919102?auto=format&fit=crop&w=1080&q=80' },
  { label: '📚 Books', url: 'https://images.unsplash.com/photo-1512820790803-83ca734da794?auto=format&fit=crop&w=1080&q=80' },
  { label: '🎧 Music', url: 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=1080&q=80' },
  { label: '🏏 Cricket', url: 'https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?auto=format&fit=crop&w=1080&q=80' },
];

/**
 * Reads and optimizes an image file from local PC disk into a clean JPEG data URL.
 */
function readOptimizedImageFile(file, maxWidth = 1200, maxHeight = 1200, quality = 0.85) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onerror = reject;
    reader.onload = (e) => {
      const img = new Image();
      img.onerror = () => reject(new Error('Failed to load image file'));
      img.onload = () => {
        let width = img.width || 1200;
        let height = img.height || 800;

        if (width > maxWidth || height > maxHeight) {
          if (width / height > maxWidth / maxHeight) {
            height = Math.round((height * maxWidth) / width);
            width = maxWidth;
          } else {
            width = Math.round((width * maxHeight) / height);
            height = maxHeight;
          }
        }

        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        const ctx = canvas.getContext('2d');
        ctx.drawImage(img, 0, 0, width, height);
        const dataUrl = canvas.toDataURL('image/jpeg', quality);
        resolve({ url: dataUrl, width, height });
      };
      img.src = e.target.result;
    };
    reader.readAsDataURL(file);
  });
}

/**
 * CreatePostModal Component.
 * Enables any user (all 5 core creators or newly registered profiles) to publish
 * authentic original posts with 1 to 3 photos (via local PC files or URLs) and captions.
 */
export function CreatePostModal({ isOpen, onClose, currentUser, onPostCreated }) {
  const [images, setImages] = useState([]);
  const [activeImageIndex, setActiveImageIndex] = useState(0);
  const [caption, setCaption] = useState('');
  const [urlInput, setUrlInput] = useState('');
  const [altTextInput, setAltTextInput] = useState('');
  const [inputMode, setInputMode] = useState('file'); // 'file' or 'url'
  const [loading, setLoading] = useState(false);
  const [resolvingUrl, setResolvingUrl] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // Reset state when modal opens
  useEffect(() => {
    if (isOpen) {
      setImages([]);
      setActiveImageIndex(0);
      setCaption('');
      setUrlInput('');
      setAltTextInput('');
      setInputMode('file');
      setError(null);
      setLoading(false);
      setResolvingUrl(false);
    }
  }, [isOpen]);

  // Handle ESC key to close
  useEffect(() => {
    const handleKeyDown = (e) => {
      if (e.key === 'Escape' && isOpen) {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen || !currentUser) return null;

  // Handle Local File Upload from PC
  const handleFileChange = async (e) => {
    const files = Array.from(e.target.files || []);
    if (!files.length) return;

    setError(null);
    const availableSlots = 3 - images.length;
    if (availableSlots <= 0) {
      setError('You can add up to 3 photos per post.');
      return;
    }

    const filesToProcess = files.slice(0, availableSlots);

    try {
      const processed = await Promise.all(
        filesToProcess.map(async (file, idx) => {
          const res = await readOptimizedImageFile(file);
          return {
            id: `local-${Date.now()}-${idx}`,
            url: res.url,
            width: res.width,
            height: res.height,
            altText: file.name.replace(/\.[^/.]+$/, '').replace(/[-_]/g, ' ') || 'Photo',
          };
        })
      );

      setImages((prev) => {
        const next = [...prev, ...processed].slice(0, 3);
        return next;
      });
      setActiveImageIndex(images.length);
    } catch (err) {
      setError('Failed to process image file. Please choose another image.');
    }

    // Reset file input
    if (fileInputRef.current) {
      fileInputRef.current.value = '';
    }
  };

  // Handle Image URL input
  const handleAddUrl = async (e) => {
    if (e && e.preventDefault) e.preventDefault();
    const cleanUrl = urlInput.trim();
    if (!cleanUrl) return;

    if (images.length >= 3) {
      setError('You can add up to 3 photos per post.');
      return;
    }

    if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://') && !cleanUrl.startsWith('data:image/')) {
      setError('Please provide a valid web image URL (starting with https://).');
      return;
    }

    setError(null);
    setResolvingUrl(true);

    try {
      // 1. Resolve and format to standard ?auto=format&fit=crop&w=1080&q=80
      const finalUrl = await resolveImageUrlApi(cleanUrl);

      // 2. Pre-validate image loading in memory so a broken image is NEVER added!
      await new Promise((resolve, reject) => {
        const testImg = new Image();
        testImg.onload = () => {
          resolve({
            width: testImg.naturalWidth || 1080,
            height: testImg.naturalHeight || 1080,
          });
        };
        testImg.onerror = () => {
          reject(new Error('Image failed to load from this URL. Please verify the URL or try one of the curated presets below.'));
        };
        testImg.src = finalUrl;
      }).then(({ width, height }) => {
        const newImg = {
          id: `url-${Date.now()}-${images.length}`,
          url: finalUrl,
          width: width,
          height: height,
          altText: altTextInput.trim() || 'Instagram photo',
        };

        setImages((prev) => [...prev, newImg].slice(0, 3));
        setActiveImageIndex(images.length);
        setUrlInput('');
        setAltTextInput('');
        setError(null);
      });
    } catch (err) {
      console.warn('Failed to load image from URL:', err);
      setError(err.message || 'Could not load image from this URL. Please verify the URL or choose one of the photo presets below.');
    } finally {
      setResolvingUrl(false);
    }
  };

  // Handle Preset selection
  const handleAddPreset = async (presetUrl, label) => {
    if (images.length >= 3) {
      setError('You can add up to 3 photos per post.');
      return;
    }
    setError(null);
    const newImg = {
      id: `url-preset-${Date.now()}-${images.length}`,
      url: presetUrl,
      width: 1080,
      height: 1080,
      altText: label.replace(/^[^\w\s]+/, '').trim() || 'Instagram photo',
    };
    setImages((prev) => [...prev, newImg].slice(0, 3));
    setActiveImageIndex(images.length);
    setUrlInput('');
  };

  // Remove a photo from selected list
  const handleRemoveImage = (indexToRemove) => {
    setImages((prev) => {
      const next = prev.filter((_, idx) => idx !== indexToRemove);
      if (activeImageIndex >= next.length) {
        setActiveImageIndex(Math.max(0, next.length - 1));
      }
      return next;
    });
  };

  // Update alt text for current active image
  const handleUpdateActiveAltText = (text) => {
    setImages((prev) =>
      prev.map((img, idx) => (idx === activeImageIndex ? { ...img, altText: text } : img))
    );
  };

  // Carousel navigation
  const handlePrev = () => {
    if (activeImageIndex > 0) setActiveImageIndex((prev) => prev - 1);
  };

  const handleNext = () => {
    if (activeImageIndex < images.length - 1) setActiveImageIndex((prev) => prev + 1);
  };

  // Quick hashtag insertion
  const handleInsertTag = (tag) => {
    setCaption((prev) => {
      const trimmed = prev.trim();
      if (!trimmed) return tag + ' ';
      return `${trimmed} ${tag} `;
    });
  };

  // Submit and create the post
  const handleSubmitPost = async (e) => {
    e.preventDefault();
    setError(null);

    const cleanText = caption.trim();
    if (!cleanText) {
      setError('Please write a caption or thoughts for your post (1 to 280 characters).');
      return;
    }

    if (cleanText.length > 280) {
      setError('Caption cannot exceed 280 characters.');
      return;
    }

    if (images.length === 0) {
      setError('Please add at least 1 image (up to 3) for your post.');
      return;
    }

    setLoading(true);

    try {
      const mediaPayload = images.map((img, idx) => ({
        position: idx,
        altText: (img.altText || '').trim() || `Photo by @${currentUser.handle}`,
        width: img.width || 1080,
        height: img.height || 1080,
        smallUrl: img.url,
        largeUrl: img.url,
      }));

      const newPost = await createOriginalPostApi({
        text: cleanText,
        media: mediaPayload,
      });

      if (onPostCreated) {
        onPostCreated(newPost);
      }
      onClose();
    } catch (err) {
      console.error('Failed to create post:', err);
      setError(err.message || 'Could not publish post. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const currentActiveImage = images[activeImageIndex] || null;

  return (
    <div className="create-post-overlay" role="dialog" aria-modal="true" aria-labelledby="create-post-title">
      <div className="create-post-overlay__backdrop" onClick={onClose} aria-hidden="true" />

      <div className="create-post-modal">
        {/* Header */}
        <header className="create-post-modal__header">
          <h2 id="create-post-title" className="create-post-modal__title">
            Create New Post
          </h2>
          <button
            type="button"
            className="create-post-modal__close-btn"
            onClick={onClose}
            aria-label="Close dialog"
          >
            &times;
          </button>
        </header>

        {error && (
          <div className="create-post-modal__error" role="alert">
            <span className="create-post-modal__error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <div className="create-post-modal__body">
          {/* Left Column: Media Stage & Image Pickers */}
          <section className="create-post-modal__media-stage">
            {images.length > 0 ? (
              <div className="create-post-preview">
                {/* Carousel Image Counter */}
                {images.length > 1 && (
                  <span className="create-post-preview__counter">
                    {activeImageIndex + 1} / {images.length}
                  </span>
                )}

                {/* Left/Right Navigation */}
                {images.length > 1 && activeImageIndex > 0 && (
                  <button
                    type="button"
                    className="create-post-preview__arrow create-post-preview__arrow--prev"
                    onClick={handlePrev}
                    aria-label="Previous image"
                  >
                    &#8249;
                  </button>
                )}
                {images.length > 1 && activeImageIndex < images.length - 1 && (
                  <button
                    type="button"
                    className="create-post-preview__arrow create-post-preview__arrow--next"
                    onClick={handleNext}
                    aria-label="Next image"
                  >
                    &#8250;
                  </button>
                )}

                {/* Active Preview Image */}
                <img
                  src={currentActiveImage.url}
                  alt={currentActiveImage.altText || 'Preview'}
                  className="create-post-preview__img"
                  onError={(e) => {
                    e.currentTarget.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=1080&q=80';
                  }}
                />

                {/* Carousel Pagination Dots */}
                {images.length > 1 && (
                  <div className="create-post-preview__dots">
                    {images.map((_, idx) => (
                      <button
                        key={idx}
                        type="button"
                        className={`create-post-preview__dot ${idx === activeImageIndex ? 'is-active' : ''}`}
                        onClick={() => setActiveImageIndex(idx)}
                        aria-label={`View photo ${idx + 1}`}
                      />
                    ))}
                  </div>
                )}
              </div>
            ) : (
              <div className="create-post-dropzone">
                <span className="create-post-dropzone__icon">📸</span>
                <p className="create-post-dropzone__heading">Upload up to 3 photos</p>
                <p className="create-post-dropzone__sub">
                  Select pictures from your computer or paste image links
                </p>
              </div>
            )}

            {/* Thumbnails list with delete buttons */}
            {images.length > 0 && (
              <div className="create-post-thumbnails">
                {images.map((img, idx) => (
                  <div
                    key={img.id}
                    className={`create-post-thumb ${idx === activeImageIndex ? 'is-active' : ''}`}
                    onClick={() => setActiveImageIndex(idx)}
                    title={`Photo ${idx + 1}`}
                  >
                    <img
                      src={img.url}
                      alt={`Thumbnail ${idx + 1}`}
                      onError={(e) => {
                        e.currentTarget.src = 'https://images.unsplash.com/photo-1546069901-ba9599a7e63c?auto=format&fit=crop&w=150&q=80';
                      }}
                    />
                    <button
                      type="button"
                      className="create-post-thumb__remove"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleRemoveImage(idx);
                      }}
                      title="Remove this photo"
                    >
                      &times;
                    </button>
                  </div>
                ))}
                {images.length < 3 && (
                  <button
                    type="button"
                    className="create-post-thumb__add"
                    onClick={() => fileInputRef.current?.click()}
                    title="Add another photo"
                  >
                    +
                  </button>
                )}
              </div>
            )}

            {/* Source Switcher: Upload File from PC vs Web URL */}
            <div className="create-post-tabs">
              <button
                type="button"
                className={`create-post-tab ${inputMode === 'file' ? 'is-active' : ''}`}
                onClick={() => setInputMode('file')}
              >
                📁 Upload from PC ({images.length}/3)
              </button>
              <button
                type="button"
                className={`create-post-tab ${inputMode === 'url' ? 'is-active' : ''}`}
                onClick={() => setInputMode('url')}
              >
                🔗 Paste Image URL
              </button>
            </div>

            {/* File Upload Mode */}
            {inputMode === 'file' && (
              <div className="create-post-file-picker">
                <input
                  ref={fileInputRef}
                  type="file"
                  id="create-post-file-input"
                  accept="image/png, image/jpeg, image/webp, image/gif"
                  multiple
                  onChange={handleFileChange}
                  style={{ display: 'none' }}
                />
                <button
                  type="button"
                  className="create-post-browse-btn"
                  onClick={() => fileInputRef.current?.click()}
                  disabled={images.length >= 3}
                >
                  {images.length >= 3 ? '✓ 3 Photos Selected' : 'Choose Pictures from Local Files'}
                </button>
                <span className="create-post-hint">Supports JPEG, PNG, WebP up to 3 photos</span>
              </div>
            )}

            {/* URL Input Mode */}
            {inputMode === 'url' && (
              <div className="create-post-url-section">
                <form className="create-post-url-form" onSubmit={handleAddUrl}>
                  <input
                    type="url"
                    className="create-post-url-input"
                    placeholder="Paste Unsplash image URL or photo link..."
                    value={urlInput}
                    onChange={(e) => setUrlInput(e.target.value)}
                    disabled={images.length >= 3 || resolvingUrl}
                  />
                  <button
                    type="submit"
                    className="create-post-url-btn"
                    disabled={!urlInput.trim() || images.length >= 3 || resolvingUrl}
                  >
                    {resolvingUrl ? 'Adding...' : 'Add Photo'}
                  </button>
                </form>

                <div className="create-post-url-presets">
                  <span className="create-post-url-presets-title">Quick Unsplash Presets:</span>
                  <div className="create-post-url-presets-list">
                    {UNSPLASH_PRESETS.map((p) => (
                      <button
                        key={p.label}
                        type="button"
                        className="create-post-preset-btn"
                        onClick={() => handleAddPreset(p.url, p.label)}
                        disabled={images.length >= 3 || resolvingUrl}
                        title={`Add ${p.label}`}
                      >
                        {p.label}
                      </button>
                    ))}
                  </div>
                </div>

                <span className="create-post-hint">
                  Auto-formatted with <code>?auto=format&fit=crop&w=1080&q=80</code>
                </span>
              </div>
            )}

            {/* Active Image Custom Alt Text */}
            {currentActiveImage && (
              <div className="create-post-alt-box">
                <label className="create-post-alt-label">
                  Alt Text for Photo {activeImageIndex + 1}:
                </label>
                <input
                  type="text"
                  className="create-post-alt-input"
                  placeholder="Describe this photo for screen readers (optional)"
                  value={currentActiveImage.altText}
                  onChange={(e) => handleUpdateActiveAltText(e.target.value)}
                  maxLength={100}
                />
              </div>
            )}
          </section>

          {/* Right Column: Caption, Tags & Share */}
          <section className="create-post-modal__details">
            {/* Author Chip */}
            <div className="create-post-author">
              <img
                src={
                  currentUser.avatar?.smallUrl ||
                  currentUser.avatar?.largeUrl ||
                  currentUser.avatarUrl ||
                  'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80'
                }
                alt={currentUser.handle}
                className="create-post-author__avatar"
                onError={(e) => {
                  e.target.src =
                    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80';
                }}
              />
              <div className="create-post-author__info">
                <span className="create-post-author__name">
                  {currentUser.displayName || currentUser.handle}
                </span>
                <span className="create-post-author__handle">@{currentUser.handle}</span>
              </div>
            </div>

            {/* Caption Textarea */}
            <div className="create-post-caption-box">
              <label htmlFor="create-post-caption" className="create-post-caption-label">
                Write a caption
              </label>
              <textarea
                id="create-post-caption"
                className="create-post-caption-input"
                placeholder="Write a caption, #hashtags, thoughts..."
                rows={5}
                value={caption}
                onChange={(e) => setCaption(e.target.value)}
                maxLength={280}
                required
              />
              <div className="create-post-counter">{caption.length} / 280</div>
            </div>

            {/* Hashtag Suggestions */}
            <div className="create-post-tags">
              <span className="create-post-tags__label">Suggested tags:</span>
              <div className="create-post-tags__list">
                {['#food', '#flowers', '#nature', '#books', '#music', '#cricket', '#life'].map(
                  (tag) => (
                    <button
                      key={tag}
                      type="button"
                      className="create-post-tag-chip"
                      onClick={() => handleInsertTag(tag)}
                    >
                      {tag}
                    </button>
                  )
                )}
              </div>
            </div>

            {/* Submit / Cancel Actions */}
            <div className="create-post-actions">
              <button
                type="button"
                className="create-post-btn create-post-btn--cancel"
                onClick={onClose}
                disabled={loading}
              >
                Cancel
              </button>
              <button
                type="button"
                className="create-post-btn create-post-btn--share"
                onClick={handleSubmitPost}
                disabled={loading || images.length === 0 || !caption.trim()}
              >
                {loading ? 'Publishing...' : 'Share Post'}
              </button>
            </div>
          </section>
        </div>
      </div>
    </div>
  );
}
