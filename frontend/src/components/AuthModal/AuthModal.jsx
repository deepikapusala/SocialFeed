import React, { useState, useEffect } from 'react';
import { loginApi, registerApi } from '../../utils/api';
import './AuthModal.css';

/**
 * Available Demo Profiles configured in the project.
 */
export const DEMO_PROFILES = [
  {
    name: 'Deepika',
    handle: 'deepu',
    password: 'TestPassword123!',
    icon: '👩',
    role: 'Creator',
  },
  {
    name: 'Sneha',
    handle: 'sneha',
    password: 'TestPassword123!',
    icon: '🌸',
    role: 'Aesthetics',
  },
  {
    name: 'Asha',
    handle: 'asha',
    password: 'TestPassword123!',
    icon: '📸',
    role: 'Photography',
  },
  {
    name: 'Anirudh',
    handle: 'ani',
    password: 'TestPassword123!',
    icon: '🎧',
    role: 'Tech & Music',
  },
  {
    name: 'Virat',
    handle: 'virat',
    password: 'TestPassword123!',
    icon: '🏃',
    role: 'Fitness & Travel',
  },
];

/**
 * Authentication Modal for Sign In and Sign Up.
 * Provides preconfigured one-click credentials for all 5 demo profiles.
 */
export function AuthModal({ isOpen, onClose, onAuthSuccess }) {
  const [isSignUp, setIsSignUp] = useState(false);
  const [selectedProfileIndex, setSelectedProfileIndex] = useState(0); // Default to Deepika or Asha
  const [handle, setHandle] = useState(DEMO_PROFILES[0].handle);
  const [displayName, setDisplayName] = useState(DEMO_PROFILES[0].name);
  const [password, setPassword] = useState(DEMO_PROFILES[0].password);
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');

  // Close on Escape key
  useEffect(() => {
    if (!isOpen) return;
    const handleKeyDown = (e) => {
      if (e.key === 'Escape') {
        onClose();
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [isOpen, onClose]);

  if (!isOpen) return null;

  const handleSelectProfile = (p, index) => {
    setSelectedProfileIndex(index);
    setHandle(p.handle);
    setPassword(p.password);
    setDisplayName(p.name);
    setErrorMessage('');
  };

  const handleDirectLogin = async (p) => {
    setHandle(p.handle);
    setPassword(p.password);
    setErrorMessage('');
    setLoading(true);

    try {
      const data = await loginApi({
        handle: p.handle,
        password: p.password,
      });
      onAuthSuccess(data.user, data.accessToken, data);
      onClose();
    } catch (err) {
      console.error('Authentication failed:', err);
      setErrorMessage(err.message || 'Authentication failed. Please check credentials.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setLoading(true);

    try {
      let data;
      if (isSignUp) {
        data = await registerApi({
          handle: handle.trim(),
          displayName: displayName.trim() || handle.trim(),
          password,
        });
      } else {
        data = await loginApi({
          handle: handle.trim(),
          password,
        });
      }

      onAuthSuccess(data.user, data.accessToken, data);
      onClose();
    } catch (err) {
      console.error('Authentication failed:', err);
      setErrorMessage(err.message || 'Authentication failed. Please check your credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-labelledby="auth-modal-title">
      <div className="auth-modal" onClick={(e) => e.stopPropagation()}>
        {/* Close Button */}
        <button
          type="button"
          className="auth-modal__close-btn"
          onClick={onClose}
          aria-label="Close authentication modal"
        >
          ✕
        </button>

        {/* Modal Header */}
        <div className="auth-modal__header">
          <div className="auth-modal__icon">📸</div>
          <h2 id="auth-modal-title" className="auth-modal__title">
            {isSignUp ? 'Create an Account' : 'Choose Account & Sign In'}
          </h2>
          <p className="auth-modal__subtitle">
            {isSignUp
              ? 'Join to follow creators and curate your personalized feed'
              : 'Pick one of your 5 profiles or enter credentials below'}
          </p>
        </div>

        {/* 5 Demo Profiles Quick Picker */}
        <div className="auth-profiles-picker">
          <div className="auth-profiles-picker__label">
            <span>✨ Select from 5 Profiles:</span>
            <span className="auth-profiles-picker__hint">Click to fill</span>
          </div>
          <div className="auth-profiles-grid">
            {DEMO_PROFILES.map((p, idx) => {
              const isSelected = handle.toLowerCase() === p.handle.toLowerCase();
              return (
                <button
                  key={p.handle}
                  type="button"
                  className={`auth-profile-chip ${isSelected ? 'auth-profile-chip--selected' : ''}`}
                  onClick={() => handleSelectProfile(p, idx)}
                  title={`Sign in as ${p.name} (@${p.handle})`}
                >
                  <span className="auth-profile-chip__icon">{p.icon}</span>
                  <div className="auth-profile-chip__info">
                    <span className="auth-profile-chip__name">{p.name}</span>
                    <span className="auth-profile-chip__handle">@{p.handle}</span>
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        {/* Active Profile Info Box */}
        <div className="auth-demo-card">
          <div className="auth-demo-card__header">
            <span className="auth-demo-card__badge">Selected Profile</span>
            <button
              type="button"
              className="auth-demo-card__btn"
              onClick={() => handleDirectLogin({ handle, password })}
              disabled={loading || !handle || !password}
              title="Quick login with 1 click"
            >
              ⚡ 1-Click Login as @{handle}
            </button>
          </div>
          <div className="auth-demo-card__credentials">
            <div className="auth-demo-card__item">
              <span className="auth-demo-card__label">Handle:</span>
              <code className="auth-demo-card__val">{handle}</code>
            </div>
            <div className="auth-demo-card__item">
              <span className="auth-demo-card__label">Password:</span>
              <code className="auth-demo-card__val">{password}</code>
            </div>
          </div>
        </div>

        {/* Tabs: Sign In / Sign Up */}
        <div className="auth-tabs" role="tablist">
          <button
            type="button"
            role="tab"
            aria-selected={!isSignUp}
            className={`auth-tab ${!isSignUp ? 'auth-tab--active' : ''}`}
            onClick={() => {
              setIsSignUp(false);
              setErrorMessage('');
            }}
          >
            Sign In
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={isSignUp}
            className={`auth-tab ${isSignUp ? 'auth-tab--active' : ''}`}
            onClick={() => {
              setIsSignUp(true);
              setErrorMessage('');
            }}
          >
            Sign Up
          </button>
        </div>

        {/* Error Notification */}
        {errorMessage && (
          <div className="auth-modal__error" role="alert">
            <span className="auth-modal__error-icon">⚠️</span>
            <span>{errorMessage}</span>
          </div>
        )}

        {/* Auth Form */}
        <form className="auth-form" onSubmit={handleSubmit}>
          {isSignUp && (
            <div className="auth-form__group">
              <label htmlFor="auth-display-name" className="auth-form__label">
                Display Name
              </label>
              <input
                id="auth-display-name"
                type="text"
                className="auth-form__input"
                placeholder="e.g. Deepika"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                required={isSignUp}
              />
            </div>
          )}

          <div className="auth-form__group">
            <label htmlFor="auth-handle" className="auth-form__label">
              Username / Handle
            </label>
            <div className="auth-form__input-wrapper">
              <span className="auth-form__prefix">@</span>
              <input
                id="auth-handle"
                type="text"
                className="auth-form__input auth-form__input--prefixed"
                placeholder="deepu"
                value={handle}
                onChange={(e) => setHandle(e.target.value)}
                required
                autoCapitalize="none"
                autoCorrect="off"
              />
            </div>
          </div>

          <div className="auth-form__group">
            <label htmlFor="auth-password" className="auth-form__label">
              Password
            </label>
            <div className="auth-form__input-wrapper">
              <input
                id="auth-password"
                type={showPassword ? 'text' : 'password'}
                className="auth-form__input auth-form__input--password"
                placeholder="deepika123"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                required
                minLength={6}
              />
              <button
                type="button"
                className="auth-form__toggle-pw"
                onClick={() => setShowPassword((prev) => !prev)}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? '🙈' : '👁️'}
              </button>
            </div>
          </div>

          <button
            type="submit"
            className="auth-form__submit-btn"
            disabled={loading || !handle || !password}
          >
            {loading ? (
              <span className="auth-form__spinner" />
            ) : isSignUp ? (
              'Create Account'
            ) : (
              `Sign In as @${handle || 'user'}`
            )}
          </button>
        </form>

        <div className="auth-modal__footer">
          {isSignUp ? (
            <p>
              Already have an account?{' '}
              <button
                type="button"
                className="auth-link-btn"
                onClick={() => {
                  setIsSignUp(false);
                  setErrorMessage('');
                }}
              >
                Sign In
              </button>
            </p>
          ) : (
            <p>
              Don't have an account yet?{' '}
              <button
                type="button"
                className="auth-link-btn"
                onClick={() => {
                  setIsSignUp(true);
                  setErrorMessage('');
                }}
              >
                Sign Up
              </button>
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
