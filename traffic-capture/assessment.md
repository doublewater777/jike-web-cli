# Site Assessment: jike

- **URL**: https://web.okjike.com/
- **Framework**: React SPA (Vite build, mount point: `#root`, no SSR framework)
- **Protocol**: REST (POST-for-query hybrid — many read ops use POST with JSON body for pagination/filtering)
- **Protection**: none (serviceWorker active but no anti-bot)
- **Auth required**: yes (JWT via `x-jike-access-token` header, cookie-based login via browser)
- **Iframes**: no
- **Site profile**: Auth+CRUD
- **Capture strategy**: API-first
- **Key observations**:
  - API base: `https://api.ruguoapp.com/1.0/`
  - Auth: JWT token in `x-jike-access-token` header; login uses SMS/WeChat via browser
  - Real-time: Socket.io at `jike-io.ruguoapp.com`
  - CDN: `cdnv2.ruguoapp.com` for images, `avatar.ruguoapp.com` for avatars
  - Pagination: `related/keywordTip` uses query params
  - Request bodies for POST queries include pagination/filter params as JSON
  - All responses use `{"success": true, "data": {...}}` envelope
  - No anti-bot protection — httpx should work directly with the JWT token
  - Chinese-locale UI (zh)
