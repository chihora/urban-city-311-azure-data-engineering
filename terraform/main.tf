terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = "=4.1.0"
    }
  }
}

# Configure Microsoft Azure.
# Subscription ID is provided through ARM_SUBSCRIPTION_ID.
provider "azurerm" {
  features {}
}

# Reference the existing Azure resource group.
data "azurerm_resource_group" "urban_city_rg" {
  name = "service_requests"
}

# Manage the existing Azure Storage account.
resource "azurerm_storage_account" "urban_city_storage" {
  name                = "urbancitystorage1"
  resource_group_name = data.azurerm_resource_group.urban_city_rg.name
  location            = "southcentralus"

  account_tier             = "Standard"
  account_replication_type = "GRS"
  account_kind             = "StorageV2"
  access_tier              = "Hot"

  min_tls_version                  = "TLS1_2"
  https_traffic_only_enabled       = true
  allow_nested_items_to_be_public  = false
  cross_tenant_replication_enabled = false
  public_network_access_enabled    = true
  shared_access_key_enabled        = true

  tags = {}
}

# Existing Bronze container.
resource "azurerm_storage_container" "bronze" {
  name                  = "bronze"
  storage_account_name  = azurerm_storage_account.urban_city_storage.name
  container_access_type = "private"
}

# Existing Silver container.
resource "azurerm_storage_container" "silver" {
  name                  = "silver"
  storage_account_name  = azurerm_storage_account.urban_city_storage.name
  container_access_type = "private"
}


# Create Azure PostgreSQL Flexible Server.
resource "azurerm_postgresql_flexible_server" "db_server" {
  name                = "urbancity311pg-fkn-2026"
  resource_group_name = data.azurerm_resource_group.urban_city_rg.name
  location            = "centralus"

  version                       = "16"
  public_network_access_enabled = true

  administrator_login    = var.username
  administrator_password = var.pg_password

  zone = "1"

  storage_mb   = 32768
  storage_tier = "P30"

  sku_name    = "GP_Standard_D4s_v3"
  create_mode = "Default"

  authentication {
    password_auth_enabled = true
  }

  lifecycle {
    prevent_destroy = true
  }
}

# Create the PostgreSQL database.
resource "azurerm_postgresql_flexible_server_database" "db_database" {
  name      = "urban_city_db"
  server_id = azurerm_postgresql_flexible_server.db_server.id

  charset   = "UTF8"
  collation = "en_US.utf8"

  # Protect the database against accidental deletion.
  lifecycle {
    prevent_destroy = true
  }
}


# ==========================================
# Azure Data Factory
# ==========================================

# Create Azure Data Factory.
resource "azurerm_data_factory" "data_factory_server" {
  name                = "urbancity311factory-fkn-2026"
  location            = data.azurerm_resource_group.urban_city_rg.location
  resource_group_name = data.azurerm_resource_group.urban_city_rg.name

  tags = {
    environment = "staging"
    project     = "urban-city-311"
  }
}

# Connect Azure Data Factory to the existing
# Azure Blob Storage account.
resource "azurerm_data_factory_linked_service_azure_blob_storage" "blobstoragels" {
  name            = "blob_storage_ls"
  data_factory_id = azurerm_data_factory.data_factory_server.id

  connection_string = azurerm_storage_account.urban_city_storage.primary_connection_string
}

# Create a Parquet dataset referencing
# the existing Silver container.
resource "azurerm_data_factory_dataset_parquet" "urbancityds" {
  name                = "urban_city_parquet_ds"
  data_factory_id     = azurerm_data_factory.data_factory_server.id
  linked_service_name = azurerm_data_factory_linked_service_azure_blob_storage.blobstoragels.name

  compression_codec = "snappy"

  azure_blob_storage_location {
    container = azurerm_storage_container.silver.name
    filename  = "urban_service_requests.parquet"
  }
}

