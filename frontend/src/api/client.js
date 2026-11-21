const API_BASE_URL = "http://localhost:8000/api/v1";

export async function apiFetch(endpoint, options = {}) {
  const token = localStorage.getItem("learnsphere_token");
  
  const headers = {
    "Content-Type": "application/json",
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...options.headers,
  };

  const response = await fetch(`${API_BASE_URL}${endpoint}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    let errorDetail = "An error occurred";
    try {
      const errorData = await response.json();
      errorDetail = errorData.detail || errorData.message || JSON.stringify(errorData);
    } catch {
      errorDetail = `Request failed with status ${response.status}`;
    }
    throw new Error(errorDetail);
  }

  return response.json();
}

export const api = {
  auth: {
    login: (credentials) => apiFetch("/auth/login", { method: "POST", body: JSON.stringify(credentials) }),
    register: (userData) => apiFetch("/auth/register", { method: "POST", body: JSON.stringify(userData) }),
    demoLogin: () => apiFetch("/auth/demo-login", { method: "POST" }),
    getMe: () => apiFetch("/auth/me"),
  },
  subjects: {
    getAll: () => apiFetch("/subjects"),
    getOne: (id) => apiFetch(`/subjects/${id}`),
    createCustom: (data) => apiFetch("/subjects/custom", { method: "POST", body: JSON.stringify(data) }),
  },
  assessment: {
    start: (subjectId) => apiFetch("/assessment/start", { method: "POST", body: JSON.stringify({ subject_id: subjectId }) }),
    submit: (assessmentId, answers) => apiFetch("/assessment/submit", { 
      method: "POST", 
      body: JSON.stringify({ assessment_id: assessmentId, answers }) 
    }),
  },
  studyPlans: {
    getCurrent: (subjectId) => apiFetch(`/study-plans/current${subjectId ? `?subject_id=${subjectId}` : ""}`),
    generate: (subjectId, availableHours = 2.0, learningGoal) => apiFetch("/study-plans/generate", {
      method: "POST",
      body: JSON.stringify({ subject_id: subjectId, available_hours: availableHours, learning_goal: learningGoal })
    }),
    toggleTask: (taskId) => apiFetch(`/study-plans/tasks/${taskId}/toggle`, { method: "PATCH" }),
    approveRevision: (studyPlanId, approved) => apiFetch("/study-plans/approve-revision", {
      method: "POST",
      body: JSON.stringify({ study_plan_id: studyPlanId, approved })
    }),
  },
  tutor: {
    chat: (payload) => apiFetch("/tutor/chat", { method: "POST", body: JSON.stringify(payload) }),
    getHistory: (subjectId) => apiFetch(`/tutor/history${subjectId ? `?subject_id=${subjectId}` : ""}`),
  },
  quiz: {
    generate: (payload) => apiFetch("/quiz/generate", { method: "POST", body: JSON.stringify(payload) }),
    submit: (quizId, answers) => apiFetch("/quiz/submit", {
      method: "POST",
      body: JSON.stringify({ quiz_id: quizId, answers })
    }),
    getHistory: (subjectId) => apiFetch(`/quiz/history${subjectId ? `?subject_id=${subjectId}` : ""}`),
  },
  analytics: {
    getOverview: () => apiFetch("/analytics/overview"),
  },
  agents: {
    getActivity: (agentName) => apiFetch(`/agents/activity${agentName ? `?agent_name=${encodeURIComponent(agentName)}` : ""}`),
    getStatus: () => apiFetch("/agents/status"),
    runWorkflow: (subjectId, actionType = "diagnostic_to_plan") => apiFetch("/agents/run-workflow", {
      method: "POST",
      body: JSON.stringify({ subject_id: subjectId, action_type: actionType })
    }),
  },
  profile: {
    get: () => apiFetch("/profile"),
    updateGoal: (goalData) => apiFetch("/profile/goal", { method: "PUT", body: JSON.stringify(goalData) }),
  }
};
