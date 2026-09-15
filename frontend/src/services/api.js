const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api/v1";

export async function loginUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/users/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Login failed");
  }

  return data;
}
export async function registerUser(email, password) {
  const response = await fetch(`${API_BASE_URL}/users/`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      email,
      password,
    }),
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Registration failed");
  }

  return data;
}
export async function getCurrentUser(userId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(`${API_BASE_URL}/users/${userId}`, {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to fetch user");
  }

  return data;
}
export async function uploadDocument(file) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("You must be logged in");
  }

  const formData = new FormData();

  formData.append("file", file);

  const response = await fetch(
    `${API_BASE_URL}/documents/upload`,
    {
      method: "POST",
      headers: {
        Authorization: `Bearer ${token}`,
      },
      body: formData,
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Document upload failed");
  }

  return data;
}
export async function getMyDocuments() {
  const token = localStorage.getItem("access_token");

  if (!token) {
    throw new Error("You must be logged in");
  }

  const response = await fetch(
    `${API_BASE_URL}/documents/`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.detail || "Failed to load documents");
  }

  return data;
}
export async function getDocumentResult(documentId) {
  const token = localStorage.getItem("access_token");

  const response = await fetch(
    `${API_BASE_URL}/documents/${documentId}/result`,
    {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    }
  );

  if (!response.ok) {
    throw new Error("Failed to fetch document result");
  }

  return response.json();
}