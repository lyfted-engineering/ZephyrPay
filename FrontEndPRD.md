**Product Requirements Document (Frontend)**

**Product Name:** ZephyrPay – Frontend Platform

**Overview:**
This PRD outlines the frontend architecture, tooling, and UI/UX implementation plan for the ZephyrPay MVP. ZephyrPay is a crypto-native payment and access management platform for IRL communities, supporting Bitcoin Lightning and Ethereum payments, NFT-based memberships, subscriptions, check-ins, and loyalty rewards.

---

## 🎯 Objectives
- Build a performant, responsive, and accessible frontend using Next.js
- Provide role-based user experiences (Admin, Operator, Member)
- Seamlessly integrate with backend APIs and smart contract events
- Deliver modular, scalable components for payments, POS, auth, and membership flows

---

## 🧰 Technology Stack

### Framework:
- **Next.js (v14+)** – App Router, SSR/ISR, file-based routing

### Chosen Starter Template:
- **[Next.js SaaS Starter by Vercel](https://github.com/vercel/nextjs-saas-starter)**
  - Includes: Auth (JWT-based), RBAC, Team/User Dashboard, Stripe-integrated Subscriptions
  - Advantages: Minimal UI, Tailwind ready, API route support
  - Customization Path: Replace Stripe logic with LN/ETH payment components

### Styling:
- **Tailwind CSS** – Utility-first styling framework
- **ShadCN/UI** – Headless UI components

### State Management:
- **React Context API** for auth/session state
- **SWR/React Query** for API data fetching

### Wallet & Crypto Libraries:
- **wagmi + viem** – Ethereum wallet connection and contract interaction
- **lnurl-auth / Alby SDK** – For Lightning Network auth and invoice generation
- **qrcode.react** – QR code display for Lightning and ETH payments

---

## 👥 User Personas & Interfaces

### Admin:
- Manage users, roles, NFTs, and venue data
- View payment analytics and loyalty stats
- Deploy access rules and perks

### Operator (POS user):
- Checkout dashboard with item entry, crypto method selection
- Scan/check NFT memberships or confirm Lightning payments
- See POS history and earnings

### Member:
- Auth and wallet linking UI
- View NFT membership status and perks
- Pay via Lightning or ETH
- Redeem loyalty rewards
- Event check-in via QR scan or button

---

## 📲 Core UI Pages

### Public
- `/` – Landing page with marketing + call to action
- `/login` – Login form (email/password or wallet login)
- `/register` – Registration form

### Authenticated
- `/dashboard` – Role-based dashboard home
- `/profile` – View + edit account and wallets
- `/subscriptions` – Manage subscription tiers
- `/membership` – NFT membership status + mint/verify
- `/checkin` – Check-in page with QR scanner
- `/rewards` – Loyalty NFT rewards & redemption
- `/pos` – Operator interface for checkouts
- `/admin` – Admin panel (visible to `role=admin` only)

---

## 🔐 Authentication & RBAC
- Auth Flow: Email + password login with JWT
- Wallet Linking: Metamask & Lightning wallet via lnurl-auth
- Middleware-protected routes based on roles
- Role Support: Admin, Operator, Member

---

## 🔄 API Integration
- Fully integrated with backend endpoints:
  - Auth: `/auth/*`
  - Payments: `/lightning/invoice`, `/eth/payment/verify`
  - NFT: `/nft/verify`, `/subscriptions/*`, `/rewards/*`, etc.
  - POS: `/pos/checkout`, `/pos/history`
  - Profile: `/user/profile`, `/user/link-wallet`

---

## 📆 Development Phases (Frontend)

### Phase 1 – Bootstrap (Week 1)
- Setup repo with Next.js SaaS Starter
- Implement auth + registration
- Role-based routing & layout setup

### Phase 2 – Wallets & Payment UI (Week 2)
- ETH wallet connect (wagmi)
- LN wallet connect (lnurl-auth)
- Payment QR UI for both networks

### Phase 3 – Membership & Subscriptions (Week 3)
- Display NFT status
- Subscription flow (monthly, quarterly, yearly)
- Mint NFT call-to-action and success screen

### Phase 4 – POS Interface & Check-in (Week 4)
- POS cashier UI with Lightning/ETH checkout
- Check-in scanner for QR or wallet presence

### Phase 5 – Loyalty & Admin Panel (Week 5)
- View + redeem rewards (NFTs)
- Admin control panel for user + content ops

---

## ✅ KPIs for Frontend MVP
- <2s page load time
- >95% Lighthouse Accessibility Score
- Seamless wallet connection (Metamask, Alby)
- Fully integrated POS flow in <2 clicks
- NFT verified in under 5 seconds

---

**Prepared by:** [Your Team]  
**Date:** [Insert Date]  
**Version:** Frontend MVP v1.0
