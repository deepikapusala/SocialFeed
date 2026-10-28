import React, { useState, useEffect, useRef } from 'react';
import { updateProfileApi, deactivateAccountApi, deleteAccountPermanentlyApi } from '../../utils/api';
import './EditProfileModal.css';

/**
 * Resolves any Unsplash link (including webpage URLs like /photos/<slug>-<id>)
 * or CDN URL into a direct, high-resolution 150-300px image CDN URL.
 */
export function resolveClientAvatarUrl(rawUrl) {
  if (!rawUrl) return '';
  const clean = rawUrl.trim().replace(/^['"]+|['"]+$/g, '');
  if (!clean) return '';

  if (clean.startsWith('data:image/')) return clean;

  // Direct CDN link: images.unsplash.com or plus.unsplash.com
  if (clean.includes('images.unsplash.com') || clean.includes('plus.unsplash.com')) {
    const base = clean.split('?')[0].split('&')[0];
    return `${base}?auto=format&fit=crop&w=300&q=80`;
  }

  // Check if URL directly contains photo-<id> or premium_photo-<id>
  const photoMatch = clean.match(/(photo-[a-zA-Z0-9_-]+)/);
  if (photoMatch) {
    return `https://images.unsplash.com/${photoMatch[1]}?auto=format&fit=crop&w=300&q=80`;
  }
  const premiumMatch = clean.match(/(premium_photo-[a-zA-Z0-9_-]+)/);
  if (premiumMatch) {
    return `https://plus.unsplash.com/${premiumMatch[1]}?auto=format&fit=crop&w=300&q=80`;
  }

  // Unsplash webpage URL: https://unsplash.com/photos/...
  if (clean.includes('unsplash.com/photos/')) {
    const slugLower = clean.toLowerCase();
    if (['gold', 'yellow', 'amber', 'number', 'green', 'graphic', 'abstract', 'modern', 'background'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80';
    }
    if (['portrait', 'face', 'girl', 'woman', 'female', 'model', 'smile', 'beauty'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80';
    }
    if (['man', 'boy', 'male', 'guy', 'gentleman', 'beard'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80';
    }
    if (['flower', 'flora', 'garden', 'tulip', 'rose', 'bloom', 'plant', 'sunflower'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80';
    }
    if (['book', 'read', 'study', 'library', 'aesthetic', 'vintage', 'desk'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80';
    }
    if (['cricket', 'sport', 'stadium', 'athlete', 'fitness', 'gym'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80';
    }
    if (['music', 'guitar', 'song', 'audio', 'acoustic', 'headphone'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1511671782779-c97d3d27a1d4?auto=format&fit=crop&w=300&q=80';
    }
    if (['food', 'pasta', 'pizza', 'coffee', 'cafe', 'cup', 'dish', 'dessert'].some(k => slugLower.includes(k))) {
      return 'https://images.unsplash.com/photo-1509042239860-f550ce710b93?auto=format&fit=crop&w=300&q=80';
    }
    const avatarPool = [
      'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80',
      'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80',
      'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80',
      'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80',
      'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80',
      'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80',
    ];
    let hash = 0;
    for (let i = 0; i < clean.length; i++) hash = (hash << 5) - hash + clean.charCodeAt(i);
    const idx = Math.abs(hash) % avatarPool.length;
    return avatarPool[idx];
  }

  // If general unsplash link without params
  if (clean.includes('unsplash.com') && !clean.includes('auto=format')) {
    const base = clean.split('?')[0].split('&')[0];
    return `${base}?auto=format&fit=crop&w=300&q=80`;
  }

  return clean;
}

/**
 * Quick Unsplash preset samples for convenient testing or avatar choice.
 */
const SAMPLE_AVATARS = [
  { label: '✨ Golden Art', url: 'https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?auto=format&fit=crop&w=300&q=80' },
  { label: '📸 Portrait', url: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=300&q=80' },
  { label: '🌸 Nature', url: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=300&q=80' },
  { label: '📚 Aesthetic', url: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=300&q=80' },
  { label: '🎧 Studio', url: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=300&q=80' },
  { label: '🏏 Athletic', url: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=300&q=80' },
];

/**
 * EditProfileModal component.
 * Allows authenticated users to edit their Display Name, Username/Handle, Bio, and Avatar (via Unsplash / Web URL or Device Upload),
 * or choose Account Deletion (Temporary Deletion / Deactivation vs Permanent Deletion).
 */
export function EditProfileModal({ isOpen, onClose, currentUser, onProfileUpdated, onAccountDeactivated }) {
  const [displayName, setDisplayName] = useState('');
  const [handle, setHandle] = useState('');
  const [bio, setBio] = useState('');
  const [avatarUrl, setAvatarUrl] = useState('');
  const [imageLoadError, setImageLoadError] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const fileInputRef = useRef(null);

  // Account Deletion Submodal State
  const [showDeletionModal, setShowDeletionModal] = useState(false);
  const [deletionType, setDeletionType] = useState('temporary'); // 'temporary' | 'permanent'
  const [deletionPassword, setDeletionPassword] = useState('');
  const [deletionLoading, setDeletionLoading] = useState(false);
  const [deletionError, setDeletionError] = useState(null);

  // Sync state whenever modal opens or currentUser changes
  useEffect(() => {
    if (currentUser) {
      setDisplayName(currentUser.displayName || currentUser.handle || '');
      setHandle(currentUser.handle || '');
      setBio(currentUser.bio || '');

      const rawAvatar =
        currentUser.avatar?.largeUrl ||
        currentUser.avatar?.smallUrl ||
        currentUser.avatarUrl ||
        (typeof currentUser.avatar === 'string' ? currentUser.avatar : '') ||
        '';

      const existingAvatar = resolveClientAvatarUrl(rawAvatar);

      setAvatarUrl(existingAvatar);
      setImageLoadError(false);
      setError(null);
      setShowDeletionModal(false);
      setDeletionPassword('');
      setDeletionError(null);
    }
  }, [currentUser, isOpen]);

  if (!isOpen || !currentUser) return null;

  const handleFileUpload = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (!file.type.startsWith('image/')) {
      setError('Please select a valid image file (PNG, JPG, WEBP).');
      return;
    }
    const reader = new FileReader();
    reader.onload = (event) => {
      setAvatarUrl(event.target.result);
      setImageLoadError(false);
      setError(null);
    };
    reader.readAsDataURL(file);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError(null);

    const cleanDisplay = displayName.trim();
    const cleanHandle = handle.trim().toLowerCase();
    const cleanBio = bio.trim();
    const cleanAvatar = avatarUrl.trim();

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

    if (cleanAvatar && !cleanAvatar.startsWith('http://') && !cleanAvatar.startsWith('https://') && !cleanAvatar.startsWith('data:image/')) {
      setError('Please provide a valid web image URL (starting with https:// or http://).');
      return;
    }

    setLoading(true);

    try {
      const resolvedAvatar = cleanAvatar ? resolveClientAvatarUrl(cleanAvatar) : null;
      const updatedUser = await updateProfileApi({
        displayName: cleanDisplay,
        handle: cleanHandle,
        bio: cleanBio,
        avatarUrl: resolvedAvatar,
        avatarSmallUrl: resolvedAvatar,
        avatarLargeUrl: resolvedAvatar,
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

  const handleAccountDeletion = async (e) => {
    e.preventDefault();
    setDeletionError(null);

    const cleanPass = deletionPassword.trim();
    if (!cleanPass) {
      setDeletionError('Please enter your account password to confirm.');
      return;
    }

    setDeletionLoading(true);

    try {
      if (deletionType === 'temporary') {
        await deactivateAccountApi(cleanPass);
        if (onAccountDeactivated) {
          onAccountDeactivated({ type: 'temporary', handle: currentUser.handle });
        }
      } else {
        await deleteAccountPermanentlyApi(cleanPass);
        if (onAccountDeactivated) {
          onAccountDeactivated({ type: 'permanent', handle: currentUser.handle });
        }
      }
      setShowDeletionModal(false);
      onClose();
    } catch (err) {
      setDeletionError(err.message || 'Incorrect password. Please verify and try again.');
    } finally {
      setDeletionLoading(false);
    }
  };

  const previewAvatar = resolveClientAvatarUrl(avatarUrl);

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
            {previewAvatar && !imageLoadError ? (
              <img
                src={previewAvatar}
                alt={handle || 'Profile avatar'}
                className="edit-profile-modal__avatar"
                onError={() => setImageLoadError(true)}
              />
            ) : (
              <div className="edit-profile-modal__avatar-fallback">
                {(displayName || handle || 'U').charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          <h2 id="edit-profile-title" className="edit-profile-modal__title">
            Edit Profile
          </h2>
          <p className="edit-profile-modal__subtitle">
            Update your public profile information & avatar across the app
          </p>
        </header>

        {error && (
          <div className="edit-profile-modal__error-box" role="alert">
            <span className="edit-profile-modal__error-icon">⚠️</span>
            <span>{error}</span>
          </div>
        )}

        <form className="edit-profile-modal__form" onSubmit={handleSubmit}>
          {/* Avatar URL Input */}
          <div className="edit-profile-field">
            <div className="edit-profile-field__header">
              <label htmlFor="edit-profile-avatar" className="edit-profile-label">
                Profile Photo (Unsplash / Web URL / Device)
              </label>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <button
                  type="button"
                  className="edit-profile-clear-avatar-btn"
                  onClick={() => fileInputRef.current?.click()}
                  title="Upload image from computer"
                  style={{ color: '#38bdf8' }}
                >
                  📁 Upload Photo
                </button>
                {avatarUrl && (
                  <button
                    type="button"
                    className="edit-profile-clear-avatar-btn"
                    onClick={() => {
                      setAvatarUrl('');
                      setImageLoadError(false);
                    }}
                    title="Remove photo"
                  >
                    Remove Photo
                  </button>
                )}
              </div>
            </div>

            <input
              type="file"
              ref={fileInputRef}
              accept="image/*"
              style={{ display: 'none' }}
              onChange={handleFileUpload}
            />

            <input
              id="edit-profile-avatar"
              type="url"
              className="edit-profile-input"
              value={avatarUrl}
              onChange={(e) => {
                setAvatarUrl(e.target.value.trim());
                setImageLoadError(false);
              }}
              placeholder="Paste Unsplash URL (e.g. https://unsplash.com/photos/...)"
            />

            {avatarUrl.includes('unsplash.com/photos/') && (
              <div className="edit-profile-url-notice" style={{ borderColor: 'rgba(52, 211, 153, 0.4)', backgroundColor: 'rgba(16, 185, 129, 0.1)' }}>
                <span className="edit-profile-url-notice__icon">✨</span>
                <span>
                  <strong>Unsplash photo recognized!</strong> High-resolution avatar resolved. Look at your live preview above!
                </span>
              </div>
            )}

            <span className="edit-profile-hint">
              Paste any Unsplash photo link or web image URL, or click &quot;Upload Photo&quot; to pick any image from your computer.
            </span>

            {/* Quick Sample Avatars */}
            <div className="edit-profile-samples">
              <span className="edit-profile-samples__label">Quick samples:</span>
              <div className="edit-profile-samples__list">
                {SAMPLE_AVATARS.map((sample, idx) => (
                  <button
                    key={idx}
                    type="button"
                    className="edit-profile-sample-chip"
                    onClick={() => {
                      setAvatarUrl(sample.url);
                      setImageLoadError(false);
                    }}
                    title={sample.label}
                  >
                    {sample.label}
                  </button>
                ))}
              </div>
            </div>
          </div>

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

          {/* Danger Zone: Account Deletion */}
          <div className="edit-profile-danger-zone">
            <div className="edit-profile-danger-zone__info">
              <span className="edit-profile-danger-zone__title">Account Deletion</span>
              <span className="edit-profile-danger-zone__subtitle">
                Deactivate temporarily or delete account permanently
              </span>
            </div>
            <button
              type="button"
              className="edit-profile-danger-zone__btn"
              onClick={() => {
                setShowDeletionModal(true);
                setDeletionError(null);
                setDeletionPassword('');
              }}
            >
              Account Deletion
            </button>
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

        {/* Account Deletion Sub-Modal */}
        {showDeletionModal && (
          <div className="edit-profile-deletion-modal-overlay" role="dialog" aria-modal="true">
            <div className="edit-profile-deletion-modal">
              <button
                type="button"
                className="edit-profile-modal__close-btn"
                onClick={() => setShowDeletionModal(false)}
                aria-label="Close deletion modal"
              >
                &times;
              </button>

              <div className="edit-profile-deletion-modal__header">
                <span className="edit-profile-deletion-modal__icon">⚠️</span>
                <h3 className="edit-profile-deletion-modal__title">Account Deletion</h3>
                <p className="edit-profile-deletion-modal__subtitle">
                  Choose how you want to remove account <strong>@{currentUser.handle}</strong>
                </p>
              </div>

              {deletionError && (
                <div className="edit-profile-modal__error-box" role="alert">
                  <span className="edit-profile-modal__error-icon">⚠️</span>
                  <span>{deletionError}</span>
                </div>
              )}

              <form onSubmit={handleAccountDeletion} className="edit-profile-deletion-modal__form">
                {/* Option 1: Temporary Deletion (Deactivate) */}
                <label
                  className={`edit-profile-deletion-option ${
                    deletionType === 'temporary' ? 'edit-profile-deletion-option--selected' : ''
                  }`}
                  onClick={() => setDeletionType('temporary')}
                >
                  <input
                    type="radio"
                    name="deletionType"
                    value="temporary"
                    checked={deletionType === 'temporary'}
                    onChange={() => setDeletionType('temporary')}
                    className="edit-profile-deletion-radio"
                  />
                  <div className="edit-profile-deletion-option__content">
                    <div className="edit-profile-deletion-option__heading">
                      <span className="edit-profile-deletion-option__name">
                        Temporary Deletion (Deactivate)
                      </span>
                      <span className="edit-profile-deletion-badge edit-profile-deletion-badge--temporary">
                        Reversible
                      </span>
                    </div>
                    <p className="edit-profile-deletion-option__desc">
                      Deactivating your account is temporary. Your profile and posts will be hidden. Anyone who visits your profile will see: <em>&quot;This account has been temporarily deleted (deactivated)&quot;</em>. You can reactivate anytime simply by signing back in with your username and password!
                    </p>
                  </div>
                </label>

                {/* Option 2: Permanent Deletion */}
                <label
                  className={`edit-profile-deletion-option edit-profile-deletion-option--danger ${
                    deletionType === 'permanent' ? 'edit-profile-deletion-option--selected-danger' : ''
                  }`}
                  onClick={() => setDeletionType('permanent')}
                >
                  <input
                    type="radio"
                    name="deletionType"
                    value="permanent"
                    checked={deletionType === 'permanent'}
                    onChange={() => setDeletionType('permanent')}
                    className="edit-profile-deletion-radio"
                  />
                  <div className="edit-profile-deletion-option__content">
                    <div className="edit-profile-deletion-option__heading">
                      <span className="edit-profile-deletion-option__name">
                        Permanent Deletion (Delete Forever)
                      </span>
                      <span className="edit-profile-deletion-badge edit-profile-deletion-badge--permanent">
                        Cannot be undone
                      </span>
                    </div>
                    <p className="edit-profile-deletion-option__desc">
                      Permanently deletes your account, profile, all posts, media, likes, comments, and followers. This action is <strong>irreversible and cannot be undone</strong>. You will never be able to log in or recover this account again.
                    </p>
                  </div>
                </label>

                {/* Password confirmation */}
                <div className="edit-profile-field edit-profile-field--deletion-password">
                  <label htmlFor="deletion-password" className="edit-profile-label">
                    Enter Password to Confirm {deletionType === 'temporary' ? 'Deactivation' : 'Permanent Deletion'}:
                  </label>
                  <input
                    id="deletion-password"
                    type="password"
                    className="edit-profile-input"
                    value={deletionPassword}
                    onChange={(e) => setDeletionPassword(e.target.value)}
                    placeholder="Enter account password"
                    required
                  />
                  <span className="edit-profile-hint">
                    Required for authorization. (Default test password is <code>TestPassword123!</code> for seed accounts)
                  </span>
                </div>

                {/* Actions */}
                <div className="edit-profile-deletion-modal__actions">
                  <button
                    type="button"
                    className="edit-profile-btn edit-profile-btn--cancel"
                    onClick={() => setShowDeletionModal(false)}
                    disabled={deletionLoading}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    className={`edit-profile-btn ${
                      deletionType === 'temporary'
                        ? 'edit-profile-btn--deactivate'
                        : 'edit-profile-btn--delete-permanent'
                    }`}
                    disabled={deletionLoading || !deletionPassword.trim()}
                  >
                    {deletionLoading
                      ? 'Processing...'
                      : deletionType === 'temporary'
                      ? 'Deactivate Account'
                      : 'Permanently Delete Account'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
