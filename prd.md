**Product Requirements Document (PRD)**

**Product Name:** ZephyrPay

**Overview:**
ZephyrPay is a crypto-native payment and access management platform for member-only spaces like coworking venues, social clubs, hacker houses, maker spaces, and event hubs. The platform enables seamless Bitcoin Lightning and Ethereum-based payments, while offering NFT-gated memberships, loyalty systems, recurring subscriptions, and a crypto-powered POS (point-of-sale) experience.

---

## 1. 🎯 Goals & Objectives

- Support fast, low-fee payments via Bitcoin Lightning Network
- Enable Ethereum-based memberships and NFT loyalty systems
- Facilitate one-time and recurring payments in crypto
- Provide an API-first platform for third-party integration
- Support IRL POS systems that accept crypto (Lightning, ETH, Stablecoins)
- Deliver a secure, composable, and scalable MVP for pilot use in real spaces
- Build a performant, responsive, and accessible frontend using Next.js

---

## 2. 👥 Target Users

- Space Operators (Coworking spaces, Clubs, Event venues)
- Community Members (freelancers, artists, founders, hackers)
- Developers integrating the API into access control or booking tools

---

## 3. 🧩 Key Features (MVP Locked)

### Backend Features:
- Crypto Payments (Lightning, Ethereum, USDC)
- NFT Memberships (ERC-721)
- Subscriptions (Smart contract + off-chain)
- Loyalty Rewards (NFT-based)
- POS System for IRL checkout
- Role-based Access Control (RBAC)
- Full REST API with secure endpoints
- Wallet Linking (ETH, Lightning)

### Frontend Features:
- Role-based user dashboards (Admin, Operator, Member)
- POS checkout interface
- NFT and Subscription status displays
- Lightning + Ethereum QR payment flows
- Check-in and loyalty redemption UI
- Admin dashboard for managing platform operations

---

## 4. 🧰 Technology Stack

### Backend:
- **FastAPI (Python)**
- **PostgreSQL (Supabase)**
- **Redis** (sessions/cache)
- **LNBits** (Lightning integration)
- **Ethers.js / Web3.py** (Ethereum interaction)

### Frontend:
- **Next.js (App Router, SSR)**
- **Tailwind CSS + ShadCN/UI**
- **wagmi + viem** (ETH wallet)
- **lnurl-auth, Alby SDK** (Lightning wallet)
- **qrcode.react** (QR generator)
- **SWR/React Query + Context API**

### Starter Template:
- **[Next.js SaaS Starter by Vercel](https://github.com/vercel/nextjs-saas-starter)**
  - Includes RBAC, Auth, Dashboard, Tailwind, Subscription UX
  - Replaces Stripe with custom LN/ETH integration

---

## 5. 📲 Core UI Pages (Frontend)

- `/` – Landing page
- `/login`, `/register` – Auth flows
- `/dashboard` – Role-based view
- `/profile`, `/subscriptions`, `/membership`
- `/pos`, `/checkin`, `/rewards`, `/admin`

---

## 6. 🔐 Authentication & RBAC

- Email/password login with JWT
- Wallet linking (Metamask, lnurl-auth)
- Route guards for role-based UI
- Admin, Operator, Member roles

---

## 7. 🔄 Backend API Endpoints

- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/recover`
- `POST /auth/reset`
- `GET /user/profile`
- `PUT /user/profile`
- `POST /user/link-wallet`
- `GET /user/transactions`
- `POST /lightning/invoice`
- `GET /lightning/invoice/:id`
- `POST /eth/payment/verify`
- `POST /nft/verify`
- `POST /subscriptions/create`
- `POST /subscriptions/cancel`
- `GET /subscriptions/status`
- `POST /access/unlock`
- `POST /events/checkin`
- `POST /rewards/redeem`
- `GET /rewards`
- `GET /perks`
- `POST /pos/checkout`
- `GET /pos/history`

---

## 8. 🧾 Smart Contracts

- **Membership NFT (ERC-721)**
  - Metadata: tier, expiration, perks, location
- **Subscription Contract**
  - Superfluid / ERC-4337
- **Loyalty NFT (ERC-1155)**
  - Auto-issued via webhook

---

## 9. 📈 Development Timeline (8 Weeks)

| Week | Milestone |
|------|-----------|
| 1    | Setup backend + frontend starter template |
| 2    | Auth system, RBAC, Lightning invoice UI/API |
| 3    | ETH wallet integration, QR UI, NFT minting/display |
| 4    | POS dashboard, payment + check-in flows |
| 5    | Subscription flows + Superfluid integration |
| 6    | Loyalty + rewards interface, mint NFTs |
| 7    | Admin dashboard + webhook testing |
| 8    | QA + Pilot Deployment to partner venue |

---

## 10. ✅ Success Metrics

- Payment confirmation in < 5 seconds
- NFT validation in < 5 seconds
- < 2s frontend page load
- 95% Lighthouse Accessibility Score
- Pilot tested in 1–3 IRL venues

---

## 11. 🚀 Future Considerations

- Mobile App version
- Fiat Off-Ramp (Strike, MoonPay)
- zkSync / L2 rollup support
- DAO ownership tools

---

**Prepared by:** Toby Morning
**Date:** 3/30/25 
**Version:** MVP v1.1

