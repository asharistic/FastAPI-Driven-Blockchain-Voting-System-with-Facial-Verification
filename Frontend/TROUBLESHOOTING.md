# Troubleshooting Login Issues

## Common Issues and Solutions

### 1. "Login failed. Please check your credentials."

**Possible Causes:**
- Backend server is not running
- CORS issues (should be fixed now)
- Wrong credentials
- Network connectivity issues

**Solutions:**

#### Check Backend is Running
1. Open a new terminal
2. Navigate to project root: `cd C:\Users\HP\Downloads\FaceVoteChain`
3. Activate virtual environment: `.\.venv\Scripts\Activate.ps1`
4. Start backend: `uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload`
5. You should see: "Uvicorn running on http://127.0.0.1:5000"

#### Verify Credentials
- **Username:** `admin`
- **Password:** `admin123`
- Make sure there are no extra spaces

#### Check Browser Console
1. Open browser DevTools (F12)
2. Go to Console tab
3. Try logging in again
4. Check for any error messages
5. Go to Network tab and check the login request:
   - Status should be 200 (not 401, 404, or CORS error)
   - Check the request URL: should be `http://127.0.0.1:5000/api/auth/login`

### 2. "Cannot connect to backend server"

**Solution:**
- Make sure backend is running on port 5000
- Check if port 5000 is available
- Try accessing: `http://127.0.0.1:5000/health` in browser
- Should return: `{"status": "healthy", ...}`

### 3. CORS Errors in Browser Console

**Solution:**
- The backend now has CORS configured
- If you still see CORS errors, restart the backend server
- Make sure you're using the updated `backend/main.py` with CORS middleware

### 4. Network Error

**Solution:**
1. Check if backend is accessible:
   ```powershell
   curl http://127.0.0.1:5000/health
   ```
   Or visit in browser: `http://127.0.0.1:5000/health`

2. Check firewall settings
3. Make sure no other service is using port 5000

## Step-by-Step Debugging

### Step 1: Verify Backend is Running
```powershell
# In project root
.\.venv\Scripts\Activate.ps1
uvicorn backend.main:app --host 127.0.0.1 --port 5000 --reload
```

### Step 2: Test Backend API Directly
Open browser and go to:
- `http://127.0.0.1:5000/health` - Should return JSON
- `http://127.0.0.1:5000/docs` - Should show Swagger UI

### Step 3: Test Login API
You can test the login endpoint directly using curl or Postman:

```powershell
curl -X POST "http://127.0.0.1:5000/api/auth/login" -H "Content-Type: application/json" -d "{\"username\":\"admin\",\"password\":\"admin123\"}"
```

Should return:
```json
{
  "access_token": "...",
  "token_type": "bearer"
}
```

### Step 4: Check Frontend Console
1. Open browser DevTools (F12)
2. Go to Network tab
3. Try logging in
4. Look for the `/api/auth/login` request
5. Check:
   - Status code
   - Response body
   - Request headers

### Step 5: Clear Browser Cache
1. Clear localStorage: Open Console and run:
   ```javascript
   localStorage.clear()
   ```
2. Refresh the page
3. Try logging in again

## Quick Fix Checklist

- [ ] Backend server is running on port 5000
- [ ] Frontend is running on port 3000
- [ ] Using correct credentials: `admin` / `admin123`
- [ ] No CORS errors in browser console
- [ ] Backend has CORS middleware (check `backend/main.py`)
- [ ] Backend `/health` endpoint works
- [ ] No firewall blocking port 5000

## Still Having Issues?

1. Check backend logs for errors
2. Check browser console for detailed error messages
3. Verify both servers are running:
   - Backend: `http://127.0.0.1:5000`
   - Frontend: `http://localhost:3000`

