# 🧪 Comprehensive Bot Test Questions

Based on your ingested data, here are all the important test questions organized by category:

---

## 📚 **1. ACADEMICS & REGULATIONS**

### Career Services & Placement
1. What is the Career Services Policy for 2023?
2. How do I register for campus placements?
3. What is the Academic Benefit Plan for placement?
4. What are the placement eligibility criteria?
5. Can I opt-out of placements? What are the consequences?
6. What documents do I need for placement registration?
7. What are the placement FAQs?
8. How does the internship program work?

### Attendance & Registration
9. What is the attendance policy for late registration?
10. How is attendance marked if I register late?
11. What is the minimum attendance requirement?
12. What happens if I don't meet the attendance criteria?

### Program Changes & Transfers
13. How can I change my program/branch?
14. What are the guidelines for program change for 2022-23 batch?
15. What is the credit transfer policy?
16. Can I transfer credits from another university?
17. What is the Semester/Year Abroad Policy?

### Library Services
18. What is the library policy at LPU?
19. What are the library timings?
20. How many books can I borrow?
21. What happens if I return books late?
22. How do I access online library resources?

### SPC (Student Placement Coordinator)
23. What are the guidelines for SPC appointment?
24. How do I become an SPC?
25. What are the responsibilities of an SPC?

### International Students
26. How do I generate or renew my FSIS?
27. What is the process for FRRO registration?
28. How do I get an exit bonafide certificate?
29. What documents are needed for passport claims?

### Administration
30. What are the interaction timings with higher authorities?
31. How can I meet the Dean or Director?
32. What is the process for meeting university officials?

---

## 🎓 **2. ADMISSIONS & FEES**

### Admission Process
33. What are the candidate instructions for admission?
34. What documents are required for admission?
35. What is the admission process at LPU?
36. When is the admission deadline?

### Fee Payment
37. How do I deposit my fees?
38. What are the fee deposit instructions?
39. What payment methods are accepted?
40. What is the fee refund policy?
41. Can I pay fees in installments?

### Scholarships & Financial Aid
42. What scholarships are available at LPU?
43. How do I apply for state scholarships?
44. What is the process for scholarship application?
45. What documents are needed for scholarship?
46. Which states offer scholarships to LPU students?

### Education Loans
47. How do I get an education loan?
48. What is the process for continuing students to get loans?
49. Which banks provide education loans for LPU?
50. What documents are needed for education loan?

---

## 📝 **3. EXAMINATIONS**

### Exam Policies
51. What are the ETP (End Term Paper) guidelines?
52. How do I register for reappear examinations?
53. What is the exam schedule?
54. What documents do I need to bring to the exam hall?
55. What are the exam rules and regulations?
56. What happens if I miss an exam?
57. How do I apply for reappear exams?
58. What is the fee for reappear examinations?

---

## 🏠 **4. HOSTEL & ACCOMMODATION**

### Hostel Rules & Regulations
59. What are the hostel rules at LPU?
60. What are the hostel check-in and check-out timings?
61. What items are allowed in the hostel?
62. What items are prohibited in the hostel?
63. What is the hostel curfew timing?
64. Can I have visitors in the hostel?
65. What are the mess timings?
66. How is the hostel room allocated?

### Hostel Services
67. What laundry services are available in the hostel?
68. How do I report hostel maintenance issues?
69. What Wi-Fi facilities are available in the hostel?
70. What security measures are in place in the hostel?
71. How do I change my hostel room?
72. Can I choose my roommate?

### Hostel Fees & Facilities
73. What is included in the hostel fee?
74. What amenities are provided in the hostel?
75. Is AC available in hostel rooms?
76. What recreational facilities are available for hostel residents?

### Emergency Services
77. What are the emergency contact numbers for the hostel?
78. Who is the hostel warden?
79. What medical facilities are available for hostel students?
80. What should I do in case of a medical emergency in the hostel?

---

## 🏥 **5. HEALTH & EMERGENCY**

### Medical Services
81. Where is the university hospital located?
82. What are the hospital timings?
83. What medical services are provided on campus?
84. Is there an ambulance service available?
85. How do I get medical treatment on campus?

### Emergency Contacts
86. What are the emergency contact numbers at LPU?
87. Who do I contact in case of an emergency?
88. What is the security helpline number?
89. What is the hospital emergency number?

---

## 🗺️ **6. CAMPUS NAVIGATION & MAPS**

### Location Finding
90. Where is Block 34 located?
91. How do I reach the library from my hostel?
92. Where is the main auditorium?
93. Where can I find parking on campus?
94. Where is the administrative block?
95. How do I get to the sports complex?
96. Where are the computer labs located?
97. Where is the student activity center?

### Facilities Location
98. Where is the nearest ATM on campus?
99. Where are the food courts located?
100. Where is the stationary shop?
101. Where can I print documents on campus?
102. Where is the post office on campus?

---

## 🔗 **7. GENERAL QUERIES**

### Mixed Category Questions (Testing RAG Retrieval Quality)
103. I want to change my program and also need to know the hostel rules
104. What are the placement policies and scholarship options available?
105. How do I prepare for exams and what are the library resources?
106. I'm an international student - what documents do I need and where is the FRRO office?
107. What are the late registration attendance rules and exam reappear process?

### Conversational Questions
108. Hi, what can you help me with?
109. Tell me about LPU
110. I'm a new student, what should I know?
111. What services are available on campus?
112. Who should I contact for academic issues?

### Edge Cases (Should Say "No Information")
113. What is the weather today?
114. How do I apply for other universities?
115. What is the Delhi metro schedule?
116. Tell me about IIT admission process
117. What time does the nearby mall close?

---

## 🎯 **TESTING STRATEGY**

### Priority 1: Core Functionality (Questions 1-80)
- Test document retrieval accuracy
- Verify detailed responses with specific information
- Check citation of sources
- Validate metadata filtering

### Priority 2: Navigation & Maps (Questions 90-102)
- Test location-based queries
- Verify block/building information
- Check navigation instructions

### Priority 3: Edge Cases & Mixed Queries (Questions 103-117)
- Test multi-document retrieval
- Verify "no information" handling
- Check conversational responses
- Test greeting handling

---

## ✅ **EXPECTED RESPONSE QUALITY**

For each answer, the bot should:
1. ✅ Provide **detailed, comprehensive information**
2. ✅ Use **bullet points and structured formatting**
3. ✅ Include **specific details** (dates, amounts, procedures)
4. ✅ **Never mention source file names** in the response
5. ✅ Say **"I don't have that information"** if data is not available
6. ✅ Be **friendly and professional**

---

## 📊 **PERFORMANCE METRICS TO TRACK**

1. **Response Speed**: Should be under 2-3 seconds per query
2. **Accuracy**: Correct information from relevant documents
3. **Completeness**: Detailed answers covering all aspects
4. **Relevance**: Only information from context, no hallucinations
5. **User Experience**: Clear, structured, easy-to-read responses

---

**Total Test Questions**: 117
**Data Sources**: 33 documents across 7 categories
**Coverage**: Academics, Admissions, Exams, Hostel, Health, Maps, General
