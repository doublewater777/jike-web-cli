# JIKE.md — 即刻 (Jike) API Map

- **Site**: https://web.okjike.com/
- **API Base**: https://api.ruguoapp.com/1.0/
- **Protocol**: REST (POST-for-query hybrid — many reads use POST with JSON body)
- **Auth**: JWT token in `x-jike-access-token` header (extracted from browser session)
- **Protection**: None — httpx works directly
- **Response envelope**: `{"success": true, "data": {...}}` or `{"data": [...], "loadMoreKey": "..."}`

## Data Model

### User
```
id, username (UUID), screenName, briefIntro, avatarImage {format, picUrl},
profileImageUrl, bio, following (bool), muting, isWatching,
statsCount {followedCount, followingCount, topicSubscribedCount, ...}
```

### Post (ORIGINAL_POST)
```
id, type ("ORIGINAL_POST"), content (text/HTML), urlsInText, status,
likeCount, commentCount, repostCount, shareCount,
pictures [{format, picUrl, ...}], linkInfo {title, description, pictureUrl, linkUrl},
topic {id, type, content}, user {id, username, screenName, avatarImage},
createdAt, isFeatured, collected, collectTime, withSDR, withAIGC,
scrollSubtitles, readTrackInfo
```

### Topic
```
id, type, content, intro, approximateSubscribersCount, subscribersCount,
topicType, isVerified, subscribedStatusRawValue, tabs [...],
squarePicture {format, picUrl}, entryTab, ...
```

### Notification
```
id, type, createdAt, actionType, actionItem, linkUrl, linkType,
referenceItem, stoppable, stopped
```

### Comment
```
id, type, content, user {id, username, screenName, avatarImage},
createdAt, likeCount, replyCount, ...
```

## API Endpoints

### Feed
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| POST | `/personalUpdate/followingUpdates` | Following feed | `{limit, loadMoreKey?}` |
| POST | `/personalUpdate/single` | Single update | `{id}` |
| POST | `/recommendFeed/list` | Explore/recommend feed | `{limit, loadMoreKey?}` |

### Posts
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| GET | `/originalPosts/get` | Get a post | `?id=<postId>` |

### Users
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| GET | `/users/profile` | Own or user profile | `?username=<uuid>` (optional) |
| POST | `/userRelation/getFollowingList` | User's following list | `{username, limit, loadMoreKey?}` |
| POST | `/userRelation/getFollowerList` | User's follower list | `{username, limit, loadMoreKey?}` |

### Topics
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| GET | `/topics/getDetail` | Topic info | `?id=<topicId>` |
| POST | `/topics/tabs/square/feed` | Topic posts | `{topicId, limit, loadMoreKey?, tab?}` |

### Notifications
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| POST | `/notifications/list` | Notification list | `{limit, loadMoreKey?}` |
| GET | `/notifications/unread` | Unread notification count | — |

### Search
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| GET | `/related/keywordTip` | Search suggestions | `?keyword=<q>&limit=<n>` |

### Comments
| Method | Path | Description | Params |
|--------|------|-------------|--------|
| POST | `/comments/listPrimary` | Post primary comments | `{targetId, limit, loadMoreKey?}` |

## Auth Scheme

1. User logs into web.okjike.com via browser (SMS/WeChat)
2. SPA obtains JWT access token (stored in localStorage/cookie)
3. All API requests include `x-jike-access-token: <jwt>` header
4. Token expiry unknown — refresh via browser re-login

## CLI Command Structure

```
cli-web-jike
├── auth login          — Browser-based login, extract JWT token
├── auth status         — Check auth state
├── auth logout         — Remove auth
├── feed following      — Following feed
├── feed explore        — Explore/discover feed
├── posts get <id>      — Get a post by ID
├── users profile [username]  — Get user profile
├── users following [username] — List user's following
├── users followers [username] — List user's followers
├── topics get <id>     — Get topic detail
├── topics feed <id>    — Topic posts feed
├── notifications list  — List notifications
├── notifications unread — Unread notification count
├── search <keyword>    — Search suggestions
├── comments list <post_id> — List comments on a post
```
