import React from 'react';
import './TopBar.css';

/**
 * TopBar Component
 * - Search bar: Type tag (e.g. #art, #nature) or press Enter to filter posts.
 * - Toggle button: Switch between Dark Mode (Pure Black 🌙) and Light Mode (Baby Pink 🌸).
 */
export function TopBar({ searchQuery, onSearchChange, onClearSearch, theme, onToggleTheme }) {
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
            placeholder="Search tags (e.g. #art, #nature, #coffee)..."
            value={searchQuery}
            onChange={(e) => onSearchChange(e.target.value)}
            onKeyDown={handleKeyDown}
            aria-label="Search posts by tag or caption"
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
