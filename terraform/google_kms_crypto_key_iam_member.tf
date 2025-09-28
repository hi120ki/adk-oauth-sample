resource "google_kms_crypto_key_iam_member" "tink_key_encrypter_decrypter" {
  crypto_key_id = google_kms_crypto_key.tink_key.id
  role          = "roles/cloudkms.cryptoKeyEncrypterDecrypter"
  member        = "serviceAccount:${google_service_account.cloud_run_sa.email}"
}
