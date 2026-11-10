# NCD_HDM package post-processing

The packaging pipeline leaves some objects out of the export, or fails validation on them. `postprocess.py` puts them back into the exported `metadata.json`.

```sh
python <path to>/package_postprocess/postprocess.py <path>/COMPLETE/metadata.json <path>/metadata_postprocessed.json
```

The folder is self-contained. Python 3 is the only requirement, and the script can run from any working directory. Everything it adds comes from `src/`:

| File | Content | Origin |
|---|---|---|
| `src/programStageWorkingLists.json` | The 3 working lists | Export from metadata.dev.dhis2.org/ncd-tkt, with the codes from Phase 0 |
| `src/programIndicatorGroups.json` | The 3 program indicator groups | The indicator groups and recall cleaning bundles |
| `src/rtsl_restore.json` | Program indicator `rDI98qauCo6` and all 76 RTSL program rule actions | RTSL `metadata-package/NCD_HTN_TRK_metadata-en.json` (NCD_HTN_TRK_DHIS2.40.5) |

The org unit group definition is in the script itself.

To change a working list or a group, edit its file in `src/`.

Each step only runs if it's still needed, so the script can safely run twice; a second run prints "nothing to change".

| Step | What | Source |
|---|---|---|
| 1 | Org unit group `fkAYMQA1Rjw` *HDM - Hypertension and diabetes tracker facilities*. Shipped without members, and with HDM sharing. The script stops if an exchange uses a level or a group that isn't in the file | dev instance values (in the script) |
| 2 | Program indicator groups `GoP3Y38aICc` (HTN, 20), `VvNaVAZeuKr` (DM, 23), `pzYPQKO8m4f` (recall, 4). Only program indicators that are in the package are kept as members | `src/programIndicatorGroups.json` |
| 3 | Working lists *Due today*, *High-Risk DM*, *High-Risk HTN*. Their sharing is changed from the HTN groups to the HDM groups | `src/programStageWorkingLists.json` |
| 4 | Exchange data sharing: HDM - Admin `rw------` becomes `rwrw----`, so Admin can run the exchanges (E3012 otherwise) | — |
| 5 | HTN group UIDs left in rule conditions or action data are replaced by HDM group UIDs. In this package that's rule `jlRAKblOoGW`, which used `d2:inUserGroup('olmLfefTfPQ')` | — |
| 6 | **From the RTSL source:**<ul><li>the expression of program indicator `rDI98qauCo6` (TEI header: name, sex, age);</li><li>any RTSL rule action whose rule is in the package but which is itself missing.</li></ul>`OU4RRHGolAV` ("My BP") is skipped on purpose, because rule `G3mmWXPoplk` replaces it | `src/rtsl_restore.json` |

To add more objects that the pipeline rejects:
- **A program indicator:** add its ID to `RESTORE_PIS`, and copy that program indicator from the RTSL file into the `programIndicators` list of `src/rtsl_restore.json`.
- **A rule action:** no change is needed. Neutralise or remove the action on the export instance, and the script restores it from RTSL automatically, unless its ID is in `SKIP_ACTIONS`.

## Run on `714c43d` (2026-11-10)

- Steps 1–6 applied. Step 6 restored only the `rDI98qauCo6` expression, because every other RTSL action was already in the package.
- The second run was idempotent.
- `importMode=VALIDATE` on the local 2.42.7.1 instance: status OK, 9 created, 683 updated, 0 errors.
