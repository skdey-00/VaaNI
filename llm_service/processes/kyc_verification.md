# KYC Verification Process

This document outlines the RBI-compliant Know Your Customer (KYC) verification process for banking services in India.

## Purpose of KYC

KYC verification is mandated by RBI to:
1. Prevent money laundering and terrorist financing
2. Verify the true identity of customers
3. Understand customer's financial dealings
4. Manage risk appropriately
5. Ensure compliance with Prevention of Money Laundering Act (PMLA), 2002

## KYC Documents Requirements

### Officially Valid Documents (OVDs)

**Proof of Identity (POI):**
- Aadhaar Card (issued by UIDAI)
- PAN Card (issued by Income Tax Department)
- Passport (issued by Ministry of External Affairs)
- Driving License (issued by Regional Transport Office)
- Voter ID Card (issued by Election Commission)
- NREGA Job Card (with photograph)

**Proof of Address (POA):**
- Aadhaar Card (current address)
- Passport
- Driving License
- Voter ID Card
- Utility Bill (electricity, telephone, gas, water) - not older than 2 months
- Bank Account Statement or Passbook (scheduled commercial bank) - not older than 3 months
- Property Tax Receipt
- Letter from employer (public sector/registered companies)

**For Recent Photograph:**
- Passport size color photograph (35mm x 35mm minimum)
- Should clearly show full face, front view
- Neutral expression, eyes visible
- Plain or light background

## KYC Verification Methods

### Method 1: Aadhaar-based e-KYC (Paperless)

**Eligibility:**
- Customer has valid Aadhaar card
- Mobile number registered with Aadhaar
- Customer consents to e-KYC

**Procedure:**
1. Enter customer's 12-digit Aadhaar number
2. Select authentication type:
   - **OTP (One Time Password)** - Preferred method
   - **Biometric** - Using fingerprint/iris device
3. For OTP:
   - Request UIDAI to send OTP to customer's Aadhaar-linked mobile
   - Customer receives 6-digit OTP
   - Enter OTP in system within validity period
4. For Biometric:
   - Capture fingerprint or iris scan using authorized device
   - Ensure biometric device is UIDAI-certified
5. System receives:
   - Customer's name, photo, address, DOB, gender from UIDAI
   - KYC completion status
6. Complete CKYCR (Central KYC Records Registry) verification
7. Generate KYC reference number (KRN)

**Benefits:**
- Instant verification (2-5 minutes)
- No paper documents required
- Reduces customer visit to branch

### Method 2: Offline Aadhaar Verification

**When to use:**
- Customer's mobile not linked with Aadhaar
- Customer prefers not to share Aadhaar number
- OTP-based authentication not possible

**Procedure:**
1. Download Aadhaar XML from UIDAI website using customer's Aadhaar number
2. Customer provides sharing code (4-digit password)
3. Enter sharing code to decrypt XML file
4. Retrieve customer details from XML
5. Mask Aadhaar number (show only last 4 digits)
6. Print XML with details (optional)
7. Store digitally in encrypted format

**Note:** Ensure consent of customer is recorded before downloading.

### Method 3: Paper-based KYC (Offline Mode)

**When to use:**
- Customer doesn't have Aadhaar
- e-KYC infrastructure not available
- Customer prefers paper-based verification

**Procedure:**
1. **Document Collection:**
   - Collect original documents for verification
   - Take self-attested copies
   - Verify authenticity of originals
   - Note: For address proof, current address should be verifiable

2. **Document Verification:**
   - Check if documents are not expired
   - Verify photograph matches customer
   - Check for tampering or alterations
   - Cross-check details across multiple documents

3. **Attestation:**
   - Write "Original verified and returned on [date]" on copies
   - Sign and stamp with official seal
   - Mention employee verification code

4. **CKYCR Registration:**
   - Upload KYC details to Central KYC Records Registry
   - Obtain CKYCR number
   - Link customer ID with CKYCR

## Special Categories

### Category 1: Non-Resident Indians (NRIs)

**Documents Required:**
- Valid Passport with visa stamp
- Overseas address proof (utility bill, bank statement)
- PAN Card (or Form 60 declaration)
- Recent photograph
- OCI/PIO card (if applicable)

**Process:**
1. Verify passport validity and visa
2. Get NRI status declaration
3. For NRE accounts: Need proof of NRE status (employment visa, student visa)
4. For NRO accounts: Can hold jointly with resident Indian

### Category 2: Foreign Nationals

**Documents Required:**
- Valid Passport with valid visa/Work Permit/Residence Permit
- Overseas address proof
- Indian address proof (if staying in India)
- Recent photograph
- PAN (or apply for PAN)
- Form 49AA for PAN application

**Process:**
1. Verify visa validity and stay permit
2. Check employment/business purpose
3. Enhanced due diligence required
4. Branch manager approval needed

### Category 3: Companies, LLPs, Partnership Firms

**Documents Required:**
- Certificate of Incorporation/Registration
- PAN of entity
- Memorandum & Articles of Association / Partnership Deed
- Board Resolution / Authorization letter
- List of Directors/Partners with addresses
- PAN of directors/partners
- Photographs of authorized signatories
- Office address proof (electricity bill, lease agreement)
- GST registration (if applicable)

**Process:**
1. Verify entity registration with MCA/Registrar
2. Verify authorized signatories from Board Resolution
3. Obtain KYC for all authorized signatories
4. Verify place of business
5. Upload to CKYCR in entity category

### Category 4: Trusts, Societies, Associations

**Documents Required:**
- Registration certificate
- Trust Deed / Society Bye-laws
- PAN of trust/society
- Resolution by Board/Managing Committee
- List of office bearers
- Photographs of authorized signatories
- Office address proof

### Category 5: Minors

**For below 10 years:**
- KYC of guardian (parent)
- Minor's birth certificate
- Minor's photograph
- Relationship proof (if guardian is not natural parent)

**For 10-18 years:**
- Minor's own KYC (Aadhaar if available)
- Guardian details
- Photograph of minor

### Category 6: Senior Citizens

**Documents:**
- Standard OVDs (PAN, Aadhaar, etc.)
- Age proof for senior citizen benefits:
  - Birth certificate
  - School leaving certificate
  - Passport (shows DOB)
  - Aadhaar (shows DOB)
  - Government pension document

## Enhanced Due Diligence (EDD)

**When EDD is Required:**
- High-value accounts (deposits > ₹50 lakh)
- Politically Exposed Persons (PEPs)
- Customers from high-risk jurisdictions
- Complex company structures (beneficial ownership unclear)
- Cash-intensive businesses

**EDD Process:**
1. Verify identity of beneficial owners
2. Understand purpose and nature of relationship
3. Verify source of funds/wealth
4. Conduct regular monitoring
5. Obtain Branch Manager/Regional Manager approval

## CKYCR (Central KYC Records Registry)

CKYCR is a centralized repository of KYC records maintained by CERSAI.

**Process:**
1. After completing KYC, upload customer details to CKYCR
2. Obtain 14-digit CKYC number
3. Customer can use same KYC for other financial institutions
4. For modified KYC, update CKYCR with new details

**Benefits:**
- Customer doesn't need to submit KYC documents multiple times
- Faster onboarding at other banks
- Centralized monitoring

## Periodic KYC Updation

**Time Periods:**
- **High Risk Customers**: Every 2 years
- **Medium Risk Customers**: Every 8 years
- **Low Risk Customers**: Every 10 years

**Trigger for Re-KYC:**
- Change in customer's address
- Change in constitution (for companies)
- Material change in business activities
- System-driven alerts

## Re-KYC Process

1. **Notification:**
   - Send intimation to customer via SMS/Email/letter
   - Give 30 days notice period

2. **Document Collection:**
   - Get updated KYC documents
   - For address change: Get new address proof
   - For PAN change: Get new PAN card

3. **Verification:**
   - Follow same process as fresh KYC
   - Update records in core banking system
   - Update CKYCR

4. **If No Response:**
   - Send reminder after 15 days
   - Allow partial debit operations after KYC expiry
   - Freeze credit operations after 6 months of non-updation
   - Close account after 1 year (with notice)

## Common Scenarios and Handling

### Scenario 1: Customer has only Aadhaar, PAN is not available

**Action:**
- Accept Aadhaar as POI and POA
- Collect Form 60 declaration
- Explain PAN limitations (TDS deduction, cannot open demat account)
- Advise to apply for PAN

### Scenario 2: Address on Aadhaar is different from current address

**Action:**
- Use Aadhaar as identity proof
- Get separate address proof (utility bill, passport)
- If no recent address proof: Accept self-declaration with explanation

### Scenario 3: Customer is illiterate (cannot sign)

**Action:**
- Take left thumb impression (LTI)
- Ensure thumb impression is clear
- Get photograph of customer giving thumb impression
- Attest thumb impression with witness signature

### Scenario 4: Customer documents are in regional language

**Action:**
- Accept documents with English translation
- Translation should be on bank's letterhead
- Verifying officer should sign translation
- Or ask customer for documents in English/Hindi

### Scenario 5: Customer name differs across documents

**Action:**
- Identify document that establishes legal name (Passport, PAN)
- If name changed due to marriage: Get marriage certificate
- If name changed legally: Get Gazette notification
- Get declaration from customer explaining difference

### Scenario 6: Customer's photograph on document is old

**Action:**
- Accept document if other details match
- Obtain fresh photograph of customer
- Verify identity through additional questions
- For high-risk cases: Request additional ID proof

## Compliance Checks

Before completing KYC, verify:

1. **Watch List Screening:**
   - Check customer against UN sanctions list
   - Check against OFAC list (for international customers)
   - Verify not in CBI/Enforcement Directorate lists

2. **PEP Check:**
   - Identify if customer is Politically Exposed Person
   - PEP includes: MPs, MLAs, bureaucrats, senior judicial officers, military generals
   - Family members and close associates also considered PEPs
   - Obtain senior management approval for PEP accounts

3. **Existing CKYC:**
   - Check if customer already has CKYC number
   - Download KYC from CKYC registry
   - Verify if KYC is current and complete

## Quality Assurance

**Reviewer Checklist:**
- All mandatory fields filled
- Documents are valid (not expired)
- Photographs are clear and recent
- Signatures/thumb impressions are proper
- Address proof is current
- PAN verified with Income Tax database
- CKYC number generated
- Risk category assigned correctly

## Penalties for Non-Compliance

- Penalty up to ₹1 lakh for initial violation
- Additional ₹10,000 per day for continued violation
- Criminal prosecution for intentional violations
- Director/officer-in-charge can be penalized

## Turnaround Time (TAT)

- **e-KYC**: 5-10 minutes
- **Offline KYC with Aadhaar XML**: 15-20 minutes
- **Paper-based KYC**: 30-60 minutes
- **Entity KYC (Company/LLP)**: 1-2 working days
- **NRI KYC**: 1-2 working days (verification may take time)
