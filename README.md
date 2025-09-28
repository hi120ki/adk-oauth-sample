# adk-oauth-sample

A minimal Starlette application that fronts a Google OAuth flow and brokers access for a Vertex AI agent by ADK.

The app stores encrypted refresh tokens, exposes a small tool for fetching user profile info, and is designed to run on Cloud Run.

## Prerequisites

- Python 3.12+
- `uv` for dependency management
- Google Cloud project with KMS and Secret Manager configured for required keys (`GCP_KMS_KEY_URI`, `GSM_*`, `GOOGLE_CLOUD_*`, `APP_NAME`, `REDIRECT_URI`)

## Setup

### 1. Nodify variables

We have following variables in this project, and you need to modify them.

- `<your-project-name>`: Your Google Cloud project name.
- `<your-project-id>`: Your Google Cloud project ID.
- `<location>`: The location where you want to create the Agent Engine and use Gemini models. For example, `us-central1`.
- `<your-principal>`: The principal (user or service account) that will be allowed to access the Cloud Run service with IAP. For example, `user:test@example.com`

### 2. Initialize Google Agent Engine

Before deploying the app, you need to initialize the Google Agent Engine. The Google Agent Engine provides session management and state persistence for agents.

```bash
uv sync
cat <<EOF > .env
GOOGLE_CLOUD_PROJECT=<your-project-name>
GOOGLE_CLOUD_LOCATION=<location>
EOF
uv run script/init.py
```

After running the script, you should see a new Agent Engine created in your Google Cloud project.

`projects/<your-project-id>/locations/<location>/reasoningEngines/<agent-engine-id>`

This ID will be used in the `.env` file as `APP_NAME`.

### 3. Apply terraform in your Google Cloud project

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

After applying the terraform, you should see the following KMS key ID which will be used in the `.env` file as `GCP_KMS_KEY_URI`.

`gcp-kms://projects/<your-project-name>/locations/<location>/keyRings/key-ring/cryptoKeys/tink-key`

### 4. Setup Google Secret Manager Secrets

After applying the terraform, you should see the following Secret Manager secrets in your Google Cloud project.

- `session-secret-key`: A random string used to sign session cookies. You can generate a random string with 32 or 64 characters.
- `google-client-id`: Your Google OAuth Client ID.
- `google-client-secret`: Your Google OAuth Client Secret.

We need to move to the Google Cloud Console to create the OAuth Client ID and Secret with `Web application` type and proper redirect URIs.

### 5. Create env file

```bash
cat <<EOF > .env
GSM_GOOGLE_CLIENT_ID=google-client-id
GSM_GOOGLE_CLIENT_SECRET=google-client-secret
GSM_SESSION_SECRET_KEY_NAME=session-secret-key
GOOGLE_GENAI_USE_VERTEXAI=TRUE
GOOGLE_CLOUD_PROJECT=<your-project-name>
GOOGLE_CLOUD_LOCATION=<location>
APP_NAME=projects/<your-project-id>/locations/<location>/reasoningEngines/<agent-engine-id>
GCP_KMS_KEY_URI=gcp-kms://projects/<your-project-name>/locations/<location>/keyRings/key-ring/cryptoKeys/tink-key
IAP_AUDIENCE=/projects/<your-project-id>/locations/<location>/services/adk-oauth-sample
REDIRECT_URI=http://localhost:8000/callback
EOF
```

### 6. Fix cloudrun.yaml file

Modify `cloudrun.yaml` file to set the correct environment variables.

## Run Locally

```bash
uv run app/main.py
# or
make run
```

Visit `http://localhost:8000` and complete the Google sign-in to exercise the `/llm` endpoint.

## Deploy

```bash
make build    # build and push container image
make replace  # update the Cloud Run service defined in cloudrun.yaml
```
