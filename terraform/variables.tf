variable "credentials" {
  description = "My Credentials"
  default     = "your-credentials-path"
}

variable "project" {
  description = "Project"
  default     = "zoomcamp-data-engr"
}

variable "region" {
  description = "Region"
  #Update the below to your desired region
  default     = "us-central1"
}

variable "location" {
  description = "Project Location"
  #Update the below to your desired location
  default     = "US"
}

variable "bq_dataset_name" {
  description = "My BigQuery Dataset Name"
  #Update the below to what you want your dataset to be called
  default     = "de_proj_dataset"
}

variable "gcs_bucket_name" {
  description = "My Storage Bucket Name"
  #Update the below to a unique bucket name
  default     = "de-proj-bucket"
}

variable "dataproc_name" {
  description = "My Dataproc Name"
  #Update the below to a unique bucket name
  default     = "de-proj-dataproc"
}

variable "gcs_storage_class" {
  description = "Bucket Storage Class"
  default     = "STANDARD"
}

variable "service_account" {
  description = "My Service Account"
  default     = "zoomcamp-mod-2@zoomcamp-data-engr.iam.gserviceaccount.com"
}

variable "gcp_project_id" {
  description = "My Project ID"
  default     = "zoomcamp-data-engr"
}

variable "power_plant_url" {
  description = "Powper plant data"
  default     = "https://datasets.wri.org/private-admin/dataset/53623dfd-3df6-4f15-a091-67457cdb571f/resource/66bcdacc-3d0e-46ad-9271-a5a76b1853d2/download/globalpowerplantdatabasev130.zip"
}

variable "country_code_url" {
  description = "Country code table"
  default     = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
}

#service_account = "zoomcamp-mod-2@zoomcamp-data-engr.iam.gserviceaccount.com"
#        GCP_PROJECT_ID     = "zoomcamp-data-engr"
#        GCP_GCS_BUCKET     = "de-proj-bucket"
#        BIGQUERY_DATASET   = "de_proj_dataset"
#        DATAPROC_NAME      = "de-proj-dataproc"
#        POWER_PLANT_URL    = "https://datasets.wri.org/private-admin/dataset/53623dfd-3df6-4f15-a091-67457cdb571f/resource/66bcdacc-3d0e-46ad-9271-a5a76b1853d2/download/globalpowerplantdatabasev130.zip"
#        COUNTRY_URL        = "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"