terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "5.6.0"
    }
  }
}

provider "google" {
  credentials = file(var.credentials)
  project     = var.project
  region      = var.region
}

resource "google_storage_bucket" "demo-bucket" {
  name          = var.gcs_bucket_name
  location      = var.location
  force_destroy = true

  lifecycle_rule {
    condition {
      age = 1
    }
    action {
      type = "AbortIncompleteMultipartUpload"
    }
  }
}

resource "google_bigquery_dataset" "demo_dataset" {
  dataset_id = var.bq_dataset_name
  location   = var.location
}

resource "google_dataproc_cluster" "dataproc_cluster" {
  name   = var.dataproc_name
  region = var.region

  cluster_config {
    master_config {
      num_instances = 1
      machine_type  = "n4-standard-2"
      disk_config {
        boot_disk_type   = "hyperdisk-balanced"
        boot_disk_size_gb = 50   
      }
    }

    worker_config { 
      num_instances = 0               #For a small job like this we don't need workers
    }

    gce_cluster_config {
      zone = "us-central1-a"                # Adjust to a valid zone in us-central1
      network = "default"         # Uses the default VPC network
    }
    
    software_config {
      image_version = "2.2-debian12"
      override_properties = {
        "dataproc:dataproc.allow.zero.workers" = "true"
      }
    }
  }
}

#resource "google_composer_environment" "cloud_composer" {
#  name   = "de-cloud-composer"
#  region = var.region
#
#  config {
#    node_config {
#      service_account = "zoomcamp-mod-2@zoomcamp-data-engr.iam.gserviceaccount.com"
#    }
#
#    environment_size = "ENVIRONMENT_SIZE_SMALL"
#
#    software_config {
#      image_version = "composer-3-airflow-2.10.2-build.12"
#      env_variables = {
#        GCP_PROJECT_ID     = var.project
#        GCP_GCS_BUCKET     = var.gcs_bucket_name
#        BIGQUERY_DATASET   = var.bq_dataset_name
#        DATAPROC_NAME      = var.dataproc_name
#        POWER_PLANT_URL    = var.power_plant_url
#        COUNTRY_URL        = var.country_code
#      }
#    }
#  }
#}