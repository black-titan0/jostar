# Jostar

The word "جستار" (jostâr) in Farsi refers to an "essay" or "discourse."
The Jostar is a backend system designed to allow users to post and rate "Jostars".
It includes features for creating, sharing, and rating Jostars, as well as mechanisms to prevent rating manipulation and provide secure access to users.
This project is a system design exercise, so I tried to keep thing scalable and distributed.

## Table of Contents

- [Features](#features)
- [Architecture](#architecture)
- [API Documentation](#api-documentation)
- [Kafka Integration](#kafka-integration)
- [Rating Manipulation Prevention](#rating-manipulation-prevention)


## Features

- **User Authentication**: Secure access with JWT authentication.
- **Create Jostars**: Users can post new Jostars and share them.
- **Rate Jostars**: Users can rate Jostars and view aggregated ratings.
- **Share Links**: Generate shareable links for Jostars.
- **Rating Manipulation Prevention**: Detect and mitigate coordinated rating attacks.
- **Kafka Integration**: Asynchronous rating processing with Kafka.
- **Redis Integration**: Using redis to keep data consistent and easy to access.


## Architecture

The diagram below, shows an overview of the system's architecture, components and their relations.

![Design drawio (1)](https://github.com/user-attachments/assets/00314ea0-a2f8-474d-ac2a-b318ce97175b)



The architecture includes components such as:
- Django REST Framework for API endpoints.
- Kafka for asynchronous processing of ratings.
- Redis for caching and rate limiting.
- PostgreSQL for data persistence.


## API Documentation

Jostar API provides a set of endpoints for managing and interacting with Jostars. Below are detailed descriptions of each endpoint, including parameters and example usage.

### Accessing Swagger UI

You can access the interactive API documentation via Swagger UI:

- **Swagger UI**: /swagger/

### API Endpoints

#### 1. **User Signup**

- **Endpoint**: `POST /api/users/signup/`
- **Description**: Register a new user.
- **Request Body**:
  - Example:
    ```json
    {
      "username": "Rostam",
      "password": "Sohrab1234",
      "email": "rostam.dastan@gmail.com"
    }
    ```
- **Responses**:
  - `201 Created`: User successfully registered.
  - `400 Bad Request`: Invalid input data.

#### 2. **Obtain Token**

- **Endpoint**: `POST /api/users/token/`
- **Description**: Obtain a JWT token for user authentication.
- **Request Body**:
  - Example:
    ```json
    {
      "username": "Rostam",
      "password": "Sohrab1234"
    }
    ```
- **Responses**:
  - `200 OK`: Returns access and refresh tokens.
  - `401 Unauthorized`: Invalid credentials.

#### 3. **Refresh Token**

- **Endpoint**: `POST /api/users/token/refresh/`
- **Description**: Refresh JWT access token using a refresh token.
- **Request Body**:
  - Example:
    ```json
    {
      "refresh": "your_refresh_token"
    }
    ```
- **Responses**:
  - `200 OK`: Returns a new access token.
  - `401 Unauthorized`: Invalid or expired refresh token.

#### 4. **Create a Jostar**

- **Endpoint**: `POST /api/jostars/`
- **Description**: Create a new Jostar post.
- **Request Body**:
  - Example:
    ```json
    {
      "title": "تجربه تلخ سفر به مازندران با کاووس",
      "content": "مرا بیهده خواندن پیش خویش -  نه رسم کیان بد نه آیین پیش"
    }
    ```
- **Responses**:
  - `201 Created`: Jostar successfully created.
  - `400 Bad Request`: Invalid input data.

#### 5. **List Jostars**

- **Endpoint**: `GET /api/jostars/list`
- **Description**: Retrieve a paginated list of Jostars.
- **Query Parameters**:
  - `page`: (optional) The page number to retrieve.
  - - `page_size`: (optional) The size of each page.
- **Responses**:
  - `200 OK`: Returns a list of Jostars.
  - `401 Unauthorized`: Authentication required.

#### 6. **Rate a Jostar**

- **Endpoint**: `POST /api/jostars/rate`
- **Description**: Submit a rating for a Jostar.
- **Request Body**:
  - Example:
    ```json
    {
      "jostar_id": 1731,
      "rating": 4
    }
    ```
- **Query Parameters**:
  - `share_token`: (optional) Token for rating through a shared link.
- **Responses**:
  - `202 Accepted`: Rating submitted successfully.
  - `400 Bad Request`: Invalid input or already rated.

#### 7. **Share a Jostar**

- **Endpoint**: `GET /api/jostars/share/<jostar_id>`
- **Description**: Generate a shareable link for a Jostar.
- **Path Parameters**:
  - `jostar_id`: The ID of the Jostar to share.
- **Responses**:
  - `200 OK`: Returns the shareable link.
  - `404 Not Found`: Jostar not found.

#### 8. **Get Jostar by Shared Link**

- **Endpoint**: `GET /api/jostars/shared/<token>`
- **Description**: Retrieve Jostar details using a shared link token.
- **Path Parameters**:
  - `token`: The encrypted token from the shared link.
- **Responses**:
  - `200 OK`: Returns the Jostar details.
  - `400 Bad Request`: Invalid or broken link.
  - `404 Not Found`: Jostar not found.


## Kafka Integration

The Jostar system uses Apache Kafka to handle ratings processing asynchronously. This design choice helps to decouple the rating submission from its processing, ensuring that user interactions remain fast and responsive even under high load.

### Overview

- **Producer**: When a user submits a rating, a message is published to a Kafka topic.
- **Consumer**: A Kafka consumer processes these messages in bulk, updating the database with new ratings and recalculating Jostar statistics.

## Rating Manipulation Prevention

To ensure the integrity of the rating system and prevent malicious attempts to manipulate ratings, the Jostar system employs two key strategies: weighted ratings and share link tracking. These methods help maintain fairness and accuracy in the ratings.

### 1. Weighted Ratings

The system dynamically assigns weights to ratings based on the frequency of recent ratings for a specific Jostar. This approach helps mitigate the impact of sudden bursts of ratings, which might indicate a coordinated manipulation effort.

#### Methodology

- **Weight Calculation**: The weight of a rating decreases as the number of ratings in the past hour increases. This is calculated using an exponential function that reduces the weight of each additional rating.
- **Redis Caching**: The number of ratings in the past hour is stored in Redis to quickly determine the weight for each new rating.

#### Formula

The weight of a new rating is calculated as follows:

$w = \frac{1}{C \times  e^{R(N - M)}}$

where:
- $N$  is the number of ratings in the past hour.
- $R$ (RATING_WEIGHT_DOWNGRADING_FACTOR) controls how quickly the weight decreases.
- $M$ (MAX_NORMAL_RATING_COUNT_IN_ONE_HOUR) is the threshold for normal rating frequency.
- $C$ (RATING_WEIGHT_NORMALIZER_FACTOR) normalizes the weight to ensure it remains within a reasonable range.

#### Code

```python
def get_rating_weight(jostar_id):
    rating_weight_redis_key = f"jrw:{jostar_id}"
    number_of_ratings_in_past_hour = RedisProxy.get_cached_value(rating_weight_redis_key)
    
    if number_of_ratings_in_past_hour:
        n = int(number_of_ratings_in_past_hour)
        RedisProxy.increment_key(key=rating_weight_redis_key)
        
        weight = (
            (1 / (math.exp(settings.RATING_WEIGHT_DOWNGRADING_FACTOR * (n - settings.MAX_NORMAL_RATING_COUNT_IN_ONE_HOUR))))
            / settings.RATING_WEIGHT_NORMALIZER_FACTOR
        )
        return weight
    else:
        RedisProxy.cache_with_ttl(key=rating_weight_redis_key, value=1, ttl=60 * 60)
        return 1
```

### 2. Share Link Tracking

To mitigate rating manipulation through shared links, the system monitors and controls the impact of ratings submitted via these links, ensuring that a single share link cannot unduly influence the ratings of a Jostar.

#### Methodology

- **Encoded Links**: Each shareable link is encoded with information about the user who created it and the Jostar it targets. This allows tracking of how many ratings are submitted via each link.
- **Redis Tracking**: The system uses Redis to keep track of the number of ratings submitted through each share link within a specified time period (e.g., an hour).

#### Implementation Details

1. **Cache Management**: When a rating is submitted with a share token, the system checks Redis to see if there's already a count of ratings from that link.
2. **Incremental Counting**: If a count exists, it is incremented. Otherwise, a new count is initialized with a TTL (time-to-live) of one hour.
3. **Limit Enforcement**: If the number of ratings from the same share link exceeds a predefined threshold (`MAX_NORMAL_RATING_FROM_SAME_SHARE_LINK`), further ratings are ignored for averaging purposes.

#### Code

```python
def get_should_effect_average(share_token):
    if share_token:
        share_token_redis_key = f"stc:{share_token}"
        number_of_ratings_from_this_share_link = RedisProxy.get_cached_value(share_token_redis_key)
        
        if number_of_ratings_from_this_share_link:
            number_of_ratings_from_this_share_link = int(number_of_ratings_from_this_share_link)
            RedisProxy.increment_key(key=share_token_redis_key)
            
            if number_of_ratings_from_this_share_link > settings.MAX_NORMAL_RATING_FROM_SAME_SHARE_LINK:
                return False
        else:
            RedisProxy.cache_with_ttl(key=share_token_redis_key, value=1, ttl=60 * 60)
    
    return True
```

### Benefits

- **Fairness**: Ensures that the rating system remains fair and accurate by reducing the impact of coordinated attacks.
- **Prevents Abuse**: By monitoring the number of ratings from a single share link, the system can prevent attempts to manipulate ratings through social media or other channels.
- **Security**: Protects against attempts to manipulate ratings through social engineering or mass-rating campaigns.
- **Real-Time Monitoring**: Using Redis allows for quick checks and updates, ensuring that the system can respond in real-time to abnormal patterns.

These strategies enhance the robustness of the rating system by intelligently managing ratings and responding to potential manipulation in real time.
