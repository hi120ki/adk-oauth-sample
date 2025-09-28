resource "google_service_account" "cloud_run_sa" {
  project      = var.project_id
  account_id   = "cloud-run-sa"
  display_name = "Cloud Run Service Account"
}
