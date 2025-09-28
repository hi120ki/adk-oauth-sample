resource "google_secret_manager_secret" "session_secret_key" {
  project   = var.project_id
  secret_id = "session-secret-key"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "google_client_id" {
  project   = var.project_id
  secret_id = "google-client-id"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}

resource "google_secret_manager_secret" "google_client_secret" {
  project   = var.project_id
  secret_id = "google-client-secret"

  replication {
    user_managed {
      replicas {
        location = var.region
      }
    }
  }
}
