import React, { useState, useEffect } from 'react';
import { updateProfileApi } from '../../utils/api';
import './EditProfileModal.css';

/**
 * EditProfileModal component.
 * Allows authenticated users to edit their Display Name, Username/Handle, and Bio.
 * Persists updates to PostgreSQL users table via PATCH /users/me.
 */
export function EditProfileModal({ isOpen, onClose, currentUser, onProfileUpdated }) {
  const [displayName, setDisplayName] = useState('');
  const [handle, setHandle] = useState('');
  const [bio, setBio] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  // Sync state whenever modal opens or currentUser changes
  useEffect(() => {
    if (currentUser) {
      setDisplayName(currentUser.displayName || currentUser.handle || '');
      setHandle(currentUser.handle || '');
      setBio(currentUser.bio || '');
      setError(null);
    }
  }, [currentUser, isOpen]);

  if (!isOpen || !currentUser) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const cleanDisplay = displayName.trim();
    const cleanHandle = handle.trim().toLowerCase();
    const cleanBio = bio.trim();

    if (!cleanDisplay) {
      setError('Display name cannot be empty.');
      return;
    }

    if (!cleanHandle) {
      setError('Username / handle cannot be empty.');
      return;
    }

    if (!/^[a-z0-9_]+$/.test(cleanHandle)) {
      setError('Username can only contain lowercase letters, numbers, and underscores.');
      return;
    }

    setLoading(true);

    try {
      const updatedUser = await updateProfileApi({
        displayName: cleanDisplay,
        handle: cleanHandle,
        bio: cleanBio,
      });

      if (onProfileUpdated) {
        onProfileUpdated(updatedUser);
      }
      onClose();
    } catch (err) {
      setError(err.message || 'Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const userAvatar =
    currentUser.avatar?.smallUrl ||
    currentUser.avatar?.largeUrl ||
    currentUser.avatarUrl ||
    currentUser.avatar ||
    null;

  return (
    <div className="edit-profile-overlay" role="dialog" aria-modal="true" aria-labelledby="edit-profile-title">
      <div className="edit-profile-overlay__backdrop" onClick={onClose} aria-hidden="true" />

      <div className="edit-profile-modal">
        <button
          type="button"
          className="edit-profile-modal__close-btn"
          onClick={onClose}
          aria-label="Close edit profile modal"
        >
          &times;
        </button>

        <header className="edit-profile-modal__header">
          <div className="edit-profile-modal__avatar-wrapper">
            {userAvatar ? (
              <img
                src={userAvatar}
                alt={currentUser.handle}
                className="edit-profile-modal__avatar"
                onError={(e) => {
                  e.target.style.display = 'none';
                  if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className="edit-profile-modal__avatar-fallback"
              style={{ display: userAvatar ? 'none' : 'flex' }}
            >
              {(displayName || handle || 'U').charAt(0).toUpperCase()}
            </div>
          </div>

          <h2 id="edit-profile-title" className="edit-profile-modal__title">
            Edit Profile
          </h2>
          <p className="edit-profile-modal__subtitle">
            Update your public profile information across the app
          </p>
        </header>

        {error && (
          <div className="edit-profile-modal__error-box" role="alert">
            <span className="edit-profile-modal__error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form className="edit-profile-modal__form" onSubmit={handleSubmit}>
          {/* Display Name Input */}
          <div className="edit-profile-field">
            <label htmlFor="edit-profile-display-name" className="edit-profile-label">
              Display Name
            </label>
            <input
              id="edit-profile-display-name"
              type="text"
              className="edit-profile-input"
              value={displayName}
              onChange={(e) => setDisplayName(e.target.value)}
              placeholder="e.g. Deepika"
              maxLength={50}
              required
            />
          </div>

          {/* Username / Handle Input */}
          <div className="edit-profile-field">
            <label htmlFor="edit-profile-handle" className="edit-profile-label">
              Username / Handle
            </label>
            <div className="edit-profile-input-wrapper">
              <span className="edit-profile-prefix">@</span>
              <input
                id="edit-profile-handle"
                type="text"
                className="edit-profile-input edit-profile-input--with-prefix"
                value={handle}
                onChange={(e) => setHandle(e.target.value.toLowerCase().replace(/[^a-z0-9_]/g, ''))}
                placeholder="username"
                maxLength={30}
                required
              />
            </div>
            <span className="edit-profile-hint">Lowercase letters, numbers, and underscores only.</span>
          </div>

          {/* Bio Input */}
          <div className="edit-profile-field">
            <label htmlFor="edit-profile-bio" className="edit-profile-label">
              Bio
            </label>
            <textarea
              id="edit-profile-bio"
              className="edit-profile-textarea"
              value={bio}
              onChange={(e) => setBio(e.target.value)}
              placeholder="Tell others about your niche, hobbies, or passion..."
              maxLength={500}
              rows={3}
            />
            <span className="edit-profile-counter">{bio.length} / 500</span>
          </div>

          {/* Actions */}
          <div className="edit-profile-modal__actions">
            <button
              type="button"
              className="edit-profile-btn edit-profile-btn--cancel"
              onClick={onClose}
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="edit-profile-btn edit-profile-btn--submit"
              disabled={loading || !displayName.trim() || !handle.trim()}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
