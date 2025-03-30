@startuml

entity User {
  +id: UUID
  +email: string
  +password_hash: string
  +username: string
  +eth_address: string
  +ln_pubkey: string
  +role: enum {ADMIN, OPERATOR, MEMBER}
  +created_at: datetime
  +updated_at: datetime
}

entity AuthToken {
  +id: UUID
  +user_id: UUID
  +token: string
  +expires_at: datetime
}

entity PasswordResetRequest {
  +id: UUID
  +user_id: UUID
  +token: string
  +expires_at: datetime
}

entity NFTMembership {
  +id: UUID
  +user_id: UUID
  +token_id: string
  +tier: string
  +expiration: datetime
  +location: string
  +perks: json
  +contract_address: string
  +minted_at: datetime
}

entity LightningInvoice {
  +id: UUID
  +user_id: UUID
  +invoice_id: string
  +amount_sats: int
  +description: string
  +status: enum {PENDING, PAID, EXPIRED}
  +expires_at: datetime
  +paid_at: datetime
}

entity EthereumPayment {
  +id: UUID
  +user_id: UUID
  +tx_hash: string
  +amount_eth: float
  +token: string
  +status: enum {CONFIRMED, FAILED, PENDING}
  +timestamp: datetime
}

entity Subscription {
  +id: UUID
  +user_id: UUID
  +type: enum {MONTHLY, QUARTERLY, ANNUAL}
  +status: enum {ACTIVE, PAUSED, CANCELLED}
  +start_date: datetime
  +end_date: datetime
  +superfluid_stream_id: string
}

entity POSPayment {
  +id: UUID
  +user_id: UUID
  +operator_id: UUID
  +amount: float
  +currency: enum {SAT, ETH, USDC}
  +method: enum {LIGHTNING, ETHEREUM}
  +items: json
  +status: enum {PAID, CANCELLED}
  +paid_at: datetime
}

entity LoyaltyReward {
  +id: UUID
  +user_id: UUID
  +reward_type: enum {ATTENDANCE, SPENDING, EVENT}
  +points: int
  +nft_reward_id: UUID
  +issued_at: datetime
}

entity NFTLoyaltyReward {
  +id: UUID
  +user_id: UUID
  +token_id: string
  +reward_type: string
  +contract_address: string
  +minted_at: datetime
}

entity CheckInEvent {
  +id: UUID
  +user_id: UUID
  +event_name: string
  +location: string
  +timestamp: datetime
}

User ||--o{ AuthToken
User ||--o{ PasswordResetRequest
User ||--o{ NFTMembership
User ||--o{ LightningInvoice
User ||--o{ EthereumPayment
User ||--o{ Subscription
User ||--o{ POSPayment
User ||--o{ LoyaltyReward
User ||--o{ NFTLoyaltyReward
User ||--o{ CheckInEvent

@enduml
