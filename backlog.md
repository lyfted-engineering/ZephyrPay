Here’s a **detailed backlog of Epics and User Stories** for the **ZephyrPay MVP**, structured to be immediately usable in GitHub Issues or Shortcut (formerly Clubhouse). The backlog is organized by Epics, each with clear user stories, acceptance criteria, and developer-friendly descriptions.

---

# 🧩 ZephyrPay MVP Backlog

---

## 🔐 Epic 1: User Authentication & Account Management

**Goal**: Enable secure registration, login, password reset, and wallet linking.

---

### 📌 Story 1.1: User Registration  
**As a** new user  
**I want to** register with my email and password  
**So that** I can create an account on ZephyrPay  

**Acceptance Criteria**:
- Validate email and password
- Store hashed password securely
- Return JWT on successful registration

---

### 📌 Story 1.2: User Login  
**As a** registered user  
**I want to** log in with my credentials  
**So that** I can access the platform  

**Acceptance Criteria**:
- Validate credentials
- Issue JWT and refresh token
- Deny access if credentials invalid

---

### 📌 Story 1.3: Password Recovery  
**As a** user  
**I want to** recover my account if I forget my password  
**So that** I can regain access securely  

**Acceptance Criteria**:
- Send reset token via email
- Validate token and allow password reset

---

### 📌 Story 1.4: Link ETH & LN Wallets  
**As a** user  
**I want to** link my Ethereum and Lightning wallets  
**So that** I can use crypto features  

**Acceptance Criteria**:
- Accept public ETH and LN keys
- Persist linkage in user profile

---

## 🧑‍💼 Epic 2: Role-Based Access Control (RBAC)

**Goal**: Assign user roles and restrict access by permission level.

---

### 📌 Story 2.1: Assign Roles  
**As an** admin  
**I want to** assign roles to users (Admin, Operator, Member)  
**So that** they have the correct access  

**Acceptance Criteria**:
- Assignable on registration or via admin UI
- Stored in `user.role` field

---

### 📌 Story 2.2: Middleware Enforcement  
**As a** system  
**I want to** block unauthorized access  
**So that** users only access permitted endpoints  

**Acceptance Criteria**:
- Middleware checks JWT + role
- Returns 403 if unauthorized

---

## ⚡ Epic 3: Payments (Lightning & Ethereum)

**Goal**: Allow users to make crypto payments.

---

### 📌 Story 3.1: Generate Lightning Invoice  
**As a** member  
**I want to** generate a Lightning invoice  
**So that** I can pay for access or services  

**Acceptance Criteria**:
- Call LNBits API
- Return invoice string + QR code

---

### 📌 Story 3.2: Confirm Lightning Payment  
**As a** system  
**I want to** check payment status  
**So that** I can unlock services  

**Acceptance Criteria**:
- Poll or listen for `PAID` status
- Trigger webhook/action on confirmation

---

### 📌 Story 3.3: Verify Ethereum Payment  
**As a** member  
**I want to** send ETH or USDC  
**So that** I can unlock access  

**Acceptance Criteria**:
- Accept `tx_hash`, validate via Infura
- Confirm amount + token + status

---

## 🧾 Epic 4: NFT Membership System

**Goal**: Represent membership using ERC-721 NFTs.

---

### 📌 Story 4.1: Mint NFT Membership  
**As a** user  
**I want to** mint a membership NFT  
**So that** I can access Zo Houses  

**Acceptance Criteria**:
- Use smart contract to mint
- Store metadata: tier, expiration, perks

---

### 📌 Story 4.2: Verify NFT Ownership  
**As a** system  
**I want to** verify NFT ownership  
**So that** I can grant or deny access  

**Acceptance Criteria**:
- Accept ETH address
- Return `true/false` for valid token ID

---

## 🧾 Epic 5: Subscription & Streaming Payments

**Goal**: Enable recurring billing and reward systems.

---

### 📌 Story 5.1: Create Subscription  
**As a** user  
**I want to** subscribe monthly or annually  
**So that** I don’t have to pay each time  

**Acceptance Criteria**:
- Use Superfluid or DB tracking
- Return active stream or token

---

### 📌 Story 5.2: Cancel or Pause Subscription  
**As a** user  
**I want to** cancel or pause my subscription  
**So that** I can stop charges  

**Acceptance Criteria**:
- Stop stream or update DB status

---

## 🧾 Epic 6: POS Interface & Checkouts

**Goal**: Allow operators to collect crypto payments IRL.

---

### 📌 Story 6.1: Checkout With Lightning  
**As a** space operator  
**I want to** generate a Lightning invoice  
**So that** I can receive IRL payment  

---

### 📌 Story 6.2: Checkout With Ethereum  
**As a** space operator  
**I want to** collect ETH/USDC via QR  
**So that** I can accept crypto at the register  

---

### 📌 Story 6.3: View Checkout History  
**As a** merchant  
**I want to** see a list of past payments  
**So that** I can track performance  

---

## 🎟️ Epic 7: Loyalty & Rewards

**Goal**: Reward members for engagement.

---

### 📌 Story 7.1: Issue Loyalty NFTs  
**As a** system  
**I want to** mint NFTs for event attendance  
**So that** users feel rewarded  

---

### 📌 Story 7.2: Redeem Perks  
**As a** member  
**I want to** trade loyalty points for rewards  
**So that** I benefit from consistent usage  

---

## 📍 Epic 8: Event Check-in System

**Goal**: Enable space operators to log physical presence.

---

### 📌 Story 8.1: Check In With NFT or Payment  
**As a** user  
**I want to** check in via QR or NFT scan  
**So that** my attendance is logged  

---

## 🧰 Epic 9: DevOps & Infra

**Goal**: Provide stable backend infra and environments.

---

### 📌 Story 9.1: CI/CD Pipeline  
**As a** developer  
**I want to** auto-deploy code from GitHub  
**So that** we streamline testing  

---

### 📌 Story 9.2: Supabase + LNBits + IPFS Setup  
**As a** team  
**We need to** configure backend services  
**So that** app works across all layers  

---

## 🧪 Epic 10: Testing & QA

---

### 📌 Story 10.1: Unit Tests  
**As a** developer  
**I want to** ensure all modules are tested  
**So that** the code is reliable  

---

### 📌 Story 10.2: E2E Tests  
**As a** QA tester  
**I want to** simulate real user flows  
**So that** we can catch bugs before launch  

---

## 📈 Epic 11: MVP Launch & Pilot

---

### 📌 Story 11.1: Admin Dashboard  
**As an** admin  
**I want to** monitor user activity and payments  
**So that** I can manage operations  

---

### 📌 Story 11.2: Deploy to Partner Venue  
**As a** pilot team  
**We want to** test the platform in a real venue  
**So that** we validate UX and performance  

---
