# Pizza API Documentation

Base URL: `/api/v2`

This application is a FastAPI backend for pizza ordering, reviews, authentication, and email-based account verification/reset.

## Authentication

Most protected endpoints expect a JWT access token in the `Authorization` header:

```http
Authorization: Bearer <access_token>
```

## Roles

The project uses role-based access control with these roles:

- `user`
- `Admin`
- `Staff`

## Auth Endpoints

### `POST /auth/signup`

Creates a new user account and sends a verification email.

Request body:

```json
{
  "username": "johndoe",
  "first_name": "John",
  "last_name": "Doe",
  "email": "johndoe@example.com",
  "role": "user",
  "password": "strongpassword123"
}
```

Response:

```json
{
  "message": "User created successfully please verify your email.",
  "user": {
    "uid": "uuid",
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "email": "johndoe@example.com",
    "is_verified": false,
    "role": "user",
    "created_at": "2024-06-01T12:00:00"
  }
}
```

### `GET /auth/verify/{token}`

Verifies the user email using the token sent in the signup email.

Response:

```json
{
  "message": "Email verified successfully"
}
```

### `POST /auth/login`

Authenticates a user and returns access and refresh tokens.

Request body:

```json
{
  "email": "johndoe@example.com",
  "password": "strongpassword123"
}
```

Response:

```json
{
  "access_token": "...",
  "refresh_token": "..."
}
```

Notes:

- User email must be verified before login is allowed.
- Returns `401` for wrong credentials.
- Returns `403` if email is not verified.

### `GET /auth/refresh_token`

Creates a new access token from a valid refresh token.

Response:

```json
{
  "access_token": "..."
}
```

### `GET /auth/logout`

Adds the current access token to the Redis blocklist.

Response:

```json
{
  "message": "Successfully logged out"
}
```

### `GET /auth/me`

Returns the currently authenticated user with their orders and reviews.

Response model: `UserDetailRead`

### `POST /auth/send_mail`

Sends a welcome email to one or more addresses.

Request body:

```json
{
  "addresses": ["johndoe@example.com"]
}
```

Response:

```json
{
  "message": "Email sent successfully to the provided addresses."
}
```

### `POST /auth/password_reset`

Starts the password reset flow and emails a reset link.

Request body:

```json
{
  "email": "johndoe@example.com"
}
```

Response:

```json
{
  "message": "Password reset email sent successfully."
}
```

Compatibility note:

- The same handler is also exposed as `POST /auth/password_rest` to support older clients.

### `GET /auth/reset-password?token=...`

Compatibility endpoint for reset links sent by email.

Response:

```json
{
  "message": "Token received. Submit your new password to this same route using POST."
}
```

### `POST /auth/reset-password?token=...`

Resets the password using the email token.

Request body:

```json
{
  "new_password": "newpassword123",
  "confirm_new_password": "newpassword123"
}
```

Response:

```json
{
  "message": "Password reset successfully"
}
```

### `POST /auth/password-reset-confirm/{token}`

Alternative password reset confirmation endpoint.

Request body:

```json
{
  "new_password": "newpassword123",
  "confirm_new_password": "newpassword123"
}
```

Response:

```json
{
  "message": "Password reset successfully"
}
```

## Orders Endpoints

### `GET /orders/`

Returns all orders.

Access:

- `Admin`
- `Staff`

### `POST /orders/`

Creates a new order for the current user.

Request body:

```json
{
  "quantity": 2,
  "pizza_size": "medium",
  "flavour": "pepperoni"
}
```

### `PUT /orders/{order_id}`

Updates an order.

Access:

- Owner of the order
- `Admin`

### `DELETE /orders/{order_id}`

Deletes an order.

Access:

- Owner of the order
- `Admin`

### `GET /orders/{order_uid}`

Returns one order by ID.

Access:

- `Admin`
- `Staff`

### `GET /orders/user/{user_id}`

Returns all orders for a specific user.

Access:

- The user themselves or `Admin`

## Reviews Endpoints

### `GET /reviews/`

Returns all reviews.

### `POST /reviews/{orders_id}`

Creates a review for an order owned by the current user.

Request body:

```json
{
  "comment": "Great pizza and fast delivery!",
  "rating": 5
}
```

### `GET /reviews/{review_uid}`

Returns one review by ID.

Access:

- Authenticated users

### `DELETE /reviews/{review_uid}`

Deletes a review.

Access:

- Owner of the review

### `GET /reviews/user/{user_uid}`

Returns all reviews written by a user.

Access:

- The user themselves or `Admin`

## Common Status Codes

- `200` OK
- `400` Bad Request
- `401` Unauthorized
- `403` Forbidden
- `404` Not Found

## Admin Endpoints

All admin endpoints require:

- Valid access token
- Role: `Admin`

### `GET /admin/dashboard`

Returns platform summary metrics.

Response:

```json
{
  "users_count": 120,
  "verified_users_count": 95,
  "admins_count": 2,
  "staff_count": 6,
  "orders_count": 430,
  "reviews_count": 287
}
```

### `GET /admin/users`

Returns all users ordered by newest first.

### `GET /admin/users/{user_id}`

Returns a single user record.

### `PATCH /admin/users/{user_id}/role`

Updates a user's role.

Request body:

```json
{
  "role": "Staff"
}
```

Allowed roles:

- `user`
- `Admin`
- `Staff`

### `PATCH /admin/users/{user_id}/verify`

Sets user verification status.

Request body:

```json
{
  "is_verified": true
}
```

## Implementation Notes

- Email verification tokens are time-limited.
- Password reset tokens are also time-limited.
- Celery is used to send emails asynchronously.
- The API is mounted under version `v2`.
- On Windows, Celery is configured to use the `solo` worker pool.

## Quick Examples

### Signup flow

1. `POST /api/v2/auth/signup`
2. Receive a verification email
3. Click the verification link
4. Log in with `POST /api/v2/auth/login`

### Password reset flow

1. `POST /api/v2/auth/password_reset`
2. Receive password reset email
3. Open reset link
4. Submit `new_password` and `confirm_new_password`
5. Password is updated
