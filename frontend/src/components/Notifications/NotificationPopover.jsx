import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  fetchNotificationsApi,
  markAllNotificationsReadApi,
  markSingleNotificationReadApi,
  formatRelativeTime,
} from '../../utils/api';
import './NotificationPopover.css';

/**
 * NotificationPopover Component
 * - Displays Instagram-style heart icon between Auth button and Theme toggle.
 * - In default/logged-out state: Shows clean outline heart. Clicking prompts sign in.
 * - In logged-in state: Shows red badge/dot when there are unread notifications.
 * - Clicking opens a sleek notifications panel with real-time updates from PostgreSQL.
 */
export function NotificationPopover({ currentUser, onOpenAuth, onSelectPost }) {
  const [isOpen, setIsOpen] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [unreadCount, setUnreadCount] = useState(0);
  const [loading, setLoading] = useState(false);
  const popoverRef = useRef(null);

  // Load notifications from backend API
  const loadNotifications = useCallback(async () => {
    if (!currentUser) {
      setNotifications([]);
      setUnreadCount(0);
      return;
    }

    try {
      const data = await fetchNotificationsApi(null, 20);
      const rawItems = data.items || [];
      // Deduplicate items logically by actor + eventType + targetPostId
      const seen = new Set();
      const dedupedItems = rawItems.filter((item) => {
        const key = `${item.actor?.id || item.actor?.handle}_${item.eventType}_${item.targetPost?.id || 'null'}`;
        if (seen.has(key)) return false;
        seen.add(key);
        return true;
      });
      setNotifications(dedupedItems);
      setUnreadCount(dedupedItems.filter((n) => !n.isRead).length);
    } catch (err) {
      console.warn('Failed to fetch notifications:', err);
    }
  }, [currentUser]);

  // Initial load and periodic polling every 12 seconds when logged in
  useEffect(() => {
    loadNotifications();

    if (!currentUser) return;

    const interval = setInterval(() => {
      loadNotifications();
    }, 12000);

    return () => clearInterval(interval);
  }, [currentUser, loadNotifications]);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (popoverRef.current && !popoverRef.current.contains(e.target)) {
        setIsOpen(false);
      }
    };

    if (isOpen) {
      document.addEventListener('mousedown', handleClickOutside);
    }
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isOpen]);

  // Toggle open / handle click
  const handleHeartClick = () => {
    if (!currentUser) {
      if (onOpenAuth) {
        onOpenAuth();
      }
      return;
    }

    setIsOpen((prev) => !prev);
    if (!isOpen) {
      loadNotifications();
    }
  };

  // Mark all notifications as read
  const handleMarkAllRead = async () => {
    if (loading || unreadCount === 0) return;
    setLoading(true);
    try {
      await markAllNotificationsReadApi();
      setUnreadCount(0);
      setNotifications((prev) =>
        prev.map((n) => ({ ...n, isRead: true, readAt: new Date().toISOString() }))
      );
    } catch (err) {
      console.error('Failed to mark all read:', err);
    } finally {
      setLoading(false);
    }
  };

  // Mark a single notification as read
  const handleNotificationClick = async (notif) => {
    if (!notif.isRead) {
      try {
        await markSingleNotificationReadApi(notif.id);
        setUnreadCount((prev) => Math.max(0, prev - 1));
        setNotifications((prev) =>
          prev.map((n) =>
            n.id === notif.id ? { ...n, isRead: true, readAt: new Date().toISOString() } : n
          )
        );
      } catch (err) {
        console.error('Failed to mark notification read:', err);
      }
    }

    if (notif.targetPost && notif.targetPost.id && onSelectPost) {
      // If it is a reply (comment) notification, open the parent post that was commented on!
      const targetPostId =
        notif.eventType === 'reply' && notif.targetPost.replyToId
          ? notif.targetPost.replyToId
          : notif.targetPost.id;

      onSelectPost(targetPostId, {
        notification: notif,
        actor: notif.actor,
        eventType: notif.eventType,
        targetPost: notif.targetPost,
      });
      setIsOpen(false);
    }
  };

  // Render notification message text
  const renderMessage = (notif) => {
    const actorHandle = notif.actor?.handle || 'someone';
    switch (notif.eventType) {
      case 'like':
        return (
          <>
            <strong>@{actorHandle}</strong> liked your photo.
          </>
        );
      case 'follow':
        return (
          <>
            <strong>@{actorHandle}</strong> started following you.
          </>
        );
      case 'follow_accepted':
        return (
          <>
            <strong>@{actorHandle}</strong> accepted your follow request.
          </>
        );
      case 'reply':
        return (
          <>
            <strong>@{actorHandle}</strong> commented: &ldquo;
            {notif.targetPost?.text || 'on your photo'}
            &rdquo;
          </>
        );
      case 'repost':
        return (
          <>
            <strong>@{actorHandle}</strong> reposted your photo.
          </>
        );
      default:
        return (
          <>
            <strong>@{actorHandle}</strong> interacted with your profile.
          </>
        );
    }
  };

  // Event icon tag
  const getEventBadge = (eventType) => {
    switch (eventType) {
      case 'like':
        return <span className="notif-item__badge notif-item__badge--like">❤️</span>;
      case 'follow':
      case 'follow_accepted':
        return <span className="notif-item__badge notif-item__badge--follow">👤</span>;
      case 'reply':
        return <span className="notif-item__badge notif-item__badge--reply">💬</span>;
      case 'repost':
        return <span className="notif-item__badge notif-item__badge--repost">🔄</span>;
      default:
        return <span className="notif-item__badge">✨</span>;
    }
  };

  const hasUnread = currentUser && unreadCount > 0;

  return (
    <div className="notif-popover-container" ref={popoverRef}>
      {/* Heart Icon Button */}
      <button
        type="button"
        className={`topbar__heart-btn ${isOpen ? 'topbar__heart-btn--active' : ''}`}
        onClick={handleHeartClick}
        aria-label={
          hasUnread
            ? `${unreadCount} unread notifications`
            : 'Notifications'
        }
        title={
          !currentUser
            ? 'Sign in to view notifications'
            : hasUnread
            ? `${unreadCount} new notification${unreadCount === 1 ? '' : 's'}`
            : 'Notifications'
        }
      >
        <svg
          className="topbar__heart-svg"
          viewBox="0 0 24 24"
          width="24"
          height="24"
          fill="none"
          stroke="currentColor"
          strokeWidth="2"
          strokeLinecap="round"
          strokeLinejoin="round"
          aria-hidden="true"
        >
          <path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z" />
        </svg>

        {/* Red notification dot on heart icon when unread notifications exist */}
        {hasUnread && (
          <span className="topbar__heart-red-dot" aria-hidden="true" />
        )}
      </button>

      {/* Floating popup badge preview (shows on hover or when unread) */}
      {hasUnread && !isOpen && (
        <div className="notif-bubble-badge" title={`${unreadCount} new notifications`}>
          <span className="notif-bubble-heart">❤️</span>
          <span className="notif-bubble-count">{unreadCount}</span>
        </div>
      )}

      {/* Notifications Dropdown Window */}
      {isOpen && currentUser && (
        <div className="notif-dropdown" role="region" aria-label="Notifications Panel">
          <div className="notif-dropdown__header">
            <div className="notif-dropdown__title-group">
              <span className="notif-dropdown__heart-icon">❤️</span>
              <h3 className="notif-dropdown__title">Notifications</h3>
              {unreadCount > 0 && (
                <span className="notif-dropdown__unread-pill">{unreadCount} new</span>
              )}
            </div>

            {unreadCount > 0 && (
              <button
                type="button"
                className="notif-dropdown__mark-all-btn"
                onClick={handleMarkAllRead}
                disabled={loading}
              >
                Mark all read
              </button>
            )}
          </div>

          <div className="notif-dropdown__body">
            {notifications.length === 0 ? (
              <div className="notif-dropdown__empty">
                <span className="notif-dropdown__empty-icon">🍃</span>
                <p className="notif-dropdown__empty-title">No notifications yet</p>
                <p className="notif-dropdown__empty-subtitle">
                  When someone likes your photos or follows you, you'll see it here!
                </p>
              </div>
            ) : (
              <div className="notif-dropdown__list" role="list">
                {notifications.map((notif) => {
                  const avatarUrl =
                    notif.actor?.avatar?.smallUrl ||
                    notif.actor?.avatar?.largeUrl ||
                    'https://images.unsplash.com/photo-1534528741775-53994a69daeb?auto=format&fit=crop&w=150&q=80';

                  return (
                    <div
                      key={notif.id}
                      className={`notif-item ${!notif.isRead ? 'notif-item--unread' : ''}`}
                      onClick={() => handleNotificationClick(notif)}
                      role="listitem"
                      tabIndex={0}
                    >
                      <div className="notif-item__avatar-container">
                        <img
                          src={avatarUrl}
                          alt={notif.actor?.handle || 'User'}
                          className="notif-item__avatar"
                          loading="lazy"
                        />
                        {getEventBadge(notif.eventType)}
                      </div>

                      <div className="notif-item__content">
                        <p className="notif-item__text">{renderMessage(notif)}</p>
                        <span className="notif-item__time">
                          {formatRelativeTime(notif.createdAt)}
                        </span>
                      </div>

                      {!notif.isRead && (
                        <span
                          className="notif-item__unread-indicator"
                          title="Unread notification"
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          <div className="notif-dropdown__footer">
            <span>
              Connected as <strong>@{currentUser.handle}</strong>
            </span>
          </div>
        </div>
      )}
    </div>
  );
}

export default NotificationPopover;
