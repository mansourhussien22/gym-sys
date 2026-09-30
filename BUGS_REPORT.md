# FitZone Pro - Comprehensive Bug Report

**Generated:** 2026-10-01 02:30:26

**Total Bugs:** 6

---

## Critical (1)

### [BUG-030/031] Names placed in '...' inside onclick - breaks on quotes
- **File:** `templates/index.html`
- **Location:** `Template literals`
- **Issue:** Names placed in '...' inside onclick - breaks on quotes
- **Fix:** Use JSON.stringify() or escape

---

## Major (4)

### [BUG-057] Sensitive data (payments, salaries) not encrypted
- **File:** `data/data.json`
- **Location:** `Full file`
- **Issue:** Sensitive data (payments, salaries) not encrypted
- **Fix:** Encrypt file or use a database

### [BUG-058] No pagination - all data returned at once
- **File:** `server.py`
- **Location:** `/api/members, /api/payments`
- **Issue:** No pagination - all data returned at once
- **Fix:** Add ?page=N&limit=M

### [BUG-033] Wipes body.innerHTML - loses event listeners
- **File:** `templates/index.html`
- **Location:** `exitApplication()`
- **Issue:** Wipes body.innerHTML - loses event listeners
- **Fix:** Use a modal overlay instead

### [BUG-016] Uses cv2.imshow - fails on headless servers
- **File:** `services/qr_manager.py`
- **Location:** `scan_from_webcam()`
- **Issue:** Uses cv2.imshow - fails on headless servers
- **Fix:** Separate desktop GUI from server code

---

## Minor (1)

### [BUG-014] No max length - 100k chars stored
- **File:** `models/person.py`
- **Location:** `name.setter`
- **Issue:** No max length - 100k chars stored
- **Fix:** Limit to 100 chars

---

