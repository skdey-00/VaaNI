# Fund Transfer and Remittance Process

This document outlines the process for various fund transfer methods available in Indian banking.

## Types of Fund Transfers

### 1. NEFT (National Electronic Funds Transfer)
- **Settlement**: Hourly batches (12 settlements on weekdays, 6 on Saturdays)
- **Available**: 24x7 (including holidays)
- **Timings**: All 24 hours
- **Transaction Limit**: No minimum or maximum limit
- **Charges**: Zero (regulated by RBI)
- **Settlement Time**: Within 2 hours (usually in next batch)

### 2. RTGS (Real Time Gross Settlement)
- **Settlement**: Real-time, individual transaction
- **Available**: 24x7 (including holidays)
- **Minimum Amount**: ₹2 lakh
- **Maximum Amount**: No upper limit
- **Charges**: Zero (regulated by RBI)
- **Settlement Time**: Real-time (within 30 minutes)

### 3. IMPS (Immediate Payment Service)
- **Settlement**: Real-time
- **Available**: 24x7 (including holidays)
- **Minimum Amount**: ₹1
- **Maximum Amount**: ₹2 lakh (some banks up to ₹5 lakh)
- **Charges**: Up to ₹5 per transaction (some banks free)
- **Settlement Time**: Instant (within seconds)

### 4. UPI (Unified Payments Interface)
- **Settlement**: Real-time
- **Available**: 24x7
- **Minimum Amount**: ₹1
- **Maximum Amount**: ₹1 lakh
- **Charges**: Zero for customers
- **Settlement Time**: Instant
- **Requirements**: UPI ID, QR code, or mobile number + account linked

## Fund Transfer Procedure

### Step 1: Customer Requirement Analysis

**Understand Customer's Need:**
- Transfer amount
- Urgency (instant vs same day vs next day)
- Destination bank
- Purpose of transfer
- Is it a one-time or recurring transfer?

**Channel Selection Guide:**

| Amount | Urgency | Recommended Mode |
|--------|---------|------------------|
| < ₹2 lakh | Instant | IMPS / UPI |
| < ₹2 lakh | Same day | NEFT |
| ₹2 lakh - ₹5 lakh | Instant | IMPS (if bank allows) |
| ₹2 lakh+ | Real-time | RTGS |
| ₹5 lakh+ | Any | RTGS |
| International | - | Wire Transfer (SWIFT) |

### Step 2: Customer and Account Verification

**For Walk-in Customers:**
- Verify customer identity (check passbook/ID card)
- Ensure customer is account holder
- Check if account is active
- Verify account has sufficient balance

**Account Status Check:**
- Account not frozen or dormant
- Account not under lien
- Sufficient balance for transfer + charges

**Transaction Limits:**
- Check daily transaction limit for customer
- Check per-transaction limit
- Check monthly limit for certain transfers
- For retail customers: Usually ₹2-5 lakh per day (varies by bank)
- For corporate customers: Higher limits as per arrangement

### Step 3: Beneficiary Addition

**For New Beneficiary:**

**Beneficiary Details Required:**
1. **Account Number**: Complete account number (10-16 digits)
2. **Confirm Account Number**: Re-enter to verify
3. **Beneficiary Name**: As per bank records
4. **Bank Name**: Name of destination bank
5. **Branch Name**: Branch where account is maintained
6. **IFSC Code**: 11-character code (format: XXXX0XXXXXX)
   - First 4 characters: Bank code
   - 5th character: '0'
   - Last 6 characters: Branch code
7. **Beneficiary Type**: Individual, Corporate, etc.
8. **Beneficiary Address**: Optional for some transfers

**IFSC Code Verification:**
- Verify IFSC from RBI website or bank branch
- Verify IFSC from beneficiary's cheque leaf
- Verify IFSC from bank website

**For IMPS/UPI:**
- Mobile number of beneficiary
- MMID (Mobile Money Identifier) - 7-digit code
- OR UPI ID (example: name@bank)
- OR Aadhaar number (if mapped)

**For International Transfer:**
- SWIFT code (8 or 11 characters)
- IBAN (International Bank Account Number) for Europe
- Routing number / ABA for USA
- Beneficiary bank address
- Intermediary bank details (if any)

**Beneficiary Addition Process:**
1. Enter beneficiary details in system
2. Get customer's confirmation
3. System may send OTP to customer's registered mobile
4. Verify OTP
5. Beneficiary added successfully

**Cool-off Period:**
- For new beneficiary: 30 minutes cool-off before first transfer
- Some banks: 24 hours cool-off
- After cool-off: Transfer can be executed

**Activation:**
- Some banks require activation link click
- Customer needs to approve beneficiary
- After activation, fund transfer possible

### Step 4: Transfer Transaction Execution

**Transfer Details:**
- **Amount**: Amount to be transferred (in rupees)
- **Purpose**: Purpose code for international transfers
- **Remarks**: Transaction reference (maximum 30 characters)
- **Debit Account**: Customer's account to be debited

**For NEFT:**
- No minimum or maximum limit
- Settlement in hourly batches
- Good for transfers where instant settlement not required

**For RTGS:**
- Minimum ₹2 lakh
- Real-time settlement
- Suitable for high-value transactions

**For IMPS:**
- Instant settlement
- Maximum ₹2 lakh per transaction
- Works on mobile number + MMID or account + IFSC

**For UPI:**
- Requires UPI ID (Virtual Payment Address)
- Instant settlement
- Uses 2-factor authentication (mobile app + PIN)

**Transaction Modes:**
1. **Branch Channel**: Fill form, debit account
2. **Internet Banking**: Self-service by customer
3. **Mobile Banking**: Using bank's mobile app
4. **ATM**: Funds transfer using ATM
5. **Standing Instruction**: Auto-debit at scheduled intervals

### Step 5: Authentication and Authorization

**Authentication Methods:**
1. **Signature Verification**: For branch transactions
2. **OTP (One Time Password)**: Sent to registered mobile
3. **Debit Card + PIN**: For certain channels
4. **MPIN**: For UPI and mobile banking
5. **Grid Card**: For corporate banking
6. **Digital Signature**: For high-value corporate transactions

**Two-Factor Authentication (2FA):**
- First factor: Something you know (PIN, password)
- Second factor: Something you have (OTP, mobile)
- Mandatory for all fund transfers above ₹1,000

**Authorization Levels:**
- For retail: Single factor (usually)
- For corporate: Dual authorization (maker + checker)
- For very high-value: Additional approval required

### Step 6: Transaction Processing

**Inward Processing (at destination):**
- Receiving bank credits beneficiary account
- Beneficiary gets credit confirmation SMS
- Fund available for withdrawal

**Outward Processing (at origin):**
- Debit customer account
- Generate UTR (Unique Transaction Reference) number
- Send confirmation to customer
- Update transaction records

**UTR Number:**
- 22-character unique reference
- Format: [Bank Code][Date][Sequence]
- Used for tracking transaction
- Required for any grievance/complaint

### Step 7: Confirmation and Receipt

**Transaction Successful:**
1. Debit customer account
2. Generate transaction reference (UTR/RRN)
3. Send SMS confirmation to customer
4. Provide transaction receipt with:
   - Transaction date and time
   - Beneficiary name and account
   - Amount transferred
   - Transaction reference number
   - Bank name and branch
   - Authorizing official signature

**Transaction Failed:**
1. Amount not debited OR
2. Debit but credit failed
3. Reverse debit (if amount debited)
4. Inform customer about failure
5. Check failure reason:
   - Invalid beneficiary
   - Insufficient funds
   - Technical error
   - Beneficiary account closed
   - Timeout
6. Customer can retry

**Pending Transaction:**
- Debit done, credit pending
- Usually due to technical issues
- Will be auto-reversed if not credited
- Takes 24-48 hours for reversal

## Standing Instructions for Recurring Transfers

**Purpose:**
- Auto-debit for recurring payments
- SIP (Systematic Investment Plan)
- Loan EMI payment
- Rent payment
- School fees
- Insurance premium

**Setup:**
1. Fill standing instruction form
2. Specify:
   - Beneficiary details
   - Amount (fixed or variable)
   - Frequency (monthly/quarterly/annually)
   - Start date and end date (or indefinite)
   - Debit account
3. Get customer signature
4. System auto-debits on specified date
5. Send intimation after each debit

**Modification:**
- Customer can modify standing instruction
- Change amount, frequency, or end date
- Submit modification form

**Cancellation:**
- Submit cancellation request
- Takes 7-15 days to effect
- No further debits after cancellation

## International Remittance (Outward)

**Purpose:**
- Send money abroad
- Family maintenance
- Education expenses
- Medical treatment abroad
- Business payments

**Documents Required:**
- Form A2 (Application for Remittance)
- PAN card
- Purpose declaration
- Supporting documents:
  - Student admission letter (for education)
  - Medical invoice (for medical treatment)
  - Invoice from supplier (for trade)
  - Employment contract (for family maintenance)

**Limits and Charges (Liberalized Remittance Scheme - LRS):**
- **Limit**: USD 2,50,000 per financial year per person
- **Charges**:
  - SWIFT charges: ₹500-2,000
  - Correspondent bank charges: USD 10-50
  - Purpose code requirement: Mandatory
- **Tax Collection at Source (TCS)**:
  - 5% for remittance up to ₹7 lakh (for education/medical)
  - 20% for remittance above ₹7 lakh (other purposes)
  - Applicable from FY 2020-21

**Procedure:**
1. Fill Form A2 with purpose code
2. Get KYC documents
3. Obtain forex dealer authorization
4. Convert INR to foreign currency
5. Execute SWIFT transfer
6. Provide SWIFT copy to customer

**Purpose Codes (Common):**
- S0301: Private visit (tourism, personal)
- S0302: Business visit
- S0305: Employment
- S0308: Education
- S0309: Medical treatment
- S0401: Gift / Donation
- S0501: Maintenance of close relatives

**SWIFT Message Format:**
- MT103: Single customer credit transfer
- MT202: General financial institution transfer
- Contains full details of remittance

## Return / Reversal of Transactions

**Return Reasons:**
1. **Credit Returns**:
   - Beneficiary account closed
   - Account number incorrect
   - Name mismatch
   - Beneficiary refuses
   - Court order

2. **Debit Returns**:
   - Insufficient funds
   - Account frozen
   - Invalid debit instruction
   - Customer request

**Return Process:**
- Originating bank receives return message
- Credit customer account (if debit done)
- Inform customer about return
- Reason for return provided
- Customer can correct and retry

**Time Limits for Return:**
- NEFT: Usually within 2 hours of credit
- RTGS: Within 1 hour of credit
- IMPS: Within 1 hour of credit

## Common Scenarios and Handling

### Scenario 1: Customer claims amount not received

**Action:**
1. Check transaction status in system
2. Verify if debit happened
3. Check if credit happened at beneficiary end
4. If credit not received:
   - Check if transaction is pending
   - Check if return initiated by beneficiary bank
   - Obtain UTR number
   - Contact beneficiary bank with UTR
   - Provide customer with reference number for follow-up
5. If debit not happened:
   - Transaction failed
   - Amount not deducted from account
   - Ask customer to check passbook/statement

### Scenario 2: Wrong beneficiary credited

**Action:**
1. Obtain written request from customer
2. Contact beneficiary bank
3. Request beneficiary bank to:
   - Contact beneficiary
   - Obtain consent for reversal
   - Reverse the transaction
4. If beneficiary agrees: Process reversal
5. If beneficiary refuses: Customer to approach civil court
6. Bank cannot unilaterally reverse without beneficiary consent

### Scenario 3: Transaction timeout

**Action:**
1. Check transaction status
2. If debited but not credited:
   - System will auto-reverse in 24-48 hours
   - Provide customer with reference number
   - Follow up after 2 working days
3. If amount reversed:
   - Ask customer to retry
4. If amount not reversed:
   - File complaint with IT
   - Escalate to transaction processing team

### Scenario 4: Beneficiary not added

**Action:**
1. Add beneficiary in system
2. Verify beneficiary details
3. Activate beneficiary (cool-off period)
4. Customer should authenticate via OTP
5. After activation, proceed with transfer

### Scenario 5: Daily limit exceeded

**Action:**
1. Inform customer about daily transfer limit
2. Options:
   - Wait till next day (limit resets at midnight)
   - Request for temporary limit enhancement
   - Split transaction into multiple days
   - Use alternative channel (some channels have separate limits)

### Scenario 6: International transfer declined

**Action:**
1. Check LRS limit (USD 2,50,000 per year)
2. Check TCS applicable
3. Verify Form A2 is complete
4. Check purpose code is correct
5. Verify supporting documents
6. Check forex availability
7. Resolve issue and retry

## Fraud Prevention and Security

### Red Flags to Watch
- Customer being coached by third party
- Urgent transfer request (pressuring tactic)
- Transfer to unknown beneficiary
- Transfer to account in high-risk jurisdiction
- Unusual transaction pattern for customer
- Customer unable to explain purpose

### Precautions
1. Verify customer identity
2. Confirm transfer purpose
3. Warn customer about phishing
4. Educate about OTP safety
5. Never share OTP
6. Report suspicious transactions
7. For elderly customers: Additional caution, explain clearly

## Charges and Fees

**Customer Charges (RBI mandated, most banks waive):**
- NEFT: Zero charges
- RTGS: Zero charges
- IMPS: Zero charges (some banks charge ₹5)
- UPI: Zero charges

**Bank Charges (interbank):**
- NEFT: Minimal (regulated by RBI)
- RTGS: Minimal (regulated by RBI)
- IMPS: Minimal (regulated by RBI)

**For International:**
- Outward remittance charges: ₹500-2,000
- SWIFT charges: USD 10-50
- TT (Telegraphic Transfer) charges: Variable

## Turnaround Time (TAT)

| Transfer Type | Settlement Time |
|---------------|-----------------|
| IMPS / UPI | Instant (within seconds) |
| RTGS | Real-time (within 30 minutes) |
| NEFT | Within 2 hours (next batch) |
| Cheque | Local: 1-2 days; Outstation: 3-7 days |
| International (Wire) | 1-3 working days |

## Important Information for Customers

### Customer Tips
1. **Always verify beneficiary details**: Double-check account number and IFSC
2. **Keep transaction reference**: UTR/RRN for tracking
3. **Never share OTP**: Bank never asks for OTP
4. **Report suspicious transactions**: Immediately inform branch
5. **Check SMS confirmation**: Verify amount and beneficiary
6. **Use standing instructions**: For recurring transfers, avoid manual transfers
7. **Know your limits**: Daily and monthly transaction limits

### Mode Selection Guide
- **Instant below ₹2 lakh**: Use IMPS or UPI
- **Non-urgent below ₹2 lakh**: Use NEFT (no extra charges)
- **₹2 lakh and above**: Use RTGS
- **Scheduled future transfers**: Use standing instructions
- **International**: Use SWIFT/TT

## Grievance Redressal

### If Transaction Not Credited
1. Wait for 24-48 hours (some transactions take time)
2. Check with beneficiary bank
3. Obtain transaction reference (UTR/RRN)
4. Lodge complaint at branch with reference number
5. If not resolved in 7 days: Approach banking ombudsman

### Banking Ombudsman
- File complaint online at RBI ombudsman website
- Or send written complaint to ombudsman
- Attach transaction proof
- Ombudsman decision is binding on bank (if customer accepts)

### NACH (National Automated Clearing House)
- For bulk credits: Dividends, interest, pension, salary
- For bulk debits: Loan EMI, insurance premium, utility bills
- Requires customer mandate (NACH form)
- Settled on daily basis
- No minimum/maximum limit
