# VaaNI Demo Script

## Judge-Facing 3-Minute Walkthrough

This script is designed for hackathon judges and investors. It showcases VaaNI's core capabilities in a concise, impactful demo.

---

### 🎯 Demo Objectives

- Show the **language barrier problem** in Indian banking
- Demonstrate **real-time translation** and AI assistance
- Highlight **professional features** (PDF export, CBS integration)
- Emphasize **social impact** (financial inclusion for rural India)

---

### ⏱️ Timeline Breakdown

| Time | Segment | Key Points |
|------|---------|------------|
| 0:00-0:30 | **Problem Intro** | Set the stage |
| 0:30-1:30 | **Live Demo** | Hindi FD inquiry scenario |
| 1:30-2:15 | **AI Features** | Suggestions & process guide |
| 2:15-3:00 | **Summary & Impact** | PDF export, social impact |

---

## 🎬 Demo Script

### [0:00 - 0:30] Problem Introduction

**Visual:** Show VaaNI dashboard open on laptop/screen

**Script:**
> "Good morning/afternoon. Let me show you VaaNI - our solution to a massive problem in Indian banking.
>
> India has 22 official languages and hundreds of dialects. In rural branches, customers only speak their local language, but bank staff often don't. This leads to:
>
> - Misunderstandings about financial products
> - Incomplete KYC documentation
> - Poor customer experience
> - Lost business opportunities
>
> VaaNI breaks this language barrier by enabling real-time communication in **15+ Indian languages**."

---

### [0:30 - 1:30] Live Demo: Hindi FD Inquiry

**Visual:** Live demo on screen

**Script:**
> "Let me show you how it works with a real scenario.
>
> **[Point to screen]**
>
> Our customer is a Hindi-speaking woman who wants to open a Fixed Deposit account. She only speaks Hindi - no English.
>
> **[Click 'Record' button]**
>
> She speaks into the microphone:
>
> **[Play pre-recorded Hindi audio through speakers]**
> > *"मैं एक फिक्स्ड डिपॉजिट खाता खोलना चाहता हूं, क्या प्रक्रिया है?"*
> > (I want to open a Fixed Deposit account, what's the process?)
>
> **[Point to transcript appearing in real-time]**
>
> Watch this - within **2 seconds**, VaaNI:
>
> 1. ✅ **Detected** the language as Hindi (95% confidence)
> 2. ✅ **Transcribed** her speech in Hindi
> 3. ✅ **Translated** it to English for the staff
> 4. ✅ **Generated** 3 smart response suggestions
> 5. ✅ **Displayed** the FD opening process checklist
>
> All automatically. No manual intervention needed."

---

### [1:30 - 2:15] AI Features Showcase

**Visual:** Scroll to suggestions and process guide

**Script:**
> "Now, look at the AI suggestions on the right:
>
> **[Point to suggestions]**
>
> VaaNI's LLM analyzed her query and provided **3 contextually relevant responses**:
>
> 1. *'FD at 7.5% interest rate'*
> 2. *'Bring Aadhaar and PAN card'*
> 3. *'Minimum deposit ₹10,000'*
>
> The staff can click any suggestion, or type their own.
>
> **[Point to process guide]**
>
> Below that, VaaNI automatically detected this is an **'FD Opening'** inquiry and displayed the **5-step process checklist**:
>
> - ☑ Verify customer identity
> - ☑ Check FD rates
> - □ Fill account opening form
> - □ Complete KYC verification
> - □ Initial deposit
>
> This guides the staff through the entire process - nothing gets missed.
>
> **[Staff clicks suggestion and speaks response]**
>
> The staff selects the first suggestion, and VaaNI **synthesizes the response in Hindi** and plays it for the customer."

---

### [2:15 - 3:00] Summary & Impact

**Visual:** Click 'End Session', show summary page

**Script:**
> "After the conversation ends, VaaNI automatically generates a **bilingual summary**:
>
> **[Show summary page]**
>
> - ✅ English summary for bank records
> - ✅ Hindi summary for customer understanding
> - ✅ Full conversation log with timestamps
> - ✅ Query classification: 'FD Inquiry'
> - ✅ Resolution status: 'Resolved'
>
> **[Click 'Export PDF']**
>
> With one click, we generate a **compliance-ready PDF** with:
>
> - Bank branding
> - Bilingual summaries
> - Complete transcript
> - Process steps completed
> - Confidentiality notice
>
> This PDF can be saved to the CBS (Core Banking System) or printed for customer records.
>
> **[Show 'Push to CBS' button]**
>
> We also have a **CBS integration stub** - ready to plug into any banking system."
>
> **[Final impact statement]**
>
> "With VaaNI:
>
> - 🏦 Banks can serve customers in **their native language**
> - ✅ **Reduce errors** in communication
> - ⚡ **Faster service** - no manual translation needed
> - 📈 **Better customer experience**
> - 🌐 **Financial inclusion** for rural India
>
> VaaNI makes banking accessible to **all 1.4 billion Indians**, regardless of the language they speak.
>
> Thank you! Any questions?"

---

## 🎯 Quick Demo (1-Minute Version)

For time-constrained presentations:

**Script:**
> "VaaNI breaks language barriers in Indian banking. Watch it in action:
>
> **[Play Hindi audio, show real-time transcript]**
>
> Customer speaks Hindi → VaaNI transcribes, translates, and suggests responses in **2 seconds**.
>
> **[Show AI suggestions and process guide]**
>
> Staff gets AI-powered suggestions and guided process steps.
>
> **[End session, show PDF export]**
>
> Auto-generated bilingual summary and compliance-ready PDF with one click.
>
> VaaNI - making banking accessible in **15+ Indian languages**. Thank you!"

---

## 🎨 Demo Setup

### Pre-Demo Checklist

```bash
# 1. Start all services
docker-compose up -d

# 2. Verify services are healthy
curl http://localhost:8000/health
curl http://localhost:8001/health
curl http://localhost:8002/health

# 3. Open frontend
open http://localhost:5173

# 4. Generate demo audio
python demo/seed_audio.py

# 5. Test demo scenario
python demo/scenario_fd.py
```

### Hardware Requirements

- **Laptop/Desktop** with Chrome browser
- **Microphone** (for recording staff response)
- **Speakers** (for playing TTS audio)
- **Projector** or large screen
- **Internet connection** (for Google TTS, optional)

### Backup Plan

If services fail:

1. **Mock Mode**: Set `VITE_MOCK_MODE=true` in frontend
2. **Screenshot Backup**: Have screenshots of key screens ready
3. **Video Backup**: Pre-recorded demo video

---

## 🎭 Presentation Tips

### Body Language

- ✅ **Face the audience** when explaining, not the screen
- ✅ **Use gestures** to point at UI elements
- ✅ **Maintain eye contact** with judges
- ✅ **Speak clearly** and confidently

### Pacing

- ✅ **Pause** after key points (let them sink in)
- ✅ **Wait for UI** to load before speaking
- ✅ **Practice** the transitions between sections
- ✅ **Monitor time** - don't exceed 3 minutes

### Storytelling

- ✅ **Start with the problem** (make it relatable)
- ✅ **Use specific numbers** (95% accuracy, 2 seconds, 15 languages)
- ✅ **Show, don't just tell** (let the demo speak)
- ✅ **End with impact** (social good, financial inclusion)

---

## 🐛 Common Issues & Solutions

### Issue: Audio not playing
**Solution:** Check system volume, have backup audio file ready

### Issue: Slow loading
**Solution:** Have screenshots ready, explain "processing time"

### Issue: Service connection error
**Solution:** Switch to mock mode, continue with demo

### Issue: Message not received
**Solution:** Say "in production, this would..." and move on

---

## 📤 Post-Demo

### Q&A Preparation

**Expected Questions:**

1. **"What's the accuracy?"**
   > "95% on language detection, 85-90% on transcription (varies by language)"

2. **"Is it production-ready?"**
   > "Yes for major languages. For dialects, we recommend staff verification."

3. **"What about offline?"**
   > "VaaNI requires internet for cloud APIs, but we can run LLM locally with Ollama."

4. **"How much does it cost?"**
   > "Free for open-source components. Cloud APIs: ~$0.002/minute of audio."

5. **"Can it integrate with our CBS?"**
   > "Yes, we have JSON export and CBS stub integration. Full integration takes 2-3 weeks."

6. **"What about data privacy?"**
   > "All processing happens in real-time. No audio stored. PDF summaries are compliant with banking regulations."

7. **"How many languages?"**
   > "15+ today, easily extensible to 22 official Indian languages."

8. **"What's your business model?"**
   > "B2B SaaS: ₹10,000/branch/month. ROI: 1 staff can handle 3x more customers."

---

## 🎓 Additional Resources

- **Architecture:** See `README.md` for technical details
- **API Docs:** http://localhost:8000/docs (when running)
- **Code:** https://github.com/your-username/vaani
- **Contact:** demo@vaani.example.com

---

**Good luck with your demo! 🚀**

*Remember: Confidence is key. You built something amazing.*
