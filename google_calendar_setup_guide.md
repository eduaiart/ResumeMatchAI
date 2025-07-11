# Google Calendar Integration Setup Guide

Your Google OAuth client was deleted, which is why you're seeing the "Access blocked: Authorization Error" message. Here's how to fix it:

## Step 1: Create New Google Cloud Project & OAuth Credentials

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable Google Calendar API**
   - Go to "APIs & Services" → "Library"
   - Search for "Google Calendar API"
   - Click "Enable"

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in the required information:
     - App name: "Fit2Hire"
     - User support email: your email
     - Developer contact: your email
   - Add scopes: `https://www.googleapis.com/auth/calendar`
   - Add test users (include your email address)

4. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Name: "Fit2Hire Calendar Integration"
   - **Authorized redirect URIs**: Add your Replit domain
     - Format: `https://your-repl-name.your-username.repl.co/oauth2callback`
     - Example: `https://fit2hire-app.yourname.repl.co/oauth2callback`

## Step 2: Update Replit Secrets

1. Copy your new Client ID and Client Secret from Google Cloud Console
2. In Replit, go to "Secrets" (lock icon in sidebar)
3. Update the values:
   - `GOOGLE_CLIENT_ID`: Your new client ID
   - `GOOGLE_CLIENT_SECRET`: Your new client secret

## Step 3: Test the Integration

1. Go to your Fit2Hire application
2. Click "Appointments" in the navigation
3. Try to schedule an appointment - this will trigger the OAuth flow
4. You should be redirected to Google for authentication

## Common Issues & Solutions

**Issue**: "Access blocked: Authorization Error"
**Solution**: Make sure your redirect URI in Google Cloud Console exactly matches your Replit domain

**Issue**: "OAuth client was deleted"
**Solution**: You need to create a new OAuth client (follow steps above)

**Issue**: "Invalid redirect URI"
**Solution**: Check that your Replit domain is correctly added to authorized redirect URIs

## Your Current Google Cloud Run Domain

Based on your deployment, your redirect URI should be:
```
https://fit2start-1077229103364.europe-west1.run.app/oauth2callback
```

Make sure this exact URL is added to your Google Cloud Console OAuth credentials.

## Testing Checklist

- [ ] Google Calendar API is enabled
- [ ] OAuth consent screen is configured
- [ ] OAuth client ID is created with correct redirect URI
- [ ] Replit secrets are updated with new credentials
- [ ] Test authentication flow works

Once you've completed these steps, the Google Calendar integration should work properly!