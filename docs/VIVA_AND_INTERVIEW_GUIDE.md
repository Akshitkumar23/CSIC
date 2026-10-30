# CSIC — Viva & Technical Interview Q&A Guide
### (Strict Question & Answer Format in Hinglish | Focus: Basic SQL & Cloud)

---

## 1. PROJECT OVERVIEW & ARCHITECTURE

### Q1: Yeh project fundamentally kya hai aur iska primary kaam kya hai?
* **Answer:** Yeh ek **3-Tier Cloud Web Application** hai (College Student Information & Academic Assistant). Iska primary kaam students ko unki Attendance, Examination Marks, Fee Invoices, Timetable aur College Notices securely dikhana hai, aur ek AI Chatbot provide karna hai jo verified academic record batata hai.
* **Tech Stack:**
  - Database: **Cloud PostgreSQL 16 (Supabase)** + **Embedded SQLite (Fallback)**
  - Backend: **Python 3.12 (FastAPI)**
  - Frontend: **React 18 (TypeScript + Tailwind CSS)**
  - Cloud Platform: **Vercel** (Serverless Deployment)

---

### Q2: Is project me Python kyo use kiya? Sirf React Frontend aur Cloud SQL se direct kaam kyo nahi kiya?
* **Answer:** Browser (React) se direct Cloud SQL database ko connect karna physically dangerous aur insecure hota hai:
  1. Browser me database ka username aur password dalenge to koi bhi user Inspect Element karke poora database delete ya chori kar sakta hai.
  2. Browser raw SQL queries bhejega to SQL Injection aur data tampering easily ho jayega.
  3. Beech me **Python (FastAPI)** ek secure barrier (API Gateway) ka kaam karta hai. Frontend sirf API request bhejta hai, Python token verify karta hai, aur safe parameterized SQL query run karke sirf authorized data return karta hai.
* **File Reference:** [`backend/app/main.py`](file:///d:/Projects/CSIC/backend/app/main.py), [`backend/app/api/v1/auth.py`](file:///d:/Projects/CSIC/backend/app/api/v1/auth.py)

---

### Q3: 3-Tier Architecture kya hota hai aur is project me kaise implement hua hai?
* **Answer:** 3-Tier Architecture me application 3 alag-alag layers me banti hoti hai:
  1. **Presentation Tier (Frontend):** React UI jo browser me render hota hai.
  2. **Application Tier (Backend API):** Python FastAPI jo business logic, authorization aur token validation handle karta hai.
  3. **Data Tier (Database):** Cloud PostgreSQL jahan 13 relational tables me structured data permanently store rehta hai.
* **Kaam:** User UI par click karta hai $\rightarrow$ React API call karta hai $\rightarrow$ FastAPI SQL query execute karta hai $\rightarrow$ Database data deta hai $\rightarrow$ UI update ho jati hai.

---

## 2. BASIC SQL & RELATIONAL DATABASE DESIGN (TOP PRIORITY)

### Q4: Database me kitni tables hain aur kaun-kaun si hain?
* **Answer:** Total **13 Relational Tables** hain:
  1. `users`: Students, Faculty aur Admins ke login accounts aur roles.
  2. `courses`: Degree programs (e.g., B.Tech CSE, B.Tech ECE).
  3. `subjects`: Semesters ke subjects (e.g., CS401 Cloud Computing, 4 Credits).
  4. `enrollments`: Students aur Courses ka junction (Roll Number, Semester, Section).
  5. `attendance_records`: Class-wise daily attendance (`present`, `absent`, `excused`).
  6. `examinations`: Scheduled exams (Mid-Term, End-Term, Quiz) with max marks.
  7. `marks`: Student-wise exam scores aur grades.
  8. `fee_records`: Fee invoices, amounts, due dates aur payment status.
  9. `timetable_entries`: Day-wise weekly lecture slots, rooms, aur timings.
  10. `notices`: University announcements aur circulars.
  11. `chat_sessions`: Student chat conversations.
  12. `chat_messages`: Chatbot user queries aur verified bot replies.
  13. `search_information`: Quick search knowledge items.
* **File Reference:** [`database/migrations/001_simple_schema.sql`](file:///d:/Projects/CSIC/database/migrations/001_simple_schema.sql)

---

### Q5: Primary Key aur Foreign Key kya hoti hai? Tumne kahan use ki hai?
* **Answer:**
  - **Primary Key (PK):** Table ke har row ko uniquely identify karne wala column jo kabhi NULL ya duplicate nahi ho sakta.
    - *Example:* `users.id`, `courses.id`, `subjects.id`, `enrollments.id`.
  - **Foreign Key (FK):** Ek table ka column jo dusri table ki Primary Key ko point karta hai aur relational link banata hai.
    - *Example:* `enrollments.user_id` points to `users.id`, aur `subjects.course_id` points to `courses.id`.

---

### Q6: `ON DELETE CASCADE` kya hota hai aur kyo lagaya?
* **Answer:** Jab parent table ka koi record delete hota hai, to child table me usse jude saare records automatically delete ho jate hain.
* **Kyo lagaya:** Agar ek student college chhod deta hai aur `users` table se uska record delete hota hai, to `enrollments`, `attendance_records`, aur `marks` table me uske orphan (anath) records na bachein.
* **`ON DELETE SET NULL` kahan lagaya:** `subjects.faculty_id REFERENCES users(id) ON DELETE SET NULL`. Agar koi faculty teacher resign kare, to subject delete nahi hona chahiye, bas `faculty_id` NULL ho jaye.
* **File Reference:** [`database/migrations/001_simple_schema.sql`](file:///d:/Projects/CSIC/database/migrations/001_simple_schema.sql) line 37, 42, 54.

---

### Q7: Composite Unique Constraint kya hota hai aur tumhare project me kahan use hua hai?
* **Answer:** Jab do ya do se zyada columns ka combination poori table me unique hona compulsory ho.
* **Project me use:**
  ```sql
  UNIQUE(enrollment_id, subject_id, session_date)
  ```
  Iska kaam yeh hai ki ek student ki ek hi subject me same date ko 2 attendance records insert nahi ho sakte. Duplicate attendance lagna database level par hi impossible hai.
* **Dusra Example:**
  ```sql
  UNIQUE(examination_id, enrollment_id)
  ```
  Ek student ko ek examination ke do alag-alag marks nahi mil sakte.

---

### Q8: `CHECK` Constraints kya hote hain aur tumne kahan lagaye hain?
* **Answer:** Column me aane wali value par condition lagana taki koi invalid data database me insert na ho sake.
* **Project me examples:**
  1. `role VARCHAR(20) CHECK (role IN ('student', 'faculty', 'admin'))` $\rightarrow$ Sirf ye 3 roles hi allow honge.
  2. `semester INT CHECK (semester BETWEEN 1 AND 8)` $\rightarrow$ Semester 1 se 8 ke beech hi ho sakta hai.
  3. `amount NUMERIC(10,2) CHECK (amount > 0)` $\rightarrow$ Fee amount hamesha positive hona chahiye.
  4. `marks_obtained NUMERIC(5,2) CHECK (marks_obtained >= 0)` $\rightarrow$ Marks negative nahi ho sakte.

---

### Q9: Tumhara database Normalized hai? 1NF, 2NF, 3NF kaise proof karoge?
* **Answer:** Yes, hamara schema strictly **Third Normal Form (3NF)** me hai:
  1. **1NF (First Normal Form):** Har column me atomic (single) values hain, koi array ya comma-separated values nahi hain. Har table me Primary Key hai.
  2. **2NF (Second Normal Form):** 1NF me hai aur koi Partial Dependency nahi hai. Non-key attributes poori primary key par depend karte hain. Example: Student ka roll number aur name attendance table me nahi rakha gaya; wo `enrollments` aur `users` table me hai.
  3. **3NF (Third Normal Form):** 2NF me hai aur koi Transitive Dependency ($A \rightarrow B \rightarrow C$) nahi hai. Example: `marks` table me subject ka course name ya credits store nahi hote; wo `subjects` $\rightarrow$ `courses` ke foreign key relations se nikalte hain.

---

### Q10: Attendance calculate karne ki SQL Query kya hai aur kaise kaam karti hai?
* **Answer:**
```sql
SELECT 
    s.id AS subject_id,
    s.code AS subject_code,
    s.name AS subject_name,
    COUNT(a.id) AS total_sessions,
    SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END) AS attended_sessions,
    SUM(CASE WHEN a.status = 'excused' THEN 1 ELSE 0 END) AS excused_sessions,
    ROUND(
        (SUM(CASE WHEN a.status IN ('present', 'excused') THEN 1.0 ELSE 0.0 END) / 
        NULLIF(COUNT(a.id), 0)) * 100.0, 
        1
    ) AS attendance_percentage
FROM enrollments e
JOIN subjects s ON s.course_id = e.course_id AND s.semester = e.semester
LEFT JOIN attendance_records a 
    ON a.enrollment_id = e.id AND a.subject_id = s.id
WHERE e.user_id = ?
GROUP BY s.id, s.code, s.name;
```
* **Line-by-Line Kaam:**
  - `JOIN subjects s`: Student ke registered course aur current semester ke subjects filter karta hai.
  - `LEFT JOIN attendance_records a`: Agar kisi subject ki ek bhi class nahi hui ho, tab bhi subject dashboard me 0 sessions ke sath show hoga (gayab nahi hoga).
  - `SUM(CASE WHEN a.status = 'present' THEN 1 ELSE 0 END)`: Conditional counting karta hai bina subquery ke.
  - `NULLIF(COUNT(a.id), 0)`: Agar total sessions 0 hon to denominator NULL ban jata hai, jisse **Divide-by-Zero error** se crash hone se bach jata hai.

---

### Q11: Student Profile fetch karne ke liye 3-Table JOIN kaise chal raha hai?
* **Answer:**
```sql
SELECT
    u.id, u.name, u.email, u.phone, u.role,
    e.roll_number, e.semester, e.section, e.status AS enrollment_status,
    c.code AS program_code, c.name AS program_name
FROM users u
JOIN enrollments e ON e.user_id = u.id
JOIN courses c ON c.id = e.course_id
WHERE u.id = ?;
```
* **Kaam:**
  - `users` se personal identity (Name, Email, Phone).
  - `enrollments` se academic identity (Roll Number, Semester, Section).
  - `courses` se degree program details (Program Code, Program Name).

---

### Q12: `INNER JOIN` aur `LEFT JOIN` me kya fark hai aur tumne project me kahan lagaya?
* **Answer:**
  - `INNER JOIN` sirf wahi rows return karta hai jinka match dono tables me milta hai.
  - `LEFT JOIN` left table ki saari rows deta hai, chahe right table me matching row ho ya na ho (match na milne par NULL deta hai).
  - **Project me use:** Timetable me `LEFT JOIN users u ON u.id = s.faculty_id` lagaya hai taki agar kisi subject ko abhi tak koi teacher assign na hua ho, tab bhi timetable slot screen par dikhe aur crash na ho.

---

### Q13: SQL Injection attack kya hota hai aur tumne is project me use kaise roka?
* **Answer:**
  - **Attack:** Jab user login ya search input me malicious SQL commands daalta hai (jaise `' OR '1'='1`). Agar backend simple string formatting (`f"SELECT * FROM users WHERE email = '{email}'"`) use kare, to hacker bina password ke login kar sakta hai ya data drop kar sakta hai.
  - **Solution in CSIC:** Humne poore project me **Parameterized Queries (Prepared Statements)** use ki hain:
    ```python
    sql = "SELECT id, name, email, password_hash, role FROM users WHERE LOWER(email) = LOWER(?);"
    cursor.execute(sql, (resolved_email,))
    ```
  - **Kaise protect hota hai:** Database driver user input ko code/syntax ki tarah compile nahi karta, balki strictly ek plain string literal value manta hai. Isliye SQL Injection impossible hai.
* **File Reference:** [`backend/app/repositories/sql_repository.py`](file:///d:/Projects/CSIC/backend/app/repositories/sql_repository.py) line 284-289.

---

### Q14: Database Indexing kya hoti hai aur tumne kaunse indexes banaye hain?
* **Answer:** Indexing database me book ke index page jaisi hoti hai, jo query search performance ko $O(N)$ (Full Table Scan) se ghata kar $O(\log N)$ (B-Tree Search) kar deti hai.
* **Project me Indexes:**
  - `CREATE INDEX idx_users_email ON users(email);` $\rightarrow$ Fast login lookup.
  - `CREATE INDEX idx_attendance_enrollment ON attendance_records(enrollment_id, subject_id);` $\rightarrow$ Fast attendance percentage calculation.
  - `CREATE INDEX idx_timetable_day ON timetable_entries(day_of_week);` $\rightarrow$ Weekly timetable filter.
* **File Reference:** [`database/migrations/001_simple_schema.sql`](file:///d:/Projects/CSIC/database/migrations/001_simple_schema.sql) line 128-135.

---

### Q15: Database me SQLite aur PostgreSQL dono ka code kyo hai?
* **Answer:**
  - **PostgreSQL (Cloud):** Hamara primary production database hai jo cloud server (Supabase/Render) par securely run hota hai.
  - **SQLite (Embedded):** Hamara local development aur serverless high-availability fallback engine hai.
  - Dono ka SQL syntax ANSI SQL standard rakha gaya hai taki same queries dono engines par chalti hain.

---

## 3. CLOUD ARCHITECTURE & DEPLOYMENT

### Q16: Is project me "Cloud" kahan aur kaise use hua hai?
* **Answer:** Project 100% Cloud-native hai:
  1. **Cloud Database Tier:** PostgreSQL 16 database **Supabase/Render Cloud** par hosted hai, jo SSL/TLS encrypted connection use karta hai.
  2. **Cloud Serverless API Tier:** Python FastAPI backend **Vercel Cloud** ke serverless compute par deployed hai.
  3. **Cloud Frontend Tier:** React Single Page Application Vercel ke global Edge CDN par hosted hai.
  4. Live Production URL: `https://csic-orpin.vercel.app`.

---

### Q17: `DATABASE_URL` kya hoti hai aur connection kaise banta hai?
* **Answer:** Yeh ek standardized connection URI hoti hai jo database protocol, user credentials, cloud host, port aur database name specify karti hai:
  `postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres?sslmode=require`
* Backend me `psycopg2` driver is URL ko parse karke cloud server se secure TCP/SSL socket connection banata hai.
* **File Reference:** [`backend/app/core/config.py`](file:///d:/Projects/CSIC/backend/app/core/config.py) line 20.

---

### Q18: Environment Variables kya hote hain aur unka use kyo kiya gaya?
* **Answer:** Sensitive data (jaise database password, JWT secret key, API keys) ko GitHub ke source code me daalna security risk hota hai. Isliye unhe OS Environment Variables me store kiya jata hai (`.env` locally aur Vercel Dashboard par).
* Code runtime par `os.environ.get("DATABASE_URL")` se use read karta hai.

---

### Q19: Serverless Architecture (Vercel) kya hota hai?
* **Answer:** Normal server me machine 24 ghante on rehti hai. Vercel Serverless me jab student website par request bhejta hai, tab ek lightweight cloud container microsecond me bootstrap hota hai, query execute karta hai, response return karta hai, aur automatically idle ho jata hai. Isse cost save hoti hai aur scaling automatic hoti hai.

---

### Q20: Connection Pooling (`psycopg2.pool`) kya hai aur kyo lagaya?
* **Answer:**
  - Har baar database se connect hone par 3-way TCP handshake aur SSL/TLS negotiation me 200-400ms ka time lagta hai.
  - Connection Pool (`ThreadedConnectionPool`) pehle se 5-10 connections open rakhta hai. Jab query aati hai, to pool se ready connection milta hai aur query 2ms me run ho jati hai, fir connection pool me wapas chala jata hai.
* **File Reference:** [`backend/app/repositories/sql_repository.py`](file:///d:/Projects/CSIC/backend/app/repositories/sql_repository.py) line 76-88.

---

### Q21: Circuit Breaker Pattern kya hai aur tumne ise kyo lagaya?
* **Answer:**
  - **Problem:** Free-tier cloud databases (jaise Supabase/Render) inactivity ke baad sleep/pause ho jate hain ya network slow ho jata hai, jisse har query 5 second hang ho sakti thi aur chatbot me 30 second lag rahe the.
  - **Solution (Circuit Breaker):** Humne class-level circuit breaker lagaya hai (`_pg_unreachable_until`). Agar Cloud Postgres fail hota hai ya 2s me connect nahi hota, to circuit breaker trip ho jata hai aur next 5 minutes ke liye saari queries turant embedded high-speed SQLite par chali jati hain (`< 1ms`).
  - **Result:** Website kabhi freeze nahi hoti aur user ko 500 error nahi milti.

---

## 4. BACKEND (PYTHON FASTAPI) & APIS

### Q22: FastAPI framework kyo use kiya? Flask ya Django kyo nahi?
* **Answer:**
  1. **Speed:** FastAPI ASGI (Starlette) par based hai jo NodeJS aur Go ke barabar fast asynchronous I/O performance deta hai.
  2. **Type Safety & Validation:** Pydantic models automatically request data ko validate karte hain.
  3. **Auto Documentation:** Swagger UI documentation (`/docs`) automatically generate ho jati hai.

---

### Q23: Backend me itni alag-alag files kyo hain (`auth.py`, `attendance.py`, `marks.py`, etc.)?
* **Answer:** Isko **Separation of Concerns (Modular Architecture)** kehte hain:
  - Ek hi 4000-line ki file banane ke bajaye har academic feature ka router alag file me rakha gaya hai.
  - `auth.py`: Sirf Login aur Token validation.
  - `attendance.py`: Sirf Attendance endpoints.
  - `marks.py`: Sirf Exam Results endpoints.
  - `fees.py`: Sirf Fee Invoices endpoints.
  - `sql_repository.py`: Central data access layer jahan sari SQL queries rehti hain.
  - Isse code maintainable hota hai aur team me kaam karna easy hota hai.

---

### Q24: User login kaise kaam karta hai? Plain text password kyo nahi save karte?
* **Answer:**
  1. Student login form me email aur cleartext password enter karta hai.
  2. Backend `get_user_by_email()` se database se user ka `password_hash` nikaalta hai.
  3. **Bcrypt** algorithm `bcrypt.checkpw(plain_password, password_hash)` se verify karta hai.
  4. Plain text password kabhi save nahi karte kyonki agar database leak ho jaye to kisi bhi user ka password expose na ho.
* **File Reference:** [`backend/app/core/security.py`](file:///d:/Projects/CSIC/backend/app/core/security.py) line 16-24.

---

### Q25: JWT (JSON Web Token) kya hota hai aur kaise kaam karta hai?
* **Answer:** JWT ek digitally signed, compact token hota hai jisme 3 parts hote hain: `Header.Payload.Signature`.
  - Login verify hone par backend `create_access_token()` se JWT create karta hai jisme `user_id`, `role`, aur `expiry_time` hota hai.
  - Frontend is token ko `LocalStorage` me store karta hai aur har request ke header me bhejta hai: `Authorization: Bearer <token>`.
  - Backend token ke digital signature ko secret key se verify karta hai bina database me session query kiye.
* **File Reference:** [`backend/app/core/security.py`](file:///d:/Projects/CSIC/backend/app/core/security.py) line 33-50.

---

### Q26: Role-Based Access Control (RBAC) kya hai? Student dusre student ka data kyo nahi dekh sakta?
* **Answer:**
  - Token ke andar user ka `role` (`student`, `faculty`, `admin`) encoded hota hai.
  - Endpoints par security dependencies lagi hain (`require_student`, `require_faculty`, `require_admin`).
  - Student boundary enforce karne ke liye `verify_student_access()` function check karta hai: agar logged-in student kisi dusre student ki `student_id` access karne ki koshish kare, to system turant `403 Forbidden` return karta hai.
* **File Reference:** [`backend/app/core/security.py`](file:///d:/Projects/CSIC/backend/app/core/security.py) line 139-145.

---

## 5. AI CHATBOT & DATA SAFETY

### Q27: Chatbot student ka data kaise batata hai? Kya AI model direct SQL queries likhta hai?
* **Answer:** **BILKUL NAHI.** AI model ko direct database connection ya SQL likhne ka access dena security hazard hai (Prompt Injection risk).
* **CSIC Solution (Zero-SQL Intent Router):**
  1. Student likhta hai: *"What is my attendance percentage?"*
  2. **Intent Router** query analyze karke classify karta hai: `QueryIntent.ATTENDANCE`.
  3. Backend ka secure, pre-defined function `get_student_attendance_summary(user_id)` database se exact verified SQL data lata hai.
  4. AI sirf us verified data ko polite conversational language me format karke present karta hai. Zero Hallucination, Zero SQL generation.
* **File Reference:** [`backend/app/services/ai/chatbot_service.py`](file:///d:/Projects/CSIC/backend/app/services/ai/chatbot_service.py) line 100-118.

---

### Q28: RAG (Retrieval-Augmented Generation) kya hota hai aur isme kahan use hua hai?
* **Answer:** Jab student college regulations ya policies ke bare me poochhta hai (e.g. *"Medical leave par minimum attendance kitni chahiye?"*):
  - Model apne man se answer nahi deta.
  - Hamara RAG engine official college document chunks me se relevant section search karta hai (`Academic Regulations Section 4.2`).
  - Model sirf us official chunk ko padhkar exact answer quote karta hai source citation ke sath.
* **File Reference:** [`backend/app/services/ai/rag_service.py`](file:///d:/Projects/CSIC/backend/app/services/ai/rag_service.py) line 416-436.

---

### Q29: Agar internet down ho ya AI API quota khatam ho jaye, to kya Chatbot crash ho jayega?
* **Answer:** Nahi Sir. Humne ek **Deterministic Rule-Based Local NLP Fallback** banaya hai. Agar Gemini API key absent ho ya quota khatam ho, tab bhi chatbot student ki attendance, marks, fees aur timetable direct relational database se fetch karke accurately display karta hai.

---

## 6. FRONTEND (REACT) & UX PERFORMANCE

### Q30: SWR (Stale-While-Revalidate) Client Cache kya hai aur kyo lagaya?
* **Answer:**
  - Pehle jab student Dashboard se Attendance ya Marks page par jata tha, to har click par 2 second loading skeleton ghumta rehta tha.
  - Humne frontend API service me ek **60-second in-memory cache** lagaya hai.
  - Jab student Dashboard kholta hai, data cache ho jata hai. Attendance page par click karte hi screen bina kisi loading delay ke **0 milliseconds** me render ho jati hai.
* **File Reference:** [`frontend/src/services/api.ts`](file:///d:/Projects/CSIC/frontend/src/services/api.ts) line 607-649.

---

### Q31: Chatbot me Optimistic UI update kya hota hai?
* **Answer:** Jab student message type karke Send dabata hai, to server ke reply aane ka wait karne ke bajaye user ka message turant screen par show ho jata hai aur niche typing indicator start ho jata hai. Jab backend se answer aata hai, to wo append ho jata hai. Isse app extremely fast aur responsive lagti hai.
* **File Reference:** [`frontend/src/pages/student/ChatPage.tsx`](file:///d:/Projects/CSIC/frontend/src/pages/student/ChatPage.tsx) line 214-226.

---

## 7. QUICK DEMO DATA FOR TEACHER PRESENTATION

| Role | Email ID | Password | Access Highlights |
| :--- | :--- | :--- | :--- |
| **Student** | `rashi@csic.edu` | `1234` | Attendance (88.5%), Marks, Fee Invoices, Timetable, AI Chatbot |
| **Student 2** | `vanshika@csic.edu` | `1234` | B.Tech CSE Section A profile |
| **Faculty** | `rajesh.kumar@csic.edu` | `1234` | Course assignments, Roster review, Attendance warnings |
| **Admin** | `admin@csic.edu` | `1234` | Full system overview, notice management, user roster |

* **Live Cloud Application URL:** `https://csic-orpin.vercel.app`
* **GitHub Repository:** `https://github.com/Akshitkumar23/CSIC`
