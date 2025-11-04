# How to Access Admin Dashboard

## Step-by-Step Guide

### 1. **Start the Frontend Server**
   ```powershell
   cd Frontend
   npm run dev
   ```
   The frontend will be available at: `http://localhost:3000`

### 2. **Access Admin Login Page**
   
   **Option A: Direct URL**
   - Open your browser and go to: `http://localhost:3000/admin/login`
   
   **Option B: Navigation Link**
   - Go to the home page: `http://localhost:3000`
   - Click on the "Admin" link in the navigation menu

### 3. **Login Credentials**
   - **Username:** `admin`
   - **Password:** `admin123`
   
   Enter these credentials and click "Sign In"

### 4. **Access Dashboard**
   After successful login, you will be automatically redirected to:
   - `http://localhost:3000/admin`

## URLs Summary

- **Home Page:** `http://localhost:3000/`
- **Register:** `http://localhost:3000/register`
- **Vote:** `http://localhost:3000/vote`
- **Admin Login:** `http://localhost:3000/admin/login`
- **Admin Dashboard:** `http://localhost:3000/admin` (requires login)

## Admin Dashboard Features

Once logged in, you can access:

1. **Dashboard** - Overview with statistics
2. **Elections** - Manage elections
3. **Candidates** - Manage candidates
4. **Voters** - View and manage voters
5. **Blockchain** - View blockchain ledger
6. **Results** - View voting results

## Troubleshooting

### If you can't access `/admin`:
- Make sure you're logged in first (visit `/admin/login`)
- Check browser console for errors
- Clear localStorage and try again:
  ```javascript
  localStorage.clear()
  ```

### If login doesn't work:
- Make sure your backend server is running on `http://127.0.0.1:5000`
- Check browser console for API errors
- Verify the backend authentication endpoint is working

## Quick Test

1. Open: `http://localhost:3000/admin/login`
2. Enter: username: `admin`, password: `admin123`
3. Click "Sign In"
4. You should be redirected to the admin dashboard

