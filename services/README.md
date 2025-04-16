# Google Cloud API Gateway Setup with Rate Limiting and Referrer Restrictions

This README documents the setup of a secure and rate-limited API Gateway on Google Cloud Platform (GCP) to proxy access to Cloud Run services. It’s written to help future me (or anyone else) understand the rationale, architecture, and steps required to replicate or extend this setup.

---

## 🚀 What This Setup Does

- Exposes multiple backend Cloud Run services via a single API Gateway endpoint.
- Enforces rate limiting at the API Gateway level to protect backend services.
- Restricts usage to a specific domain (via HTTP referer restriction).
- Requires an API key for access, allowing quota tracking and enforcement.

---

## 🧐 Why Rate Limiting?

GCP bills per request to Cloud Run. If a public-facing website or tool becomes popular (e.g. shared on Hacker News or Reddit), usage can spike, resulting in **unpredictably high charges**.

To prevent this:

- A quota is set at **100 requests per minute** across all endpoints combined.
- This totals up to 144,000 requests/day or 4.32M/month — above the free tier (2M/month) but with headroom for organic usage.

---

## 🛠️ High-Level Architecture

```
Website ➡️ [API Gateway] ➡️ [Cloud Run Services]
                    🔒
                  🔑 API Key required
                  📉 Quota enforced
                  🌍 Referer restricted
```

---

## 📌 How the Host Was Obtained

After deploying the API Gateway using:

```bash
gcloud api-gateway gateways describe GATEWAY_NAME \
  --location=REGION \
  --project=PROJECT_ID \
  --format="value(defaultHostname)"
```

You get a hostname like:

```
YOUR-GATEWAY-ID.REGION.gateway.dev
```

This is the endpoint users must call to access your backend services.

---

## 🪰 Setup Summary

### 1. Define the API in OpenAPI YAML

Your `services-api.yaml` should define:

- Paths and methods (e.g. `/generate`, `/clean`, etc.)
- `x-google-backend` with Cloud Run URLs
- `x-google-quota` to map operations to metrics
- Global `securityDefinitions` for API key usage
- Global quota under `x-google-management`

### 2. Create and Deploy API Config

```bash
gcloud api-gateway api-configs create CONFIG_ID \
  --api=API_ID \
  --openapi-spec=services-api.yaml \
  --project=PROJECT_ID
```

### 3. Create the API Gateway

```bash
gcloud api-gateway gateways create GATEWAY_NAME \
  --api=API_ID \
  --api-config=CONFIG_ID \
  --location=REGION \
  --project=PROJECT_ID
```

### 4. Enable Quotas

This happens automatically when the API config is properly linked to a **Managed Service**.

If not, you may need to:

- Recreate the API with `--managed-service=SERVICE_ID`
- Confirm quota enforcement using 429s during testing

---

## 🔑 API Key Management

### Create an API Key

```bash
gcloud alpha services api-keys create \
  --display-name="My Gateway Key" \
  --project=PROJECT_ID
```

### Restrict It to Your API

```bash
gcloud alpha services api-keys update KEY_ID \
  --api-target=service=YOUR-MANAGED-SERVICE-NAME \
  --project=PROJECT_ID
```

### Add a Referrer Restriction

Since this key is used client-side (e.g. from a browser), restrict it to your domain:

```bash
PATCH https://apikeys.googleapis.com/v2/projects/PROJECT_NUM/locations/global/keys/KEY_ID?updateMask=restrictions

{
  "restrictions": {
    "browserKeyRestrictions": {
      "allowedReferrers": [
        "https://yourdomain.com/*"
      ]
    }
  }
}
```

This ensures that even if someone copies your frontend or inspects the network tab, the key will **only work from your site**.

---

## 🔒 Access Control for Cloud Run

Each Cloud Run service **must not allow unauthenticated access** directly.

Use:

```bash
gcloud run services remove-iam-policy-binding SERVICE_NAME \
  --region=REGION \
  --platform=managed \
  --member="allUsers" \
  --role="roles/run.invoker"
```

And then grant **API Gateway’s service account** permission to invoke:

```bash
gcloud run services add-iam-policy-binding SERVICE_NAME \
  --region=REGION \
  --platform=managed \
  --member="serviceAccount:SERVICE_PROJECT_NUMBER@gcp-sa-apigateway.iam.gserviceaccount.com" \
  --role="roles/run.invoker"
```

This ensures that only traffic going through your API Gateway reaches your backend.

---

## 🧪 How to Test

- Hit the endpoint with your API key:
  ```bash
  curl -X POST "https://GATEWAY_HOST/path?key=YOUR_API_KEY"
  ```
- Try removing the key → should get `401`
- Try exceeding quota → should get `429`
- Try calling the Cloud Run backend directly → should get `403`

---

## ➕ Adding a New Service

1. Add a new `/new_path` in `services-api.yaml` with `x-google-backend`.
2. Add `x-google-quota` if it should be throttled.
3. Deploy updated config and point your gateway to it:
   ```bash
   gcloud api-gateway api-configs create ...
   gcloud api-gateway gateways update ...
   ```

---

## 📎 Summary

- All traffic goes through **API Gateway**, not directly to Cloud Run.
- **Rate limits** and **domain restrictions** protect you from abuse.
- API key is required but **only valid from your domain**.
- You can confidently extend this setup with new services in the future.

---

Stay safe. Future me, don’t forget to breathe before debugging GCP quota issues.
