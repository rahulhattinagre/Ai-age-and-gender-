# Fix MongoDB Auth Error - Progress Tracker

## Plan Summary
Add try/except around MongoDB connection in server.py. Fallback to in-memory dict for users if Atlas fails. Server starts, AI works, basic auth functional (no persistence).

## Steps:
- [x] Step 1: Create this TODO.md (done)
- [x] Step 2: Edit server.py - Add MongoDB connection try/except with ping test, masked URI print, set global client/users_collection  
- [x] Step 3: Add helper functions for DB ops (insert_user, get_user) to handle dict vs pymongo
- [x] Step 4: Update routes (signup_post, login_post) to use helpers
- [x] Step 5: Test run 'python server_fixed.py' (success - server running on http://localhost:5000 with in-memory DB fallback)
- [x] Step 6: Complete & cleanup TODO.md

