**Product Requirements Document (PRD)**

**Product Name:** ZephyrPay

**Overview:**
ZephyrPay is a crypto-native payment and access management platform for member-only spaces like coworking venues, social clubs, hacker houses, maker spaces, and event hubs. The platform enables seamless Bitcoin Lightning and Ethereum-based payments, while offering NFT-gated memberships, loyalty systems, recurring subscriptions, and a crypto-powered POS (point-of-sale) experience.

---

### 1. **Goals & Objectives**

- Support **fast, low-fee payments** via Bitcoin Lightning Network.
- Enable **Ethereum-based memberships** and **NFT loyalty systems**.
- Facilitate **one-time and recurring payments** in crypto.
- Provide an **API-first** platform for third-party integration.
- Support **IRL POS systems** that accept crypto (Lightning, ETH, Stablecoins).
- Deliver a secure, composable, and scalable MVP for pilot use in real spaces.

---

### 2. **Target Users**

- Space Operators (Coworking spaces, Clubs, Event venues)
- Community Members (freelancers, artists, founders, hackers)
- Developers integrating the API into access control or booking tools

---

### 3. **Key Features (MVP Locked)**

#### 3.1 **Payment System**
- Accept payments in:
  - Bitcoin (via Lightning Network)
  - Ethereum (ETH)
  - ERC-20 tokens (USDC)
- Support payment via:
  - QR codes
  - WalletConnect (ETH)
  - LNURL (Lightning)
- Invoice creation, expiration, and status tracking
- Payment history per user and merchant

#### 3.2 **NFT-Gated Memberships**
- Mint ERC-721/1155 NFTs to represent:
  - Membership Tier (e.g. Basic, Premium)
  - Expiration Date
  - Perks / Metadata (IRL perks, guest passes)
- NFT Verification Endpoint
- On-chain + off-chain user linking (ETH wallet + LN pubkey)

#### 3.3 **Subscriptions**
- Monthly, Quarterly, and Annual recurring billing options
- Implementation Types:
  - ETH Smart Contract (Superfluid or ERC-4337 AA for automation)
  - Lightning recurring reminders + webhook logic
- Admin control to pause, cancel, or edit subscriptions

#### 3.4 **POS for IRL Spaces**
- Simple mobile-first cashier interface
- Add line-items, select payment method
- Generate Lightning invoices or ETH QR codes
- Confirm payment via WebSocket / Webhook
- Loyalty point tracking / NFT drop post-payment

#### 3.5 **Loyalty & Rewards Engine**
- Issue NFT badges for:
  - Attendance
  - Spending milestones
  - Event participation
- Webhook-triggered minting
- Points-to-NFT conversion (off-chain loyalty → on-chain reward)

#### 3.6 **API Platform**
- OpenAPI-compliant REST API
- Key Endpoints:
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
- API Key + OAuth 2.0 based Auth
- Role-Based Access Control (RBAC):
  - Roles: Admin, Operator, Member
  - Middleware for role-specific endpoint access

---

### 4. **System Architecture**

#### Backend Stack
- **FastAPI** (Python)
- **PostgreSQL** (via Supabase)
- **Redis** (for session/state cache)
- **LNBits** (for Bitcoin Lightning integration)
- **Ethers.js/Web3.py** (for Ethereum on-chain interactions)

#### Infrastructure
- **Dockerized Microservices**
- Hosted on **DigitalOcean** / **Railway** for MVP
- Option to run on **Umbrel** or local nodes for Lightning
- IPFS optional for NFT metadata

#### Webhooks
- Event-driven actions for:
  - Successful payment
  - NFT minted
  - Subscription renewal
  - Loyalty milestone achieved

---

### 5. **Smart Contracts**

#### Membership NFT Contract (ERC-721)
- Metadata:
  - `tier`
  - `expiration`
  - `perks[]`
  - `location`
- Mintable via admin or payment trigger

#### Subscription Contract
- Supports streaming payments (via Superfluid)
- Emits `SubscriptionActive` and `SubscriptionCancelled` events
- Linked to NFT issuance for perks

#### Loyalty NFT Contract
- Batch minting support (ERC-1155)
- Issued on webhook trigger

---

### 6. **Security & Compliance**
- Non-custodial wallet integrations preferred
- Rate-limiting on API endpoints
- SIWE (Sign-In with Ethereum) and lnurl-auth for login
- Encrypted storage of wallet linkage
- Role-Based Access Control (RBAC)
- JWT-based authentication and refresh tokens

---

### 7. **MVP Development Timeline (8 Weeks)**

| Week | Milestone |
|------|-----------|
| 1-2  | Auth system + RBAC + Lightning integration + invoice APIs |
| 2-3  | NFT minting, verification API, user linking |
| 3-4  | POS cashier UI + payment flow test + user profile APIs |
| 4-5  | Subscriptions API + off-chain logic |
| 5-6  | Smart contract deployments + Superfluid integration |
| 6-7  | Webhook + loyalty NFT logic |
| 8    | Final polish, admin dashboard, pilot testing |

---

### 8. **KPIs for Success**
- 100% uptime of payment flow
- <5 sec average payment confirmation time
- At least 2 successful Lightning + NFT IRL activations
- Pilot run at 1–3 real-world partner venues

---

### 9. **Future Considerations**
- Fiat off-ramps (e.g., Strike, MoonPay)
- DAO tools for venue ownership
- zkSync or L2 Ethereum support
- Mobile app for check-ins and loyalty tracking

---

**Prepared by:** Toby Morning
**Date:** 3/30/25 
**Version:** MVP v1.1

