export const MOCK_AUTH_USERNAME = "admin";
export const MOCK_AUTH_PASSWORD = "admin";
export const MOCK_AUTH_STORAGE_KEY = "medcomply-agent-demo-auth";

export function isMockAuthenticated(): boolean {
  if (typeof window === "undefined") {
    return false;
  }
  return window.localStorage.getItem(MOCK_AUTH_STORAGE_KEY) === "true";
}

export function signInMockUser(username: string, password: string): boolean {
  const authenticated = username === MOCK_AUTH_USERNAME && password === MOCK_AUTH_PASSWORD;
  if (authenticated) {
    window.localStorage.setItem(MOCK_AUTH_STORAGE_KEY, "true");
  }
  return authenticated;
}

export function signOutMockUser(): void {
  if (typeof window === "undefined") {
    return;
  }
  window.localStorage.removeItem(MOCK_AUTH_STORAGE_KEY);
}
