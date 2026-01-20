# Multi-User System Implementation Guide

## Overview
This system now supports **complete user isolation** where each user has their own:
- Cameras
- Recordings
- Profile settings
- Dashboard view

## What Changed?

### Backend Changes

#### 1. **Database Schema** (`setup_db.py`)
- **users table**: Added `email` and `created_at` columns
- **cameras table**: NEW - Links cameras to specific users
- **recordings table**: Added `user_id`, `camera_id`, and `file_size` columns
- **user_settings table**: NEW - Stores user preferences

#### 2. **Authentication** (`routes/auth.py`)
- Implemented **JWT (JSON Web Token)** authentication
- Login now returns a token valid for 30 days
- Signup automatically logs in the user
- Added `@token_required` decorator for protected routes

#### 3. **User-Specific Routes** (`app.py`)
All routes now require authentication and filter data by user:
- `/api/cameras` - Get user's cameras only
- `/api/cameras` (POST) - Save camera for user
- `/api/cameras/<id>` (DELETE) - Delete user's camera
- `/api/recordings` - Get user's recordings only
- `/api/recordings/<id>` (DELETE) - Delete user's recording
- `/api/upload` - Upload recording for user
- `/api/profile/update` - Update user profile
- `/api/profile/change-password` - Change password

### Frontend Changes

#### 1. **API Layer** (`api.js`)
- Added `getAuthHeaders()` function to include JWT token
- All API calls now send Authorization header
- New functions: `getUserCameras()`, `saveCamera()`, `deleteCamera()`

#### 2. **Config** (`config.js`)
- Added new API endpoints for user-specific operations

#### 3. **Dashboard** (`Dashboard.js`)
- Cameras are now stored in database (not just localStorage)
- Profile modal with account management
- User-specific data loading

## How It Works

### User Registration Flow
```
1. User signs up → Backend creates user in database
2. Backend generates JWT token
3. Token stored in localStorage
4. User automatically logged in
```

### User Login Flow
```
1. User enters credentials
2. Backend verifies and generates JWT token
3. Token stored in localStorage
4. All subsequent API calls include this token
```

### Camera Management Flow
```
1. User clicks "Add Camera"
2. Code generated (requires JWT token)
3. Camera paired with mobile device
4. Camera saved to database with user_id
5. Only this user can see/manage this camera
```

### Recording Flow
```
1. User starts recording on their camera
2. Recording uploaded with JWT token
3. Backend saves file as: user{id}_rec_timestamp.webm
4. Database entry includes user_id
5. Only this user can view/delete this recording
```

## Database Structure

### users
```sql
id | username | password | email | created_at
```

### cameras
```sql
id | user_id | name | code | status | created_at
```

### recordings
```sql
id | user_id | camera_id | filename | camera_name | recording_start_time | timestamp | file_size
```

### user_settings
```sql
id | user_id | theme | notifications_enabled
```

## Security Features

1. **JWT Authentication**: Secure token-based auth
2. **User Isolation**: Users can only access their own data
3. **Token Expiration**: Tokens expire after 30 days
4. **Password Protection**: Passwords stored (should be hashed in production)
5. **Authorization Checks**: Every route verifies user ownership

## Setup Instructions

### 1. Install Dependencies
```bash
cd backend
pip install -r requirements.txt
```

### 2. Initialize Database
```bash
python setup_db.py
```

This will:
- Create all tables
- Add admin user (username: admin, password: 123)
- Set up user isolation structure

### 3. Start Backend
```bash
python app.py
```

### 4. Start Frontend
```bash
cd ../WebWatch
npm start
```

## Testing Multi-User System

### Test Scenario 1: Two Users
1. **User 1 (admin)**:
   - Login with username: `admin`, password: `123`
   - Add Camera 1 with code `123456`
   - Record video
   - Logout

2. **User 2 (new user)**:
   - Signup with username: `user2`, password: `password123`
   - Dashboard is empty (no cameras from User 1)
   - Add Camera 2 with code `789012`
   - Record video
   - Only sees their own recordings

3. **Verify Isolation**:
   - Login as User 1 again
   - Should only see Camera 1 and their recordings
   - User 2's data is completely hidden

### Test Scenario 2: Profile Management
1. Login as any user
2. Click profile avatar in sidebar
3. Update username/email
4. Change password
5. View account statistics

## File Organization

### Recordings
- Format: `user{user_id}_rec_{timestamp}.webm`
- Example: `user1_rec_2026-01-16_10-30-45.webm`
- Stored in: `backend/recordings/`

### Database
- File: `backend/webwatch.db`
- SQLite database with all user data

## Migration from Old System

If you have existing data:

1. **Existing recordings** without user_id:
   - Will still be accessible
   - Assign to admin user manually if needed

2. **LocalStorage cameras**:
   - Will be migrated on first login
   - Save them to database using new API

## Production Recommendations

1. **Password Hashing**: Use bcrypt or similar
2. **HTTPS Only**: Enforce SSL/TLS
3. **Token Refresh**: Implement refresh tokens
4. **Rate Limiting**: Prevent brute force attacks
5. **Input Validation**: Sanitize all user inputs
6. **Database Backups**: Regular automated backups
7. **Environment Variables**: Store secrets securely

## API Reference

### Authentication
- `POST /api/auth/login` - Login user
- `POST /api/auth/signup` - Register new user
- `GET /api/auth/verify` - Verify token validity

### Cameras
- `GET /api/cameras` - Get user's cameras
- `POST /api/cameras` - Save new camera
- `DELETE /api/cameras/<id>` - Delete camera

### Recordings
- `GET /api/recordings` - Get user's recordings
- `POST /api/upload` - Upload recording
- `DELETE /api/recordings/<id>` - Delete recording

### Profile
- `PUT /api/profile/update` - Update profile
- `PUT /api/profile/change-password` - Change password

### Code Generation
- `GET /api/code/generate` - Generate pairing code

## Troubleshooting

### Token Expired
- User will be logged out automatically
- Need to login again

### Camera Not Showing
- Check if token is valid
- Verify camera was saved with correct user_id
- Check browser console for errors

### Recording Upload Fails
- Verify token is included in request
- Check file size (max 100MB)
- Ensure backend is running

## Support

For issues or questions:
1. Check browser console for errors
2. Check backend terminal for logs
3. Verify database structure with `sqlite3 webwatch.db`
4. Test API endpoints with Postman/curl

---

**System Status**: ✅ Multi-User System Active
**Version**: 2.0
**Last Updated**: January 16, 2026
