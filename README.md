# LessonLift

AI-Powered Lesson Plan Generator for educators

## Features

- AI-powered lesson plan generation
- User authentication with Supabase
- Subscription management with Stripe
- Free trial system (3 lessons)
- Tiered pricing plans (Starter, Professional, Enterprise)
- Lesson history and management
- Responsive design with React + TypeScript + Vite

## Tech Stack

- **Frontend**: React 18, TypeScript, Vite, Tailwind CSS
- **Backend**: Supabase (Auth, Database, Edge Functions)
- **Payments**: Stripe
- **Deployment**: Netlify

## Quick Deploy to Netlify

### Option 1: Connect GitHub Repository

1. Go to [app.netlify.com](https://app.netlify.com)
2. Click "Add new site" → "Import an existing project"
3. Choose "GitHub" and authorize Netlify
4. Select the `lessonlift` repository
5. Configure build settings (auto-detected from netlify.toml):
   - Build command: `npm run build`
   - Publish directory: `dist`
6. Add environment variables (see below)
7. Click "Deploy site"

### Option 2: Manual Deploy

1. Download the production build archive: `lessonlift-netlify-deploy.tar.gz`
2. Extract the archive locally
3. Go to [app.netlify.com](https://app.netlify.com)
4. Click "Add new site" → "Deploy manually"
5. Drag and drop the extracted folder
6. Add environment variables (see below)
7. Redeploy after adding environment variables

## Environment Variables

Add these in Netlify Site Settings → Environment Variables:

```
VITE_SUPABASE_URL=your_supabase_project_url
VITE_SUPABASE_ANON_KEY=your_supabase_anon_key
VITE_STRIPE_PUBLISHABLE_KEY=your_stripe_publishable_key
```

## Supabase Setup

1. Create a new Supabase project
2. Run all migrations in `supabase/migrations/` folder (in order)
3. Deploy edge functions:
   - `generate-lesson` - AI lesson generation
   - `stripe-checkout` - Create Stripe checkout sessions
   - `stripe-webhook` - Handle Stripe webhook events
4. Configure Stripe webhook URL in Stripe Dashboard

## Stripe Setup

1. Create a Stripe account
2. Set up products and pricing:
   - Starter Plan: $19.99/month (50 lessons/month)
   - Professional Plan: $39.99/month (200 lessons/month)
   - Enterprise Plan: $79.99/month (unlimited lessons)
3. Configure webhook endpoint: `https://your-project.supabase.co/functions/v1/stripe-webhook`
4. Add webhook events: `checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`

## Local Development

```bash
# Install dependencies
npm install

# Start dev server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Project Structure

```
lessonlift/
├── src/
│   ├── components/       # React components
│   ├── contexts/         # React contexts (Auth)
│   ├── hooks/            # Custom React hooks
│   ├── lib/              # Third-party library configs
│   ├── pages/            # Page components
│   ├── services/         # API services
│   └── utils/            # Utility functions
├── supabase/
│   ├── functions/        # Edge functions
│   └── migrations/       # Database migrations
└── public/               # Static assets
```

## License

All rights reserved.
