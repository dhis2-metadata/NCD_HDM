---
edit_url: "https://github.com/dhis2-metadata/NCD_HDM/blob/master/docs/release_note.md"
revision_date: '2026-11-10'
tags:
- Implement
- Metadata
---

# Release Note { #ncd-hdm-release-note }

## 1.0.0 { #ncd-hdm-release-note-1-0-0 }

Initial release of the **Hypertension and Diabetes Management** (NCD_HDM) toolkit for DHIS2 2.42. The toolkit supports routine monitoring of hypertension (HTN) and diabetes mellitus (DM) in health facilities. A country can report the core indicators through monthly aggregate forms, through the HTN/DM Tracker program, or through an electronic medical record (EMR) that sends patient data to the Tracker program. All three paths produce the same indicators. The indicators follow the HEARTS360 definitions and the WHO HEARTS thresholds (blood pressure <140/90 mmHg, HbA1c <7% or fasting blood sugar <126 mg/dL). Dashboards support analysis at facility, district and national levels for:

* Patients under care, new registrations and loss to follow-up
* Blood pressure and blood sugar control among patients under care
* Assessment of diabetes complications (chronic kidney disease, diabetic foot, visual acuity) and medication coverage
* Recall of overdue patients by phone, and their return to care

The package contains:

| Component | Content |
|---|---|
| Tracker program | **Hypertension and Diabetes**, with a repeatable *Hypertension & Diabetes visit* stage and an optional *Calling report* stage. 51 program rules and 47 program indicators |
| Working lists | *Due today*, *High-Risk DM*, *High-Risk HTN* |
| Aggregate datasets | *Hypertension monthly summary*, *Diabetes monthly summary*, *HTN/DM quarterly cohorts*, *Hypertension and diabetes recall monthly summary*, *HTN/DM estimated population (annual)* |
| Validation rules | 38 rules on the hypertension and diabetes monthly summaries (16 HTN, 22 DM) |
| Aggregate data exchanges | Three exchanges that write program indicator values from the Tracker program into the aggregate datasets |
| Dashboards | *NCD_HDM - NCD control overview*, *NCD_HDM - Hypertension indicators*, *NCD_HDM - Diabetes indicators*, *NCD_HDM - Hypertension and diabetes recall* |
| User groups | *HDM - Access*, *HDM - Admin*, *HDM - Data Capture* |

The Tracker program is based on the Resolve to Save Lives (RTSL) "Hypertension & Diabetes" package and keeps its program, stage and attribute IDs. Compared with the RTSL package, this release adds:

* A complications assessment for diabetes patients
* Insulin, aspirin, beta blocker and "other diabetes medication" in the medicines list
* Range checks for blood sugar readings in mg/dL and mmol/L
* High-risk flags and valid-reading fields calculated by program rules
* Program indicators that follow the HEARTS360 patient categories exactly, use calendar-month time windows, and count FBS readings in mmol/L
* Program indicators for complications, medicines and the calling report, instead of a nightly SQL job

See the [system design guide](#ncd-hdm-design-tracker-comparison) for the full comparison.
