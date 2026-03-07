import Cookies from 'js-cookie'

const ACCESS_TOKEN_KEY = 'memora_access_token'
const REFRESH_TOKEN_KEY = 'memora_refresh_token'

export function saveTokens(accessToken: string, refreshToken: string): void {
  Cookies.set(ACCESS_TOKEN_KEY, accessToken, {
    expires: 1, // 1 day
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  })
  Cookies.set(REFRESH_TOKEN_KEY, refreshToken, {
    expires: 30, // 30 days
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'strict',
  })
}

export function getAccessToken(): string | null {
  return Cookies.get(ACCESS_TOKEN_KEY) ?? null
}

export function getRefreshToken(): string | null {
  return Cookies.get(REFRESH_TOKEN_KEY) ?? null
}

export function clearTokens(): void {
  Cookies.remove(ACCESS_TOKEN_KEY)
  Cookies.remove(REFRESH_TOKEN_KEY)
}

export function isAuthenticated(): boolean {
  return Boolean(getAccessToken())
}
