output "tink_kek_uri" {
  value       = "gcp-kms://${google_kms_crypto_key.tink_key.id}"
  description = "Use this as the KEK URI in Tink"
}
