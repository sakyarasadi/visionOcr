# GCP Deployment Guide

This guide shows how to deploy the visionOCR app to Google Cloud Platform **without** committing your service account credentials to GitHub.

## Security Overview

✅ **Safe:** Service account JSON file is in `.gitignore` - it won't be committed to GitHub  
✅ **Safe:** Credentials passed via environment variable or GCP Secret Manager  
✅ **Safe:** Dockerfile doesn't copy the JSON file

## Option 1: Deploy with Secret Manager (Recommended)

### Step 1: Store credentials in Secret Manager
```bash
# Create a secret with your service account JSON
gcloud secrets create vision-credentials \
    --data-file=sublime-lens-479204-m6-03eb13e666f6.json \
    --project=sublime-lens-479204-m6
```

### Step 2: Build and deploy
```bash
# Build and push to Google Container Registry
gcloud builds submit --tag gcr.io/sublime-lens-479204-m6/visionocr

# Deploy to Cloud Run with secret
gcloud run deploy visionocr \
  --image gcr.io/sublime-lens-479204-m6/visionocr \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --update-secrets GOOGLE_APPLICATION_CREDENTIALS_JSON=vision-credentials:latest \
  --allow-unauthenticated
```

## Option 2: Deploy with Environment Variable

### Step 1: Prepare credentials as environment variable
```bash
# Read the JSON file and encode it (one line)
export CREDS=$(cat sublime-lens-479204-m6-03eb13e666f6.json | tr -d '\n')
```

### Step 2: Build and deploy
```bash
# Build and push
gcloud builds submit --tag gcr.io/sublime-lens-479204-m6/visionocr

# Deploy with environment variable
gcloud run deploy visionocr \
  --image gcr.io/sublime-lens-479204-m6/visionocr \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --update-env-vars GOOGLE_APPLICATION_CREDENTIALS_JSON="$CREDS" \
  --allow-unauthenticated
```

## Option 3: Use Workload Identity (Most Secure)

### Step 1: Enable Workload Identity
```bash
# Grant Cloud Run service account the necessary permissions
gcloud projects add-iam-policy-binding sublime-lens-479204-m6 \
  --member="serviceAccount:cloud-vision@sublime-lens-479204-m6.iam.gserviceaccount.com" \
  --role="roles/cloudtranslate.user"

gcloud projects add-iam-policy-binding sublime-lens-479204-m6 \
  --member="serviceAccount:cloud-vision@sublime-lens-479204-m6.iam.gserviceaccount.com" \
  --role="roles/vision.imageAnnotator"
```

### Step 2: Deploy with service account
```bash
gcloud builds submit --tag gcr.io/sublime-lens-479204-m6/visionocr

gcloud run deploy visionocr \
  --image gcr.io/sublime-lens-479204-m6/visionocr \
  --platform managed \
  --region us-central1 \
  --memory 2Gi \
  --service-account=cloud-vision@sublime-lens-479204-m6.iam.gserviceaccount.com \
  --allow-unauthenticated
```

## Local Development

For local development, just keep your `sublime-lens-479204-m6-03eb13e666f6.json` file in the project directory. The app will automatically use it, and `.gitignore` will prevent it from being committed.

```bash
python app.py
```

## Testing the Deployment

```bash
# Get your Cloud Run URL
export SERVICE_URL=$(gcloud run services describe visionocr --region=us-central1 --format='value(status.url)')

# Test the endpoint
curl -X POST $SERVICE_URL/ocr \
  -F "image=@test_image.jpg"
```

## Important Notes

- ⚠️ **Never commit** `sublime-lens-479204-m6-03eb13e666f6.json` to GitHub
- ⚠️ The JSON file is in `.gitignore` to protect you
- ⚠️ If you accidentally commit it, **immediately** revoke the key in GCP Console
- ✅ For production, use Secret Manager or Workload Identity
- ✅ The app works both locally (with file) and on GCP (with env var)

