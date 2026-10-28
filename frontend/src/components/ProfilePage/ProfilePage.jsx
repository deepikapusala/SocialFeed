import React, { useState, useEffect, useCallback } from 'react';
import {
  fetchUserProfileApi,
  fetchUserPostsApi,
  fetchUserFollowersApi,
  fetchUserFollowingApi,
} from '../../utils/api';
import { PhotoCard } from '../PhotoCard/PhotoCard';
import './ProfilePage.css';

/**
 * Instagram-style Profile Page Component.
 * Supports:
 * - Profile header with avatar, handle, display name, bio
 * - Stat counters: Posts, Followers (clickable), Following (clickable)
 * - Followers & Following interactive modal dialogs
 * - Tabbed navigation: Posts (My Feed), Reposts, Saved
 * - Interactive post grid opening PhotoViewer on click
 * - Follow / Unfollow toggle for other creators
 * - Edit Profile button for own profile
 */
export function ProfilePage({
  targetHandleOrId,
  currentUser,
  onBackToFeed,
  onSelectPost,
  onOpenEditProfile,
  onOpenAuth,
  onToggleFollow,
  followingMap = {},
  onNavigateProfile,
}) {
  const [profile, setProfile] = useState(null);
  const [posts, setPosts] = useState([]);
  const [activeTab, setActiveTab] = useState('posts'); // 'posts' | 'reposts' | 'saved'
  const [loading, setLoading] = useState(true);
  const [postsLoading, setPostsLoading] = useState(false);
  const [error, setError] = useState(null);

  // Followers & Following modal state
  const [modalType, setModalType] = useState(null); // 'followers' | 'following' | null
  const [userList, setUserList] = useState([]);
  const [userListLoading, setUserListLoading] = useState(false);

  const cleanTarget = (targetHandleOrId || '').replace(/^@/, '');

  // Is viewer looking at their own profile?
  const isOwnProfile = Boolean(
    currentUser &&
    profile &&
    (currentUser.id === profile.id ||
      currentUser.handle?.toLowerCase() === profile.handle?.toLowerCase())
  );

  const isFollowing = Boolean(
    profile && followingMap[profile.handle?.toLowerCase()]
  );

  // 1. Load user profile details
  const loadProfile = useCallback(async () => {
    if (!cleanTarget) return;
    setLoading(true);
    setError(null);
    try {
      const data = await fetchUserProfileApi(cleanTarget);
      setProfile(data);
    } catch (err) {
      console.error('Failed to load profile:', err);
      setError(err.message || 'Profile not found');
    } finally {
      setLoading(false);
    }
  }, [cleanTarget]);

  useEffect(() => {
    loadProfile();
  }, [loadProfile]);

  // 2. Load tab posts (posts or reposts)
  useEffect(() => {
    if (!cleanTarget || activeTab === 'saved') return;
    let isCancelled = false;
    setPostsLoading(true);

    fetchUserPostsApi(cleanTarget, activeTab)
      .then((res) => {
        if (!isCancelled) {
          setPosts(res.items || []);
        }
      })
      .catch((err) => {
        console.warn(`Failed to fetch ${activeTab} for user:`, err);
        if (!isCancelled) {
          setPosts([]);
        }
      })
      .finally(() => {
        if (!isCancelled) {
          setPostsLoading(false);
        }
      });

    return () => {
      isCancelled = true;
    };
  }, [cleanTarget, activeTab]);

  // 3. Open followers or following modal
  const handleOpenListModal = async (type) => {
    setModalType(type);
    setUserListLoading(true);
    setUserList([]);
    try {
      if (type === 'followers') {
        const list = await fetchUserFollowersApi(cleanTarget);
        setUserList(list);
      } else if (type === 'following') {
        const list = await fetchUserFollowingApi(cleanTarget);
        setUserList(list);
      }
    } catch (err) {
      console.warn(`Failed to fetch ${type}:`, err);
      setUserList([]);
    } finally {
      setUserListLoading(false);
    }
  };

  const handleCloseListModal = () => {
    setModalType(null);
    setUserList([]);
  };

  const handleFollowToggle = () => {
    if (!currentUser) {
      if (onOpenAuth) onOpenAuth();
      return;
    }
    if (!profile) return;

    if (onToggleFollow) {
      onToggleFollow({
        authorId: profile.id,
        authorHandle: profile.handle,
        shouldFollow: !isFollowing,
      });
    }

    // Update local profile followers count optimistically
    setProfile((prev) => {
      if (!prev) return null;
      const currentFollowers = prev.followersCount ?? prev.followerCount ?? 0;
      const updatedCount = !isFollowing
        ? currentFollowers + 1
        : Math.max(0, currentFollowers - 1);
      return {
        ...prev,
        followersCount: updatedCount,
        followerCount: updatedCount,
      };
    });
  };

  if (loading) {
    return (
      <div className="profile-page profile-page--loading">
        <div className="profile-page__spinner" />
        <p>Loading profile...</p>
      </div>
    );
  }

  if (error || !profile) {
    return (
      <div className="profile-page profile-page--error">
        <h2>Profile Not Found</h2>
        <p>{error || "The profile you requested doesn't exist or is unavailable."}</p>
        <button
          type="button"
          className="profile-page__back-btn"
          onClick={onBackToFeed}
        >
          ← Back to Feed
        </button>
      </div>
    );
  }

  const avatarUrl =
    profile.avatar?.largeUrl ||
    profile.avatar?.smallUrl ||
    profile.avatarUrl ||
    (typeof profile.avatar === 'string' ? profile.avatar : null);

  const postsCount = profile.postsCount ?? profile.postCount ?? posts.length;
  const followersCount = profile.followersCount ?? profile.followerCount ?? 0;
  const followingCount = profile.followingCount ?? 0;

  return (
    <div className="profile-page">
      {/* Top Breadcrumb Navigation */}
      <div className="profile-page__top-nav">
        <button
          type="button"
          className="profile-page__back-btn"
          onClick={onBackToFeed}
          title="Return to main feed"
        >
          ← Back to Feed
        </button>
      </div>

      {/* Profile Header (Instagram layout) */}
      <header className="profile-header">
        <div className="profile-header__avatar-container">
          <div className="profile-header__avatar-ring">
            {avatarUrl ? (
              <img
                src={avatarUrl}
                alt={profile.displayName || profile.handle}
                className="profile-header__avatar"
                onError={(e) => {
                  e.target.style.display = 'none';
                  if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className="profile-header__avatar-fallback"
              style={{ display: avatarUrl ? 'none' : 'flex' }}
            >
              {(profile.displayName || profile.handle || 'U').charAt(0).toUpperCase()}
            </div>
          </div>
        </div>

        <div className="profile-header__info">
          {/* Top Line: Username & Action Buttons */}
          <div className="profile-header__title-row">
            <h1 className="profile-header__handle">@{profile.handle}</h1>

            <div className="profile-header__actions">
              {isOwnProfile ? (
                <>
                  <button
                    type="button"
                    className="profile-header__btn profile-header__btn--edit"
                    onClick={onOpenEditProfile}
                    title="Edit profile photo, display name & bio"
                  >
                    Edit Profile
                  </button>
                </>
              ) : (
                <button
                  type="button"
                  className={`profile-header__btn ${
                    isFollowing
                      ? 'profile-header__btn--following'
                      : 'profile-header__btn--follow'
                  }`}
                  onClick={handleFollowToggle}
                >
                  {isFollowing ? 'Following' : 'Follow'}
                </button>
              )}
            </div>
          </div>

          {/* Stats Row: Posts, Followers, Following */}
          <ul className="profile-header__stats" aria-label="User statistics">
            <li className="profile-header__stat-item">
              <span className="profile-header__stat-num">{postsCount}</span>
              <span className="profile-header__stat-label">posts</span>
            </li>
            <li
              className="profile-header__stat-item profile-header__stat-item--clickable"
              onClick={() => handleOpenListModal('followers')}
              title="Click to view followers"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleOpenListModal('followers')}
            >
              <span className="profile-header__stat-num">{followersCount}</span>
              <span className="profile-header__stat-label">followers</span>
            </li>
            <li
              className="profile-header__stat-item profile-header__stat-item--clickable"
              onClick={() => handleOpenListModal('following')}
              title="Click to view following"
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === 'Enter' && handleOpenListModal('following')}
            >
              <span className="profile-header__stat-num">{followingCount}</span>
              <span className="profile-header__stat-label">following</span>
            </li>
          </ul>

          {/* Display Name & Bio */}
          <div className="profile-header__bio-section">
            <div className="profile-header__display-name">
              {profile.displayName || profile.handle}
            </div>
            {profile.bio && (
              <p className="profile-header__bio-text">{profile.bio}</p>
            )}
          </div>
        </div>
      </header>

      {/* Tabs Navigation Bar (Posts / Reposts / Saved) */}
      <nav className="profile-tabs" aria-label="Profile Sections">
        <button
          type="button"
          className={`profile-tabs__btn ${
            activeTab === 'posts' ? 'profile-tabs__btn--active' : ''
          }`}
          onClick={() => setActiveTab('posts')}
        >
          <span className="profile-tabs__icon" aria-hidden="true">
            ▦
          </span>
          <span className="profile-tabs__label">POSTS</span>
        </button>

        <button
          type="button"
          className={`profile-tabs__btn ${
            activeTab === 'reposts' ? 'profile-tabs__btn--active' : ''
          }`}
          onClick={() => setActiveTab('reposts')}
        >
          <span className="profile-tabs__icon" aria-hidden="true">
            🔁
          </span>
          <span className="profile-tabs__label">REPOSTS</span>
        </button>

        <button
          type="button"
          className={`profile-tabs__btn ${
            activeTab === 'saved' ? 'profile-tabs__btn--active' : ''
          }`}
          onClick={() => setActiveTab('saved')}
        >
          <span className="profile-tabs__icon" aria-hidden="true">
            🔖
          </span>
          <span className="profile-tabs__label">SAVED</span>
        </button>
      </nav>

      {/* Tab Content Display */}
      <div className="profile-content">
        {postsLoading ? (
          <div className="profile-content__loading">
            <div className="profile-page__spinner" />
            <p>Loading posts...</p>
          </div>
        ) : activeTab === 'saved' ? (
          /* Saved Tab Placeholder as requested */
          <div className="profile-saved-placeholder">
            <div className="profile-saved-placeholder__icon">🔖</div>
            <h3 className="profile-saved-placeholder__title">Save Posts</h3>
            <p className="profile-saved-placeholder__desc">
              Save photos and videos that you want to see again. Only you can see what you've saved.
            </p>
          </div>
        ) : posts.length === 0 ? (
          /* Empty state for Posts or Reposts */
          <div className="profile-empty-posts">
            <div className="profile-empty-posts__icon">
              {activeTab === 'reposts' ? '🔁' : '📷'}
            </div>
            <h3 className="profile-empty-posts__title">
              {activeTab === 'reposts' ? 'No Reposts Yet' : 'No Posts Yet'}
            </h3>
            <p className="profile-empty-posts__desc">
              {activeTab === 'reposts'
                ? `@${profile.handle} hasn't reposted any posts yet.`
                : `@${profile.handle} hasn't shared any posts yet.`}
            </p>
          </div>
        ) : (
          /* Responsive 3-Column Instagram Photo Grid */
          <div className="profile-posts-grid">
            {posts.map((post, idx) => (
              <PhotoCard
                key={post.id}
                post={post}
                index={idx}
                onSelectPost={onSelectPost}
                onToggleFollow={onToggleFollow}
                onSelectAuthor={(handle) => {
                  if (onNavigateProfile) onNavigateProfile(handle);
                }}
              />
            ))}
          </div>
        )}
      </div>

      {/* Followers / Following Modal */}
      {modalType && (
        <div
          className="profile-modal-backdrop"
          onClick={handleCloseListModal}
          role="dialog"
          aria-modal="true"
          aria-labelledby="profile-modal-title"
        >
          <div
            className="profile-modal-card"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="profile-modal-header">
              <h3 id="profile-modal-title" className="profile-modal-title">
                {modalType === 'followers' ? 'Followers' : 'Following'}
              </h3>
              <button
                type="button"
                className="profile-modal-close"
                onClick={handleCloseListModal}
                aria-label="Close"
              >
                ✕
              </button>
            </div>

            <div className="profile-modal-body">
              {userListLoading ? (
                <div className="profile-modal-loading">
                  <div className="profile-page__spinner" />
                  <p>Loading {modalType}...</p>
                </div>
              ) : userList.length === 0 ? (
                <div className="profile-modal-empty">
                  <p>No {modalType} to show.</p>
                </div>
              ) : (
                <div className="profile-modal-list">
                  {userList.map((item) => {
                    const uAvatar =
                      item.avatar?.smallUrl ||
                      item.avatar?.largeUrl ||
                      item.avatarUrl ||
                      (typeof item.avatar === 'string' ? item.avatar : null);
                    const isSelf =
                      currentUser &&
                      (currentUser.id === item.id ||
                        currentUser.handle?.toLowerCase() === item.handle?.toLowerCase());
                    const isFollowingItem = Boolean(
                      followingMap[item.handle?.toLowerCase()]
                    );

                    return (
                      <div key={item.id || item.handle} className="profile-modal-user-item">
                        <div
                          className="profile-modal-user-info"
                          onClick={() => {
                            handleCloseListModal();
                            if (onNavigateProfile) onNavigateProfile(item.handle);
                          }}
                          role="button"
                          tabIndex={0}
                        >
                          <div className="profile-modal-avatar-wrapper">
                            {uAvatar ? (
                              <img
                                src={uAvatar}
                                alt={item.handle}
                                className="profile-modal-avatar"
                                onError={(e) => {
                                  e.target.style.display = 'none';
                                  if (e.target.nextSibling)
                                    e.target.nextSibling.style.display = 'flex';
                                }}
                              />
                            ) : null}
                            <div
                              className="profile-modal-avatar-fallback"
                              style={{ display: uAvatar ? 'none' : 'flex' }}
                            >
                              {(item.displayName || item.handle || 'U')
                                .charAt(0)
                                .toUpperCase()}
                            </div>
                          </div>

                          <div className="profile-modal-names">
                            <span className="profile-modal-display-name">
                              {item.displayName || item.handle}
                            </span>
                            <span className="profile-modal-handle">@{item.handle}</span>
                          </div>
                        </div>

                        {!isSelf && currentUser && (
                          <button
                            type="button"
                            className={`profile-modal-follow-btn ${
                              isFollowingItem ? 'profile-modal-follow-btn--following' : ''
                            }`}
                            onClick={() => {
                              if (onToggleFollow) {
                                onToggleFollow({
                                  authorId: item.id,
                                  authorHandle: item.handle,
                                  shouldFollow: !isFollowingItem,
                                });
                              }
                            }}
                          >
                            {isFollowingItem ? 'Following' : 'Follow'}
                          </button>
                        )}
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default ProfilePage;
