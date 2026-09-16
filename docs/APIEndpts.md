
These URLs are called **API Endpoints** (or **API Routes**). 

They are the communication channels that the frontend or clients use to fetch data, create posts, like posts, check server health, and more.

Because your backend is built with **FastAPI**, you have interactive API documentation pages automatically available in your browser:

* **Swagger UI (Interactive API Docs):** [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) *(you can test and view all endpoints here)*
* **ReDoc UI:** [http://127.0.0.1:8000/redoc](http://127.0.0.1:8000/redoc)
* **OpenAPI Schema (JSON):** [http://127.0.0.1:8000/openapi.json](http://127.0.0.1:8000/openapi.json)

---

### Complete List of API Endpoints in Your Project

Here is the breakdown of all backend endpoints defined in the project codebase ([00_Assignment_Brief_and_API_Contract.md](file:///f:/Instagram/docs/00_Assignment_Brief_and_API_Contract.md) and [app/main.py](file:///f:/Instagram/backend/app/main.py)):

#### 1. System & Health Check
| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `GET` | `http://127.0.0.1:8000/health/live` | **Liveness Probe**: Quick check returning `{"status": "ok"}`. |
| `GET` | `http://127.0.0.1:8000/health/ready` | **Readiness Probe**: Checks whether the database connection is live (`{"status": "ready"}`). |

---

#### 2. Feed
| Method | Endpoint | Description / Parameters |
| :--- | :--- | :--- |
| `GET` | `http://127.0.0.1:8000/feed` | Retrieves the paginated chronological feed of posts.<br>• *Query params:* `limit` (e.g. `?limit=10`), `cursor` (for next page). |

---

#### 3. Posts & Comments
| Method | Endpoint | Description / Parameters |
| :--- | :--- | :--- |
| `GET` | `http://127.0.0.1:8000/posts/{id}` | Retrieves details for a specific post by UUID. |
| `GET` | `http://127.0.0.1:8000/posts/{id}/replies` | Retrieves paginated replies/comments for a specific post. |
| `POST` | `http://127.0.0.1:8000/posts` | Creates a new post, reply, or repost. (Accepts JSON body: `text`, `kind`, `media`, etc.). |
| `POST` / `PUT` | `http://127.0.0.1:8000/posts/{id}/like` | Likes a post for the current user. |
| `DELETE` | `http://127.0.0.1:8000/posts/{id}/like` | Removes the like from a post. |

---

#### 4. Search
| Method | Endpoint | Description / Parameters |
| :--- | :--- | :--- |
| `GET` | `http://127.0.0.1:8000/search/posts` *(or `/search`)* | Searches original posts by text query.<br>• *Example:* `http://127.0.0.1:8000/search/posts?q=coffee` |

---

#### 5. Users & Profiles
| Method | Endpoint | Description / Parameters |
| :--- | :--- | :--- |
| `GET` | `http://127.0.0.1:8000/users/{id}` | Retrieves user profile info (name, handle, avatar, counts). |
| `GET` | `http://127.0.0.1:8000/users/{id}/media` | Retrieves the photo grid/media gallery for that user profile. |

---

### Tip
If you want to view, test, or send sample requests to any of these endpoints right now, open **[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)** in your browser while your backend is running.