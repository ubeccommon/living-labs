# Database Schema Documentation

**Schema:** ubec_sensors
**Database:** ubec_sensors
**Generated:** 2025-10-07T05:55:32.198407
**PostgreSQL Version:** PostgreSQL 14.19 (Ubuntu 14.19-0ubuntu0.22.04.1) on x86_64-pc-linux-gnu

## Summary

- **Total Tables:** 8
- **Total Columns:** 146
- **Total Relationships:** 6
- **Total Indexes:** 28
- **Database Size:** 22 MB

## Tables

### devices

**Rows:** 1 | **Size:** 112 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| device_id | varchar(50) | ✗ | - |
| serial_number | varchar(100) | ✗ | - |
| steward_id | uuid | ✓ | - |
| api_key_hash | varchar(64) | ✗ | - |
| api_secret_hash | varchar(64) | ✗ | - |
| location | point | ✓ | - |
| sensors | ARRAY | ✓ | - |
| status | varchar(20) | ✓ | 'active'::character varying |
| registered_at | timestamp without time zone | ✓ | CURRENT_TIMESTAMP |
| last_seen | timestamp without time zone | ✓ | - |
| metadata | jsonb | ✓ | - |
| timezone | varchar(50) | ✓ | 'UTC'::character varying |
| location_name | varchar(255) | ✓ | - |
| name | varchar(255) | ✗ | - |
| user_id | integer | ✓ | - |
| description | text | ✓ | - |
| api_key | varchar(64) | ✓ | - |
| is_active | boolean | ✓ | true |
| created_at | timestamp without time zone | ✓ | CURRENT_TIMESTAMP |
| updated_at | timestamp without time zone | ✓ | CURRENT_TIMESTAMP |
| total_ubec_earned | numeric(20,7) | ✓ | 0 |
| last_distribution_at | timestamp with time zone | ✓ | - |
| distribution_count | integer | ✓ | 0 |

**Constraints:**

- `devices_pkey` (PRIMARY KEY)
- `devices_serial_number_key` (UNIQUE)
- `devices_steward_id_fkey` (FOREIGN KEY)

**Indexes:**

- `devices_pkey` (PRIMARY, UNIQUE)
- `devices_serial_number_key` (UNIQUE)
- `idx_devices_active_lastseen`
- `idx_devices_device_id`
- `idx_devices_sensors_gin`
- `idx_devices_user`

---

### environmental_metrics

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| device_id | varchar(50) | ✓ | - |
| location | point | ✗ | - |
| location_name | varchar(255) | ✓ | - |
| recorded_at | timestamp with time zone | ✗ | - |
| aqi | integer | ✓ | - |
| pm1_avg | numeric(8,2) | ✓ | - |
| pm25_avg | numeric(8,2) | ✓ | - |
| pm4_avg | numeric(8,2) | ✓ | - |
| pm10_avg | numeric(8,2) | ✓ | - |
| co2_ppm | numeric(8,2) | ✓ | - |
| voc_ppb | numeric(8,2) | ✓ | - |
| temperature_c | numeric(5,2) | ✓ | - |
| humidity_pct | numeric(5,2) | ✓ | - |
| pressure_hpa | numeric(7,2) | ✓ | - |
| illuminance_lux | numeric(10,2) | ✓ | - |
| uv_index | numeric(4,2) | ✓ | - |
| water_temp_surface | numeric(5,2) | ✓ | - |
| water_temp_5m | numeric(5,2) | ✓ | - |
| water_ph | numeric(4,2) | ✓ | - |
| water_level_cm | numeric(8,2) | ✓ | - |
| rain_rate_mmh | numeric(6,2) | ✓ | - |
| rain_accumulation_mm | numeric(8,2) | ✓ | - |
| soil_moisture_avg | numeric(5,2) | ✓ | - |
| soil_temp_avg | numeric(5,2) | ✓ | - |
| soil_ph | numeric(4,2) | ✓ | - |
| soil_npk | jsonb | ✓ | '{}'::jsonb |
| wind_speed_ms | numeric(5,2) | ✓ | - |
| wind_direction_deg | numeric(5,1) | ✓ | - |
| sound_level_db | numeric(5,1) | ✓ | - |
| leaf_wetness_pct | numeric(5,2) | ✓ | - |
| observation_count | integer | ✓ | 0 |
| data_quality_score | numeric(5,4) | ✓ | - |
| raw_data | jsonb | ✓ | '{}'::jsonb |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `environmental_metrics_aqi_check` (CHECK)
- `environmental_metrics_co2_ppm_check` (CHECK)
- `environmental_metrics_data_quality_score_check` (CHECK)
- `environmental_metrics_device_id_fkey` (FOREIGN KEY)
- `environmental_metrics_humidity_pct_check` (CHECK)
- `environmental_metrics_illuminance_lux_check` (CHECK)
- `environmental_metrics_leaf_wetness_pct_check` (CHECK)
- `environmental_metrics_pkey` (PRIMARY KEY)
- `environmental_metrics_pm10_avg_check` (CHECK)
- `environmental_metrics_pm1_avg_check` (CHECK)
- `environmental_metrics_pm25_avg_check` (CHECK)
- `environmental_metrics_pm4_avg_check` (CHECK)
- `environmental_metrics_pressure_hpa_check` (CHECK)
- `environmental_metrics_rain_accumulation_mm_check` (CHECK)
- `environmental_metrics_rain_rate_mmh_check` (CHECK)
- `environmental_metrics_soil_moisture_avg_check` (CHECK)
- `environmental_metrics_soil_ph_check` (CHECK)
- `environmental_metrics_sound_level_db_check` (CHECK)
- `environmental_metrics_temperature_c_check` (CHECK)
- `environmental_metrics_uv_index_check` (CHECK)
- `environmental_metrics_voc_ppb_check` (CHECK)
- `environmental_metrics_water_level_cm_check` (CHECK)
- `environmental_metrics_water_ph_check` (CHECK)
- `environmental_metrics_wind_direction_deg_check` (CHECK)
- `environmental_metrics_wind_speed_ms_check` (CHECK)

**Indexes:**

- `environmental_metrics_pkey` (PRIMARY, UNIQUE)
- `idx_env_metrics_device_time`
- `idx_env_metrics_location_time`
- `idx_env_metrics_recorded_at`

---

### observation_cache

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| observation_id | uuid | ✗ | - |
| ipfs_cid | varchar(100) | ✗ | - |
| stellar_tx_hash | varchar(100) | ✗ | - |
| device_id | varchar(100) | ✗ | - |
| recorded_at | timestamp without time zone | ✗ | - |
| created_at | timestamp without time zone | ✓ | now() |

**Constraints:**

- `cache_note` (CHECK)
- `observation_cache_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_obs_cache_device`
- `observation_cache_pkey` (PRIMARY, UNIQUE)

---

### reward_calculations

**Rows:** 0 | **Size:** 24 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| device_id | varchar(50) | ✓ | - |
| period_start | timestamp without time zone | ✗ | - |
| period_end | timestamp without time zone | ✗ | - |
| period_type | varchar(20) | ✗ | - |
| ubec_amount | numeric(20,7) | ✗ | - |
| quality_average | double precision | ✓ | - |
| data_points | integer | ✓ | - |
| status | varchar(20) | ✓ | 'pending'::character varying |
| transaction_hash | varchar(64) | ✓ | - |
| calculated_at | timestamp without time zone | ✓ | CURRENT_TIMESTAMP |
| paid_at | timestamp without time zone | ✓ | - |
| sensor_count | integer | ✓ | - |
| sensor_complexity_multiplier | numeric(5,2) | ✓ | 1.0 |
| sensor_types | ARRAY | ✓ | '{}'::text[] |

**Constraints:**

- `reward_calculations_device_id_fkey` (FOREIGN KEY)
- `reward_calculations_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_rewards_device_period`
- `reward_calculations_pkey` (PRIMARY, UNIQUE)

---

### sensor_readings

**Rows:** 15 | **Size:** 24 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| time | timestamp with time zone | ✗ | CURRENT_TIMESTAMP |
| device_id | varchar(50) | ✓ | - |
| air_temperature | double precision | ✓ | - |
| humidity | double precision | ✓ | - |
| pressure | double precision | ✓ | - |
| soil_moisture | double precision | ✓ | - |
| soil_temperature | double precision | ✓ | - |
| light_intensity | double precision | ✓ | - |
| uv_index | double precision | ✓ | - |
| quality_score | double precision | ✓ | - |
| warnings | ARRAY | ✓ | - |
| tz_offset_seconds | integer | ✓ | - |
| is_dst | boolean | ✓ | - |

**Constraints:**

- `sensor_readings_device_id_fkey` (FOREIGN KEY)

**Indexes:**

- `idx_sensor_readings_device_time`
- `sensor_readings_time_idx`

---

### sensor_types

**Rows:** 24 | **Size:** 64 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| sensor_code | varchar(50) | ✗ | - |
| sensor_name | varchar(255) | ✗ | - |
| category | varchar(100) | ✗ | - |
| manufacturer | varchar(100) | ✓ | - |
| unit | varchar(50) | ✓ | - |
| min_value | numeric | ✓ | - |
| max_value | numeric | ✓ | - |
| precision_digits | integer | ✓ | 2 |
| status | varchar(20) | ✓ | 'active'::character varying |
| ubec_bonus | numeric(5,2) | ✓ | 0.5 |
| metadata | jsonb | ✓ | '{}'::jsonb |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `sensor_types_pkey` (PRIMARY KEY)
- `sensor_types_status_check` (CHECK)

**Indexes:**

- `idx_sensor_types_category`
- `idx_sensor_types_status`
- `sensor_types_pkey` (PRIMARY, UNIQUE)

---

### stewards

**Rows:** 1 | **Size:** 48 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| email | varchar(255) | ✗ | - |
| stellar_address | varchar(56) | ✓ | - |
| created_at | timestamp without time zone | ✓ | CURRENT_TIMESTAMP |
| metadata | jsonb | ✓ | - |
| stewardship_began | timestamp with time zone | ✓ | now() |
| land_relationship | text | ✓ | - |
| observation_count | integer | ✓ | 0 |
| total_ubec_earned | numeric(20,7) | ✓ | 0 |
| last_observation_at | timestamp with time zone | ✓ | - |
| devices_stewarded | integer | ✓ | 0 |
| role | varchar(50) | ✓ | 'steward'::character varying |

**Constraints:**

- `farmers_email_key` (UNIQUE)
- `farmers_pkey` (PRIMARY KEY)

**Indexes:**

- `farmers_email_key` (UNIQUE)
- `farmers_pkey` (PRIMARY, UNIQUE)

---

### ubecrc_distributions

**Rows:** 3 | **Size:** 80 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| steward_id | uuid | ✓ | - |
| device_id | varchar(50) | ✓ | - |
| observation_id | uuid | ✓ | - |
| phenomenon_id | uuid | ✓ | - |
| gift_id | uuid | ✓ | - |
| ubec_amount | numeric(20,7) | ✗ | - |
| base_amount | numeric(20,7) | ✓ | 7.44 |
| bonus_amount | numeric(20,7) | ✓ | 0 |
| sensor_count | integer | ✓ | - |
| sensor_types | ARRAY | ✓ | - |
| bonus_breakdown | jsonb | ✓ | '{}'::jsonb |
| recipient_wallet | varchar(100) | ✗ | - |
| sender_wallet | varchar(56) | ✓ | - |
| transaction_hash | varchar(100) | ✓ | - |
| transaction_status | varchar(20) | ✓ | 'pending'::character varying |
| transaction_memo | text | ✓ | - |
| transaction_response | jsonb | ✓ | - |
| created_at | timestamp with time zone | ✓ | now() |
| processed_at | timestamp with time zone | ✓ | - |
| completed_at | timestamp with time zone | ✓ | - |
| failed_at | timestamp with time zone | ✓ | - |
| retry_count | integer | ✓ | 0 |
| next_retry_at | timestamp with time zone | ✓ | - |
| distribution_reason | varchar(50) | ✓ | 'observation'::character varying |
| quality_score | numeric(5,4) | ✓ | - |
| error_message | text | ✓ | - |
| metadata | jsonb | ✓ | '{}'::jsonb |

**Constraints:**

- `ubecrc_distributions_device_id_fkey` (FOREIGN KEY)
- `ubecrc_distributions_pkey` (PRIMARY KEY)
- `ubecrc_distributions_steward_id_fkey` (FOREIGN KEY)
- `ubecrc_distributions_ubec_amount_check` (CHECK)

**Indexes:**

- `idx_distributions_device`
- `idx_distributions_status`
- `idx_distributions_steward`
- `ubecrc_distributions_pkey` (PRIMARY, UNIQUE)

---

## Relationships

| From Table | Column | To Table | Column | On Delete |
|------------|--------|----------|--------|------------|
| devices | steward_id | stewards | id | NO ACTION |
| environmental_metrics | device_id | devices | device_id | NO ACTION |
| reward_calculations | device_id | devices | device_id | NO ACTION |
| sensor_readings | device_id | devices | device_id | NO ACTION |
| ubecrc_distributions | device_id | devices | device_id | NO ACTION |
| ubecrc_distributions | steward_id | stewards | id | NO ACTION |

