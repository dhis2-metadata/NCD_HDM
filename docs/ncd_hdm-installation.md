---
edit_url: "https://github.com/dhis2-metadata/NCD_HDM/blob/master/docs/ncd_hdm-installation.md"
revision_date: '2026-11-10'
tags:
- Implement
- Metadata
---

# Hypertension and Diabetes Management (HDM) Installation Guide { #ncd-hdm-installation }

This document is the installation guide for the NCD Hypertension and Diabetes Management (NCD_HDM) package.

System default language: English

## Overview { #ncd-hdm-installation-overview }

The metadata reference and metadata json files give technical details on the package version and content.

The package has one metadata file, `COMPLETE/metadata.json`, with the following components:

| Component | Content |
|---|---|
| Tracker program | **Hypertension and Diabetes** (`pMIglSEqPGS`). Two stages: *Hypertension & Diabetes visit* (repeatable) and *Calling report* (repeatable, for recall of overdue patients). 51 program rules, 47 program indicators |
| Working lists | *Due today*, *High-Risk DM*, *High-Risk HTN* (program stage working lists on the visit stage) |
| Aggregate datasets | *Hypertension monthly summary*, *Diabetes monthly summary*, *HTN/DM quarterly cohorts*, *Hypertension and diabetes recall monthly summary*, *HTN/DM estimated population (annual)* |
| Aggregate data exchanges | *ADEX - HTN DM - Current period*, *ADEX - HTN DM - Previous periods* and *ADEX - HTN DM - Calling report - Current month*. They write program indicator values from the Tracker program into the aggregate datasets |
| Organisation unit group | *HDM - Hypertension and diabetes tracker facilities* (`fkAYMQA1Rjw`, code `NCD_HDM_FACILITIES`). The facilities the exchanges collect data for. Empty after import |
| Dashboards | *NCD_HDM - NCD control overview*, *NCD_HDM - Hypertension indicators*, *NCD_HDM - Diabetes indicators*, *NCD_HDM - Hypertension and diabetes recall* |
| User groups | *HDM - Access*, *HDM - Admin*, *HDM - Data Capture* |

A country that only reports aggregate data uses the datasets and dashboards, and enters the monthly figures directly. A country running the Tracker program gets the same figures from program indicators through the aggregate data exchanges. The [system design guide](#ncd-hdm-design) describes the design.

## Installation { #ncd-hdm-installation-steps }

Installing the package has these steps:

1. [Preparing the metadata file](#ncd-hdm-preparing-the-metadata-file)
2. [Importing the metadata file into DHIS2](#ncd-hdm-importing-metadata)
3. [Configuring the imported metadata](#ncd-hdm-configuration)
4. [Setting up recall of overdue patients](#ncd-hdm-recall) (Tracker only)
5. [Adapting the program after import](#ncd-hdm-adapting-the-program)

Read through each section of this guide before you start. Some sections only apply to one type of import:

1. import into a blank DHIS2 instance
2. import into a DHIS2 instance with existing metadata

Test the steps on a test or staging instance first, and only then apply them to a production instance.

## Requirements { #ncd-hdm-installation-requirements }

- **DHIS2 version.** The package is for DHIS2 2.42. It was tested on 2.42.7.1.
- **User account.** You need an administrator account (Superuser role) on the instance.
- **Android.** The Tracker program was tested with the DHIS2 Android Capture app 3.5.0.
- **Recall scripts (optional).** The database scripts for recall of overdue patients need direct access to the DHIS2 PostgreSQL database. The Capture plugin alternative does not. See [Setting up recall of overdue patients](#ncd-hdm-recall).

Make sure the server and the DHIS2 application are well secured, and that access rights to the collected data are defined. Securing a DHIS2 system is outside the scope of this document; search "DHIS2 Security" in [DHIS2 docs](docs.dhis2.org) for latest best practices.

## Preparing the metadata file { #ncd-hdm-preparing-the-metadata-file }

Make the changes below in a plain text editor, not a word processor like Microsoft Word.

### Default category combination { #ncd-hdm-default-data-dimension }

The package uses the default category, category option, category combination and category option combination with these UIDs:

| Object | UID |
|---|---|
| Category | `GLevLNI9wkl` |
| Category option | `xYerKDKCefk` |
| Category combination | `bjDvmb4bfuf` |
| Category option combination | `HllvX50cXC0` |

Check the defaults on your instance, for example with `GET /api/categoryCombos?filter=name:eq:default&fields=id`. If your instance uses other UIDs (older instances can), replace the package UIDs with yours in `metadata.json` before importing.

### Package user and user role { #ncd-hdm-package-user }

The file contains a user `package_admin` (`vUeLeQMSwhN`) and a user role *Package User Role* (`nCNR71ZbTHK`) with no authorities. They are left over from the packaging process. You can remove both from the file before importing, or delete them after the import.

### Organisation unit group for the data exchanges { #ncd-hdm-adex-ou }

Every request in the three aggregate data exchanges collects data for the organisation unit group *HDM - Hypertension and diabetes tracker facilities* (`OU_GROUP-fkAYMQA1Rjw`). The group is part of the package but has no members after import. You don't need to change the exchanges in the file. Add the facilities after the import (see [Aggregate data exchanges](#ncd-hdm-config-adex)).

If you already have a group of Tracker facilities, you can use it instead. Replace `fkAYMQA1Rjw` in the `"ou"` of every exchange request with its UID, and remove the package group from the file.

Don't change the exchanges to a level (`LEVEL-<n>`). With a level, the exchange writes program indicator values for every facility at that level that has any Tracker data, and overwrites the monthly figures that aggregate-only facilities enter by hand, for example where a facility has some test or transferred patients. With the group, only Tracker facilities get exchange values.

## Importing metadata { #ncd-hdm-importing-metadata }

Use the [Import/Export](#import_export) app to import the metadata file. Run a "dry run" first to find any problems. If the dry run reports issues or conflicts, see [Handling import conflicts](#ncd-hdm-handling-import-conflicts). If the dry run works without errors, run the import. If the import succeeds without errors, go on to [Configuration](#ncd-hdm-configuration). Some conflicts only show up during the actual import; the import summary then lists the errors to resolve.

Import with the default settings: import strategy *New and updates*, atomic mode *All*.

On a blank DHIS2 2.42 instance the import creates about 680 objects and updates a few shared library objects that may already exist (indicator types, category options).

### Handling import conflicts { #ncd-hdm-handling-import-conflicts }

> **NOTE**
>
> If you are importing the package into a new DHIS2 instance, you will not get import conflicts, because there is no metadata in the target database. After importing the metadata, go to [Configuration](#ncd-hdm-configuration).

The most common conflict is an object in the package whose name, short name or code already exists in the target database. Objects in this package that are likely to clash with existing metadata are:

- the tracked entity type *Person* (`MCPQUTHX1Ze`)
- the indicator types *Numerator only (number)* and *Percentage*
- the `GEN -` tracked entity attributes from the Common Metadata Library (given name, family name, date of birth, sex, address, national ID)
- the category *Sex* and its options *Female* and *Male*

There are three ways to solve a conflict. Which one fits depends on the type of object.

#### Alternative 1 { #ncd-hdm-conflict-alternative-1 }

Rename the existing object in your DHIS2 database. You don't need to change the .json file, because the change is made in the DHIS2 user interface, which is less error-prone. The package is left as it is, which helps when updates to the package are released, and package objects are often referenced in training material and documentation.

#### Alternative 2 { #ncd-hdm-conflict-alternative-2 }

Rename the object in the .json file. The existing DHIS2 metadata is left as it is. This matters when training material or documentation such as SOPs or data dictionaries refer to the existing object, and users are not confused by changes to metadata they know.

For alternatives 1 and 2, the change can be as small as a prefix or suffix on the name.

#### Alternative 3 { #ncd-hdm-conflict-alternative-3 }

Change the .json file to reuse the existing metadata. For example, if a *Person* tracked entity type or a *Sex* option set already exists, remove it from the .json file and replace all references to its UID with the UID of the existing object. This avoids duplicate metadata in the database, also where there is no direct conflict. Keep in mind that:

- it requires expert knowledge of the DHIS2 metadata structure
- it does not work for all object types. Category options and category combinations are difficult because of their links to category option combinations, data values and program indicator disaggregations.
- future updates of the package become harder to apply.

## Configuration { #ncd-hdm-configuration }

After the metadata import, these steps are needed before the package works.

### Sharing { #ncd-hdm-config-sharing }

The package has three user groups, and sharing is set for all package objects:

| User group | Metadata | Data |
|---|---|---|
| HDM - Access | view | view |
| HDM - Admin | view and edit | none, except the data exchanges and the recall dataset (see below) |
| HDM - Data Capture | view | capture and view (program, stages, tracked entity type, datasets) |

The groups have no members after import. Add users to them in the **Users** app. If you use the API, add members from the group side (`POST /api/userGroups/{groupId}/users/{userId}`). The `userGroups` field of a user is ignored when a user is imported.

Data sharing that you need to check:

- **Aggregate data exchanges.** The user who runs an exchange needs *data read and write* on the exchange (`rwrw----`). Without it, previewing or running the exchange fails with `403 E3012`. Give HDM - Admin `rwrw----` on the three exchanges, or a separate group of exchange operators.
- **Target datasets.** The same user needs *data write* on the four datasets the exchanges write to. HDM - Admin has it on the recall dataset; set it on *Hypertension monthly summary*, *Diabetes monthly summary* and *HTN/DM quarterly cohorts* too.

See the [DHIS2 documentation on sharing](#sharing) for details.

### User roles { #ncd-hdm-config-user-roles }

The package does not include a usable user role. Create the roles your users need. The minimum is:

1. **Tracker data capture** (web and Android): `M_dhis-web-capture`, `M_dhis-web-dashboard`, `F_UNCOMPLETE_EVENT`. Program access comes from the HDM - Data Capture group. This role was enough for registration, visits and scheduling on Android 3.5.0.
2. **Aggregate data entry** (for aggregate-only facilities): the Data Entry app (`M_dhis-web-aggregate-data-entry`).
3. **Data analysis**: dashboards, Data Visualizer, Maps and Line Listing.
4. **Data exchange operator**: the Data Exchange app, for users who run the exchanges by hand.

See the [DHIS2 documentation](https://docs.dhis2.org/) on configuring user roles.

### Organisation unit assignment { #ncd-hdm-config-org-units }

- **Program.** Assign *Hypertension and Diabetes* to the facilities that use Tracker. It has no organisation units after import, so it isn't visible in Capture or Android until assigned.
- **Datasets.** Assign the five datasets to the facilities that report them. Aggregate-only facilities need the HTN and DM monthly summaries. Tracker facilities also need the quarterly cohorts and the recall dataset, which the exchanges fill. The estimated population dataset is used at the level where population estimates are entered.
- **Users.** Give each user their capture, data view and search organisation units. The Android app only shows a program the user can capture in.

### Aggregate data exchanges { #ncd-hdm-config-adex }

Tracker facilities get their aggregate figures from three exchanges:

| Exchange | Periods | Purpose |
|---|---|---|
| ADEX - HTN DM - Current period | this month, this quarter | HTN and DM monthly summaries and quarterly cohorts. Run daily or weekly to keep the current month up to date |
| ADEX - HTN DM - Previous periods | last 12 months, last 4 quarters | The same data, plus the recall summary, for past periods. Run monthly, or after data entry corrections |
| ADEX - HTN DM - Calling report - Current month | this month | Recall monthly summary (overdue and called patients) |

To configure them:

1. In the **Maintenance** app, add the facilities that use the Tracker program to the organisation unit group *HDM - Hypertension and diabetes tracker facilities*. While the group is empty, running an exchange fails with `E7143 Organisation unit or organisation unit level is not valid`. When a facility starts using Tracker, add it to the group; take it out if it goes back to aggregate reporting (see [Organisation unit group for the data exchanges](#ncd-hdm-adex-ou)).
2. Set the sharing described in [Sharing](#ncd-hdm-config-sharing).
3. Run analytics (see below), then run each exchange once and check the import summary.
4. Schedule the exchanges in the **Scheduler** app with an *Aggregate data exchange* job, after the nightly analytics job.

The "contactable patients overdue at the start of the month" figure reads the patients' current follow-up status. For a value close to "start of the month", schedule the calling report exchange to run early in the month.

### Analytics and dashboards { #ncd-hdm-config-analytics }

- **Analytics tables.** Run a full update after the import, not a "last years" update. Enrollment program indicators read data elements that a partial update does not add to the analytics tables, and they return no data until a full update has run. Then schedule analytics nightly.
- **Overview dashboard placeholder.** *NCD_HDM - NCD control overview* has a text item "AFTER IMPORT, INSERT HEALTH FACILITY PROFILE INDICATORS FOR NCDS HERE". Replace it with the Health Facility Profile charts if that package is installed, or delete it.
- **Maps.** The two maps (*Estimated patients with DM/HTN by district and pop*) use user orgunit x2. Change the level if your districts are at another level.
- **Population estimates.** The treatment cascade charts use the *HTN/DM estimated population (annual)* dataset. Enter the estimated adults with hypertension and diabetes each year (for example from WHO STEPS surveys).

### Android { #ncd-hdm-config-android }

No extra configuration is needed for the Android Capture app. After login the program shows its three working lists, and registration, visits, program rules and scheduling work as on the web.

- **Screenshots.** The production app blocks screenshots on data entry screens. For training material, use the *DHIS2 Capture Training* app from Google Play, which allows screenshots.
- **Settings app.** The Android Settings app can be used to adjust sync settings or limit what is downloaded to the device.

## Setting up recall of overdue patients { #ncd-hdm-recall }

> **NOTE**
>
> This section only applies to countries that use the Tracker program and the Calling report stage to call patients who missed a visit. Skip it otherwise.

A patient is overdue when a scheduled *Hypertension & Diabetes visit* is past its due date and no visit has been recorded. Recall uses three parts of the package:

- the attribute *HTN - Patient follow-up status* (`rgeuEnAI0nj`), with the values Upcoming visit, Overdue pending call and Called
- the *Calling report* stage, which is shown only when a patient is flagged overdue
- the recall dataset and the *NCD_HDM - Hypertension and diabetes recall* dashboard

DHIS2 does not set the follow-up status by itself. Program rules only run while a user has the patient open, and nothing runs when a due date passes. Without one of the two options below, no patient is flagged *Overdue pending call*: the Calling report stage never appears, and the overdue figures on the recall dashboard are 0.

| | Option A: database scripts | Option B: Capture plugin |
|---|---|---|
| How the status is set | Automatically: triggers on every change, plus a nightly job | On demand: a user clicks *Check for overdue patients* in Capture |
| Needs | Direct access to the PostgreSQL database and a cron job | App Management authority and access to the `capture` datastore namespace |
| Works on hosted instances without database access | No | Yes |
| Bulk call entry | No | Yes, a list of overdue patients with a call outcome per row |
| Android | Status is updated for all devices on the next sync | The plugin runs in web Capture only; Android users see the status after sync |

Use one of the two. Don't run both, because they write the same attribute.

### Option A: database triggers and nightly function { #ncd-hdm-recall-sql }

Install the scripts from the RTSL hypertension package ([simpledotorg/dhis2-hypertension-package](https://github.com/simpledotorg/dhis2-hypertension-package/tree/main/scripts)). They use the same program, stage and attribute UIDs as this package, and work with the `event` table of DHIS2 2.41 and later.

1. Run [`update-tracked-entity-attribute-values-trigger.sql`](https://github.com/simpledotorg/dhis2-hypertension-package/blob/main/scripts/update-tracked-entity-attribute-values-trigger.sql) on the DHIS2 database. It creates:
   - a trigger that sets *Upcoming visit* when a visit is scheduled
   - a trigger that sets *Overdue pending call* when a scheduled visit becomes overdue (as reported by the Android app)
   - a trigger that sets *Called* when a Calling report is added
   - the function `update_overdue_pending_call_trigger_function`, which flags every active enrollment whose scheduled visit is past due
2. Schedule that function every night with cron, for example `0 1 * * * psql -d dhis2 -c "select update_overdue_pending_call_trigger_function();"`.
3. Run [`update-tracked-entity-attribute-values-in-legacy-data.sql`](https://github.com/simpledotorg/dhis2-hypertension-package/blob/main/scripts/update-tracked-entity-attribute-values-in-legacy-data.sql) once, to flag patients who are already overdue.

The RTSL installation guide describes these steps in detail in [Triggers for Tracked Entity Attribute Updates](https://github.com/simpledotorg/dhis2-hypertension-package/blob/main/doc/installation_guide.md#triggers-for-tracked-entity-attribute-updates). The other RTSL scripts are not needed. This package's program indicators read the Calling report stage directly, and the aggregate data exchanges replace the `sql_agg_calculate_and_store` procedure.

The scripts write to DHIS2 tables directly. Test them again after every DHIS2 upgrade.

### Option B: Patient recall plugin for Capture { #ncd-hdm-recall-plugin }

The [Patient recall plugin](https://github.com/iambodo/patient-recall-plugin) is a Capture *Bulk Data Entry* plugin. When a user clicks **Check for overdue patients**, it:

- flags overdue patients in the user's organisation units
- clears patients who are no longer overdue
- lists the patients who have not been called yet, with their phone number and scheduled date
- lets the user record the call result for many patients at once. **Save all** creates the Calling report events and sets the status to *Called*.

The plugin is a prototype, tested on DHIS2 2.42.4. Capture supports Bulk Data Entry plugins from 2.40.9, 2.41.5, 2.42.1 and 2.43.

1. **Install the app.** Build it (`pnpm install && pnpm build`, which creates `build/bundle/patient-recall-plugin-<version>.zip`) or download a release. In **App Management**, choose *Manual install* and upload the .zip. The plugin is then served at `https://<your-instance>/api/apps/patient-recall-plugin/plugin.html`.
2. **Configure it in the datastore.** Open the **Datastore Management** app. In the namespace `capture`, create the key `bulkDataEntry` if it doesn't exist, and add this entry to its `config` array. Replace `<your-instance>` with your server URL:

    ```json
    {
      "version": 1,
      "config": [
        {
          "title": { "en": "Check for overdue patients (NCD)" },
          "configKey": "ncdOverdueCheck",
          "programId": "pMIglSEqPGS",
          "pluginSource": "https://<your-instance>/api/apps/patient-recall-plugin/plugin.html",
          "programStageId": "anb2cjLx3WM",
          "overdueAttributeId": "rgeuEnAI0nj",
          "overdueValue": "OVERDUE_PENDING_CALL",
          "clearedValue": "UPCOMING_VISIT",
          "calledValue": "CALLED",
          "givenNameAttributeId": "sB1IHYu2xQT",
          "familyNameAttributeId": "ENRjVGxVL6l",
          "phoneAttributeId": "YRDy9xy9jD0",
          "callEventStageId": "W7BCOaSquMd",
          "bulkEntryStageId": "W7BCOaSquMd",
          "resultDataElementId": "q362A7evMYt",
          "reasonDataElementId": "MZkqsWH2KSe",
          "reasonShowWhenResultCode": "REMOVE_FROM_OVERDUE"
        }
      ]
    }
    ```

    With this configuration, the plugin uses the Calling report's *HTN - Result of call* for the outcome (Agreed to visit, Remind to call later, Remove from overdue). It shows *HTN - Remove from overdue list because* only when the result is *Remove from overdue*.
3. **Check it works.** In Capture, select the program and an organisation unit. **Check for overdue patients** appears under *Bulk data entry* in the sidebar of the program overview page.

Known limitations:

- The status only changes when someone runs the check.
- The check covers all organisation units the user can capture in, not only the selected one.
- Any Calling report after the last visit hides the patient from the list, including "Remind to call later".

## Duplicated metadata { #ncd-hdm-duplicated-metadata }

> **NOTE**
>
> This section only applies if you are importing into a DHIS2 database that already has metadata. If you are working with a new DHIS2 instance, skip this section and go to [Adapting the program](#ncd-hdm-adapting-the-program). If you use third-party applications that rely on the current metadata, keep in mind that this update could break them.

Even when the import has no conflicts, the package can add duplicates of metadata that already exists: data elements, tracked entity attributes or option sets. Decisions about changing metadata must also consider the documents and resources linked to both the existing and the imported metadata. Resolving duplicates is not only about cleaning the database: it must not break integrations with other systems, training material or SOPs. This depends on the context.

DHIS2 can hide some of the complexity of duplicated metadata. For example, duplicate option sets can be hidden from groups of users with [sharing](#sharing).

## Upgrading from an earlier version { #ncd-hdm-upgrading }

An import adds and updates objects, but does not delete objects that were removed from the package. After upgrading, delete the objects that the new version no longer contains, so they don't show up as duplicates or as unused metadata in the data integrity checks.

Since the 2.42 test release of 8 November 2026, these objects were removed:

| Type | Removed | Replaced by |
|---|---|---|
| Indicators | `ZyfjMWI4LHs`, `yAEDlB6jP42`, `aS7o26RVdXZ`, `U4DRlKLmRbz`, `Kxe2dNdmHdK` (exact duplicates) | `TPgrKjNz7Mi`, `k4l2QHOvnIU`, `FNoQF19z0TP`, `HD1akWHggQM`, `SICUo17izs4` |
| Data elements | `xRDI8grTMBO`, `U5IKNG5tmY7`, `wOzeBad0fcs`, `Xkdjv0TpxBu` (not in any dataset) | |
| Validation rules | `elGj1b7TPtJ`, `mFdU8Thg6BT`, `w0Q21KNc69U` (blood sugar uncontrolled lower/upper) | |
| Category option combos | 10 duplicate COCs of *Sex*, *Sex and Age (0-18+ years)* and *Result of call* | the 10 COCs in the package |

If an instance has the duplicate category option combos, merge them into the package COCs with `POST /api/categoryOptionCombos/merge` before deleting, so no data is lost.

## Adapting the program { #ncd-hdm-adapting-the-program }

After the import you may want to adapt the program. Examples of local adaptations:

- adapting the medicine lists to the national treatment protocol
- removing the Calling report stage, the recall dataset and the recall dashboard, if facilities don't call overdue patients
- adding variables to the form
- adapting data element and option names to national conventions
- adding translations
- changing indicators to match local case definitions

Take great care if you change or remove any of the included forms or metadata. Changes can break program rules, program indicators, the aggregate data exchanges and the validation rules. Program indicators feed the aggregate data elements through the *aggregateExportDataElement* mapping and the program's category mappings (Sex, Age, Result of call). If you rename or remove one of these, check the matching data element, exchange request and category mapping.

## Removing metadata { #ncd-hdm-removing-metadata }

Remove metadata you don't need, to keep the instance clean and avoid errors. This requires advanced knowledge of DHIS2 and the dependencies between objects.

To delete the program, delete its program rules first. `DELETE /api/programs/pMIglSEqPGS` fails with "Transaction silently rolled back because it has been marked as rollback-only", because program rules point at the program stages. A single metadata delete of rules and program fails too, because the importer deletes the program before the rules. Use two metadata imports with import strategy *Delete*:

1. the program rules and program rule variables of the program (their actions are deleted with the rules)
2. the program

The program stages, sections and program indicators are deleted with the program.
