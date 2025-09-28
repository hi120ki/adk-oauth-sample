resource "google_iap_web_iam_member" "cloud_run_iap_member" {
  for_each = toset(var.iap_allowed_principals)

  provider = google-beta
  project  = var.project_id
  role     = "roles/iap.httpsResourceAccessor"
  member   = each.value

  depends_on = [google_project_service_identity.iap_identity]
}
