# PULSEPOINT CYBER-MEDICAL INTELLIGENCE — DATA PRIVACY & GOVERNANCE

## 1. Privacy Philosophy: Minimum Necessary & Data Minimization

In alignment with **HIPAA Security & Privacy Rules** and **GDPR Principles for Special Category Health Data**, PulsePoint enforces strict data minimization protocols across all analytical tiers.

---

## 2. De-Identification & Synthetic Data Demonstrations

- **Synthetic Cohort Specification:**  
  The default demonstration dataset is generated via `data_pipeline/synthetic_generator.py` using non-identifiable parametric distributions conditioned on published Framingham, NHANES, and CDC epidemiological literature.
- **De-Identification Markers:**  
  Every demonstration record contains an explicit immutable flag (`is_synthetic = 1`) and synthetic patient identifiers (`PT-10001` through `PT-16000`). No authentic Protected Health Information (PHI) is present.
- **Tableau Public Safe Publication:**  
  Authentic patient records must **NEVER** be published to public cloud dashboards. Synthetic exports are clearly stamped for demonstration use only.

---

## 3. Small Cell Frequency Suppression (HIPAA Safe Harbor)

To prevent attribute disclosure and identity re-identification when cross-tabulating small demographic segments (e.g., age cohort x region x condition):
- Any cell count where `1 <= count < 5` is masked automatically as `<5 (Suppressed for Privacy)` using `apply_small_cell_suppression()`.
- Unmasked aggregate statistics require a minimum subgroup threshold of `N >= 5` patients.

---

## 4. Role-Based Privacy Masking in Data Exports

When exporting cohort data (`reporting/csv_exporter.py`):
1. **Clinicians & Administrators:** Receive full authorized cohort records required for clinical intervention.
2. **Researchers:** Receive pseudonymized tokens (`ANON-RES-00001`), with exact assessment dates stripped down to assessment year only.
3. **Read-Only Viewers:** Export privileges are strictly blocked.
