# Post and Comment Management API

This is a simple API for managing posts and comments with AI moderation and automatic response features, built using FastAPI and Pydantic.

## Features

- **User Registration and Authentication**: Allows users to register and log in using JWT for secure access.
- **Post Management**: Create, update, retrieve, and delete posts.
- **Comment Management**: Create, update, retrieve, and delete comments on posts.
- **Content Moderation with AI**: Automatically checks posts and comments for profanity and offensive language after creation, blocking inappropriate content.
- **Comment Analytics**: Provides insights on the number of comments added to posts over a specified period.
  - Example endpoint: `/api/comments-daily-breakdown?date_from=2020-02-02&date_to=2022-02-15`
- **Automatic Responses**: Users can enable automatic responses to comments with a configurable delay. Responses will be relevant to the post and comment.


### System Requirements
I made some changes after recording this video - updated pydentic model for comment list to see if it is active

And moderation feature will not work for you without genai api token. I believe you know, but should have said

Loom link: [Loom](https://www.loom.com/share/2f3dfddd2420438ea3dc6dd4e76c61d7?sid=1a336d28-ac49-4778-a531-e715ab18e3f0)

Before running the Library Service Project, ensure that your system meets the following requirements:

1. **Docker and Docker Compose:**
   - Docker: [Install Docker](https://docs.docker.com/get-docker/)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/vshvanska/fastapi_app.git
   ```
   ```
   cd library-service
   ```
2. **Build and Run Docker Containers:**
- Execute the following command to build and run the Docker containers:
  ```bash
  docker-compose up --build
  ```

3. **Access the API:**
   - Open your browser and navigate to [http://localhost:8000/doc](http://localhost:8000/doc) for API documentation.

## Automated Tests

The project includes a suite of automated tests to ensure the reliability of implemented functionalities. To run the tests within the Docker environment, use the following command:
Actually the level of project test coverage - 80%

```bash
docker-compose exec app pytest
```

