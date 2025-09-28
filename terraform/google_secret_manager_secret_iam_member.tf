resource "google_secret_manager_secret_iam_member" "session_secret_key_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.session_secret_key.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "google_client_id_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_client_id.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}

resource "google_secret_manager_secret_iam_member" "google_client_secret_accessor" {
  project   = var.project_id
  secret_id = google_secret_manager_secret.google_client_secret.secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
