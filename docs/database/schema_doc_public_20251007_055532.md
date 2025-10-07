# Database Schema Documentation

**Schema:** public
**Database:** ubec_sensors
**Generated:** 2025-10-07T05:55:32.150002
**PostgreSQL Version:** PostgreSQL 14.19 (Ubuntu 14.19-0ubuntu0.22.04.1) on x86_64-pc-linux-gnu

## Summary

- **Total Tables:** 1
- **Total Columns:** 5
- **Total Relationships:** 0
- **Total Indexes:** 1
- **Database Size:** 22 MB

## Tables

### spatial_ref_sys

**Rows:** 8,500 | **Size:** 7280 kB

| Column | Type | Nullable | Default |
|--------|------|----------|----------|
| srid | integer | ✗ | - |
| auth_name | varchar(256) | ✓ | - |
| auth_srid | integer | ✓ | - |
| srtext | varchar(2048) | ✓ | - |
| proj4text | varchar(2048) | ✓ | - |

**Constraints:**

- `spatial_ref_sys_pkey` (PRIMARY KEY)
- `spatial_ref_sys_srid_check` (CHECK)

**Indexes:**

- `spatial_ref_sys_pkey` (PRIMARY, UNIQUE)

---

