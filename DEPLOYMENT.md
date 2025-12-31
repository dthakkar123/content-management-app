# Deployment Guide for Railway

This guide details how to deploy the Content Management App to [Railway](https://railway.app), which supports the required PostgreSQL vector extensions.

## Prerequisites

1.  A [Railway](https://railway.app) account.
2.  Your `ANTHROPIC_API_KEY`.
3.  Changes from this repository committed to GitHub.

## Step 1: Database Setup

1.  In Railway, choose **"New Project"** > **"Provision PostgreSQL"**.
2.  Once created, click on the PostgreSQL card.
3.  Go to the **Data** tab or use the **Query** tool (using a tool like pgAdmin or the Railway CLI) to enable pgvector:
    ```sql
    CREATE EXTENSION IF NOT EXISTS vector;
    ```
    *Note: The application attempts to create this, but it's safer to ensure it's enabled if your database user lacks superuser privileges.*

## Step 2: Backend Deployment

1.  In your Railway project, click **"New"** > **"GitHub Repo"** and select this repository.
2.  Select the `backend` directory as the root if asked, or Configure it in the settings:
    -   **Root Directory**: `/backend`
3.  Go to **Variables** and add:
    -   `DATABASE_URL`: (Railway often auto-injects this as `DATABASE_URL` if linked to the Postgres service. If not, copy the `Connection URL` from your Postgres service).
    -   `ANTHROPIC_API_KEY`: `sk-ant-...` (Your key).
    -   `SECRET_KEY`: `(Generate a random string)`.
    -   `ALLOWED_ORIGINS`: `https://your-frontend-url.up.railway.app` (You will update this after deploying frontend, for now use `*` or leave blank).
    -   `DEBUG`: `False`.
    -   `UPLOAD_DIR`: `/app/uploads`.
4.  **Persistent Storage** (Crucial for generic file uploads):
    -   Go to **Settings** > **Volumes**.
    -   Add a volume. Mount path: `/app/uploads`.
    -   *Without this, uploaded PDFs will vanish when the app restarts/redeploys.*

## Step 3: Frontend Deployment

1.  Add another service to your Railway project: **"New"** > **"GitHub Repo"**.
2.  Select the same repo, but configure:
    -   **Root Directory**: `/frontend`
    -   **Build Command**: `npm install && npm run build`
    -   **Output Directory**: `dist` (or leave default if Railway auto-detects Vite).
3.  Go to **Variables**:
    -   `VITE_API_URL`: The public URL of your *Backend* service (e.g., `https://backend-production.up.railway.app/api/v1`).
4.  **Networking**:
    -   Go to **Settings** > **Networking** and "Generate Domain" to make it public.

## Step 4: Final Connection

1.  Copy the **Frontend** public domain (e.g., `frontend-web.up.railway.app`).
2.  Go back to your **Backend** service variables.
3.  Update `ALLOWED_ORIGINS` to match your frontend domain + local dev if needed:
    `https://frontend-web.up.railway.app,http://localhost:5173`
4.  Redeploy the Backend.

## Troubleshooting

-   **Database Connection**: Ensure `DATABASE_URL` is correct.
-   **Vector Extension**: If you see errors about "type vector does not exist", run `CREATE EXTENSION vector;` in your database.
-   **CORS Errors**: Check browser console. Ensure `ALLOWED_ORIGINS` on Backend EXACTLY matches the browser URL of the Frontend (no trailing slashes usually).
