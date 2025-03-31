# ZephyrPay for NGOs — Roadmap & PRD

## 🎯 Overview
This PRD outlines a strategic product roadmap and feature plan to extend the ZephyrPay platform to support Non-Governmental Organizations (NGOs), nonprofits, and community-led initiatives. ZephyrPay's architecture—built for borderless crypto payments, NFT access, and loyalty systems—is well-positioned to empower NGOs with secure, transparent, and global fundraising and volunteer engagement tools.

---

## 🧭 Goals
- Enable NGOs to accept global donations using Lightning Network and Ethereum.
- Issue NFTs as proof of impact, supporter badges, or engagement tokens.
- Empower NGOs to engage volunteers and donors with loyalty rewards.
- Provide transparent, verifiable fundraising and impact tracking.

---

## 🛠️ Key Features

### 1. **Donation Infrastructure (Lightning & Ethereum)**
- `POST /donation/invoice` — Generate donation QR code (LN/ETH)
- `GET /donation/:ngo_id` — Public donation page for any NGO
- Optional recurring donations via `/subscriptions/create`
- Embedded widget to copy or embed on external sites

### 2. **Supporter Membership NFTs**
- Mint ERC-721 NFTs to donors as proof of support
- Tier-based NFTs based on donation amount or frequency
- Perks: voting access, reports, exclusive content, token-gated forums

### 3. **Loyalty NFTs for Volunteers**
- NFT rewards based on volunteer check-ins or logged hours
- Gamified badges (ERC-1155): e.g., “Event Organizer”, “Advocate”, “Ambassador”
- Redeem for local perks or digital recognition

### 4. **Recurring Donations (Subscription Support)**
- Via Superfluid or webhook-driven off-chain subscription
- `POST /ngo/subscription/:ngo_id`
- Tiered backer flows with periodic NFT drops

### 5. **Transparency Dashboard**
- Optional public dashboards for:
  - On-chain donation receipts
  - NFT issuance
  - Volunteer participation logs

---

## 🧱 System Architecture Additions

| Feature                   | Affected Modules           | New APIs or UI       |
|--------------------------|-----------------------------|----------------------|
| Donation QR + Public Page| POS, Frontend, API Gateway  | `/donate/:ngo_id`    |
| Membership NFTs for NGOs | NFT Smart Contract          | `/nft/mint/supporter`|
| Volunteer Rewards        | Loyalty + Check-In APIs     | `/checkin/:event_id` |
| Transparency UI          | Frontend dashboard          | `/ngo/:id/dashboard` |
| NGO Admin Roles          | RBAC                        | `role = ngo_admin`   |

---

## 📆 Roadmap

### Phase 1 — Donation & QR Flow (Week 1–2)
- Create `donate` route and donation QR generator
- Accept ETH, USDC, and Lightning invoices for NGOs
- NGO onboarding form and listing page

### Phase 2 — NFT Supporter Memberships (Week 3–4)
- Smart contract deployment for tiered NFTs
- API endpoint for supporter NFT minting
- Wallet connection UX for minting and redemption

### Phase 3 — Volunteer Loyalty NFTs + Check-In (Week 5)
- Use `/checkin` flow to reward volunteer hours
- Webhook or time-tracked engagement = NFT badge

### Phase 4 — NGO Admin Dashboards (Week 6)
- Analytics dashboard for donations and volunteers
- Download CSV + export NFT claim links

### Phase 5 — Transparency & Reporting (Week 7–8)
- Public dashboards with funding logs (read-only)
- Optional proof-of-donation NFTs

---

## ✅ KPIs
- First 5 NGOs onboarded with public donation pages
- At least 50 unique wallets mint NFT supporter badges
- 100% uptime of donation endpoints
- Average NFT minting success < 6s
- 90% volunteer retention after first reward

---

## 📌 Notes
- Use ZephyrPay’s current role system to support `ngo_admin` with scoped permissions
- NFTs for NGOs will live on same contracts with metadata adjustments
- No changes to core smart contract logic required for MVP NGO support

---

**Prepared by:** ZephyrPay Team, Priya, Zo SF  
**Version:** NGO Expansion PRD v1.0  
**Last Updated:** [Insert Date]

