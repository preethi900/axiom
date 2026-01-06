# User Profile & Security API
> [Priority: Critical] [Domain: Identity]

## User Story
**As a** mobile application developer
**I want** a secure API to manage user profiles
**So that** users can update their personal information and I can trust the data validity.

## Acceptance Criteria

### AC-01: Secure Profile Retrieval
**Given** a valid JWT token in the `Authorization` header
**When** a GET request is made to `/profile`
**Then** the system should return a 200 OK status
**And** the response body must contain the user's `email`, `full_name`, and `account_tier`.

### AC-02: Profile Update Validation
**Given** an authenticated user
**When** a PUT request is made to `/profile`
**Then** the system should return a 422 Unprocessable Entity status
**And** the error message should mention "Invalid email format".

### AC-03: Unauthorized Access Prevention
**Given** a request without an `Authorization` header or with an invalid token
**When** any request is made to `/profile`
**Then** the system must return a 401 Unauthorized status.

### AC-04: Non existing path access error
**Given** a valid JWT token in the `Authorization` header
**When** a GET request is made to `/non-existing-path`
**Then** the system should return a 404 status
**And** it should say page-not-found`.

## Technical Contract (JSON)

### GET /profile Response Model
```json
{
  "email": "user@example.com",
  "full_name": "John Doe",
  "account_tier": "gold"
}
```

### PUT /profile Request Model
```json
{
  "email": "new.email@example.com",
  "full_name": "New Name"
}
```
