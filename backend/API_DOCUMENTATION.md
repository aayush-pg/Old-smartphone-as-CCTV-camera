# Backend API Documentation

## Base URL
```
http://localhost:5000
```

## Available APIs

### 1. Health Check
**Endpoint:** `GET /`  
**Description:** Check if backend server is running  
**Response:** `"Backend Running!"`

---

### 2. Fake Login API
**Endpoint:** `POST /login`  
**Description:** Fake login endpoint (no real logic, for testing)  
**Request Body:** (Optional - any JSON or empty)  
**Response:**
```json
{
  "status": "ok"
}
```
**Status Code:** 200

---

### 3. Real Login API
**Endpoint:** `POST /api/auth/login`  
**Description:** Real login with hardcoded credentials  
**Request Body:**
```json
{
  "username": "admin",
  "password": "123"
}
```
**Success Response (200):**
```json
{
  "status": "ok",
  "message": "login successful"
}
```
**Error Response (401):**
```json
{
  "status": "error",
  "message": "Invalid username or password"
}
```

---

### 4. Code Generator API
**Endpoint:** `GET /api/code/generate`  
**Description:** Generate random 6-digit code (for OTP/pairing)  
**Request Body:** None  
**Response:**
```json
{
  "code": "654321"
}
```
**Status Code:** 200  
**Note:** Code is always 6 digits (100000 to 999999)

---

## Testing with Postman

### Test Fake Login:
1. Method: `POST`
2. URL: `http://localhost:5000/login`
3. Body: (optional)
4. Expected Response: `{"status": "ok"}`

### Test Real Login (Success):
1. Method: `POST`
2. URL: `http://localhost:5000/api/auth/login`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "username": "admin",
     "password": "123"
   }
   ```
5. Expected Response: `{"status": "ok", "message": "login successful"}` (200)

### Test Real Login (Failure):
1. Method: `POST`
2. URL: `http://localhost:5000/api/auth/login`
3. Headers: `Content-Type: application/json`
4. Body (raw JSON):
   ```json
   {
     "username": "wrong",
     "password": "wrong"
   }
   ```
5. Expected Response: `{"status": "error", "message": "Invalid username or password"}` (401)

### Test Code Generator:
1. Method: `GET`
2. URL: `http://localhost:5000/api/code/generate`
3. Expected Response: `{"code": "123456"}` (random 6-digit code)

---

## Frontend Integration Example

### Using fetch() in JavaScript:
```javascript
// Fake Login
fetch('http://localhost:5000/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({})
})
.then(response => response.json())
.then(data => console.log(data));

// Real Login
fetch('http://localhost:5000/api/auth/login', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin',
    password: '123'
  })
})
.then(response => {
  if (response.status === 200) {
    return response.json();
  } else {
    throw new Error('Login failed');
  }
})
.then(data => console.log(data))
.catch(error => console.error(error));

// Generate Code
fetch('http://localhost:5000/api/code/generate', {
  method: 'GET'
})
.then(response => response.json())
.then(data => console.log(data.code));
```

---

## CORS Configuration
CORS is enabled for all origins (`*`) in development.  
Frontend can call backend APIs without CORS errors.

---

## Notes
- All APIs return JSON responses
- POST requests require `Content-Type: application/json` header
- Status codes: 200 (Success), 401 (Unauthorized)
- Backend runs on port 5000 by default

