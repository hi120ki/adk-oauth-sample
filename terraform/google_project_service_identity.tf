resource "google_project_service_identity" "iap_identity" {
  provider = google-beta
  project  = var.project_id
  service  = "iap.googleapis.com"
}
