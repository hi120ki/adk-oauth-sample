resource "google_project_iam_member" "iap_run_invoker" {
  project = var.project_id
  role    = "roles/run.invoker"
  member  = "serviceAccount:service-${var.project_number}@gcp-sa-iap.iam.gserviceaccount.com"

  depends_on = [google_project_service_identity.iap_identity]
}

resource "google_project_iam_member" "aiplatform_express_user" {
  project = var.project_id
  role    = "roles/aiplatform.expressUser"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_project_iam_member" "reasoning_engine" {
  project = var.project_id
  role    = "roles/aiplatform.reasoningEngineServiceAgent"
  member  = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
