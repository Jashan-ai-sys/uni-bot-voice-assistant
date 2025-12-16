# Quick FAQ Verification Test

## 🎯 Purpose
Fast verification that the bot is working correctly across all document types.

---

## ✅ Core Functionality (5 questions)

1. **Hi, what can you help me with?**
   - Tests: Greeting handling, basic response

2. **What is the Career Services Policy?**
   - Tests: Academic documents, policy retrieval

3. **What are the hostel rules?**
   - Tests: Hostel documents, structured responses

4. **How do I pay my fees?**
   - Tests: Admissions/fee documents

5. **Where is Block 34?**
   - Tests: Map/navigation documents

---

## 📋 Category Coverage (15 questions)

### Academics (3 questions)
6. What is the attendance policy?
7. How do I apply for placements?
8. What are the library timings?

### Admissions & Fees (3 questions)
9. What documents are needed for admission?
10. How can I get a scholarship?
11. What is the fee refund policy?

### Examinations (2 questions)
12. What are the ETP guidelines?
13. How do I register for reappear exams?

### Hostel (3 questions)
14. What items are prohibited in the hostel?
15. What are the mess timings?
16. Can I have visitors in the hostel?

### Emergency & Health (2 questions)
17. What are the emergency contact numbers?
18. Where is the university hospital?

### Navigation (2 questions)
19. Where is the library?
20. How do I reach the administrative block?

---

## 🔍 Quality Checks

### Response should include:
- ✅ **Detailed information** (not just yes/no)
- ✅ **Bullet points** or structured format
- ✅ **Specific details** (numbers, times, procedures)
- ✅ **No source file mentions** ("hostel.pdf" etc.)
- ✅ **Professional tone**

### Red Flags:
- ❌ "I don't have that information" (for questions 1-20)
- ❌ Very short answers (< 30 words)
- ❌ Mentions of file names
- ❌ Hallucinated information

---

## ⚡ Quick Test (1 minute)

**Essential 3-Question Test:**
1. What are the hostel rules?
2. How do I apply for scholarships?
3. Where is Block 34?

If all 3 answer correctly with details → **Bot is working** ✅

---

## 🎯 Expected Response Times

- **Current Setup**: 2-3 seconds
- **With TinyLlama**: 1-2 seconds  
- **With WSL2+GPU**: 0.5-1 second

---

## 📊 Success Criteria

**Pass**: 18-20 questions answered correctly with details  
**Acceptable**: 15-17 questions answered correctly  
**Needs Fix**: < 15 questions answered correctly

---

## 💡 Usage

**For Quick Check:**
- Ask questions 1-5 (**~2 minutes**)

**For Full Verification:**
- Ask all 20 questions (**~5 minutes**)

**For Specific Category:**
- Pick relevant section (Academics, Hostel, etc.)
