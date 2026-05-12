# TEST.md — jike Test Plan & Results


## Part 1: Test Plan


### Test Inventory

| File | Tests | Layer |
|------|-------|-------|
| test_core.py | 31 | Unit (mocked) |
| test_e2e.py | 22 | E2E (live) + Subprocess |

**Total: 53 tests**


### test_core.py

**TestExceptions** (6 tests) — Unit (mocked)

- `test_base_error_to_dict` — base error to dict
- `test_auth_error_code` — auth error code
- `test_rate_limit_error_with_retry_after` — rate limit error with retry after
- `test_not_found_error_code` — not found error code
- `test_server_error_status_code` — server error status code
- `test_network_error_code` — network error code

**TestRaiseForStatus** (6 tests) — Unit (mocked)

- `test_401_raises_auth_error` — 401 raises auth error
- `test_403_raises_auth_error` — 403 raises auth error
- `test_404_raises_not_found` — 404 raises not found
- `test_429_raises_rate_limit` — 429 raises rate limit
- `test_500_raises_server_error` — 500 raises server error
- `test_200_does_not_raise` — 200 does not raise

**TestClient** (14 tests) — Unit (mocked)

- `test_init_sets_headers` — init sets headers
- `test_request_injects_token_header` — request injects token header
- `test_401_triggers_token_reload` — 401 triggers token reload
- `test_network_error_on_connect_failure` — network error on connect failure
- `test_get_profile` — get profile
- `test_get_profile_with_username` — get profile with username
- `test_get_post` — get post
- `test_following_feed` — following feed
- `test_following_feed_with_pagination` — following feed with pagination
- `test_explore_feed` — explore feed
- `test_search_suggestions` — search suggestions
- `test_unread_count` — unread count
- `test_close` — close
- `test_context_manager` — context manager

**TestHandleErrors** (4 tests) — Unit (mocked)

- `test_passes_through_success` — passes through success
- `test_auth_error_exits_1` — auth error exits 1
- `test_unknown_error_exits_2` — unknown error exits 2
- `test_keyboard_interrupt_exits_130` — keyboard interrupt exits 130

**TestPrintJson** (1 tests) — Unit (mocked)

- `test_prints_json_to_stdout` — prints json to stdout

### test_e2e.py

**TestLiveAPI** (12 tests) — E2E (live)

- `test_feed_following_returns_posts` — feed following returns posts
- `test_feed_explore_returns_posts` — feed explore returns posts
- `test_get_profile_own` — get profile own
- `test_get_post_by_id` — get post by id
- `test_unread_count` — unread count
- `test_search_suggestions` — search suggestions
- `test_get_topic` — get topic
- `test_topic_feed` — topic feed
- `test_notifications_list` — notifications list
- `test_get_following` — get following
- `test_get_followers` — get followers
- `test_get_comments` — get comments

**TestCLISubprocess** (10 tests) — Subprocess

- `test_help` — help
- `test_version` — version
- `test_auth_status_json` — auth status json
- `test_feed_following_json` — feed following json
- `test_users_profile_json` — users profile json
- `test_notifications_unread_json` — notifications unread json
- `test_search_suggestions_json` — search suggestions json
- `test_posts_get_json` — posts get json
- `test_topics_get_json` — topics get json
- `test_json_output_no_protocol_leak` — json output no protocol leak

---


## Part 2: Test Results


**Date:** 2026-05-12 05:51 UTC


### Summary

| Metric | Value |
|--------|-------|
| Total tests | 0 |
| Passed | 0 |
| Failed | 0 |
| Errors | 0 |
| Skipped | 0 |
| Pass rate | N/A |
| Execution time | 7.42s |
| Date | 2026-05-12 05:51 UTC |

### Raw Output

```
============================= test session starts ==============================
platform darwin -- Python 3.13.9, pytest-9.0.3, pluggy-1.5.0
rootdir: /Users/water/Desktop/dev/jike/agent-harness
plugins: anyio-4.12.1
collected 53 items

cli_web/jike/tests/test_core.py ...............................          [ 58%]
cli_web/jike/tests/test_e2e.py ...........x..........                    [100%]

======================== 52 passed, 1 xfailed in 7.42s =========================
```
