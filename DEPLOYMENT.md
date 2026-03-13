# Deployment Instructions

The AI Course Finder platform is now fully containerized and prepared for production deployment.

## Option 1: Render (Easiest)
1. Push your code to a GitHub repository.
2. Sign up on [Render.com](https://render.com/).
3. Click **New +** and select **Web Service**.
4. Connect your GitHub repository.
5. In the configuration:
   - **Environment:** Docker
   - **Branch:** main
   - **Start Command:** *(Handled by Dockerfile)*
6. Click **Create Web Service**. Render will automatically build the image and start the application.

## Option 2: AWS Elastic Beanstalk (For Scale)
1. Install AWS CLI and configure your credentials.
2. Install the Elastic Beanstalk (EB) CLI.
3. In your project directory, initialize an EB environment:
   ```bash
   eb init -p docker ai-course-finder
   ```
4. Create the environment and deploy:
   ```bash
   eb create course-finder-env
   ```
5. EB will build the Docker container and route traffic.

## Note on Database
In these simple deployments, the SQLite `elearning.db` will be recreated from the CSV file dynamically. However, since SQLite is local to the container, user data will not persist across container restarts. For a true production environment with persistent data, update `SQLALCHEMY_DATABASE_URI` in `app.py` to point to a managed PostgreSQL or MySQL database (like Render PostgreSQL or AWS RDS).
