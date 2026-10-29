import {
  Profile,
  AttendanceSummary,
  Mark,
  FeeInvoice,
  TimetableEntry,
  Notice,
  NoticeCategory,
  ChatMessage,
  ChatSession,
  StudentRosterItem,
  FacultyCourseAssignment,
  UserRole,
  FeePayment,
  AttendanceWarning,
  SearchItem,
} from '../types';


const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? (import.meta.env.PROD ? '' : 'http://localhost:8000');
const TOKEN_KEY = 'csic_auth_token';
const USER_KEY = 'csic_user_profile';

// Token Management
export const getStoredToken = (): string | null => localStorage.getItem(TOKEN_KEY);
export const setStoredToken = (token: string): void => localStorage.setItem(TOKEN_KEY, token);
export const removeStoredToken = (): void => {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
  clearUserCache();
};

export const getStoredUser = (): Profile | null => {
  try {
    const token = localStorage.getItem(TOKEN_KEY);
    const data = localStorage.getItem(USER_KEY);
    if (!token || !data) {
      return null;
    }
    const parsed = JSON.parse(data);
    if (!parsed || typeof parsed !== 'object' || !parsed.id || !parsed.role) {
      removeStoredToken();
      return null;
    }
    return parsed as Profile;
  } catch (err) {
    console.warn('[CSIC Auth] Corrupted user session in localStorage, clearing:', err);
    removeStoredToken();
    return null;
  }
};

export const setStoredUser = (user: Profile): void => {
  try {
    localStorage.setItem(USER_KEY, JSON.stringify(user));
  } catch (err) {
    console.error('[CSIC Auth] Failed to save user session to localStorage:', err);
  }
};

// ==========================================
// SYNTHETIC MOCK DATA STORE
// ==========================================

export const MOCK_STUDENT_PROFILE: Profile = {
  id: 'stu-001',
  email: 'rashi@csic.edu',
  full_name: 'Rashi',
  role: 'student',
  phone: '+91 98765 43210',
  avatar_url: '',
  roll_number: 'CS2023001',
  department: 'Computer Science & Engineering',
  program: 'B.Tech Computer Science & Engineering',
  semester: 6,
  section: 'A',
  is_active: true,
};

export const MOCK_FACULTY_PROFILE: Profile = {
  id: 'fac-001',
  email: 'rajesh.kumar@csic.edu',
  full_name: 'Akshit',
  role: 'faculty',
  phone: '+91 98765 11223',
  avatar_url: '',
  department: 'Computer Science & Engineering',
  is_active: true,
};

export const MOCK_ADMIN_PROFILE: Profile = {
  id: 'admin-001',
  email: 'admin@csic.edu',
  full_name: 'Akshit',
  role: 'admin',
  phone: '+91 98765 00001',
  avatar_url: '',
  department: 'Academic Administration',
  is_active: true,
};

export const MOCK_ATTENDANCE: AttendanceSummary = {
  overall_percentage: 72.8,
  total_conducted: 162,
  total_attended: 118,
  total_excused: 5,
  low_attendance_warning: true, // overall < 75%
  classes_needed_to_reach_threshold: 14,
  subjects: [
    {
      subject_id: 'sub-01',
      subject_code: 'CS401',
      subject_name: 'Cloud Computing & Distributed Systems',
      faculty_name: 'Dr. Rajesh Kumar',
      conducted_classes: 36,
      attended_classes: 24,
      excused_classes: 1,
      attendance_percentage: 69.44,
      percentage: 69.44, // Low attendance!
      status_warning: true,
      classes_needed_for_75: 8,
    },
    {
      subject_id: 'sub-02',
      subject_code: 'CS402',
      subject_name: 'Advanced Database Engineering',
      faculty_name: 'Prof. Anita Deshmukh',
      conducted_classes: 34,
      attended_classes: 23,
      excused_classes: 2,
      attendance_percentage: 73.53,
      percentage: 73.53, // Low attendance!
      status_warning: true,
      classes_needed_for_75: 2,
    },
    {
      subject_id: 'sub-03',
      subject_code: 'CS403',
      subject_name: 'Machine Learning & AI',
      faculty_name: 'Dr. Vikram Malhotra',
      conducted_classes: 32,
      attended_classes: 27,
      excused_classes: 0,
      attendance_percentage: 84.38,
      percentage: 84.38,
      status_warning: false,
      classes_needed_for_75: 0,
    },
    {
      subject_id: 'sub-04',
      subject_code: 'CS404',
      subject_name: 'Computer Networks & Security',
      faculty_name: 'Prof. Sunita Rao',
      conducted_classes: 30,
      attended_classes: 24,
      excused_classes: 1,
      attendance_percentage: 83.33,
      percentage: 83.33,
      status_warning: false,
      classes_needed_for_75: 0,
    },
  ],
};

export const MOCK_MARKS: Mark[] = [
  {
    id: 'mark-01',
    subject_id: 'sub-401',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing & Distributed Systems',
    exam_name: 'Mid-Term Examination',
    exam_date: '2026-09-15',
    marks_obtained: 44.5,
    max_marks: 50.0,
    percentage: 89.0,
    grade: 'A',
    is_absent: false,
    weightage: 30,
  },
  {
    id: 'mark-02',
    subject_id: 'sub-402',
    subject_code: 'CS402',
    subject_name: 'Machine Learning & Neural Networks',
    exam_name: 'Mid-Term Examination',
    exam_date: '2026-09-18',
    marks_obtained: 41.0,
    max_marks: 50.0,
    percentage: 82.0,
    grade: 'A-',
    is_absent: false,
    weightage: 30,
  },
  {
    id: 'mark-03',
    subject_id: 'sub-403',
    subject_code: 'CS403',
    subject_name: 'Database Engineering & Internals',
    exam_name: 'Mid-Term Examination',
    exam_date: '2026-09-21',
    marks_obtained: 47.0,
    max_marks: 50.0,
    percentage: 94.0,
    grade: 'A+',
    is_absent: false,
    weightage: 30,
  },
  {
    id: 'mark-04',
    subject_id: 'sub-404',
    subject_code: 'CS404',
    subject_name: 'Operating System Design',
    exam_name: 'Mid-Term Examination',
    exam_date: '2026-09-24',
    marks_obtained: 38.0,
    max_marks: 50.0,
    percentage: 76.0,
    grade: 'B+',
    is_absent: false,
    weightage: 30,
  },
  {
    id: 'mark-05',
    subject_id: 'sub-405',
    subject_code: 'CS405',
    subject_name: 'Software Verification & Testing',
    exam_name: 'Continuous Lab Assessment',
    exam_date: '2026-10-02',
    marks_obtained: 23.5,
    max_marks: 25.0,
    percentage: 94.0,
    grade: 'A+',
    is_absent: false,
    weightage: 20,
  },
  {
    id: 'mark-06',
    subject_id: 'sub-401',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing & Distributed Systems',
    exam_name: 'Quiz 1: Microservices & Containers',
    exam_date: '2026-08-28',
    marks_obtained: 19.0,
    max_marks: 20.0,
    percentage: 95.0,
    grade: 'A+',
    is_absent: false,
    weightage: 10,
  },
];

export const MOCK_FEES: FeeInvoice[] = [
  {
    id: 'inv-101',
    invoice_number: 'INV-2026-06-01',
    title: 'Semester VI Tuition & Academic Fee',
    amount: 62500.0,
    due_date: '2026-11-15',
    status: 'unpaid',
    paid_amount: 0,
  },
  {
    id: 'inv-102',
    invoice_number: 'INV-2026-06-02',
    title: 'Advanced Cloud Lab & Infrastructure Fee',
    amount: 8500.0,
    due_date: '2026-10-31',
    status: 'paid',
    paid_amount: 8500.0,
    payment_date: '2026-09-10',
    transaction_ref: 'TXN-UPI-984021',
  },
  {
    id: 'inv-103',
    invoice_number: 'INV-2026-05-01',
    title: 'Semester V Tuition & Exam Fee',
    amount: 65000.0,
    due_date: '2026-04-15',
    status: 'paid',
    paid_amount: 65000.0,
    payment_date: '2026-04-10',
    transaction_ref: 'TXN-NB-554109',
  },
  {
    id: 'inv-104',
    invoice_number: 'INV-2026-LIB-01',
    title: 'Library Overdue Book Replacement',
    amount: 450.0,
    due_date: '2026-10-05',
    status: 'overdue',
    paid_amount: 0,
  },
];

export const MOCK_TIMETABLE: TimetableEntry[] = [
  {
    id: 'tt-1',
    day_of_week: 'Monday',
    start_time: '09:00',
    end_time: '10:00',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing & Distributed Systems',
    room_number: 'LHC-302',
    faculty_name: 'Dr. Rajesh Kumar',
  },
  {
    id: 'tt-2',
    day_of_week: 'Monday',
    start_time: '10:15',
    end_time: '11:15',
    subject_code: 'CS402',
    subject_name: 'Advanced Database Engineering',
    room_number: 'LHC-204',
    faculty_name: 'Prof. Anita Deshmukh',
  },
  {
    id: 'tt-3',
    day_of_week: 'Monday',
    start_time: '11:30',
    end_time: '13:00',
    subject_code: 'CS403',
    subject_name: 'Machine Learning & AI',
    room_number: 'Computing Lab 4',
    faculty_name: 'Dr. Vikram Malhotra',
  },
  {
    id: 'tt-4',
    day_of_week: 'Tuesday',
    start_time: '09:00',
    end_time: '10:30',
    subject_code: 'CS404',
    subject_name: 'Computer Networks & Security',
    room_number: 'LHC-301',
    faculty_name: 'Prof. Sunita Rao',
  },
  {
    id: 'tt-5',
    day_of_week: 'Tuesday',
    start_time: '11:00',
    end_time: '12:30',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing (Tutorial)',
    room_number: 'Seminar Hall B',
    faculty_name: 'Dr. Rajesh Kumar',
  },
  {
    id: 'tt-6',
    day_of_week: 'Wednesday',
    start_time: '10:00',
    end_time: '11:30',
    subject_code: 'CS403',
    subject_name: 'Machine Learning & AI',
    room_number: 'LHC-101',
    faculty_name: 'Dr. Vikram Malhotra',
  },
  {
    id: 'tt-7',
    day_of_week: 'Wednesday',
    start_time: '14:00',
    end_time: '16:00',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing Lab',
    room_number: 'Lab 201',
    faculty_name: 'Dr. Rajesh Kumar',
  },
  {
    id: 'tt-8',
    day_of_week: 'Thursday',
    start_time: '09:00',
    end_time: '10:30',
    subject_code: 'CS402',
    subject_name: 'Advanced Database Engineering',
    room_number: 'LHC-204',
    faculty_name: 'Prof. Anita Deshmukh',
  },
  {
    id: 'tt-9',
    day_of_week: 'Thursday',
    start_time: '11:00',
    end_time: '12:30',
    subject_code: 'CS404',
    subject_name: 'Computer Networks & Security',
    room_number: 'LHC-302',
    faculty_name: 'Prof. Sunita Rao',
  },
  {
    id: 'tt-10',
    day_of_week: 'Friday',
    start_time: '09:30',
    end_time: '11:00',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing & Distributed Systems',
    room_number: 'Cloud Center of Excellence',
    faculty_name: 'Dr. Rajesh Kumar',
  },
  {
    id: 'tt-11',
    day_of_week: 'Friday',
    start_time: '14:00',
    end_time: '15:30',
    subject_code: 'CS404',
    subject_name: 'Computer Networks & Security',
    room_number: 'LHC-301',
    faculty_name: 'Prof. Sunita Rao',
  },
];

export const MOCK_NOTICES: Notice[] = [
  {
    id: 'not-01',
    title: 'ATTENDANCE ALERT: Mandatory 75% Cut-Off Policy Enforcement',
    category: 'urgent',
    content: 'All students are reminded that university regulations mandate a minimum of 75% attendance in each registered subject to be eligible for End-Semester Examinations. Students with current attendance below 75% must meet their academic advisors immediately.',
    published_by_name: 'Office of Dean Academic Affairs',
    published_at: '2026-10-10 10:00:00',
    target_role: 'student',
    is_urgent: true,
  },
  {
    id: 'not-02',
    title: 'End-Semester Theory & Practical Exam Schedule Released',
    category: 'examination',
    content: 'The finalized timetable for the Autumn 2026 End-Semester Examinations has been published. Practical evaluations begin on November 20, 2026, followed by theory exams commencing December 1, 2026.',
    published_by_name: 'Controller of Examinations',
    published_at: '2026-10-08 14:30:00',
    target_role: 'all',
  },
  {
    id: 'not-03',
    title: 'Semester Fee Due Date & Online Payment Portal Open',
    category: 'administrative',
    content: 'The portal for payment of Semester VI Tuition and Amenities fee is now active. The deadline for fee clearance without late charges is November 15, 2026.',
    published_by_name: 'Finance & Accounts Division',
    published_at: '2026-10-05 09:15:00',
    target_role: 'student',
  },
  {
    id: 'not-04',
    title: 'Annual Hackathon "CodeStorm 2026" Registrations Open',
    category: 'event',
    content: 'Join the premier 36-hour hackathon hosted by the CS Department. Exciting cash prizes, cloud credits, and industry mentorship opportunities available.',
    published_by_name: 'ACM Student Chapter',
    published_at: '2026-10-01 11:00:00',
    target_role: 'all',
  },
  {
    id: 'not-05',
    title: 'Technical Workshop on Cloud Computing & Distributed Systems',
    category: 'academic',
    content: 'Hands-on practical session on cloud computing, web servers, and container deployment. Room LHC-201, Friday at 4 PM.',
    published_by_name: 'Department of Computer Science',
    published_at: '2026-09-28 16:45:00',
    target_role: 'all',
  },
];

export const MOCK_STUDENT_ROSTER: StudentRosterItem[] = [
  {
    id: 'ros-1',
    student_id: 'stu-001',
    full_name: 'Rashi',
    email: 'rashi@csic.edu',
    roll_number: 'CS2023001',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    status: 'active',
    attendance_percentage: 72.8,
    gpa: 8.85,
  },
  {
    id: 'ros-2',
    student_id: 'stu-002',
    full_name: 'Vanshika',
    email: 'vanshika@csic.edu',
    roll_number: 'CS2023002',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    status: 'active',
    attendance_percentage: 88.5,
    gpa: 9.20,
  },
  {
    id: 'ros-3',
    student_id: 'stu-003',
    full_name: 'Silki',
    email: 'silki@csic.edu',
    roll_number: 'CS2023003',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    status: 'active',
    attendance_percentage: 64.2, // Warning!
    gpa: 7.90,
  },
  {
    id: 'ros-4',
    student_id: 'stu-004',
    full_name: 'Akshit',
    email: 'akshit@csic.edu',
    roll_number: 'CS2023004',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    status: 'active',
    attendance_percentage: 100.0,
    gpa: 9.60,
  },
  {
    id: 'ros-5',
    student_id: 'stu-005',
    full_name: 'Kavya Subramanian',
    email: 'kavya.subramanian@csic.edu',
    roll_number: 'CS2023005',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'B',
    status: 'active',
    attendance_percentage: 79.4,
    gpa: 8.60,
  },
  {
    id: 'ros-6',
    student_id: 'stu-006',
    full_name: 'Aditya Verma',
    email: 'aditya.verma@csic.edu',
    roll_number: 'CS2023006',
    department: 'Computer Science & Engineering',
    program: 'B.Tech CSE',
    semester: 6,
    section: 'A',
    status: 'active',
    attendance_percentage: 74.5,
    gpa: 8.12,
  },
];

export const MOCK_FACULTY_ASSIGNMENTS: FacultyCourseAssignment[] = [
  {
    id: 'fca-1',
    faculty_id: 'fac-001',
    faculty_name: 'Dr. Rajesh Kumar',
    subject_id: 'sub-01',
    subject_code: 'CS401',
    subject_name: 'Cloud Computing & Distributed Systems',
    course_section: 'Sec A (Sem 6)',
    enrolled_count: 64,
  },
  {
    id: 'fca-2',
    faculty_id: 'fac-002',
    faculty_name: 'Prof. Anita Deshmukh',
    subject_id: 'sub-02',
    subject_code: 'CS402',
    subject_name: 'Advanced Database Engineering',
    course_section: 'Sec A (Sem 6)',
    enrolled_count: 64,
  },
  {
    id: 'fca-3',
    faculty_id: 'fac-003',
    faculty_name: 'Dr. Vikram Malhotra',
    subject_id: 'sub-03',
    subject_code: 'CS403',
    subject_name: 'Machine Learning & AI',
    course_section: 'Sec B (Sem 6)',
    enrolled_count: 58,
  },
  {
    id: 'fca-4',
    faculty_id: 'fac-004',
    faculty_name: 'Prof. Sunita Rao',
    subject_id: 'sub-04',
    subject_code: 'CS404',
    subject_name: 'Computer Networks & Security',
    course_section: 'Sec A (Sem 6)',
    enrolled_count: 64,
  },
];

// In-memory notice state so admins can add/delete during a session
let noticesList: Notice[] = [...MOCK_NOTICES];
let studentsList: StudentRosterItem[] = [...MOCK_STUDENT_ROSTER];

// ==========================================
// IN-MEMORY SAFE CACHE & IN-FLIGHT DEDUPLICATION
// ==========================================

export interface CacheOptions {
  ttlMs?: number;
  skipCache?: boolean;
}

interface CacheEntry<T> {
  data: T;
  timestamp: number;
  expiresAt: number;
  userId: string;
}

export const DEFAULT_TTLS = {
  attendance: 60 * 1000,    // 60 seconds
  marks: 120 * 1000,        // 2 minutes
  fees: 60 * 1000,          // 60 seconds
  timetable: 300 * 1000,    // 5 minutes
  students: 120 * 1000,     // 2 minutes
  notices: 60 * 1000,       // 1 minute
  profile: 120 * 1000,      // 2 minutes
};

const MAX_CACHE_ENTRIES = 60;
const memoryCache = new Map<string, CacheEntry<any>>();
const inFlightRequests = new Map<string, Promise<any>>();

export const clearUserCache = (): void => {
  memoryCache.clear();
  inFlightRequests.clear();
};

export const invalidateCache = (pattern?: string): void => {
  if (!pattern) {
    memoryCache.clear();
    return;
  }
  for (const key of memoryCache.keys()) {
    if (key.includes(pattern)) {
      memoryCache.delete(key);
    }
  }
};

export const getCachedData = <T>(endpoint: string, userId?: string): T | null => {
  const effectiveUserId = userId || getStoredUser()?.id;
  if (!effectiveUserId) return null;
  const cacheKey = `GET:${effectiveUserId}:${endpoint}`;
  const entry = memoryCache.get(cacheKey);
  if (!entry) return null;
  if (entry.expiresAt <= Date.now() || entry.userId !== effectiveUserId) {
    memoryCache.delete(cacheKey);
    return null;
  }
  return entry.data as T;
};

// Helper for fetch with timeout, deduplication, and safe in-memory caching
async function requestWithFallback<T>(
  endpoint: string,
  options: RequestInit = {},
  fallbackData: T,
  cacheOptions?: CacheOptions
): Promise<T> {
  const token = getStoredToken();
  const currentUser = getStoredUser();
  const userId = currentUser?.id || 'anonymous';
  const method = (options.method || 'GET').toUpperCase();
  const isGet = method === 'GET';
  const ttlMs = cacheOptions?.ttlMs ?? 0;
  const skipCache = Boolean(cacheOptions?.skipCache);

  // 1. Check in-memory cache for safe GET requests
  if (isGet && ttlMs > 0 && userId !== 'anonymous' && !skipCache) {
    const cacheKey = `GET:${userId}:${endpoint}`;
    const cached = memoryCache.get(cacheKey);
    if (cached && cached.expiresAt > Date.now() && cached.userId === userId) {
      return cached.data as T;
    }
  }

  // 2. Fetcher execution
  const executeFetch = async (): Promise<T> => {
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const controller = new AbortController();
      const timeoutMs = 15000;
      const timeoutId = setTimeout(() => controller.abort(), timeoutMs);

      const response = await fetch(`${API_BASE_URL}${endpoint}`, {
        ...options,
        headers,
        signal: options.signal || controller.signal,
      });
      clearTimeout(timeoutId);

      if (response.ok) {
        const parsed = await response.json();

        // Save to in-memory cache for safe GET requests
        if (isGet && ttlMs > 0 && userId !== 'anonymous') {
          const cacheKey = `GET:${userId}:${endpoint}`;
          if (memoryCache.size >= MAX_CACHE_ENTRIES) {
            const oldestKey = memoryCache.keys().next().value;
            if (oldestKey) memoryCache.delete(oldestKey);
          }
          memoryCache.set(cacheKey, {
            data: parsed,
            timestamp: Date.now(),
            expiresAt: Date.now() + ttlMs,
            userId,
          });
        }

        return parsed;
      }
      if (response.status === 401 || response.status === 403) {
        removeStoredToken();
        const errJson = await response.json().catch(() => ({ detail: 'Unauthorized or Forbidden' }));
        throw new Error(errJson.detail || 'Access denied');
      }
      // In production, strictly reject non-OK responses rather than falling back to mock data
      if (import.meta.env.PROD) {
        throw new Error(`Production request failed with status ${response.status} on ${endpoint}`);
      }
      // If backend returns 404 or other status in development, gracefully fallback to mock
      console.warn(`[CSIC API] Endpoint ${endpoint} returned status ${response.status}. Using local mock data.`);
      return fallbackData;
    } catch (err: any) {
      if (err.message && (err.message.includes('Access denied') || err.message.includes('Forbidden') || err.message.includes('Unauthorized'))) {
        throw err;
      }
      if (import.meta.env.PROD) {
        throw new Error(`Production backend unreachable at ${API_BASE_URL}${endpoint}.`);
      }
      // Network failure, connection refused, or timeout: fallback to mock data seamlessly in local dev
      console.info(`[CSIC API] Backend unreachable at ${API_BASE_URL}${endpoint}. Serving mock fallback.`);
      return fallbackData;
    }
  };

  // 3. In-flight request deduplication for safe GET requests
  if (isGet) {
    const dedupKey = `${method}:${userId}:${endpoint}`;
    const existing = inFlightRequests.get(dedupKey);
    if (existing) {
      return existing as Promise<T>;
    }
    const promise = executeFetch().finally(() => {
      inFlightRequests.delete(dedupKey);
    });
    inFlightRequests.set(dedupKey, promise);
    return promise;
  }

  return executeFetch();
}

// ==========================================
// EXPORTED API METHODS
// ==========================================

export const api = {
  // Authentication
  async login(email: string, _pass: string, role: UserRole): Promise<{ token: string; user: Profile }> {
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password: _pass, role }),
      });
      if (res.ok) {
        const tokenData = await res.json();
        const token = tokenData.access_token || tokenData.token;
        if (!token) {
          throw new Error('Authentication response did not contain an access token.');
        }
        setStoredToken(token);

        // Fetch user profile through verified GET /api/v1/auth/me
        const profileRes = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`,
          },
        });
        if (!profileRes.ok) {
          const profileErr = await profileRes.json().catch(() => ({ detail: 'Failed to retrieve profile' }));
          throw new Error(profileErr.detail || 'Failed to retrieve user profile after login');
        }
        const profileData = await profileRes.json();
        const user: Profile = {
          id: profileData.id,
          email: profileData.email,
          full_name: profileData.full_name,
          role: (profileData.role || role) as UserRole,
          phone: profileData.phone || undefined,
          avatar_url: profileData.avatar_url || '',
          is_active: profileData.is_active,
        };
        setStoredUser(user);
        return { token, user };
      }
      // Server returned an explicit error (e.g. 401 Unauthorized or 500)
      let detailMsg = 'Incorrect email or password';
      try {
        const errJson = await res.json();
        if (typeof errJson.detail === 'string') {
          detailMsg = errJson.detail;
        } else if (Array.isArray(errJson.detail) && errJson.detail[0]?.msg) {
          detailMsg = errJson.detail[0].msg;
        }
      } catch {
        if (res.status >= 500) {
          detailMsg = 'Server error (' + res.status + '). Database may be temporarily connecting.';
        } else if (res.status === 401) {
          detailMsg = 'Incorrect email or password';
        } else {
          detailMsg = 'Authentication failed (' + res.status + ')';
        }
      }
      throw new Error(detailMsg);
    } catch (err: any) {
      // If error came from the server (e.g., wrong password), rethrow it
      if (err.message && !err.message.includes('Failed to fetch') && !err.message.includes('NetworkError') && !err.message.includes('aborted') && !err.message.includes('Load failed')) {
        throw err;
      }
      if (import.meta.env.PROD) {
        throw new Error('Authentication service unavailable in production. Please check backend connectivity.');
      }
      // Only if backend server is completely offline/unreachable in local dev, allow demo fallback
      console.warn('[CSIC API] Backend offline, proceeding with local demo role.');
    }

    // Role-specific synthetic profile
    let user: Profile;
    if (role === 'admin') {
      user = { ...MOCK_ADMIN_PROFILE, email: email || MOCK_ADMIN_PROFILE.email };
    } else if (role === 'faculty') {
      user = { ...MOCK_FACULTY_PROFILE, email: email || MOCK_FACULTY_PROFILE.email };
    } else {
      user = { ...MOCK_STUDENT_PROFILE, email: email || MOCK_STUDENT_PROFILE.email };
    }

    const token = `csic-jwt-token-${role}-${Date.now()}`;
    setStoredToken(token);
    setStoredUser(user);
    return { token, user };
  },

  logout(): void {
    removeStoredToken();
    clearUserCache();
  },

  getCurrentUser(): Profile | null {
    return getStoredUser();
  },

  async validateSession(): Promise<Profile | null> {
    const token = getStoredToken();
    if (!token) {
      removeStoredToken();
      return null;
    }
    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/auth/me`, {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
      });
      if (res.ok) {
        const data = await res.json();
        const user: Profile = {
          id: data.id,
          email: data.email,
          full_name: data.full_name,
          role: (data.role || 'student') as UserRole,
          phone: data.phone || undefined,
          avatar_url: data.avatar_url || '',
          is_active: data.is_active,
        };
        setStoredUser(user);
        return user;
      }
      if (res.status === 401 || res.status === 403) {
        removeStoredToken();
        return null;
      }
      return getStoredUser();
    } catch {
      return getStoredUser();
    }
  },

  // Student portal endpoints
  async getStudentProfile(studentId?: string, cacheOptions?: CacheOptions): Promise<Profile> {
    const endpoint = studentId ? `/api/v1/students/${studentId}` : `/api/v1/students/me`;
    const data = await requestWithFallback<any>(
      endpoint,
      { method: 'GET' },
      MOCK_STUDENT_PROFILE,
      { ttlMs: DEFAULT_TTLS.profile, ...cacheOptions }
    );
    if (data && data.enrollments && Array.isArray(data.enrollments) && data.enrollments.length > 0) {
      const activeEnrollment = data.enrollments[0];
      return {
        id: data.id,
        email: data.email,
        full_name: data.full_name,
        role: data.role || 'student',
        phone: data.phone,
        avatar_url: data.avatar_url || '',
        roll_number: activeEnrollment.roll_number,
        department: data.department_name,
        program: activeEnrollment.program_name,
        semester: activeEnrollment.semester_number,
        section: activeEnrollment.section,
        is_active: true,
      };
    }
    return data;
  },

  async getAttendance(studentId?: string, cacheOptions?: CacheOptions): Promise<AttendanceSummary> {
    const endpoint = studentId ? `/api/v1/attendance/student/${studentId}` : `/api/v1/attendance/me`;
    const data = await requestWithFallback<any>(
      endpoint,
      { method: 'GET' },
      MOCK_ATTENDANCE,
      { ttlMs: DEFAULT_TTLS.attendance, ...cacheOptions }
    );

    if (!data) return data;

    let totalConducted = 0;
    let totalAttended = 0;
    let totalExcused = 0;

    const subjects = (data.subjects || []).map((s: any) => {
      const conducted = s.total_sessions ?? s.conducted_classes ?? 0;
      const attended = s.attended_sessions ?? s.attended_classes ?? 0;
      const excused = s.excused_sessions ?? s.excused_classes ?? 0;
      const pct = typeof s.attendance_percentage === 'number'
        ? s.attendance_percentage
        : typeof s.percentage === 'number'
        ? s.percentage
        : conducted > 0
        ? Math.round(((attended + excused) / conducted) * 1000) / 10
        : 0;

      const neededFor75 = Math.max(0, Math.ceil(3 * conducted - 4 * (attended + excused)));

      totalConducted += conducted;
      totalAttended += attended;
      totalExcused += excused;

      return {
        subject_id: s.subject_id || s.subject_code,
        subject_code: s.subject_code,
        subject_name: s.subject_name,
        faculty_name: s.faculty_name,
        total_sessions: conducted,
        conducted_classes: conducted,
        attended_sessions: attended,
        attended_classes: attended,
        excused_sessions: excused,
        excused_classes: excused,
        absent_sessions: s.absent_sessions ?? Math.max(0, conducted - (attended + excused)),
        attendance_percentage: pct,
        percentage: pct,
        is_low_attendance: s.is_low_attendance ?? (pct < 75.0),
        status_warning: s.is_low_attendance ?? (pct < 75.0),
        classes_needed_for_75: neededFor75,
      };
    });

    const totalPresent = totalAttended + totalExcused;
    const overallPct = typeof data.overall_percentage === 'number'
      ? data.overall_percentage
      : totalConducted > 0
      ? Math.round((totalPresent / totalConducted) * 1000) / 10
      : 0;

    const classesNeededOverall = Math.max(0, Math.ceil(3 * totalConducted - 4 * totalPresent));

    return {
      student_id: data.student_id,
      roll_number: data.roll_number,
      overall_percentage: overallPct,
      total_conducted: data.total_conducted ?? totalConducted,
      total_attended: data.total_attended ?? totalAttended,
      total_excused: data.total_excused ?? totalExcused,
      low_attendance_warning: overallPct < 75.0,
      classes_needed_to_reach_threshold: classesNeededOverall,
      subjects,
    };
  },

  async getMarks(studentId?: string, cacheOptions?: CacheOptions): Promise<Mark[]> {
    const endpoint = studentId ? `/api/v1/marks/student/${studentId}` : `/api/v1/marks/me`;
    const data = await requestWithFallback<any>(
      endpoint,
      { method: 'GET' },
      MOCK_MARKS,
      { ttlMs: DEFAULT_TTLS.marks, ...cacheOptions }
    );
    if (Array.isArray(data) && data.length > 0 && data[0].subjects) {
      return data.flatMap((exam: any) => exam.subjects || []);
    }
    return Array.isArray(data) ? data : MOCK_MARKS;
  },

  async getFeeInvoices(studentId?: string, cacheOptions?: CacheOptions): Promise<FeeInvoice[]> {
    const endpoint = studentId ? `/api/v1/fees/student/${studentId}` : `/api/v1/fees/me`;
    const data = await requestWithFallback<any>(
      endpoint,
      { method: 'GET' },
      MOCK_FEES,
      { ttlMs: DEFAULT_TTLS.fees, ...cacheOptions }
    );
    if (data && Array.isArray(data.invoices)) {
      return data.invoices.map((inv: any) => ({
        ...inv,
        paid_amount: inv.paid_amount !== undefined ? inv.paid_amount : (inv.status === 'paid' ? inv.amount : 0),
      }));
    }
    return Array.isArray(data) ? data : MOCK_FEES;
  },

  async payInvoice(invoiceId: string, amount: number, paymentMethod: string = 'upi'): Promise<FeePayment> {
    const token = getStoredToken();
    const endpoint = `/api/v1/fees/invoices/${encodeURIComponent(invoiceId)}/pay?amount=${encodeURIComponent(amount)}&payment_method=${encodeURIComponent(paymentMethod)}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
    };
    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const res = await fetch(`${API_BASE_URL}${endpoint}`, {
        method: 'POST',
        headers,
      });
      if (res.ok) {
        const paymentResult = await res.json();
        invalidateCache('/api/v1/fees');
        return paymentResult;
      }
      const err = await res.json().catch(() => ({ detail: 'Payment settlement failed' }));
      throw new Error(err.detail || 'Payment settlement failed');
    } catch (err: any) {
      if (import.meta.env.PROD || err.message?.includes('Payment settlement failed') || err.message?.includes('not found')) {
        throw err;
      }
      console.warn('[CSIC API] Backend unreachable for payment. Returning local receipt.');
      return {
        id: `pay-${Date.now()}`,
        invoice_id: invoiceId,
        transaction_reference: `TXN_UPI_${Date.now()}`,
        amount_paid: amount,
        payment_date: new Date().toISOString(),
        payment_method: paymentMethod,
        status: 'success',
      };
    }
  },

  async getTimetable(studentId?: string, cacheOptions?: CacheOptions): Promise<TimetableEntry[]> {
    const endpoint = studentId ? `/api/v1/timetable/student/${studentId}` : `/api/v1/timetable/me`;
    const data = await requestWithFallback<any>(
      endpoint,
      { method: 'GET' },
      MOCK_TIMETABLE,
      { ttlMs: DEFAULT_TTLS.timetable, ...cacheOptions }
    );
    if (Array.isArray(data) && data.length > 0 && data[0].entries) {
      return data.flatMap((day: any) => day.entries || []);
    }
    return Array.isArray(data) ? data : MOCK_TIMETABLE;
  },

  async getNotices(category?: string, cacheOptions?: CacheOptions): Promise<Notice[]> {
    const list = await requestWithFallback<Notice[]>(
      `/api/v1/notices${category ? `?category=${category}` : ''}`,
      { method: 'GET' },
      noticesList,
      { ttlMs: DEFAULT_TTLS.notices, ...cacheOptions }
    );
    if (!category || category === 'all') return list;
    return list.filter((n) => n.category === category);
  },

  // Administrative & Faculty endpoints
  async getStudentRoster(): Promise<StudentRosterItem[]> {
    const token = getStoredToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/students`, {
        method: 'GET',
        headers,
      });
      if (res.ok) {
        const data = await res.json();
        if (Array.isArray(data)) {
          return data.map((st: any) => {
            const enr = (st.enrollments && st.enrollments[0]) || {};
            return {
              id: `ros-${st.id}`,
              student_id: st.id,
              full_name: st.full_name,
              email: st.email,
              roll_number: enr.roll_number || 'N/A',
              department: st.department_name || 'Computer Science & Engineering',
              program: enr.program_name || enr.program_code || 'B.Tech CSE',
              semester: enr.semester_number || 6,
              section: enr.section || 'A',
              status: enr.status || 'active',
              attendance_percentage: 82.5,
              gpa: 8.5,
            };
          });
        }
      }
      if (import.meta.env.PROD) {
        throw new Error(`Failed to load student roster: HTTP ${res.status}`);
      }
    } catch (err) {
      if (import.meta.env.PROD) throw err;
      // fallback to local data in development
    }
    return studentsList;
  },

  async addStudent(studentData: {
    full_name: string;
    email: string;
    roll_number: string;
    program?: string;
    program_code?: string;
    semester?: number;
    section?: string;
    password?: string;
    phone?: string;
    department?: string;
  }): Promise<StudentRosterItem> {
    const token = getStoredToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const payload = {
      email: studentData.email,
      password: studentData.password || 'Student@123',
      full_name: studentData.full_name,
      phone: studentData.phone || '+91 98765 00000',
      roll_number: studentData.roll_number,
      program_code: studentData.program_code || 'BTECH-CSE',
      semester_number: studentData.semester || 1,
      section: studentData.section || 'A',
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/admin/students`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const created = await res.json();
        const enr = (created.enrollments && created.enrollments[0]) || {};
        const newRosterItem: StudentRosterItem = {
          id: `ros-${created.id}`,
          student_id: created.id,
          full_name: created.full_name,
          email: created.email,
          roll_number: enr.roll_number || studentData.roll_number,
          department: created.department_name || studentData.department || 'Computer Science & Engineering',
          program: enr.program_name || enr.program_code || studentData.program || 'B.Tech CSE',
          semester: enr.semester_number || studentData.semester || 1,
          section: enr.section || studentData.section || 'A',
          status: 'active',
          attendance_percentage: 100.0,
          gpa: 8.0,
        };
        studentsList = [newRosterItem, ...studentsList];
        return newRosterItem;
      }
      const err = await res.json().catch(() => ({ detail: 'Enrollment failed' }));
      throw new Error(err.detail || 'Enrollment failed');
    } catch (err: any) {
      if (import.meta.env.PROD || err.message?.includes('Enrollment failed')) throw err;
      console.warn('[CSIC API] Backend unreachable for student creation. Adding to local store.');
    }

    const newStudent: StudentRosterItem = {
      id: `ros-${Date.now()}`,
      student_id: `st-${Math.floor(1000 + Math.random() * 9000)}`,
      full_name: studentData.full_name || 'New Student',
      email: studentData.email || 'student@university.edu',
      roll_number: studentData.roll_number || `CS2023-${Math.floor(100 + Math.random() * 900)}`,
      department: studentData.department || 'Computer Science & Engineering',
      program: studentData.program || 'B.Tech CSE',
      semester: studentData.semester || 1,
      section: studentData.section || 'A',
      status: 'active',
      attendance_percentage: 100.0,
      gpa: 8.0,
    };
    studentsList = [newStudent, ...studentsList];
    return newStudent;
  },

  async getAttendanceWarnings(): Promise<AttendanceWarning[]> {
    return requestWithFallback<AttendanceWarning[]>(
      '/api/v1/attendance/warnings',
      { method: 'GET' },
      [
        {
          student_id: 'stu-003',
          student_name: 'Silki',
          roll_number: 'CS2023003',
          overall_percentage: 71.43,
          at_risk_subjects: ['CS401', 'CS402'],
        },
      ]
    );
  },

  async getFacultyAssignments(): Promise<FacultyCourseAssignment[]> {
    return requestWithFallback<FacultyCourseAssignment[]>(
      `/api/v1/admin/faculty-assignments`,
      { method: 'GET' },
      MOCK_FACULTY_ASSIGNMENTS
    );
  },

  async publishNotice(notice: {
    title: string;
    category: NoticeCategory;
    content: string;
    target_role?: string;
  }): Promise<Notice> {
    const token = getStoredToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    const payload = {
      title: notice.title,
      category: notice.category,
      content: notice.content,
      target_role: notice.target_role || 'all',
      is_published: true,
    };

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/notices`, {
        method: 'POST',
        headers,
        body: JSON.stringify(payload),
      });
      if (res.ok) {
        const created = await res.json();
        const publishedItem: Notice = {
          id: created.id,
          title: created.title,
          category: created.category as NoticeCategory,
          content: created.content,
          published_by_name: created.published_by_name || getStoredUser()?.full_name || 'Institutional Administration',
          published_at: created.published_at ? new Date(created.published_at).toISOString().replace('T', ' ').substring(0, 19) : new Date().toISOString().replace('T', ' ').substring(0, 19),
          target_role: (created.target_role as any) || 'all',
        };
        noticesList = [publishedItem, ...noticesList];
        return publishedItem;
      }
      const err = await res.json().catch(() => ({ detail: 'Notice publication failed' }));
      throw new Error(err.detail || 'Notice publication failed');
    } catch (err: any) {
      if (import.meta.env.PROD || err.message?.includes('Notice publication failed')) throw err;
      console.warn('[CSIC API] Backend unreachable for notice publishing. Adding to local store.');
    }

    const newNotice: Notice = {
      id: `not-${Date.now()}`,
      title: notice.title,
      category: notice.category,
      content: notice.content,
      published_at: new Date().toISOString().replace('T', ' ').substring(0, 19),
      published_by_name: getStoredUser()?.full_name || 'Academic Administrator',
      target_role: (notice.target_role as any) || 'all',
    };
    noticesList = [newNotice, ...noticesList];
    return newNotice;
  },

  async deleteNotice(noticeId: string): Promise<boolean> {
    const token = getStoredToken();
    const headers: Record<string, string> = { 'Content-Type': 'application/json' };
    if (token) headers['Authorization'] = `Bearer ${token}`;

    try {
      const res = await fetch(`${API_BASE_URL}/api/v1/notices/${encodeURIComponent(noticeId)}`, {
        method: 'DELETE',
        headers,
      });
      if (res.ok || res.status === 204) {
        noticesList = noticesList.filter((n) => n.id !== noticeId);
        return true;
      }
      const err = await res.json().catch(() => ({ detail: 'Failed to delete notice from database' }));
      throw new Error(err.detail || 'Failed to delete notice from database');
    } catch (err: any) {
      if (
        import.meta.env.PROD ||
        err.message?.includes('Failed to delete notice') ||
        err.message?.includes('not found') ||
        err.message?.includes('Forbidden')
      ) {
        throw err;
      }
      console.warn('[CSIC API] Backend unreachable for notice deletion. Removing from local store.');
      noticesList = noticesList.filter((n) => n.id !== noticeId);
      return true;
    }
  },

  // Conversational AI Assistant endpoints

  async sendChatMessage(messageText: string, sessionId?: string): Promise<ChatMessage> {
    const token = getStoredToken();
    if (!token) {
      throw new Error('Authentication required: Please log in to query the CSIC Academic Assistant.');
    }

    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/message`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: messageText, session_id: sessionId }),
      });

      if (!response.ok) {
        const errData = await response.json().catch(() => ({}));
        throw new Error(errData.detail || `Server error (${response.status}): Unable to process your query.`);
      }

      const data = await response.json();
      return {
        id: data.id || `bot-msg-${Date.now()}`,
        session_id: data.session_id,
        sender: 'bot',
        text: data.reply,
        timestamp: data.timestamp || new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }),
        query_type: data.query_type,
        sources: data.sources || [],
        verified_data: data.verified_data,
      };
    } catch (err: any) {
      if (err.message && err.message.includes('Authentication')) {
        throw err;
      }
      throw new Error(err.message || 'Unable to connect to the CSIC academic server. Please verify your connection.');
    }
  },

  async getChatSessions(): Promise<ChatSession[]> {
    const token = getStoredToken();
    if (!token) return [];
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error(`Failed to load chat sessions (${response.status})`);
    }
    return response.json();
  },

  async createChatSession(title?: string): Promise<ChatSession> {
    const token = getStoredToken();
    if (!token) {
      throw new Error('Authentication required');
    }
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify(title ? { title } : {}),
    });
    if (!response.ok) {
      throw new Error(`Failed to create chat session (${response.status})`);
    }
    return response.json();
  },

  async deleteChatSession(sessionId: string): Promise<void> {
    const token = getStoredToken();
    if (!token) return;
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}`, {
      method: 'DELETE',
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok && response.status !== 404) {
      throw new Error(`Failed to delete session (${response.status})`);
    }
  },

  async getSessionMessages(sessionId: string): Promise<ChatMessage[]> {
    const token = getStoredToken();
    if (!token) return [];
    const response = await fetch(`${API_BASE_URL}/api/v1/chat/sessions/${sessionId}/messages`, {
      headers: { Authorization: `Bearer ${token}` },
    });
    if (!response.ok) {
      throw new Error(`Failed to load session messages (${response.status})`);
    }
    const data = await response.json();
    return data.map((item: any) => ({
      id: item.id,
      session_id: item.session_id,
      sender: item.sender,
      text: item.text,
      timestamp: item.timestamp,
      query_type: item.query_type,
      sources: item.sources || [],
      verified_data: item.verified_data,
    }));
  },

  async getChatSuggestions(): Promise<string[]> {
    const token = getStoredToken();
    try {
      const response = await fetch(`${API_BASE_URL}/api/v1/chat/suggestions`, {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (response.ok) {
        const data = await response.json();
        return data.suggestions || [];
      }
    } catch {
      // fallback suggestions
    }
    return [
      'What is my attendance percentage?',
      'Show my Mid-Term exam marks',
      'Do I have any pending fee invoices?',
      'What is my timetable today?',
      'What is the attendance policy?',
      'Medical leave policy for attendance?',
      'What are the exam passing marks?',
    ];
  },

  async getChatHistory(sessionId?: string): Promise<ChatMessage[]> {
    const token = getStoredToken();
    if (!token) return [];
    try {
      const url = `${API_BASE_URL}/api/v1/chat/history${sessionId ? `?session_id=${sessionId}` : ''}`;
      const response = await fetch(url, {
        headers: { Authorization: `Bearer ${token}` },
      });
      if (response.ok) {
        const data = await response.json();
        return data.map((item: any) => ({
          id: item.id,
          session_id: item.session_id,
          sender: item.sender,
          text: item.text,
          timestamp: item.timestamp,
          query_type: item.query_type,
          sources: item.sources,
          verified_data: item.verified_data,
        }));
      }
    } catch {
      // Return empty on connection issue
    }
    return [];
  },

  async searchInformation(params?: {
    branch?: string;
    year?: number;
    category?: string;
    subject?: string;
    q?: string;
  }): Promise<SearchItem[]> {
    const token = getStoredToken();
    const query = new URLSearchParams();
    if (params?.branch) query.append('branch', params.branch);
    if (params?.year) query.append('year', params.year.toString());
    if (params?.category) query.append('category', params.category);
    if (params?.subject) query.append('subject', params.subject);
    if (params?.q) query.append('q', params.q);

    const queryString = query.toString();
    const url = `${API_BASE_URL}/api/v1/search${queryString ? `?${queryString}` : ''}`;
    const response = await fetch(url, {
      headers: {
        ...(token ? { Authorization: `Bearer ${token}` } : {}),
      },
    });
    if (!response.ok) {
      throw new Error(`Failed to fetch search results (${response.status})`);
    }
    return response.json();
  },

  // Cache & Performance Utilities
  getCachedData,
  invalidateCache,
  clearUserCache,
};
