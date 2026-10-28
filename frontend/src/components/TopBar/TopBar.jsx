import React from 'react';
import { NotificationPopover } from '../Notifications/NotificationPopover';
import './TopBar.css';

/**
 * TopBar Component
 * - Search bar: Type tag (e.g. #art, #nature) or press Enter to filter posts.
 * - Toggle button: Switch between Dark Mode (Pure Black 🌙) and Light Mode (Baby Pink 🌸).
 */
export function TopBar({
  searchQuery,
  onSearchChange,
  onClearSearch,
  theme,
  onToggleTheme,
  currentUser,
  onOpenAuth,
  onOpenEditProfile,
  onOpenCreatePost,
  onLogout,
  onSelectPost,
  onViewProfile,
}) {
  // Prevent form submission page refresh when pressing Enter
  const handleSubmit = (e) => {
    e.preventDefault();
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      // Blur input on Enter to close mobile keyboard & confirm search
      e.target.blur();
    }
  };

  return (
    <header className="topbar" role="banner">
      <div className="topbar__container">

        {/* Left / Center-left: Search Bar */}
        <form className="topbar__search-wrapper" onSubmit={handleSubmit}>
          <span className="topbar__search-icon" aria-hidden="true">
            🔍
          </span>
          <input
            type="text"
            className="topbar__search-input"
            placeholder="Search caption, username (@deepu), or bio..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Search posts by caption, username, or bio"
            autoComplete="off"
          />
          {searchQuery && (
            <button
              type="button"
              className="topbar__clear-btn"
              onClick={onClearSearch}
              aria-label="Clear search"
              title="Clear search"
            >
              ✕
            </button>
          )}
        </form>

        {/* Middle: Auth Box & + Create Post Button */}
        <div className="topbar__auth-wrapper">
          {/* Instagram-style + Create Button */}
          <button
            type="button"
            className="topbar__create-post-btn"
            onClick={currentUser ? onOpenCreatePost : onOpenAuth}
            title={currentUser ? 'Create a new post' : 'Sign in to create a post'}
            aria-label="Create a new post"
          >
            <span className="topbar__create-post-icon">+</span>
            <span className="topbar__create-post-text">Create</span>
          </button>

          {currentUser ? (
            <div className="topbar__user-chip">
              {currentUser.avatar?.smallUrl || currentUser.avatar?.largeUrl || currentUser.avatarUrl ? (
                <img
                  src={
                    currentUser.avatar?.smallUrl ||
                    currentUser.avatar?.largeUrl ||
                    currentUser.avatarUrl
                  }
                  alt={currentUser.handle}
                  className="topbar__user-avatar"
                  onClick={() => onViewProfile && onViewProfile(currentUser.handle)}
                  style={{ cursor: onViewProfile ? 'pointer' : 'default' }}
                  title={`View profile of @${currentUser.handle}`}
                  onError={(e) => {
                    e.target.style.display = 'none';
                    if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                  }}
                />
              ) : null}
              <div
                className="topbar__user-avatar-fallback"
                onClick={() => onViewProfile && onViewProfile(currentUser.handle)}
                style={{
                  display:
                    currentUser.avatar?.smallUrl || currentUser.avatar?.largeUrl || currentUser.avatarUrl
                      ? 'none'
                      : 'flex',
                  cursor: onViewProfile ? 'pointer' : 'default',
                }}
                title={`View profile of @${currentUser.handle}`}
              >
                {(currentUser.displayName || currentUser.handle || 'U').charAt(0).toUpperCase()}
              </div>
              <div className="topbar__user-meta">
                <span
                  className="topbar__user-handle"
                  onClick={() => onViewProfile && onViewProfile(currentUser.handle)}
                  style={{ cursor: onViewProfile ? 'pointer' : 'default' }}
                  title={`View profile of @${currentUser.handle}`}
                >
                  @{currentUser.handle}
                </span>
                <button
                  type="button"
                  className="topbar__edit-profile-btn"
                  onClick={onOpenEditProfile}
                  title="Edit your display name, handle & bio"
                >
                  Edit Profile
                </button>
              </div>
              <button
                type="button"
                className="topbar__logout-btn"
                onClick={onLogout}
                title="Sign out of account"
              >
                Log Out
              </button>
            </div>
          ) : (
            <button
              type="button"
              className="topbar__signin-btn"
              onClick={onOpenAuth}
              title="Sign in or register demo user"
            >
              <span className="topbar__signin-icon">🔑</span>
              <span className="topbar__signin-text">Sign In / Sign Up</span>
              <span className="topbar__signin-badge">5 Profiles</span>
            </button>
          )}
        </div>

        {/* Heart Notifications Icon (Between Sign In/Up Box and Theme Toggle) */}
        <div className="topbar__notif-wrapper">
          <NotificationPopover
            currentUser={currentUser}
            onOpenAuth={onOpenAuth}
            onSelectPost={onSelectPost}
          />
        </div>

        {/* Right / Center-right: Theme Toggle (Dark Mode 🌙 / Baby Pink 🌸) */}
        <div className="topbar__theme-wrapper">
          <button
            type="button"
            className={`topbar__theme-btn ${theme === 'light' ? 'topbar__theme-btn--light' : 'topbar__theme-btn--dark'}`}
            onClick={onToggleTheme}
            aria-label={`Switch to ${theme === 'dark' ? 'Baby Pink light mode' : 'Pure dark mode'}`}
            title={`Switch to ${theme === 'dark' ? 'Baby Pink Mode' : 'Dark Mode'}`}
          >
            <span className="topbar__theme-icon">
              {theme === 'dark' ? '🌙' : '🌸'}
            </span>
            <span className="topbar__theme-label">
              {theme === 'dark' ? 'Dark Mode' : 'Baby Pink'}
            </span>
            <span className="topbar__theme-switch">
              <span className="topbar__theme-thumb" />
            </span>
          </button>
        </div>

      </div>
    </header>
  );
}
