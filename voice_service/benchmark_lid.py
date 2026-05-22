"""
LID Benchmark Script
====================

Tests the N-gram LID engine against sample sentences in each language.
Reports accuracy, precision, recall, F1 per language and confusion matrix.

Usage: python -m voice_service.benchmark_lid
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from voice_service.lid_ngram import detect, LANGUAGE_NAMES
from collections import defaultdict

# ============================================================================
# Test Data: 12 sentences per language
# ============================================================================

TEST_DATA = {
    "hi": [
        "मुझे फिक्स्ड डिपॉजिट खोलनी है",
        "क्या ब्याज दर बताएंगे",
        "मैं अपने खाते का बैलेंस जानना चाहता हूं",
        "मुझे लोन लेना है",
        "मेरा एटीएम कार्ड बंद हो गया है",
        "मुझे पैसे ट्रांसफर करने हैं",
        "क्या आप मुझे नए खाते की जानकारी दे सकते हैं",
        "ऋण की प्रक्रिया क्या है",
        "बचत खाते में कितना ब्याज मिलता है",
        "KYC के लिए कौन से दस्तावेज चाहिए",
        "ग्राहक सेवा से बात करनी है",
        "मेरी शिकायत दर्ज करें",
    ],
    "mr": [
        "मला फिक्स्ड डिपॉझिट उघडायची आहे",
        "व्याज दर किती आहे",
        "मी माझ्या खात्यातील शिल्लक जाणून घेऊ इच्छितो",
        "मला कर्ज हवे आहे",
        "माझे एटीएम कार्ड बंद झाले आहे",
        "मला पैसे पाठवायचे आहेत",
        "तुम्ही मला नवीन खात्याची माहिती देऊ शकता का",
        "कर्जाची प्रक्रिया काय आहे",
        "बचत खात्यावर किती व्याज मिळते",
        "केवायसी साठी कोणती कागदपत्रे लागतात",
        "ग्राहक सेवेशी बोलायचे आहे",
        "माझी तक्रार नोंदवा",
    ],
    "ta": [
        "எனக்கு கடன் வேண்டும்",
        "என்ன ஆவணங்கள் தேவை",
        "நான் புதிய கணக்கு திறக்க விரும்புகிறேன்",
        "எனது கணக்கில் இருந்து பணம் அனுப்ப வேண்டும்",
        "வட்டி விகிதம் எவ்வளவு",
        "எனது ஏடிஎம் அட்டை தடை செய்யப்பட்டது",
        "சேமிப்பு கணக்கு திறக்க வேண்டும்",
        "கிராஹக சேவையுடன் பேச வேண்டும்",
        "வங்கி அட்டைக்கு விண்ணப்பிக்க வேண்டும்",
        "நிரந்தர வைப்பு திட்டம் பற்றி தெரிவியுங்கள்",
        "கணக்கு இருப்பு எவ்வளவு என தெரிந்து கொள்ள வேண்டும்",
        "புகார் பதிவு செய்ய வேண்டும்",
    ],
    "te": [
        "నాకు అప్పు కావాలి",
        "ఏమి పత్రాలు అవసరం",
        "నేను కొత్త ఖాతా తెరవాలనుకుంటున్నాను",
        "నా ఖాతాలో డబ్బు బదిలీ చేయాలి",
        "వడ్డీ రేటు ఎంత",
        "నా ఏటీఎం కార్డు బ్లాక్ అయింది",
        "పొదుపు ఖాతా తెరవాలి",
        "కస్టమర్ సర్వీస్ తో మాట్లాడాలి",
        "బ్యాంక్ కార్డు కోసం దరఖాస్తు చేయాలి",
        "ఫిక్సెడ్ డిపాజిట్ గురించి చెప్పండి",
        "ఖాతాలో ఎంత ఉందో తెలుసుకోవాలి",
        "ఫిర్యాదు నమోదు చేయాలి",
    ],
    "bn": [
        "আমি একটি নতুন অ্যাকাউন্ট খুলতে চাই",
        "ঋণ নিতে চাই",
        "কী কী নথি প্রয়োজন",
        "আমার অ্যাকাউন্ট থেকে টাকা পাঠাতে হবে",
        "সুদের হার কত",
        "আমার এটিএম কার্ড বন্ধ হয়ে গেছে",
        "সঞ্চয় অ্যাকাউন্ট খুলতে চাই",
        "কাস্টমার সার্ভিসে কথা বলতে চাই",
        "ব্যাংক কার্ডের জন্য আবেদন করতে চাই",
        "ফিক্সড ডিপোজিট সম্পর্কে জানান",
        "অ্যাকাউন্টে কত টাকা আছে জানতে চাই",
        "অভিযোগ দায়ের করতে চাই",
    ],
    "kn": [
        "ನನಗೆ ಸಾಲ ಬೇಕು",
        "ಯಾವ ದಾಖಲೆಗಳು ಅಗತ್ಯ",
        "ನಾನು ಹೊಸ ಖಾತೆ ತೆರೆಯಲು ಬಯಸುತ್ತೇನೆ",
        "ನನ್ನ ಖಾತೆಯಿಂದ ಹಣ ವರ್ಗಾಯಿಸಬೇಕು",
        "ಬಡ್ಡಿ ದರ ಎಷ್ಟು",
        "ನನ್ನ ಎಟಿಎಂ ಕಾರ್ಡ್ ಬ್ಲಾಕ್ ಆಗಿದೆ",
        "ಉಳಿತಾಯ ಖಾತೆ ತೆರೆಯಬೇಕು",
        "ಕಸ್ಟಮರ್ ಸೇವೆಯೊಂದಿಗೆ ಮಾತನಾಡಬೇಕು",
        "ಬ್ಯಾಂಕ್ ಕಾರ್ಡ್‌ಗಾಗಿ ಅರ್ಜಿ ಸಲ್ಲಿಸಬೇಕು",
        "ಫಿಕ್ಸೆಡ್ ಡೆಪಾಜಿಟ್ ಬಗ್ಗೆ ತಿಳಿಸಿ",
        "ಖಾತೆಯಲ್ಲಿ ಎಷ್ಟು ಹಣವಿದೆ ತಿಳಿಯಬೇಕು",
        "ದೂರು ಸಲ್ಲಿಸಬೇಕು",
    ],
    "ml": [
        "എനിക്ക് വായ്പ വേണം",
        "എന്ത് രേഖകൾ ആവശ്യമാണ്",
        "ഞാൻ പുതിയ അക്കൗണ്ട് തുറക്കാൻ ആഗ്രഹിക്കുന്നു",
        "എന്റെ അക്കൗണ്ടിൽ നിന്ന് പണം അയക്കണം",
        "പലിശ നിരക്ക് എത്ര",
        "എന്റെ എടിഎം കാർഡ് ബ്ലോക്ക് ചെയ്തു",
        "ലാഭം അക്കൗണ്ട് തുറക്കണം",
        "കസ്റ്റമർ സർവീസുമായി സംസാരിക്കണം",
        "ബാങ്ക് കാർഡിനായി അപേക്ഷിക്കണം",
        "ഫിക്സഡ് ഡിപോസിറ്റ് സംബന്ധിച്ച് അറിയിക്കൂ",
        "അക്കൗണ്ടിൽ എത്ര പണമുണ്ടെന്ന് അറിയണം",
        "പരാതി രജിസ്റ്റർ ചെയ്യണം",
    ],
    "gu": [
        "મને લોન જોઈએ",
        "શું દસ્તાવેજ જરૂરી છે",
        "હું નવું ખાતું ખોલવા માંગુ છું",
        "મારા ખાતામાંથી પૈસા મોકલવા છે",
        "વ્યાજ દર કેટલો છે",
        "મારું એટીએમ કાર્ડ બ્લોક થઈ ગયું છે",
        "બચત ખાતું ખોલવું છે",
        "કસ્ટમર સર્વિસ સાથે વાત કરવી છે",
        "બેંક કાર્ડ માટે અરજી કરવી છે",
        "ફિક્સ્ડ ડિપોઝિટ વિશે જણાવો",
        "ખાતામાં કેટલા પૈસા છે જાણવું છે",
        "ફરિયાદ નોંધાવવી છે",
    ],
    "en": [
        "I want to open a fixed deposit account",
        "What is the current interest rate for savings",
        "Can you check my account balance",
        "I need a personal loan of five lakh rupees",
        "My ATM card has been blocked",
        "Please transfer money to another account via NEFT",
        "What documents are required for KYC verification",
        "I want to apply for a home loan",
        "Can you help me with account opening process",
        "I need to update my mobile number in my account",
        "What is the procedure for filing a complaint",
        "Please provide me with a bank statement",
    ],
}

def run_benchmark():
    """Run LID benchmark and print results."""
    languages = list(TEST_DATA.keys())
    total = 0
    correct = 0

    # Confusion matrix: actual -> predicted -> count
    confusion: Dict[str, Dict[str, int]] = defaultdict(lambda: defaultdict(int))
    # Per-language stats
    lang_correct: Dict[str, int] = defaultdict(int)
    lang_total: Dict[str, int] = defaultdict(int)

    print("=" * 70)
    print("  VaaNI N-gram LID Engine — Benchmark Results")
    print("=" * 70)
    print()

    for actual_lang, sentences in TEST_DATA.items():
        for i, sentence in enumerate(sentences):
            result = detect(sentence)
            predicted = result["language"]
            confidence = result["confidence"]
            method = result["method"]

            confusion[actual_lang][predicted] += 1
            lang_total[actual_lang] += 1
            total += 1

            is_correct = predicted == actual_lang
            if is_correct:
                correct += 1
                lang_correct[actual_lang] += 1

            status = "✓" if is_correct else "✗"
            if not is_correct:
                print(f"  {status} [{actual_lang}] → predicted [{predicted}] conf={confidence:.2f} ({method})")
                print(f"    Text: {sentence[:60]}...")

    print()
    print("-" * 70)
    print(f"  Overall Accuracy: {correct}/{total} = {correct/total*100:.1f}%")
    print("-" * 70)
    print()

    # Per-language results
    print(f"  {'Language':<12} {'Correct':<10} {'Total':<8} {'Accuracy':<10} {'Precision':<10} {'Recall':<10} {'F1':<10}")
    print("  " + "-" * 66)

    all_precision = []
    all_recall = []
    all_f1 = []

    for lang in languages:
        tp = lang_correct[lang]
        fn = lang_total[lang] - tp
        fp = sum(confusion[predicted].get(lang, 0) for predicted in languages if predicted != lang)
        # Actually: fp = total predicted as lang - correct predictions for lang
        fp = sum(confusion[actual].get(lang, 0) for actual in languages) - tp

        precision = tp / (tp + fp) if (tp + fp) > 0 else 0
        recall = tp / (tp + fn) if (tp + fn) > 0 else 0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0

        all_precision.append(precision)
        all_recall.append(recall)
        all_f1.append(f1)

        name = LANGUAGE_NAMES.get(lang, lang)
        print(f"  {name:<12} {tp:<10} {lang_total[lang]:<8} {tp/lang_total[lang]*100:<10.1f} {precision*100:<10.1f} {recall*100:<10.1f} {f1*100:<10.1f}")

    print("  " + "-" * 66)
    n = len(languages)
    print(f"  {'AVERAGE':<12} {'':<18} {correct/total*100:<10.1f} {sum(all_precision)/n*100:<10.1f} {sum(all_recall)/n*100:<10.1f} {sum(all_f1)/n*100:<10.1f}")

    # Confusion matrix
    print()
    print("-" * 70)
    print("  Confusion Matrix (actual → predicted)")
    print("-" * 70)

    # Header
    header = f"  {'':>8}"
    for lang in languages:
        header += f" {lang:>5}"
    print(header)
    print("  " + "-" * (10 + 6 * len(languages)))

    for actual in languages:
        row = f"  {actual:>8}"
        for predicted in languages:
            count = confusion[actual].get(predicted, 0)
            if actual == predicted:
                row += f" [{count:>3}]"
            elif count > 0:
                row += f"  {count:>3} "
            else:
                row += f"   -  "
        print(row)

    print()
    print("=" * 70)
    print(f"  Benchmark complete. {total} sentences tested across {len(languages)} languages.")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
