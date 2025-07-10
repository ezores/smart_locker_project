# Stripe Integration Guide

## Overview

This document provides a comprehensive guide for integrating Stripe payment processing into the Smart Locker System. The integration will enable secure payment processing for locker rentals, late fees, and subscription services.

## Features

- **Secure Payment Processing**: Stripe Checkout for one-time payments
- **Subscription Management**: Recurring payments for locker rentals
- **Webhook Handling**: Automatic payment confirmation and status updates
- **Payment History**: Complete transaction records and receipts
- **Multi-currency Support**: USD, EUR, and other major currencies

## Prerequisites

1. **Stripe Account**: Create a Stripe account at [stripe.com](https://stripe.com)
2. **API Keys**: Get your publishable and secret keys from the Stripe Dashboard
3. **Webhook Endpoint**: Set up a webhook endpoint for payment notifications

## Installation

### 1. Install Stripe Python Library

```bash
pip install stripe
```

### 2. Add to requirements.txt

```txt
stripe==7.8.0
```

### 3. Environment Variables

Add these to your `.env` file:

```env
STRIPE_PUBLISHABLE_KEY=pk_test_your_publishable_key_here
STRIPE_SECRET_KEY=sk_test_your_secret_key_here
STRIPE_WEBHOOK_SECRET=whsec_your_webhook_secret_here
```

## Backend Implementation

### 1. Stripe Configuration

```python
# backend/stripe_config.py
import stripe
import os
from flask import current_app

def init_stripe():
    """Initialize Stripe with API keys"""
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    return stripe

def get_publishable_key():
    """Get Stripe publishable key for frontend"""
    return os.getenv('STRIPE_PUBLISHABLE_KEY')
```

### 2. Payment Models

```python
# backend/models.py - Add to existing models

class Payment(db.Model):
    """Payment model for tracking transactions"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_payment_intent_id = db.Column(db.String(255), unique=True)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='usd')
    status = db.Column(db.String(20), default='pending')  # pending, completed, failed
    payment_method = db.Column(db.String(50))  # card, bank_transfer, etc.
    description = db.Column(db.Text)
    metadata = db.Column(db.JSON)  # Store additional data
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='payments')

class Subscription(db.Model):
    """Subscription model for recurring payments"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    stripe_subscription_id = db.Column(db.String(255), unique=True)
    status = db.Column(db.String(20), default='active')  # active, canceled, past_due
    current_period_start = db.Column(db.DateTime)
    current_period_end = db.Column(db.DateTime)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    currency = db.Column(db.String(3), default='usd')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='subscriptions')
```

### 3. Payment API Endpoints

```python
# backend/app.py - Add these routes

@app.route('/api/payments/create-payment-intent', methods=['POST'])
@jwt_required()
def create_payment_intent():
    """Create a Stripe Payment Intent for one-time payments"""
    try:
        data = request.get_json()
        amount = data.get('amount')  # Amount in cents
        currency = data.get('currency', 'usd')
        description = data.get('description', 'Smart Locker Payment')
        metadata = data.get('metadata', {})

        # Get current user
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        # Create Payment Intent
        intent = stripe.PaymentIntent.create(
            amount=amount,
            currency=currency,
            description=description,
            metadata={
                'user_id': current_user_id,
                'user_email': user.email,
                **metadata
            }
        )

        # Create payment record
        payment = Payment(
            user_id=current_user_id,
            stripe_payment_intent_id=intent.id,
            amount=amount / 100,  # Convert from cents
            currency=currency,
            description=description,
            metadata=metadata
        )
        db.session.add(payment)
        db.session.commit()

        return jsonify({
            'client_secret': intent.client_secret,
            'payment_id': payment.id
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/payments/create-subscription', methods=['POST'])
@jwt_required()
def create_subscription():
    """Create a Stripe Subscription for recurring payments"""
    try:
        data = request.get_json()
        price_id = data.get('price_id')  # Stripe Price ID
        metadata = data.get('metadata', {})

        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)

        # Create or get customer
        if not user.stripe_customer_id:
            customer = stripe.Customer.create(
                email=user.email,
                metadata={'user_id': current_user_id}
            )
            user.stripe_customer_id = customer.id
            db.session.commit()

        # Create subscription
        subscription = stripe.Subscription.create(
            customer=user.stripe_customer_id,
            items=[{'price': price_id}],
            metadata=metadata
        )

        # Create subscription record
        sub_record = Subscription(
            user_id=current_user_id,
            stripe_subscription_id=subscription.id,
            status=subscription.status,
            current_period_start=datetime.fromtimestamp(subscription.current_period_start),
            current_period_end=datetime.fromtimestamp(subscription.current_period_end),
            amount=subscription.items.data[0].price.unit_amount / 100,
            currency=subscription.currency
        )
        db.session.add(sub_record)
        db.session.commit()

        return jsonify({
            'subscription_id': subscription.id,
            'status': subscription.status
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/payments', methods=['GET'])
@jwt_required()
def get_payments():
    """Get payment history for current user"""
    try:
        current_user_id = get_jwt_identity()
        payments = Payment.query.filter_by(user_id=current_user_id).order_by(Payment.created_at.desc()).all()

        return jsonify([{
            'id': payment.id,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'description': payment.description,
            'payment_method': payment.payment_method,
            'created_at': payment.created_at.isoformat(),
            'metadata': payment.metadata
        } for payment in payments])

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/payments/<int:payment_id>', methods=['GET'])
@jwt_required()
def get_payment(payment_id):
    """Get specific payment details"""
    try:
        current_user_id = get_jwt_identity()
        payment = Payment.query.filter_by(id=payment_id, user_id=current_user_id).first()

        if not payment:
            return jsonify({'error': 'Payment not found'}), 404

        return jsonify({
            'id': payment.id,
            'amount': float(payment.amount),
            'currency': payment.currency,
            'status': payment.status,
            'description': payment.description,
            'payment_method': payment.payment_method,
            'created_at': payment.created_at.isoformat(),
            'metadata': payment.metadata
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/api/webhooks/stripe', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for payment events"""
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get('Stripe-Signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, os.getenv('STRIPE_WEBHOOK_SECRET')
        )
    except ValueError as e:
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError as e:
        return jsonify({'error': 'Invalid signature'}), 400

    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_payment_success(payment_intent)
    elif event['type'] == 'payment_intent.payment_failed':
        payment_intent = event['data']['object']
        handle_payment_failure(payment_intent)
    elif event['type'] == 'invoice.payment_succeeded':
        invoice = event['data']['object']
        handle_subscription_payment(invoice)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_update(subscription)

    return jsonify({'status': 'success'})

def handle_payment_success(payment_intent):
    """Handle successful payment"""
    payment = Payment.query.filter_by(
        stripe_payment_intent_id=payment_intent['id']
    ).first()

    if payment:
        payment.status = 'completed'
        payment.payment_method = payment_intent['payment_method_types'][0]
        db.session.commit()

def handle_payment_failure(payment_intent):
    """Handle failed payment"""
    payment = Payment.query.filter_by(
        stripe_payment_intent_id=payment_intent['id']
    ).first()

    if payment:
        payment.status = 'failed'
        db.session.commit()

def handle_subscription_payment(invoice):
    """Handle subscription payment"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=invoice['subscription']
    ).first()

    if subscription:
        # Create payment record for subscription
        payment = Payment(
            user_id=subscription.user_id,
            stripe_payment_intent_id=invoice['payment_intent'],
            amount=invoice['amount_paid'] / 100,
            currency=invoice['currency'],
            status='completed',
            description=f"Subscription payment - {subscription.id}",
            payment_method='subscription'
        )
        db.session.add(payment)
        db.session.commit()

def handle_subscription_update(subscription_data):
    """Handle subscription status updates"""
    subscription = Subscription.query.filter_by(
        stripe_subscription_id=subscription_data['id']
    ).first()

    if subscription:
        subscription.status = subscription_data['status']
        subscription.current_period_start = datetime.fromtimestamp(subscription_data['current_period_start'])
        subscription.current_period_end = datetime.fromtimestamp(subscription_data['current_period_end'])
        db.session.commit()
```

## Frontend Implementation

### 1. Install Stripe.js

```bash
npm install @stripe/stripe-js
```

### 2. Stripe Configuration

```javascript
// frontend/src/utils/stripe.js
import { loadStripe } from "@stripe/stripe-js";

let stripePromise;

export const getStripe = () => {
  if (!stripePromise) {
    stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLISHABLE_KEY);
  }
  return stripePromise;
};
```

### 3. Payment Component

```javascript
// frontend/src/components/PaymentForm.jsx
import React, { useState } from "react";
import { CardElement, useStripe, useElements } from "@stripe/react-stripe-js";
import axios from "axios";

const PaymentForm = ({ amount, description, onSuccess, onError }) => {
  const stripe = useStripe();
  const elements = useElements();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setLoading(true);
    setError(null);

    if (!stripe || !elements) {
      return;
    }

    try {
      // Create payment intent
      const { data } = await axios.post("/api/payments/create-payment-intent", {
        amount: amount * 100, // Convert to cents
        currency: "usd",
        description: description,
      });

      // Confirm payment
      const { error: stripeError, paymentIntent } =
        await stripe.confirmCardPayment(data.client_secret, {
          payment_method: {
            card: elements.getElement(CardElement),
          },
        });

      if (stripeError) {
        setError(stripeError.message);
        onError?.(stripeError);
      } else {
        onSuccess?.(paymentIntent);
      }
    } catch (err) {
      setError("Payment failed. Please try again.");
      onError?.(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="border rounded-lg p-4">
        <CardElement
          options={{
            style: {
              base: {
                fontSize: "16px",
                color: "#424770",
                "::placeholder": {
                  color: "#aab7c4",
                },
              },
            },
          }}
        />
      </div>

      {error && <div className="text-red-600 text-sm">{error}</div>}

      <button
        type="submit"
        disabled={!stripe || loading}
        className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 disabled:opacity-50"
      >
        {loading ? "Processing..." : `Pay $${amount}`}
      </button>
    </form>
  );
};

export default PaymentForm;
```

### 4. Stripe Provider Setup

```javascript
// frontend/src/App.jsx
import { Elements } from "@stripe/react-stripe-js";
import { getStripe } from "./utils/stripe";

function App() {
  return <Elements stripe={getStripe()}>{/* Your app components */}</Elements>;
}
```

## Usage Examples

### 1. One-time Payment

```javascript
// Create a payment for locker rental
const handleLockerPayment = async (lockerId, amount) => {
  try {
    const response = await axios.post("/api/payments/create-payment-intent", {
      amount: amount * 100,
      description: `Locker rental - ${lockerId}`,
      metadata: {
        locker_id: lockerId,
        payment_type: "rental",
      },
    });

    // Redirect to payment form or Stripe Checkout
    window.location.href = `/payment/${response.data.payment_id}`;
  } catch (error) {
    console.error("Payment creation failed:", error);
  }
};
```

### 2. Subscription Payment

```javascript
// Create a subscription for monthly locker access
const handleSubscription = async (priceId) => {
  try {
    const response = await axios.post("/api/payments/create-subscription", {
      price_id: priceId,
      metadata: {
        subscription_type: "monthly_locker",
      },
    });

    console.log("Subscription created:", response.data);
  } catch (error) {
    console.error("Subscription creation failed:", error);
  }
};
```

### 3. Payment History

```javascript
// Get user's payment history
const fetchPaymentHistory = async () => {
  try {
    const response = await axios.get("/api/payments");
    setPayments(response.data);
  } catch (error) {
    console.error("Failed to fetch payments:", error);
  }
};
```

## Testing

### 1. Test Cards

Use these test card numbers for development:

- **Success**: `4242424242424242`
- **Decline**: `4000000000000002`
- **Requires Authentication**: `4000002500003155`

### 2. Test Webhooks

Use Stripe CLI to test webhooks locally:

```bash
# Install Stripe CLI
brew install stripe/stripe-cli/stripe

# Login to Stripe
stripe login

# Forward webhooks to your local server
stripe listen --forward-to localhost:5050/api/webhooks/stripe
```

## Security Considerations

1. **Never expose secret keys** in frontend code
2. **Always verify webhook signatures** before processing events
3. **Use HTTPS** in production for all payment-related requests
4. **Implement proper error handling** for failed payments
5. **Store minimal sensitive data** - rely on Stripe for payment details

## Production Deployment

1. **Update environment variables** with production Stripe keys
2. **Configure webhook endpoints** in Stripe Dashboard
3. **Set up proper SSL certificates** for HTTPS
4. **Monitor payment logs** and webhook events
5. **Implement proper error logging** and alerting

## Support

For Stripe-specific issues:

- [Stripe Documentation](https://stripe.com/docs)
- [Stripe Support](https://support.stripe.com)
- [Stripe Community](https://community.stripe.com)

For Smart Locker System integration issues:

- Check the application logs
- Review webhook event logs in Stripe Dashboard
- Verify API key configuration
