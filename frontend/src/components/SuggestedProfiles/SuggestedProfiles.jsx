import React, { useState, useEffect } from 'react';
import { fetchUsersApi } from '../../utils/api';
import './SuggestedProfiles.css';

/**
 * Metadata for the 5 core curated profiles in the application.
 */
export const ALL_PROFILES = [
  {
    id: '158469c3-4a2d-4bc6-bf96-5a7638847875',
    handle: 'deepu',
    displayName: 'Deepika',
    niche: 'Food & Culinary',
    badge: 'Food 🍝',
    avatar: 'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80',
    bio: 'Artisanal recipes & gourmet photography ✨',
  },
  {
    id: 'bd4c55d9-31f3-42e9-a210-e1355a77101f',
    handle: 'sneha',
    displayName: 'Sneha',
    niche: 'Flowers & Blooms',
    badge: 'Flowers 🌸',
    avatar: 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=150&q=80',
    bio: 'Botanical aesthetics & garden flora 🌿',
  },
  {
    id: 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa',
    handle: 'asha',
    displayName: 'Asha Patel',
    niche: 'Books & Study',
    badge: 'Books 📚',
    avatar: 'https://images.unsplash.com/photo-1517841905240-472988babdf9?auto=format&fit=crop&w=150&q=80',
    bio: 'Book lover, stationery & study aesthetic 📖',
  },
  {
    id: '250070da-0c2b-4a91-8d1a-180a9a2d1781',
    handle: 'ani',
    displayName: 'Anirudh',
    niche: 'Music & Instruments',
    badge: 'Music 🎧',
    avatar: 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?auto=format&fit=crop&w=150&q=80',
    bio: 'Acoustic jams, audio production & beats 🎸',
  },
  {
    id: '26ee15b1-6f04-4c8f-9cf5-61e28c5472db',
    handle: 'virat',
    displayName: 'Virat',
    niche: 'Cricket & Sports',
    badge: 'Cricket 🏏',
    avatar: 'https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=150&q=80',
    bio: 'Match day passion, fitness & willow cricket 🏏',
  },
];

/**
 * SuggestedProfiles sidebar component.
 * Displays "Explore More Profiles" with core creators and newly registered community accounts.
 * Shows a "More" button to toggle and view newly registered accounts (e.g. @vivek).
 */
export function SuggestedProfiles({
  currentUser,
  onOpenAuth,
  onToggleFollow,
  followingMap = {},
  onSelectProfile,
}) {
  const [coreProfiles, setCoreProfiles] = useState(ALL_PROFILES);
  const [communityUsers, setCommunityUsers] = useState([]);
  const [showMore, setShowMore] = useState(false);

  const currentHandle = currentUser?.handle?.toLowerCase();

  // Fetch registered users from PostgreSQL to discover community accounts & sync core creators
  useEffect(() => {
    fetchUsersApi()
      .then((res) => {
        if (res?.items?.length > 0) {
          const itemsMap = new Map();
          res.items.forEach((u) => {
            itemsMap.set(u.handle.toLowerCase(), u);
          });

          // Sync core profiles with live database data (avatar, displayName, bio)
          setCoreProfiles((prev) =>
            prev.map((core) => {
              const live = itemsMap.get(core.handle.toLowerCase());
              if (!live) return core;
              return {
                ...core,
                displayName: live.displayName || core.displayName,
                bio: live.bio !== undefined && live.bio !== null && live.bio !== '' ? live.bio : core.bio,
                avatar:
                  live.avatar?.smallUrl ||
                  live.avatar?.largeUrl ||
                  live.avatarUrl ||
                  (typeof live.avatar === 'string' ? live.avatar : core.avatar),
              };
            })
          );

          const coreHandles = new Set(ALL_PROFILES.map((p) => p.handle.toLowerCase()));
          const community = res.items
            .filter((u) => !coreHandles.has(u.handle.toLowerCase()))
            .map((u) => ({
              id: u.id,
              handle: u.handle,
              displayName: u.displayName || u.handle,
              bio: u.bio || 'New Community Creator',
              badge: 'Community 🌟',
              avatar:
                u.avatar?.smallUrl ||
                u.avatar?.largeUrl ||
                u.avatarUrl ||
                (typeof u.avatar === 'string' ? u.avatar : null),
            }));
          setCommunityUsers(community);
        }
      })
      .catch(() => {});
  }, [currentUser]);

  // Filter core profiles: exclude current user if logged in
  const visibleCoreProfiles = coreProfiles.filter(
    (p) => !currentHandle || p.handle.toLowerCase() !== currentHandle
  );

  // Filter community profiles: exclude current user if logged in
  const visibleCommunityProfiles = communityUsers.filter(
    (p) => !currentHandle || p.handle.toLowerCase() !== currentHandle
  );

  const totalVisibleCount =
    visibleCoreProfiles.length + (showMore ? visibleCommunityProfiles.length : 0);

  const handleFollowClick = (profile) => {
    if (!currentUser) {
      if (onOpenAuth) onOpenAuth();
      return;
    }

    const isFollowing = Boolean(followingMap[profile.handle.toLowerCase()]);
    if (onToggleFollow) {
      onToggleFollow({
        authorId: profile.id,
        authorHandle: profile.handle,
        shouldFollow: !isFollowing,
      });
    }
  };

  const currentUserAvatar =
    currentUser?.avatar?.smallUrl ||
    currentUser?.avatar?.largeUrl ||
    currentUser?.avatarUrl ||
    currentUser?.avatar ||
    null;

  return (
    <aside className="suggested-sidebar" aria-label="Explore More Profiles">
      {/* Current User Quick Header Card (when logged in) */}
      {currentUser && (
        <div className="suggested-sidebar__my-card">
          <div className="suggested-sidebar__my-avatar-wrapper">
            {currentUserAvatar ? (
              <img
                src={currentUserAvatar}
                alt={currentUser.handle}
                className="suggested-sidebar__my-avatar"
                onClick={() => onSelectProfile && onSelectProfile(currentUser.handle)}
                style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
                title={`View posts by @${currentUser.handle}`}
                onError={(e) => {
                  e.target.style.display = 'none';
                  if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                }}
              />
            ) : null}
            <div
              className="suggested-sidebar__my-avatar-fallback"
              style={{ display: currentUserAvatar ? 'none' : 'flex' }}
            >
              {(currentUser.displayName || currentUser.handle || 'U').charAt(0).toUpperCase()}
            </div>
          </div>

          <div
            className="suggested-sidebar__my-info"
            onClick={() => onSelectProfile && onSelectProfile(currentUser.handle)}
            style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
            title={`View posts by @${currentUser.handle}`}
          >
            <span className="suggested-sidebar__my-name">
              {currentUser.displayName || currentUser.handle}
            </span>
            <span className="suggested-sidebar__my-handle">@{currentUser.handle}</span>
          </div>
          <button
            type="button"
            className="suggested-sidebar__switch-btn"
            onClick={onOpenAuth}
            title="Switch profile"
          >
            Switch
          </button>
        </div>
      )}

      {/* Main Header */}
      <div className="suggested-sidebar__header">
        <div className="suggested-sidebar__title-wrapper">
          <span className="suggested-sidebar__icon" aria-hidden="true">
            🧭
          </span>
          <h2 className="suggested-sidebar__title">Explore More Profiles</h2>
        </div>
        <span className="suggested-sidebar__count">
          {totalVisibleCount} {totalVisibleCount === 1 ? 'profile' : 'profiles'}
        </span>
      </div>

      <p className="suggested-sidebar__subtitle">
        {currentUser
          ? 'Discover content creators across different niches'
          : 'Sign in to follow creators and personalize your feed'}
      </p>

      {/* Profiles List */}
      <div className="suggested-sidebar__list" role="list">
        {/* 1. Core Curated Creators */}
        {visibleCoreProfiles.map((p) => {
          const isFollowing = currentUser
            ? Boolean(followingMap[p.handle.toLowerCase()])
            : false;

          return (
            <div key={p.handle} className="suggested-profile-card" role="listitem">
              <div
                className="suggested-profile-card__avatar-wrapper"
                onClick={() => onSelectProfile && onSelectProfile(p.handle)}
                style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
                title={`View posts by @${p.handle}`}
              >
                {p.avatar ? (
                  <img
                    src={p.avatar}
                    alt={`${p.displayName} (@${p.handle})`}
                    className="suggested-profile-card__avatar"
                    loading="lazy"
                    onError={(e) => {
                      e.target.style.display = 'none';
                      if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                    }}
                  />
                ) : null}
                <div
                  className="suggested-profile-card__avatar-fallback"
                  style={{ display: p.avatar ? 'none' : 'flex' }}
                >
                  {(p.displayName || p.handle || 'U').charAt(0).toUpperCase()}
                </div>
              </div>

              <div
                className="suggested-profile-card__content"
                onClick={() => onSelectProfile && onSelectProfile(p.handle)}
                style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
                title={`View posts by @${p.handle}`}
              >
                <div className="suggested-profile-card__names">
                  <span className="suggested-profile-card__name">{p.displayName}</span>
                  <span className="suggested-profile-card__handle">@{p.handle}</span>
                </div>
                <div className="suggested-profile-card__badge">{p.badge}</div>
              </div>

              <button
                type="button"
                className={`suggested-profile-card__follow-btn ${
                  isFollowing ? 'suggested-profile-card__follow-btn--following' : ''
                }`}
                onClick={() => handleFollowClick(p)}
                title={
                  !currentUser
                    ? 'Sign in to follow @' + p.handle
                    : isFollowing
                    ? 'Unfollow @' + p.handle
                    : 'Follow @' + p.handle
                }
              >
                {isFollowing ? 'Following' : 'Follow'}
              </button>
            </div>
          );
        })}

        {/* 2. Newly Registered Community Accounts (Expanded when showMore is true) */}
        {showMore &&
          visibleCommunityProfiles.map((p) => {
            const isFollowing = currentUser
              ? Boolean(followingMap[p.handle.toLowerCase()])
              : false;

            return (
              <div
                key={p.handle}
                className="suggested-profile-card suggested-profile-card--community"
                role="listitem"
              >
                <div
                  className="suggested-profile-card__avatar-wrapper"
                  onClick={() => onSelectProfile && onSelectProfile(p.handle)}
                  style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
                  title={`View posts by @${p.handle}`}
                >
                  {p.avatar ? (
                    <img
                      src={p.avatar}
                      alt={`${p.displayName} (@${p.handle})`}
                      className="suggested-profile-card__avatar"
                      loading="lazy"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div
                    className="suggested-profile-card__avatar-fallback"
                    style={{ display: p.avatar ? 'none' : 'flex' }}
                  >
                    {(p.displayName || p.handle || 'U').charAt(0).toUpperCase()}
                  </div>
                </div>

                <div
                  className="suggested-profile-card__content"
                  onClick={() => onSelectProfile && onSelectProfile(p.handle)}
                  style={{ cursor: onSelectProfile ? 'pointer' : 'default' }}
                  title={`View posts by @${p.handle}`}
                >
                  <div className="suggested-profile-card__names">
                    <span className="suggested-profile-card__name">{p.displayName}</span>
                    <span className="suggested-profile-card__handle">@{p.handle}</span>
                  </div>
                  <div className="suggested-profile-card__badge">{p.badge}</div>
                </div>

                <button
                  type="button"
                  className={`suggested-profile-card__follow-btn ${
                    isFollowing ? 'suggested-profile-card__follow-btn--following' : ''
                  }`}
                  onClick={() => handleFollowClick(p)}
                  title={
                    !currentUser
                      ? 'Sign in to follow @' + p.handle
                      : isFollowing
                      ? 'Unfollow @' + p.handle
                      : 'Follow @' + p.handle
                  }
                >
                  {isFollowing ? 'Following' : 'Follow'}
                </button>
              </div>
            );
          })}
      </div>

      {/* "More" Toggle Button for Newly Created Community Accounts */}
      {visibleCommunityProfiles.length > 0 && (
        <div className="suggested-sidebar__more-container">
          <button
            type="button"
            className="suggested-sidebar__more-btn"
            onClick={() => setShowMore((prev) => !prev)}
            aria-expanded={showMore}
            title={showMore ? 'Show fewer profiles' : 'Show newly registered profiles'}
          >
            <span>
              {showMore
                ? '▲ Show Less'
                : `▼ More Profiles (${visibleCommunityProfiles.length})`}
            </span>
          </button>
        </div>
      )}

      {/* Footer hint */}
      {!currentUser && (
        <div className="suggested-sidebar__hint-box">
          <span className="suggested-sidebar__hint-icon">💡</span>
          <p className="suggested-sidebar__hint-text">
            Click <strong>Follow</strong> on any profile to sign in and view their dedicated feed!
          </p>
        </div>
      )}
    </aside>
  );
}

