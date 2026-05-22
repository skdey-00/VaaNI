"""
Banking NER Benchmark Script
============================

Tests the Banking NER engine against annotated test sentences.
Reports precision, recall, F1 per entity type.

Usage: python -m voice_service.benchmark_ner
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_service.banking_ner import extract_entities, Entity
from collections import defaultdict

# ============================================================================
# Test Data: text + expected entities (text, entity_type)
# ============================================================================

TEST_CASES = [
    {
        "text": "I want to open a fixed deposit of ₹50,000 for 5 years",
        "expected": [
            ("fixed deposit", "ACCOUNT_TYPE"),
            ("₹50,000", "AMOUNT"),
            ("5 years", "TIME_PERIOD"),
        ],
    },
    {
        "text": "What is the interest rate for home loan at 8.5% per annum",
        "expected": [
            ("home loan", "LOAN_TYPE"),
            ("8.5%", "INTEREST_RATE"),
        ],
    },
    {
        "text": "I need my Aadhaar and PAN card for KYC verification",
        "expected": [
            ("Aadhaar", "DOCUMENT"),
            ("PAN", "DOCUMENT"),
            ("KYC", "DOCUMENT"),
        ],
    },
    {
        "text": "Transfer Rs 25,000 via NEFT to my savings account",
        "expected": [
            ("Rs 25,000", "AMOUNT"),
            ("NEFT", "TRANSACTION_TYPE"),
            ("savings", "ACCOUNT_TYPE"),
        ],
    },
    {
        "text": "I want to apply for personal loan of 3 lakh rupees for 36 months",
        "expected": [
            ("personal loan", "LOAN_TYPE"),
            ("3 lakh", "AMOUNT"),
            ("36 months", "TIME_PERIOD"),
        ],
    },
    {
        "text": "My ATM card is blocked, please help with complaint",
        "expected": [
            ("ATM card", "BANK_PRODUCT"),
        ],
    },
    {
        "text": "Need demat account for mutual fund SIP investment",
        "expected": [
            ("demat", "ACCOUNT_TYPE"),
            ("mutual fund", "BANK_PRODUCT"),
            ("SIP", "BANK_PRODUCT"),
        ],
    },
    {
        "text": "RTGS transfer of ₹2,50,000 for business loan processing",
        "expected": [
            ("RTGS", "TRANSACTION_TYPE"),
            ("₹2,50,000", "AMOUNT"),
            ("business loan", "LOAN_TYPE"),
        ],
    },
    {
        "text": "बचत खाता में 7.5% ब्याज दर के साथ एफडी खोलनी है",
        "expected": [
            ("बचत खाता", "ACCOUNT_TYPE"),
            ("एफडी", "ACCOUNT_TYPE"),
            ("7.5%", "INTEREST_RATE"),
        ],
    },
    {
        "text": "मुझे आधार और पैन कार्ड की जरूरत है KYC के लिए",
        "expected": [
            ("आधार", "DOCUMENT"),
            ("पैन", "DOCUMENT"),
            ("KYC", "DOCUMENT"),
        ],
    },
    {
        "text": "5 साल के लिए फिक्स्ड डिपॉजिट में ₹1,00,000 जमा करना है",
        "expected": [
            ("फिक्स्ड डिपॉजिट", "ACCOUNT_TYPE"),
            ("₹1,00,000", "AMOUNT"),
            ("5 साल", "TIME_PERIOD"),
        ],
    },
    {
        "text": "UPI से 5000 रुपये ट्रांसफर करने हैं",
        "expected": [
            ("UPI", "TRANSACTION_TYPE"),
            ("5000 रुपये", "AMOUNT"),
        ],
    },
]


def run_benchmark():
    """Run NER benchmark and print results."""
    entity_types = ["AMOUNT", "ACCOUNT_TYPE", "DOCUMENT", "TRANSACTION_TYPE",
                    "LOAN_TYPE", "INTEREST_RATE", "TIME_PERIOD", "BANK_PRODUCT"]

    # Track TP, FP, FN per entity type
    tp = defaultdict(int)
    fp = defaultdict(int)
    fn = defaultdict(int)

    total_expected = 0
    total_found = 0
    total_correct = 0

    print("=" * 70)
    print("  VaaNI Banking NER — Benchmark Results")
    print("=" * 70)
    print()

    for i, test_case in enumerate(TEST_CASES):
        text = test_case["text"]
        expected = test_case["expected"]
        entities = extract_entities(text)

        # Match expected to found
        expected_texts = {(e[0].lower(), e[1]) for e in expected}
        found_texts = {(e.text.lower(), e.entity_type) for e in entities}

        correct = expected_texts & found_texts
        missed = expected_texts - found_texts
        extra = found_texts - expected_texts

        total_expected += len(expected)
        total_found += len(entities)
        total_correct += len(correct)

        # Update counters
        for (txt, etype) in correct:
            tp[etype] += 1
        for (txt, etype) in missed:
            fn[etype] += 1
        for (txt, etype) in extra:
            fp[etype] += 1

        if missed or extra:
            print(f"  Test {i+1}: {text[:60]}...")
            if missed:
                print(f"    MISSED: {missed}")
            if extra:
                print(f"    EXTRA:  {extra}")

    print()
    print("-" * 70)
    print(f"  Overall: {total_correct}/{total_expected} correct ({total_correct/total_expected*100:.1f}%)")
    print("-" * 70)
    print()

    # Per entity type results
    print(f"  {'Entity Type':<18} {'Precision':<12} {'Recall':<12} {'F1':<12} {'TP':<5} {'FP':<5} {'FN':<5}")
    print("  " + "-" * 66)

    all_f1 = []
    for etype in entity_types:
        p = tp[etype] / (tp[etype] + fp[etype]) if (tp[etype] + fp[etype]) > 0 else 0
        r = tp[etype] / (tp[etype] + fn[etype]) if (tp[etype] + fn[etype]) > 0 else 0
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        all_f1.append(f1)

        print(f"  {etype:<18} {p*100:<12.1f} {r*100:<12.1f} {f1*100:<12.1f} {tp[etype]:<5} {fp[etype]:<5} {fn[etype]:<5}")

    print("  " + "-" * 66)
    avg_f1 = sum(all_f1) / len(all_f1) if all_f1 else 0
    print(f"  {'AVERAGE F1':<18} {'':<12} {'':<12} {avg_f1*100:<12.1f}")
    print()

    # Show a sample extraction
    print("-" * 70)
    print("  Sample Extraction:")
    print("-" * 70)
    sample = "Transfer ₹50,000 via NEFT to savings account for home loan at 8.5% for 20 years"
    entities = extract_entities(sample)
    print(f"  Input: {sample}")
    print(f"  Entities found: {len(entities)}")
    for e in entities:
        print(f"    [{e.entity_type}] \"{e.text}\" (conf: {e.confidence:.2f}) → {e.normalized_value or 'N/A'}")

    print()
    print("=" * 70)
    print(f"  Benchmark complete. {len(TEST_CASES)} test cases evaluated.")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
