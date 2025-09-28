resource "google_kms_crypto_key" "tink_key" {
  name            = "tink-key"
  key_ring        = google_kms_key_ring.ring.id
  purpose         = "ENCRYPT_DECRYPT"
  rotation_period = "${var.rotation_days * 24 * 60 * 60}s"

  version_template {
    algorithm        = "GOOGLE_SYMMETRIC_ENCRYPTION"
    protection_level = "SOFTWARE"
  }

  lifecycle {
    prevent_destroy = false
  }
}
