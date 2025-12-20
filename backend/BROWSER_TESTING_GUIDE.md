# Browser में API Testing Guide

## 📋 Overview

यह guide आपको बताता है कि browser में API को कैसे test करें।

---

## ✅ Method 1: HTML Test Page (Easiest - Recommended)

### Step 1: Server Start करें
```bash
cd backend
python app.py
```

### Step 2: Browser में खोलें
```
http://localhost:5000/test
```
या
```
http://127.0.0.1:5000/test
```

### Step 3: Test करें
- Username और Password enter करें
- "Test Login API" button click करें
- Response देखें (Success या Error)

**Default Credentials:**
- Username: `admin`
- Password: `123`

---

## ✅ Method 2: Browser Address Bar (GET Requests Only)

### Health Check
```
http://localhost:5000/
```
Expected Output: `Backend Running!`

**Note:** POST requests browser address bar से नहीं कर सकते!

---

## ✅ Method 3: Browser Developer Tools (Advanced)

### Step 1: Browser में F12 दबाएं (Developer Tools खोलें)

### Step 2: Console Tab में जाएं

### Step 3: यह code paste करें और Enter दबाएं:

```javascript
// Test with correct credentials
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
.then(response => response.json())
.then(data => console.log('Success:', data))
.catch(error => console.error('Error:', error));
```

### Step 4: Network Tab में भी देख सकते हैं
- Network tab खोलें
- Request send करें
- Request details देखें (Status Code, Response, Headers)

---

## ✅ Method 4: Browser Extensions

### Option A: Postman (Chrome Extension)
1. Chrome Web Store से Postman install करें
2. Postman open करें
3. New Request बनाएं:
   - Method: `POST`
   - URL: `http://localhost:5000/api/auth/login`
   - Body → raw → JSON:
   ```json
   {
     "username": "admin",
     "password": "123"
   }
   ```
4. Send button click करें

### Option B: REST Client (VS Code Extension)
1. VS Code में "REST Client" extension install करें
2. `.http` file बनाएं:
   ```http
   POST http://localhost:5000/api/auth/login
   Content-Type: application/json

   {
     "username": "admin",
     "password": "123"
   }
   ```
3. "Send Request" click करें

---

## 📊 Response Codes

| Status Code | Meaning | When You See This |
|-------------|---------|-------------------|
| 200 | Success | सही credentials के साथ |
| 401 | Unauthorized | गलत credentials के साथ |
| 500 | Server Error | Server में कोई problem है |
| Connection Error | Network Issue | Server चल नहीं रहा है |

---

## 🔍 Quick Test Checklist

- [ ] Server running है (`http://localhost:5000/` check करें)
- [ ] Browser में `http://localhost:5000/test` खोलें
- [ ] Username: `admin`, Password: `123` enter करें
- [ ] "Test Login API" button click करें
- [ ] Response देखें (200 Success होना चाहिए)
- [ ] "Test Wrong Credentials" button try करें
- [ ] Response देखें (401 Error होना चाहिए)

---

## 🎯 Summary

**Best Method for Beginners:**
👉 `http://localhost:5000/test` - यह सबसे आसान है!

**Why?**
- ✅ No coding required
- ✅ Visual interface
- ✅ Easy to understand
- ✅ Works in any browser
- ✅ Shows clear results

---

## ❓ Common Issues

### Issue: "Could not connect to server"
**Solution:** Server start करें: `python app.py`

### Issue: CORS Error
**Solution:** `config.py` में `CORS_ORIGINS = "*"` check करें

### Issue: 404 Not Found
**Solution:** URL check करें: `http://localhost:5000/api/auth/login` (not `/login`)

---

## 📝 Notes

1. **GET vs POST:**
   - GET requests: Browser address bar से कर सकते हैं
   - POST requests: Browser address bar से नहीं कर सकते (HTML form या JavaScript से करना होगा)

2. **Port Number:**
   - Default: `5000`
   - अगर port change करें, तो URL में भी change करें

3. **localhost vs 127.0.0.1:**
   - दोनों same हैं
   - `localhost:5000` = `127.0.0.1:5000`

