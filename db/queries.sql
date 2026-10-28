-- ============================================================================
-- Easy SQL Practice Queries
-- Based on the Social Feed schema
-- Tables used: users, posts, post_likes, follows, post_media
-- ============================================================================


-- =================https://www.instagram.com/reels/===========================================================
-- 1. GET ALL POSTS WITH THEIR AUTHOR
-- Concept: JOIN
-- Question: Show every post along with the name/handle of the user who posted it.
-- ============================================================================

SELECT
    p.id AS post_id,
    p.text,
    u.id AS user_id,
    u.handle
FROM posts p
JOIN users u
    ON p.author_id = u.id;


-- ============================================================================
-- 2. GET ONE USER'S POSTS
-- Concept: WHERE
-- Question: Show all original posts written by one particular user.
-- Replace the UUID below with the required user ID.
-- ============================================================================

SELECT
    p.id AS post_id,
    p.text,
    p.created_at
FROM posts p
WHERE p.author_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
  AND p.kind = 'original';


-- ============================================================================
-- 3. GET EACH POST AND ITS NUMBER OF LIKES
-- Concept: LEFT JOIN + GROUP BY
-- Question: For one particular user, show each of their posts and
--           the number of likes on each post.
-- ============================================================================

SELECT
    p.id AS post_id,
    COUNT(pl.user_id) AS no_of_likes
FROM posts p
LEFT JOIN post_likes pl
    ON p.id = pl.post_id
WHERE p.author_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa'
  AND p.kind = 'original'
GROUP BY p.id;


-- ============================================================================
-- 4. GET USERS AND THEIR POST COUNT
-- Concept: LEFT JOIN + GROUP BY
-- Question: Show every user and how many posts they have.
-- Users with zero posts should also appear.
-- ============================================================================

SELECT
    u.id AS user_id,
    u.handle,
    COUNT(p.id) AS no_of_posts
FROM users u
LEFT JOIN posts p
    ON u.id = p.author_id
   AND p.kind = 'original'
GROUP BY u.id, u.handle;


-- ============================================================================
-- 5. GET POSTS HAVING MORE THAN 2 LIKES
-- Concept: JOIN + GROUP BY + HAVING
-- Question: Show posts that have more than 2 likes.
-- ============================================================================

SELECT
    p.id AS post_id,
    COUNT(pl.user_id) AS no_of_likes
FROM posts p
LEFT JOIN post_likes pl
    ON p.id = pl.post_id 
GROUP BY p.id
HAVING COUNT(pl.user_id) > 2;


-- ============================================================================
-- 6. FIND THE MOST-LIKED POST
-- Concept: GROUP BY + ORDER BY + LIMIT
-- Question: Find the post that has the highest number of likes.
-- ============================================================================

SELECT
    p.id AS post_id,
    p.text,
    COUNT(pl.user_id) AS no_of_likes
FROM posts p
LEFT JOIN post_likes pl
    ON p.id = pl.post_id
GROUP BY p.id, p.text
ORDER BY no_of_likes DESC
LIMIT 1;


-- ============================================================================
-- 7. FIND THE AVERAGE NUMBER OF LIKES PER POST
-- Concept: Subquery + AVG
-- Question: Find the average number of likes received by a post.
-- ============================================================================

SELECT
    AVG(like_count) AS average_likes
FROM (
    SELECT
        p.id,
        COUNT(pl.user_id) AS like_count
    FROM posts p
    LEFT JOIN post_likes pl
        ON p.id = pl.post_id
    GROUP BY p.id
) AS post_like_counts;


-- ============================================================================
-- 8. FIND USERS WHO HAVE NO POSTS
-- Concept: LEFT JOIN + IS NULL
-- Question: Find users who have never created an original post.
-- ============================================================================

SELECT
    u.id AS user_id,
    u.handle
FROM users u
LEFT JOIN posts p
    ON u.id = p.author_id
   AND p.kind = 'original'
WHERE p.id IS NULL;


-- ============================================================================
-- 9. FIND POSTS WITH MORE LIKES THAN THE AVERAGE
-- Concept: Subquery
-- Question: Show posts whose number of likes is greater than
--           the average number of likes across all posts.
-- ============================================================================

SELECT
    p.id AS post_id,
    COUNT(pl.user_id) AS no_of_likes
FROM posts p
LEFT JOIN post_likes pl
    ON p.id = pl.post_id
GROUP BY p.id
HAVING COUNT(pl.user_id) > (
    SELECT AVG(like_count)
    FROM (
        SELECT
            p2.id,
            COUNT(pl2.user_id) AS like_count
        FROM posts p2
        LEFT JOIN post_likes pl2
            ON p2.id = pl2.post_id
        GROUP BY p2.id
    ) AS average_likes
);


-- ============================================================================
-- 10. FIND FOLLOWERS OF ONE PARTICULAR USER
-- Concept: JOIN
-- Question: Show the users who follow one particular user.
-- Replace the UUID below with the required user's ID.
-- ============================================================================

SELECT
    u.id AS follower_id,
    u.handle AS follower_handle
FROM follows f
JOIN users u
    ON f.follower_id = u.id
WHERE f.following_id = 'aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa';


-- ============================================================================
-- QUICK CONCEPT SUMMARY
-- ============================================================================
-- 1. JOIN
-- 2. WHERE
-- 3. LEFT JOIN + GROUP BY
-- 4. LEFT JOIN + GROUP BY
-- 5. GROUP BY + HAVING
-- 6. GROUP BY + ORDER BY + LIMIT
-- 7. Subquery + AVG
-- 8. LEFT JOIN + IS NULL
-- 9. Subquery + GROUP BY + HAVING
-- 10. JOIN
-- ============================================================================
