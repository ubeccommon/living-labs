# Database Schema Documentation

**Schema:** phenomenological
**Database:** ubec_sensors
**Generated:** 2025-10-07T05:55:32.282076
**PostgreSQL Version:** PostgreSQL 14.19 (Ubuntu 14.19-0ubuntu0.22.04.1) on x86_64-pc-linux-gnu

## Summary

- **Total Tables:** 22
- **Total Columns:** 260
- **Total Relationships:** 8
- **Total Indexes:** 87
- **Database Size:** 22 MB

## Tables

### conversations

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| participants | ARRAY | ✓ | - |
| about_phenomena | ARRAY | ✓ | - |
| understanding_quality | numeric(5,4) | ✓ | - |
| discovery_quality | numeric(5,4) | ✓ | - |
| harmony | numeric(5,4) | ✓ | - |
| collective_insights | jsonb | ✓ | '[]'::jsonb |
| questions_raised | jsonb | ✓ | '[]'::jsonb |
| began | timestamp with time zone | ✓ | now() |
| concluded | timestamp with time zone | ✓ | - |
| to_be_continued | boolean | ✓ | false |

**Constraints:**

- `chk_conv_harmony` (CHECK)
- `chk_discovery` (CHECK)
- `chk_understanding` (CHECK)
- `conversations_pkey` (PRIMARY KEY)

**Indexes:**

- `conversations_pkey` (PRIMARY, UNIQUE)

---

### description_evolution

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| phenomenon_id | uuid | ✓ | - |
| version | integer | ✗ | - |
| description | text | ✗ | - |
| integrated_observations | ARRAY | ✓ | - |
| integrated_from_version_id | uuid | ✓ | - |
| created_at | timestamp with time zone | ✓ | now() |
| created_by | uuid | ✓ | - |
| validated_by | ARRAY | ✓ | - |
| validation_status | text | ✓ | - |

**Constraints:**

- `description_evolution_integrated_from_version_id_fkey` (FOREIGN KEY)
- `description_evolution_pkey` (PRIMARY KEY)
- `description_evolution_validation_status_check` (CHECK)
- `uk_phenomenon_version` (UNIQUE)

**Indexes:**

- `description_evolution_pkey` (PRIMARY, UNIQUE)
- `idx_description_evolution_phenomenon`
- `idx_description_evolution_status`
- `uk_phenomenon_version` (UNIQUE)

---

### email_domain_whitelist

**Rows:** 2 | **Size:** 64 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer | ✗ | nextval('phenomenological.email_domai... |
| domain | varchar(255) | ✗ | - |
| organization | varchar(255) | ✗ | - |
| notes | text | ✓ | - |
| added_at | timestamp without time zone | ✗ | now() |
| added_by | varchar(255) | ✓ | - |

**Constraints:**

- `email_domain_whitelist_domain_key` (UNIQUE)
- `email_domain_whitelist_pkey` (PRIMARY KEY)

**Indexes:**

- `email_domain_whitelist_domain_key` (UNIQUE)
- `email_domain_whitelist_pkey` (PRIMARY, UNIQUE)
- `idx_whitelist_domain`

---

### exchanges

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| participant_a | uuid | ✓ | - |
| participant_b | uuid | ✓ | - |
| balance | numeric(10,4) | ✓ | - |
| flow_rate | numeric(10,4) | ✓ | - |
| energy_exchange | boolean | ✓ | false |
| information_exchange | boolean | ✓ | false |
| material_exchange | boolean | ✓ | false |
| initiated | timestamp with time zone | ✓ | now() |
| last_exchange | timestamp with time zone | ✓ | - |
| exchange_count | integer | ✓ | 0 |
| mutual_benefit | numeric(5,4) | ✓ | - |
| trust_level | numeric(5,4) | ✓ | - |

**Constraints:**

- `chk_balance` (CHECK)
- `chk_mutual_benefit` (CHECK)
- `chk_trust` (CHECK)
- `exchanges_pkey` (PRIMARY KEY)
- `uk_exchange_participants` (UNIQUE)

**Indexes:**

- `exchanges_pkey` (PRIMARY, UNIQUE)
- `uk_exchange_participants` (UNIQUE)

---

### experiments

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| question | text | ✗ | - |
| hypothesis | jsonb | ✓ | - |
| methodology | text | ✗ | - |
| investigators | ARRAY | ✓ | - |
| phenomena_studied | ARRAY | ✓ | - |
| phases | jsonb | ✓ | '[]'::jsonb |
| current_phase | text | ✓ | - |
| observations_made | ARRAY | ✓ | - |
| patterns_recognized | ARRAY | ✓ | - |
| surprises | jsonb | ✓ | '[]'::jsonb |
| methodology_insights | jsonb | ✓ | - |
| next_questions | ARRAY | ✓ | - |

**Constraints:**

- `chk_methodology` (CHECK)
- `experiments_pkey` (PRIMARY KEY)

**Indexes:**

- `experiments_pkey` (PRIMARY, UNIQUE)

---

### gestures

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| movement_quality | text | ✗ | - |
| spatial_form | USER-DEFINED | ✓ | - |
| directionality | jsonb | ✓ | - |
| tempo | numeric(10,4) | ✓ | - |
| acceleration | numeric(10,4) | ✓ | - |
| carrier_type | text | ✗ | - |
| carrier_id | uuid | ✗ | - |
| preceded_by | uuid | ✓ | - |
| followed_by | uuid | ✓ | - |
| harmonizes_with | ARRAY | ✓ | - |

**Constraints:**

- `gestures_followed_by_fkey` (FOREIGN KEY)
- `gestures_pkey` (PRIMARY KEY)
- `gestures_preceded_by_fkey` (FOREIGN KEY)

**Indexes:**

- `gestures_pkey` (PRIMARY, UNIQUE)

---

### impressions

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| observer_id | uuid | ✓ | - |
| phenomenon_id | uuid | ✓ | - |
| visual_impression | text | ✓ | - |
| auditory_impression | text | ✓ | - |
| tactile_impression | text | ✓ | - |
| olfactory_impression | text | ✓ | - |
| gustatory_impression | text | ✓ | - |
| etheric_impression | text | ✓ | - |
| astral_impression | text | ✓ | - |
| spiritual_impression | text | ✓ | - |
| synthesis | text | ✓ | - |
| metaphor | text | ✓ | - |
| vividness | numeric(5,4) | ✓ | - |
| confidence | numeric(5,4) | ✓ | - |
| received_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `chk_confidence` (CHECK)
- `chk_vividness` (CHECK)
- `impressions_pkey` (PRIMARY KEY)

**Indexes:**

- `impressions_pkey` (PRIMARY, UNIQUE)

---

### ip_whitelist

**Rows:** 0 | **Size:** 32 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer | ✗ | nextval('phenomenological.ip_whitelis... |
| ip_address | varchar(45) | ✗ | - |
| organization | varchar(255) | ✗ | - |
| notes | text | ✓ | - |
| added_at | timestamp without time zone | ✗ | now() |
| added_by | varchar(255) | ✓ | - |

**Constraints:**

- `ip_whitelist_ip_address_key` (UNIQUE)
- `ip_whitelist_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_whitelist_ip`
- `ip_whitelist_ip_address_key` (UNIQUE)
- `ip_whitelist_pkey` (PRIMARY, UNIQUE)

---

### learning_journeys

**Rows:** 0 | **Size:** 32 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| traveler_id | uuid | ✓ | - |
| guide_id | uuid | ✓ | - |
| stages | jsonb | ✓ | '[]'::jsonb |
| current_stage | integer | ✓ | 0 |
| wonder_moments | jsonb | ✓ | '[]'::jsonb |
| confusion_moments | jsonb | ✓ | '[]'::jsonb |
| clarity_moments | jsonb | ✓ | '[]'::jsonb |
| pace | text | ✓ | - |
| depth_tendency | numeric(5,4) | ✓ | - |
| breadth_tendency | numeric(5,4) | ✓ | - |
| initial_understanding | jsonb | ✓ | - |
| current_understanding | jsonb | ✓ | - |
| capacities_developed | jsonb | ✓ | '[]'::jsonb |

**Constraints:**

- `chk_breadth` (CHECK)
- `chk_depth` (CHECK)
- `chk_pace` (CHECK)
- `learning_journeys_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_journeys_guide`
- `idx_journeys_traveler`
- `learning_journeys_pkey` (PRIMARY, UNIQUE)

---

### metamorphoses

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| subject_type | varchar(50) | ✗ | - |
| subject_id | uuid | ✗ | - |
| metamorphosis_type | varchar(100) | ✗ | - |
| from_state | jsonb | ✗ | - |
| to_state | jsonb | ✗ | - |
| catalyst | jsonb | ✓ | - |
| duration | interval | ✓ | - |
| began_at | timestamp with time zone | ✗ | - |
| completed_at | timestamp with time zone | ✓ | - |
| created_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `metamorphoses_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_metamorphoses_subject`
- `idx_metamorphoses_time`
- `idx_metamorphoses_type`
- `metamorphoses_pkey` (PRIMARY, UNIQUE)

---

### observations

**Rows:** 10 | **Size:** 256 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| observer_id | uuid | ✗ | - |
| phenomenon_id | uuid | ✗ | - |
| perceived_at | timestamp with time zone | ✓ | now() |
| perception | jsonb | ✗ | - |
| imagination | jsonb | ✓ | - |
| attention_quality | numeric(5,4) | ✓ | - |
| clarity | numeric(5,4) | ✓ | - |
| conditions | jsonb | ✓ | '{}'::jsonb |
| created_at | timestamp with time zone | ✓ | now() |
| observation_id | uuid | ✓ | gen_random_uuid() |
| observer_id_text | text | ✓ | - |
| phenomenon_type | text | ✓ | 'environmental'::text |
| intensity | double precision | ✓ | 0.5 |
| location_coords | point | ✓ | - |
| ipfs_hash | text | ✓ | - |
| stellar_tx_hash | text | ✓ | - |
| metadata | jsonb | ✓ | '{}'::jsonb |

**Constraints:**

- `chk_perception_type` (CHECK)
- `observations_attention_quality_check` (CHECK)
- `observations_clarity_check` (CHECK)
- `observations_observer_id_fkey` (FOREIGN KEY)
- `observations_phenomenon_id_fkey` (FOREIGN KEY)
- `observations_pkey` (PRIMARY KEY)
- `unique_observation` (UNIQUE)

**Indexes:**

- `idx_observations_ipfs`
- `idx_observations_ipfs_hash`
- `idx_observations_observation_id`
- `idx_observations_observer`
- `idx_observations_perceived_at`
- `idx_observations_phenomenon`
- `idx_observations_quality`
- `idx_observations_stellar_tx`
- `idx_observations_time`
- `idx_observer`
- `idx_perceived_at`
- `observations_pkey` (PRIMARY, UNIQUE)
- `unique_observation` (UNIQUE)

---

### observers

**Rows:** 9 | **Size:** 88 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| observer_type | varchar(50) | ✗ | - |
| external_identity | jsonb | ✓ | '{}'::jsonb |
| essence | jsonb | ✓ | '{}'::jsonb |
| sensory_capacities | jsonb | ✓ | '{"sight": true, "smell": true, "tast... |
| presence_began | timestamp with time zone | ✓ | now() |
| presence_continues | boolean | ✓ | true |
| relationships | jsonb | ✓ | '{}'::jsonb |
| rhythms | jsonb | ✓ | '{}'::jsonb |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `chk_essence_type` (CHECK)
- `chk_external_identity_type` (CHECK)
- `chk_observer_type` (CHECK)
- `observers_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_observers_external_identity`
- `idx_observers_presence`
- `idx_observers_type`
- `observers_pkey` (PRIMARY, UNIQUE)

---

### patterns

**Rows:** 0 | **Size:** 48 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| pattern_type | varchar(100) | ✗ | - |
| pattern_name | varchar(255) | ✓ | - |
| observer_id | uuid | ✓ | - |
| phenomenon_ids | ARRAY | ✓ | - |
| observation_ids | ARRAY | ✓ | - |
| strength | numeric(5,4) | ✓ | - |
| confidence | numeric(5,4) | ✓ | - |
| signature | jsonb | ✓ | - |
| first_detected_at | timestamp with time zone | ✗ | - |
| last_seen_at | timestamp with time zone | ✗ | - |
| recurrence_interval | interval | ✓ | - |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `patterns_confidence_check` (CHECK)
- `patterns_observer_id_fkey` (FOREIGN KEY)
- `patterns_pkey` (PRIMARY KEY)
- `patterns_strength_check` (CHECK)

**Indexes:**

- `idx_patterns_detected`
- `idx_patterns_observer`
- `idx_patterns_strength`
- `idx_patterns_type`
- `patterns_pkey` (PRIMARY, UNIQUE)

---

### phenomena

**Rows:** 2 | **Size:** 128 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| moment | timestamp with time zone | ✗ | - |
| duration | interval | ✓ | - |
| location | USER-DEFINED | ✓ | - |
| gesture | jsonb | ✗ | - |
| mood | varchar(100) | ✓ | - |
| intensity | numeric(5,4) | ✓ | - |
| context_web | jsonb | ✓ | '{}'::jsonb |
| influenced_by | ARRAY | ✓ | - |
| influences | ARRAY | ✓ | - |
| resonances | ARRAY | ✓ | '{}'::text[] |
| created_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `chk_gesture_type` (CHECK)
- `phenomena_intensity_check` (CHECK)
- `phenomena_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_phenomena_gesture`
- `idx_phenomena_gesture_sensors`
- `idx_phenomena_location`
- `idx_phenomena_moment`
- `idx_phenomena_resonances`
- `phenomena_pkey` (PRIMARY, UNIQUE)

---

### processes

**Rows:** 0 | **Size:** 32 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| name | text | ✗ | - |
| gesture | text | ✓ | - |
| initiated | timestamp with time zone | ✓ | now() |
| phase | text | ✓ | 'beginning'::text |
| phase_transitions | jsonb | ✓ | '[]'::jsonb |
| catalysts | ARRAY | ✓ | - |
| participants | ARRAY | ✓ | - |
| manifestations | ARRAY | ✓ | - |
| vitality | numeric(5,4) | ✓ | - |
| harmony | numeric(5,4) | ✓ | - |
| resistance | numeric(5,4) | ✓ | - |

**Constraints:**

- `chk_harmony` (CHECK)
- `chk_phase` (CHECK)
- `chk_resistance` (CHECK)
- `chk_vitality` (CHECK)
- `processes_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_processes_phase`
- `idx_processes_vitality`
- `processes_pkey` (PRIMARY, UNIQUE)

---

### qualities

**Rows:** 0 | **Size:** 16 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| essence | text | ✗ | - |
| dimension | text | ✗ | - |
| phenomenon_id | uuid | ✓ | - |
| expression_gesture | jsonb | ✓ | - |
| expression_intensity | numeric(5,4) | ✓ | - |
| enhances | ARRAY | ✓ | - |
| diminishes | ARRAY | ✓ | - |
| transforms_into | ARRAY | ✓ | - |

**Constraints:**

- `chk_expression_intensity` (CHECK)
- `qualities_pkey` (PRIMARY KEY)

**Indexes:**

- `qualities_pkey` (PRIMARY, UNIQUE)

---

### reciprocal_exchanges

**Rows:** 0 | **Size:** 104 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| contributor_id | uuid | ✓ | - |
| exchange_type | varchar(50) | ✗ | - |
| reciprocity_score | numeric(5,4) | ✓ | - |
| relevance | numeric(5,4) | ✓ | - |
| beauty | numeric(5,4) | ✓ | - |
| received_by | ARRAY | ✓ | - |
| reciprocated_by | ARRAY | ✓ | - |
| stellar_transaction_hash | varchar(64) | ✓ | - |
| ubec_reciprocity_value | numeric(20,7) | ✓ | - |
| offered_at | timestamp with time zone | ✓ | now() |
| received_at | timestamp with time zone | ✓ | - |
| ipfs_hash | varchar(64) | ✓ | - |
| value_provided | jsonb | ✓ | '{}'::jsonb |
| value_received | jsonb | ✓ | '{}'::jsonb |
| reciprocal_balance | numeric(20,8) | ✓ | 0 |
| blockchain_verified | boolean | ✓ | false |
| ipfs_metadata | jsonb | ✓ | '{}'::jsonb |

**Constraints:**

- `chk_gift_type` (CHECK)
- `gifts_beauty_check` (CHECK)
- `gifts_generosity_check` (CHECK)
- `gifts_giver_id_fkey` (FOREIGN KEY)
- `gifts_pkey` (PRIMARY KEY)
- `gifts_relevance_check` (CHECK)

**Indexes:**

- `gifts_pkey` (PRIMARY, UNIQUE)
- `idx_exchanges_contributor`
- `idx_exchanges_offered_at`
- `idx_gifts_giver`
- `idx_gifts_recent`
- `idx_gifts_stellar`
- `idx_gifts_type`
- `idx_reciprocal_exchanges_contributor`
- `idx_reciprocal_exchanges_ipfs`
- `idx_reciprocal_exchanges_pending`
- `idx_reciprocal_exchanges_type`
- `idx_reciprocal_exchanges_verified`

---

### relationships

**Rows:** 0 | **Size:** 48 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| quality | text | ✗ | - |
| strength | numeric(5,4) | ✓ | 0.5 |
| participant_a_type | text | ✗ | - |
| participant_a_id | uuid | ✗ | - |
| participant_b_type | text | ✗ | - |
| participant_b_id | uuid | ✗ | - |
| emerged | timestamp with time zone | ✓ | now() |
| dissolved | timestamp with time zone | ✓ | - |
| rhythmic | boolean | ✓ | false |
| rhythm_pattern | jsonb | ✓ | - |
| flow_direction | text | ✓ | - |
| transformation_potential | numeric(5,4) | ✓ | - |
| mechanism | text | ✓ | - |
| confidence_in_mechanism | numeric(5,4) | ✓ | - |

**Constraints:**

- `chk_flow_direction` (CHECK)
- `chk_mechanism_confidence` (CHECK)
- `chk_strength` (CHECK)
- `chk_transformation` (CHECK)
- `relationships_mechanism_check` (CHECK)
- `relationships_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_relationships_active`
- `idx_relationships_mechanism`
- `idx_relationships_participants`
- `idx_relationships_quality`
- `relationships_pkey` (PRIMARY, UNIQUE)

---

### rhythms

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | uuid | ✗ | gen_random_uuid() |
| rhythm_type | varchar(100) | ✗ | - |
| rhythm_name | varchar(255) | ✓ | - |
| observer_id | uuid | ✓ | - |
| period | interval | ✗ | - |
| phase | numeric(5,4) | ✓ | - |
| amplitude | numeric(10,4) | ✓ | - |
| signature | jsonb | ✓ | - |
| first_observed | timestamp with time zone | ✗ | - |
| last_observed | timestamp with time zone | ✗ | - |
| next_expected | timestamp with time zone | ✓ | - |
| consistency | numeric(5,4) | ✓ | - |
| created_at | timestamp with time zone | ✓ | now() |
| updated_at | timestamp with time zone | ✓ | now() |

**Constraints:**

- `rhythms_consistency_check` (CHECK)
- `rhythms_observer_id_fkey` (FOREIGN KEY)
- `rhythms_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_rhythms_next`
- `idx_rhythms_observer`
- `idx_rhythms_type`
- `rhythms_pkey` (PRIMARY, UNIQUE)

---

### wallet_approval_queue

**Rows:** 0 | **Size:** 32 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer | ✗ | nextval('phenomenological.wallet_appr... |
| email | varchar(255) | ✗ | - |
| name | varchar(255) | ✗ | - |
| organization | varchar(255) | ✓ | - |
| ip_address | varchar(45) | ✗ | - |
| risk_score | integer | ✗ | - |
| risk_reasons | ARRAY | ✓ | - |
| status | varchar(50) | ✗ | 'pending'::character varying |
| submitted_at | timestamp without time zone | ✗ | now() |
| reviewed_at | timestamp without time zone | ✓ | - |
| reviewed_by | varchar(255) | ✓ | - |
| reviewer_notes | text | ✓ | - |

**Constraints:**

- `wallet_approval_queue_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_approval_status`
- `idx_approval_submitted`
- `wallet_approval_queue_pkey` (PRIMARY, UNIQUE)

---

### wallet_failed_attempts

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer | ✗ | nextval('phenomenological.wallet_fail... |
| email | varchar(255) | ✗ | - |
| ip_address | varchar(45) | ✗ | - |
| reason | text | ✗ | - |
| risk_score | integer | ✗ | - |
| user_agent | text | ✓ | - |
| attempted_at | timestamp without time zone | ✗ | now() |

**Constraints:**

- `wallet_failed_attempts_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_failed_email`
- `idx_failed_ip`
- `idx_failed_time`
- `wallet_failed_attempts_pkey` (PRIMARY, UNIQUE)

---

### wallet_security_log

**Rows:** 0 | **Size:** 40 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| id | integer | ✗ | nextval('phenomenological.wallet_secu... |
| email | varchar(255) | ✗ | - |
| ip_address | varchar(45) | ✗ | - |
| public_key | varchar(56) | ✗ | - |
| risk_score | integer | ✗ | - |
| user_agent | text | ✓ | - |
| created_at | timestamp without time zone | ✗ | now() |

**Constraints:**

- `wallet_security_log_pkey` (PRIMARY KEY)

**Indexes:**

- `idx_security_created`
- `idx_security_email`
- `idx_security_ip`
- `wallet_security_log_pkey` (PRIMARY, UNIQUE)

---

## Relationships

| From Table | Column | To Table | Column | On Delete |
|------------|--------|----------|--------|------------|
| description_evolution | integrated_from_version_id | description_evolution | id | NO ACTION |
| gestures | followed_by | gestures | id | NO ACTION |
| gestures | preceded_by | gestures | id | NO ACTION |
| observations | observer_id | observers | id | CASCADE |
| observations | phenomenon_id | phenomena | id | CASCADE |
| patterns | observer_id | observers | id | CASCADE |
| reciprocal_exchanges | contributor_id | observers | id | SET NULL |
| rhythms | observer_id | observers | id | CASCADE |

