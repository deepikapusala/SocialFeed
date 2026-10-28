# 🚀 Instagram Clone API — Complete Routes Reference & Scrum Notes

> **Base Server URL**: `http://localhost:8000`  
> **Interactive Swagger Documentation**: [`http://localhost:8000/docs`](http://localhost:8000/docs)  
> **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 📌 Quick Scrum Summary (30-Second Speaking Pitch)

> *"In our backend, we have structured RESTful endpoints following standard HTTP verbs:*
> - ***GET***: *Used for non-mutating queries like health checks, the public & home feed, user search, profile data, followers/following lists, and notification inboxes.*
> - ***POST***: *Used for creating resources and triggering discrete actions, including user registration, session login, post publishing, and marking notifications as read.*
> - ***PUT***: *Used for idempotent state toggles, specifically liking a post, reposting, and following accounts.*
> - ***PATCH***: *Used for partial resource updates with optimistic concurrency control, such as editing post text and updating profile bios/details.*
> - ***DELETE***: *Used for destructive and removal actions, including unliking, unreposting, unfollowing, soft-deleting posts, and permanent account removal.*
> - *Every endpoint is documented with strict Pydantic schemas and testable via Swagger UI at `/docs`."*

---

## 🔑 Authentication & Thunder Client Configuration

For endpoints marked **🔒 Authenticated**:
1. First send **POST `/auth/login`** or **POST `/auth/register`**.
2. Copy the `token` string from the response.
3. In **Thunder Client** (or Postman), open the **Headers** tab:
   - **Header Name**: `Authorization`
   - **Header Value**: `Bearer <YOUR_COPIED_TOKEN>`
   - **Content-Type**: `application/json` (for POST/PUT/PATCH with body)

---

## 1. 🌐 GET Routes (Directly paste in Browser or Thunder Client)

All `GET` endpoints are read-only and safe to open directly in any browser address bar.

| # | Endpoint / Browser URL | Auth Needed? | Description |
|---|------------------------|:------------:|-------------|
| 1 | `http://localhost:8000/health` | ❌ No | Liveness probe returning `{"status": "ok"}`. |
| 2 | `http://localhost:8000/health/ready` | ❌ No | Readiness probe testing active PostgreSQL connectivity. |
| 3 | `http://localhost:8000/feed` | Optional | Chronological post feed with cursor pagination. |
| 4 | `http://localhost:8000/search?q=hello` | ❌ No | Literal substring search across original post captions. |
| 5 | `http://localhost:8000/users` | ❌ No | Lists all registered accounts with active/deactivated state. |
| 6 | `http://localhost:8000/users/<USER_UUID>` | ❌ No | Fetches a user's public profile and follower statistics. |
| 7 | `http://localhost:8000/users/<USER_UUID>/followers` | ❌ No | Paginated list of followers of a given user. |
| 8 | `http://localhost:8000/users/<USER_UUID>/following` | ❌ No | Paginated list of accounts a given user is following. |
| 9 | `http://localhost:8000/users/<USER_UUID>/media` | ❌ No | Paginated media items posted by a user. |
| 10 | `http://localhost:8000/posts/<POST_UUID>` | ❌ No | Detailed post view including media and recent likers. |
| 11 | `http://localhost:8000/posts/<POST_UUID>/replies` | ❌ No | Paginated list of direct comments/replies to a post. |
| 12 | `http://localhost:8000/auth/me` | 🔒 Yes | Returns the currently authenticated user's profile. |
| 13 | `http://localhost:8000/users/me` | 🔒 Yes | Returns the caller's full profile directly from database. |
| 14 | `http://localhost:8000/notifications` | 🔒 Yes | Paginated notifications inbox for the logged-in user. |

### Query Parameters Reference for GET:
- `cursor`: Opaque pagination token (e.g. `?cursor=eyJ...`)
- `limit`: Page size limit between 1 and 50 (e.g. `?limit=10`)
- `scope`: Feed scope `home` (personalized) or `public` (e.g. `?scope=public`)
- `q`: Search query string min 2 characters (e.g. `?q=travel`)

---

## 2. 📤 POST Routes (Thunder Client)

### 2.1 Register New Account
- **Method**: `POST`
- **URL**: `http://localhost:8000/auth/register`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "handle": "john_doe",
    "displayName": "John Doe",
    "password": "Password123!",
    "bio": "Excited to join the community!"
  }
  ```
- **Returns**: HTTP 201 Created with `{ "token": "...", "user": { ... } }`

---

### 2.2 Login to Existing Account
- **Method**: `POST`
- **URL**: `http://localhost:8000/auth/login`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "handle": "deepu",
    "password": "TestPassword123!"
  }
  ```
- **Returns**: HTTP 200 OK with Bearer session token.

---

### 2.3 Logout (Revoke Session)
- **Method**: `POST`
- **URL**: `http://localhost:8000/auth/logout`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 204 No Content

---

### 2.4 Create a Post (Original, Reply, or Repost)
- **Method**: `POST`
- **URL**: `http://localhost:8000/posts`
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body (Original Post with Media)**:
  ```json
  {
    "kind": "original",
    "text": "Sunset at the beach today! 🌅",
    "media": [
      {
        "smallUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1080&q=80",
        "largeUrl": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?auto=format&fit=crop&w=1080&q=80"
      }
    ]
  }
  ```
- **Body (Reply to an existing post)**:
  ```json
  {
    "kind": "reply",
    "text": "Great photo!",
    "replyToId": "<TARGET_POST_UUID>"
  }
  ```

---

### 2.5 Resolve & Standardize Media URL
- **Method**: `POST`
- **URL**: `http://localhost:8000/posts/resolve-url`
- **Headers**: `Content-Type: application/json`
- **Body**:
  ```json
  {
    "url": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e"
  }
  ```
- **Returns**: Direct CDN small and large URLs with standard 1080px crop parameters.

---

### 2.6 Accept Follow Request
- **Method**: `POST`
- **URL**: `http://localhost:8000/users/requests/<REQUESTER_USER_UUID>/accept`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with status `accepted`.

---

### 2.7 Reject Follow Request
- **Method**: `POST`
- **URL**: `http://localhost:8000/users/requests/<REQUESTER_USER_UUID>/reject`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 204 No Content.

---

### 2.8 Mark All Notifications as Read
- **Method**: `POST`
- **URL**: `http://localhost:8000/notifications/read`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with updated unread counts.

---

### 2.9 Mark Single Notification as Read
- **Method**: `POST`
- **URL**: `http://localhost:8000/notifications/<NOTIFICATION_UUID>/read`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK.

---

### 2.10 Deactivate Account (Temporary)
- **Method**: `POST`
- **URL**: `http://localhost:8000/users/me/deactivate`
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "password": "TestPassword123!"
  }
  ```
- **Returns**: HTTP 200 OK with status `deactivated`. Reversible by logging back in.

---

### 2.11 Permanently Delete Account
- **Method**: `POST`
- **URL**: `http://localhost:8000/users/me/delete-permanently`
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "password": "TestPassword123!"
  }
  ```
- **Returns**: HTTP 200 OK with status `permanently_deleted`.

---

## 3. 🔄 PUT Routes (Idempotent State Changes in Thunder Client)

### 3.1 Like a Post
- **Method**: `PUT` *(also accepts `POST`)*
- **URL**: `http://localhost:8000/posts/<POST_UUID>/like`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `{"postId": "...", "likedByViewer": true, "likeCount": N}`.

---

### 3.2 Repost a Post
- **Method**: `PUT` *(also accepts `POST`)*
- **URL**: `http://localhost:8000/posts/<POST_UUID>/repost`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `{"postId": "...", "repostedByViewer": true, "repostCount": N}`.

---

### 3.3 Follow a User
- **Method**: `PUT`
- **URL**: `http://localhost:8000/users/<TARGET_USER_UUID>/follow`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `status: "following"` or `"pending"`.

---

## 4. ✏️ PATCH Routes (Partial Updates in Thunder Client)

### 4.1 Update Post Text (Optimistic Concurrency)
- **Method**: `PATCH`
- **URL**: `http://localhost:8000/posts/<POST_UUID>`
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "text": "Edited post caption with new thoughts!",
    "version": 1
  }
  ```
- **Notes**: Supports optimistic concurrency. The `version` ensures concurrent edits don't overwrite each other.

---

### 4.2 Update Profile
- **Method**: `PATCH`
- **URL**: `http://localhost:8000/users/me` *(or `/users/<USER_UUID>`)*
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body**:
  ```json
  {
    "displayName": "Deepika",
    "bio": "Full-stack developer building Instagram Clone.",
    "isPrivate": false,
    "avatarUrl": "https://images.unsplash.com/photo-1534528741775-53994a69daeb"
  }
  ```
- **Notes**: All fields are optional; only supplied fields are updated.

---

## 5. 🗑️ DELETE Routes (Removal Operations in Thunder Client)

### 5.1 Soft-Delete a Post
- **Method**: `DELETE`
- **URL**: `http://localhost:8000/posts/<POST_UUID>`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 204 No Content.

---

### 5.2 Unlike a Post
- **Method**: `DELETE`
- **URL**: `http://localhost:8000/posts/<POST_UUID>/like`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `{"likedByViewer": false, "likeCount": N}`.

---

### 5.3 Remove Repost
- **Method**: `DELETE`
- **URL**: `http://localhost:8000/posts/<POST_UUID>/repost`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `{"repostedByViewer": false, "repostCount": N}`.

---

### 5.4 Unfollow a User
- **Method**: `DELETE`
- **URL**: `http://localhost:8000/users/<TARGET_USER_UUID>/follow`
- **Headers**: `Authorization: Bearer <token>`
- **Body**: None
- **Returns**: HTTP 200 OK with `{"status": "not_following"}`.

---

### 5.5 Delete Account Permanently
- **Method**: `DELETE`
- **URL**: `http://localhost:8000/users/me`
- **Headers**:
  - `Authorization: Bearer <token>`
  - `Content-Type: application/json`
- **Body (Optional Confirmation)**:
  ```json
  {
    "password": "TestPassword123!"
  }
  ```
- **Returns**: HTTP 200 OK with cascading removal of all posts, follows, likes, and sessions.

---

## 📋 Scrum Meeting Quick Reference Card

| Verb | Purpose | Primary Endpoints |
|:---:|:---|:---|
| **GET** | Read & Query | `/health`, `/feed`, `/search`, `/users`, `/users/{id}`, `/posts/{id}`, `/notifications` |
| **POST** | Create & Action | `/auth/register`, `/auth/login`, `/auth/logout`, `/posts`, `/notifications/read`, `/users/me/deactivate` |
| **PUT** | Idempotent State | `/posts/{id}/like`, `/posts/{id}/repost`, `/users/{id}/follow` |
| **PATCH** | Partial Update | `/posts/{id}`, `/users/me` |
| **DELETE** | Removal & Teardown | `/posts/{id}`, `/posts/{id}/like`, `/posts/{id}/repost`, `/users/{id}/follow`, `/users/me` |
