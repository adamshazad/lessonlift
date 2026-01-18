/*
  # Fix RLS Performance and Security Issues

  ## Changes Made
  
  1. **RLS Performance Optimization**
     - Updated `stripe_customers` RLS policy to use `(select auth.uid())` for better performance
     - Updated `stripe_subscriptions` RLS policy to use `(select auth.uid())` for better performance
     - Updated `stripe_orders` RLS policy to use `(select auth.uid())` for better performance
     - This prevents re-evaluation of auth functions for each row
  
  2. **Security Notes**
     - All policies maintain the same security guarantees
     - Users can only view their own data
     - Soft-delete protection maintained (deleted_at IS NULL)
  
  ## Manual Configuration Required (Supabase Dashboard)
  
  After applying this migration, configure these settings in Supabase Dashboard:
  
  1. **Auth DB Connection Strategy**
     - Go to: Project Settings → Database → Connection Pooling
     - Change Auth connection pool from fixed "10 connections" to percentage-based
  
  2. **Leaked Password Protection**
     - Go to: Authentication → Policies → Password Protection
     - Enable "Check for compromised passwords" using HaveIBeenPwned
*/

-- Drop existing RLS policies that need optimization
DROP POLICY IF EXISTS "Users can view their own customer data" ON public.stripe_customers;
DROP POLICY IF EXISTS "Users can view their own subscription data" ON public.stripe_subscriptions;
DROP POLICY IF EXISTS "Users can view their own order data" ON public.stripe_orders;

-- Recreate stripe_customers policy with optimized RLS
CREATE POLICY "Users can view their own customer data"
  ON public.stripe_customers
  FOR SELECT
  TO authenticated
  USING (
    user_id = (select auth.uid())
    AND deleted_at IS NULL
  );

-- Recreate stripe_subscriptions policy with optimized RLS
CREATE POLICY "Users can view their own subscription data"
  ON public.stripe_subscriptions
  FOR SELECT
  TO authenticated
  USING (
    customer_id IN (
      SELECT customer_id
      FROM stripe_customers
      WHERE user_id = (select auth.uid())
      AND deleted_at IS NULL
    )
    AND deleted_at IS NULL
  );

-- Recreate stripe_orders policy with optimized RLS
CREATE POLICY "Users can view their own order data"
  ON public.stripe_orders
  FOR SELECT
  TO authenticated
  USING (
    customer_id IN (
      SELECT customer_id
      FROM stripe_customers
      WHERE user_id = (select auth.uid())
      AND deleted_at IS NULL
    )
    AND deleted_at IS NULL
  );
