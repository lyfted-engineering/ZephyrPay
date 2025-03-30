Here’s a **detailed Agile Sprint Plan** for building the MVP of **ZephyrPay**, based on an 8-week delivery timeline using **2-week sprints**. This plan is aligned with the revised PRD, feature-locked scope, and full stack architecture.

---

# 🗂️ ZephyrPay MVP — Agile Sprint Plan

## 🧭 Assumptions
- **Team Composition**:
  - 1 Backend Engineer
  - 1 Smart Contract/Blockchain Engineer
  - 1 Frontend Engineer
  - 1 DevOps/Infra Support
  - 1 PM/Scrum Master
- **Sprint Length**: 2 Weeks
- **Methodology**: Scrum with TDD/BDD and weekly check-ins

---

## ✅ Sprint 0: Kickoff & Setup (Week 0)

**Goals**:
- Set up environments, tools, and codebase structure
- Confirm product scope and tech stack

**Tasks**:
- Finalize PRD + Technical Specs
- Setup GitHub repo, branch strategy, CI/CD pipelines
- Setup Supabase, Redis, LNBits, and Web3 providers
- Docker base environment for services
- Define testing strategy (Jest/Pytest, Hardhat)
- Schedule weekly sprint review/demo

---

## 🚀 Sprint 1: Authentication, RBAC & User System (Week 1–2)

**Goals**:
- Core user auth
- Role-based access
- Wallet linking (ETH, Lightning)

**Features**:
- `POST /auth/register`
- `POST /auth/login`
- `POST /auth/recover`
- `POST /auth/reset`
- `GET /user/profile`
- `PUT /user/profile`
- `POST /user/link-wallet`
- RBAC Middleware (Admin, Operator, Member)
- JWT auth + token refresh
- SIWE + lnurl-auth integration

**Deliverables**:
- Auth flows complete
- Role-based routing secure
- Test coverage for all user flows

---

## ⚡ Sprint 2: Lightning + Ethereum Payments (Week 3–4)

**Goals**:
- Invoice management
- Payment verifications

**Features**:
- `POST /lightning/invoice`
- `GET /lightning/invoice/:id`
- `POST /eth/payment/verify`
- `GET /user/transactions`
- QR code generator for both Lightning + ETH
- ETH tx hash verification + confirmation listener

**Deliverables**:
- Payments complete via both networks
- Simulated frontend payment checkout
- End-to-end payment confirmation events

---

## 🧾 Sprint 3: NFT Memberships + POS Checkout (Week 5–6)

**Goals**:
- Membership NFT contract
- POS integration

**Features**:
- ERC-721 deployment (Membership Tier NFT)
- `POST /nft/verify`
- `POST /pos/checkout`
- `GET /pos/history`
- Membership minting logic
- POS mock UI (cashier panel)
- NFT metadata fetch (on-chain + off-chain hybrid)

**Deliverables**:
- NFT minted on ETH for new users
- POS can trigger Lightning or ETH checkout
- MVP dashboard showing transactions

---

## 🔁 Sprint 4: Subscriptions + Rewards (Week 7–8)

**Goals**:
- Recurring payments
- Loyalty logic
- Event check-ins

**Features**:
- Superfluid integration or off-chain recurring system
- `POST /subscriptions/create`
- `POST /subscriptions/cancel`
- `GET /subscriptions/status`
- `POST /events/checkin`
- `POST /rewards/redeem`
- `GET /rewards`
- Loyalty NFT issuance (ERC-1155)
- Webhook triggers for payment/visit rewards

**Deliverables**:
- Subscriptions activate and mint NFTs
- Rewards system logs usage
- MVP pilot test-ready

---

## 🧪 Sprint 5: Pilot Launch & Testing (Optional Buffer)

**Goals**:
- Deploy MVP to test venues
- Bug fixes and real-world QA

**Tasks**:
- Setup pilot environment
- Run live test at 1–2 IRL spaces
- Validate payments, access, rewards
- Capture feedback and iterate

---

## 📈 Summary Sprint Timeline

| Sprint     | Focus                              | Duration     |
|------------|-------------------------------------|--------------|
| Sprint 0   | Setup, CI/CD, Infra, Tooling        | Week 0       |
| Sprint 1   | Auth, RBAC, Wallets                 | Week 1–2     |
| Sprint 2   | Payments (Lightning + Ethereum)     | Week 3–4     |
| Sprint 3   | NFT Memberships + POS               | Week 5–6     |
| Sprint 4   | Subscriptions, Check-in, Loyalty    | Week 7–8     |
| Sprint 5   | Buffer + Pilot                      | Week 9 (opt) |

---

