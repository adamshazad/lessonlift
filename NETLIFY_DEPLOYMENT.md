# Netlify Deployment Guide for LessonLift

Your frontend is built and ready to deploy! Here's everything you need.

## 📦 What's Included in `dist/` Folder

```
dist/
├── index.html                    # Main HTML file
├── _redirects                    # SPA routing config for Netlify
├── 20250721_234954807_iOS.png   # Image asset
├── 20250913_141827376_iOS.jpg   # Image asset
└── assets/
    ├── index-CGifHRg1.css       # Compiled CSS (44KB)
    └── index-Cc-PKLAp.js        # Compiled JavaScript (563KB)
```

## 🚀 Deployment Methods

### Method 1: Netlify Drop (Quickest)

1. Go to [app.netlify.com/drop](https://app.netlify.com/drop)
2. Drag and drop the entire `dist/` folder
3. Your site will be live in seconds!
4. Add environment variables (see below)

### Method 2: Netlify CLI

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Login to Netlify
netlify login

# Deploy from project root
netlify deploy --prod --dir=dist
```

### Method 3: GitHub + Netlify (Recommended for Production)

1. Push your code to GitHub
2. Go to [app.netlify.com](https://app.netlify.com)
3. Click "Add new site" → "Import an existing project"
4. Connect your GitHub repository
5. Build settings are already configured in `netlify.toml`:
   - **Build command:** `npm run build`
   - **Publish directory:** `dist`
6. Add environment variables (see below)
7. Click "Deploy site"

## 🔐 Required Environment Variables

After deploying, add these environment variables in Netlify:

1. Go to **Site settings** → **Environment variables**
2. Add these variables:

```
VITE_SUPABASE_URL=https://rtmactxdmjjntlzwhqkm.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InllbXp4cmxlbGV1anFwbGh5bnV6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3Njc5MDkzMTgsImV4cCI6MjA4MzQ4NTMxOH0.MkUS89y632N2u2s-w9J0x9DlKt1f29NHhxFWvrvURP8
VITE_STRIPE_PUBLISHABLE_KEY=pk_test_51Pj2HGCVrhYYeZRk8dw19xB8kxEOBeWY10ZPjnnSFgbfrsrrlvmjPgpcHJLcWE0uzDv8SGVa2nifWTgHWR4DZvxs005FiX3Ofv
```

3. Click "Save" and trigger a new deployment

**Important:** These are build-time variables. After adding them, you must redeploy for changes to take effect.

## ⚙️ Netlify Configuration

Your project includes a `netlify.toml` file at the root with optimal settings:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[build.environment]
  NODE_VERSION = "18"
```

This ensures:
- ✅ Correct build command
- ✅ Correct publish directory
- ✅ SPA routing works (all routes go to index.html)
- ✅ Uses Node.js 18

## 🎯 Post-Deployment Checklist

After your site is live:

1. **Test Authentication**
   - Try signing up at `/signup`
   - Try logging in at `/login`
   - Verify email/password works

2. **Test Trial System**
   - Sign up as new user
   - Go to `/lesson-generator`
   - Generate a lesson
   - Check trial counter displays correctly

3. **Test Stripe Integration**
   - Go to `/pricing`
   - Click "Subscribe Now"
   - Verify Stripe checkout opens
   - Complete test payment (use test card: 4242 4242 4242 4242)
   - Verify redirect to success page
   - Check if plan activated in dashboard

4. **Test Plan Enforcement**
   - As trial user, try to generate 6th lesson (should block)
   - Wait 8 days (or modify DB) and verify trial expiration
   - As paid user, verify daily limits work
   - Verify monthly limits work

5. **Test All Routes**
   - Navigate to all pages
   - Refresh on different routes (should not 404)
   - Test deep linking

## 🔧 Troubleshooting

### Environment Variables Not Working
- Make sure they start with `VITE_`
- Redeploy after adding variables
- Check browser console for undefined values

### Routes Return 404
- Verify `_redirects` file exists in `dist/`
- Check Netlify deploy logs
- Ensure `netlify.toml` is in project root

### Supabase Connection Fails
- Verify environment variables are set correctly
- Check Supabase project is not paused
- Verify RLS policies are enabled

### Stripe Not Working
- Ensure webhook URL is set in Stripe dashboard
- Verify webhook secret matches environment variable
- Check Stripe is in test mode for development

## 📱 Custom Domain (Optional)

1. Go to **Domain settings** in Netlify
2. Click "Add custom domain"
3. Follow instructions to update DNS
4. SSL certificate is automatically provisioned

## 🔄 Continuous Deployment

With GitHub integration:
- Every push to `main` branch automatically rebuilds and deploys
- Pull requests create preview deployments
- Rollback to any previous deployment in one click

## 📊 Performance Optimization

Your build includes:
- ✅ Minified JavaScript (563KB)
- ✅ Minified CSS (44KB)
- ✅ Code splitting (can be improved)
- ✅ Gzip compression (enabled by Netlify)

To improve further:
- Enable dynamic imports for code splitting
- Use lazy loading for routes
- Optimize images (compress PNGs/JPGs)

## 🎉 You're Done!

Your LessonLift application is now live with:
- ✅ Full authentication system
- ✅ Free trial (5 lessons, 7 days)
- ✅ Paid plans (Starter, Standard, Pro)
- ✅ Stripe integration
- ✅ Limit enforcement
- ✅ SPA routing
- ✅ Production-ready build

Visit your Netlify URL and start generating lessons!
