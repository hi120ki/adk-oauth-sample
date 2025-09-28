resource "google_kms_key_ring" "ring" {
  project  = var.project_id
  name     = "key-ring"
  location = var.region
}
