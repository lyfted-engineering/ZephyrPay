# ZephyrPay

**ZephyrPay** is a crypto-native payment and access management platform designed for member-only spaces such as coworking hubs, social clubs, hacker houses, maker spaces, and event venues. The platform supports Bitcoin Lightning Network and Ethereum-based payments, NFT-gated memberships, subscriptions, event check-ins, and loyalty rewards—all via a robust API-first architecture with a full-featured frontend.

---

## 🚀 Features

### 🔐 Authentication & Access Control
- Email/password login with JWT
- Role-based access (Admin, Operator, Member)
- Wallet linking for Ethereum (Metamask) and Lightning Network (lnurl-auth)

### ⚡ Payments
- Bitcoin Lightning Network (via LNBits)
- Ethereum (ETH) and ERC-20 tokens (e.g., USDC)
- Invoice creation, QR code checkout, and real-time payment confirmation

### 🪪 NFT Memberships
- Mint ERC-721 NFTs for tiered memberships
- Verify ownership for access gating
- Metadata includes tier, expiration, and perks

### 🔁 Subscriptions
- Monthly, Quarterly, Annual subscriptions via:
  - Ethereum Smart Contracts (Superfluid or ERC-4337)
  - Off-chain billing with webhook logic

### 💳 Point-of-Sale (POS)
- IRL POS UI for space operators
- Lightning or Ethereum payment support
- Transaction history dashboard

### 🎖️ Loyalty & Rewards
- NFT-based loyalty rewards using ERC-1155
- Issue badges for attendance, purchases, milestones
- Redeemable through the dashboard

### 📲 Check-Ins
- Event check-in via QR code or wallet/NFT scan
- Triggers attendance logs and loyalty rewards

---

## 📦 Tech Stack

### Frontend:
- Next.js 14+ (App Router)
- Tailwind CSS + ShadCN/UI
- wagmi + viem (Ethereum)
- lnurl-auth / Alby SDK (Lightning)
- React Query + React Context
- QRCode Generator (`qrcode.react`)

### Backend:
- FastAPI (Python)
- PostgreSQL (via Supabase)
- Redis (Session cache)
- LNBits (Bitcoin Lightning)
- Web3.py / Ethers.js (Ethereum integration)

### Smart Contracts:
- ERC-721: NFT Memberships
- ERC-1155: Loyalty NFTs
- Superfluid: Streaming subscriptions

---

## 🛠️ Installation

```bash
# Clone the repo
$ git clone https://github.com/your-org/zephyrpay.git
$ cd zephyrpay

# Frontend Setup
$ cd frontend
$ npm install
$ npm run dev

# Backend Setup
$ cd backend
$ python3 -m venv venv
$ source venv/bin/activate
$ pip install -r requirements.txt
$ uvicorn main:app --reload
```

---

## 🌐 Environments

| Service       | URL                   |
|---------------|------------------------|
| Frontend      | http://localhost:3000  |
| Backend API   | http://localhost:8000  |
| Supabase DB   | Supabase.io            |
| LNBits Node   | http://localhost:5000  |
| IPFS (optional) | [Infura, Pinata]     |

---

## 🧪 Testing

```bash
# Run frontend tests
$ npm run test

# Run backend tests
$ pytest
```

---

## 📂 Project Structure

```
zephyrpay/
├── frontend/            # Next.js frontend
│   ├── pages/
│   ├── components/
│   └── utils/
├── backend/             # FastAPI backend
│   ├── api/
│   ├── models/
│   └── routes/
├── smart-contracts/     # Hardhat or Foundry setup
│   ├── MembershipNFT.sol
│   ├── LoyaltyNFT.sol
│   └── Subscription.sol
└── README.md
```

---

## 🔐 Roles & Permissions

| Role     | Description                                |
|----------|--------------------------------------------|
| Admin    | Full access to dashboard, controls, users  |
| Operator | POS access, check-ins, limited config      |
| Member   | Standard access to services + wallet views |

---

## 📆 Development Timeline (MVP)

1. Auth & Wallet Linking ✅  
2. Crypto Payments & QR Checkout ✅  
3. NFT Membership + Minting ✅  
4. POS Flow & Transactions ✅  
5. Loyalty Engine + Check-Ins ✅  
6. Admin Dashboard & Subscriptions ✅  
7. Pilot Testing at Real Venues ✅

---

## 📄 License
MIT

---

## 🤝 Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 🙌 Acknowledgements
- LNBits for Lightning integration
- wagmi/viem for Ethereum wallet support
- Vercel’s Next.js SaaS Starter for frontend scaffold
- Supabase for managed PostgreSQL + auth services

---

Built with ❤️ by the ZephyrPay team
