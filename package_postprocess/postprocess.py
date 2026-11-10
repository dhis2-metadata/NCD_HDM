"""Post-process the exported NCD_HDM package: add what the packaging pipeline leaves out or neutralises.

  python postprocess.py <package metadata.json> [<output.json>]     (default output: metadata_postprocessed.json)

Adds / fixes, each only if still needed (safe to run twice):
  1. Organisation unit group fkAYMQA1Rjw (HDM - Hypertension and diabetes tracker facilities), no members.
     The 3 aggregate data exchanges collect data for OU_GROUP-fkAYMQA1Rjw.
  2. Program indicator groups GoP3Y38aICc (HTN), VvNaVAZeuKr (DM), pzYPQKO8m4f (recall), members limited
     to program indicators that are in the package.
  3. Program stage working lists Due today, High-Risk DM, High-Risk HTN, sharing remapped to the HDM groups.
  4. Aggregate data exchanges: HDM - Admin gets data read/write (rwrw----), needed to run them (E3012).
  5. Leftover HTN group UIDs in program rule conditions / action data -> HDM groups
     (rule jlRAKblOoGW used d2:inUserGroup('olmLfefTfPQ'), the dev-only HTN Admin group).
  6. From the RTSL source package: the expression of program indicator rDI98qauCo6 (TEI header), and any RTSL
     program rule action whose rule is in the package but the action is not (except SKIP_ACTIONS).
     These fail the pipeline's validation, so they are neutralised on the export instance and put back here.
"""
import json
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parent / "src"     # everything the script needs ships in src/
WL_FILE = SRC / "programStageWorkingLists.json"    # from metadata.dev.dhis2.org/ncd-tkt (codes added in Phase 0)
PIG_FILES = [SRC / "programIndicatorGroups.json"]  # from the indicator_groups and recall cleaning bundles
RTSL_FILE = SRC / "rtsl_restore.json"              # RTSL NCD_HTN_TRK_metadata-en.json: PI rDI98qauCo6 + all rule actions

HDM_ADMIN, HDM_ACCESS, HDM_CAPTURE = "YC7GXhPDxy5", "wMfsgxzN9nt", "olcsnfUYf3r"
GROUP_MAP = {"no2QanpZgiI": HDM_ACCESS, "olmLfefTfPQ": HDM_ADMIN, "qSSuhs65xMP": HDM_CAPTURE}  # dev HTN -> HDM
GROUP_NAMES = {HDM_ADMIN: "HDM - Admin", HDM_ACCESS: "HDM - Access", HDM_CAPTURE: "HDM - Data Capture"}


def sharing(admin="rw------", access="r-------", capture="r-------", public="r-------"):
    return {"external": False, "users": {}, "public": public,
            "userGroups": {g: {"id": g, "displayName": GROUP_NAMES[g], "access": a}
                           for g, a in ((HDM_ADMIN, admin), (HDM_ACCESS, access), (HDM_CAPTURE, capture))}}


# 1. As on metadata.dev.dhis2.org/ncd-tkt, 2026-11-10 (sharing set to the package's HDM groups)
OU_GROUP = {"id": "fkAYMQA1Rjw", "code": "NCD_HDM_FACILITIES",
            "name": "HDM - Hypertension and diabetes tracker facilities",
            "shortName": "Hypertension_diabetes_facilities",
            "description": "Facilities that use the Hypertension and Diabetes Tracker program. The aggregate data "
                           "exchanges collect data for this group. Add the Tracker facilities after import.",
            "organisationUnits": [], "sharing": sharing()}
PI_GROUPS = ["GoP3Y38aICc", "VvNaVAZeuKr", "pzYPQKO8m4f"]
RESTORE_PIS = ["rDI98qauCo6"]
PI_DESCRIPTIONS = {"rDI98qauCo6": "Patient header in the program indicator widget: name, sex and age."}
SKIP_ACTIONS = {"OU4RRHGolAV"}   # RTSL "My BP" action, removed on purpose (replaced by rule G3mmWXPoplk)
WL_KEEP = {"id", "code", "name", "description", "program", "programStage", "programStageQueryCriteria",
           "translations", "attributeValues"}
SERVER_FIELDS = {"lastUpdated", "created", "lastUpdatedBy", "createdBy", "href", "access", "displayName"}

log = []


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def ids(objs):
    return {o["id"] for o in objs}


def main(src, out):
    pkg = load(src)
    pi_ids = ids(pkg["programIndicators"])

    # 1. org unit group
    grps = pkg.setdefault("organisationUnitGroups", [])
    if OU_GROUP["id"] not in ids(grps):
        grps.append(OU_GROUP)
        log.append(f"1 added organisation unit group {OU_GROUP['id']} {OU_GROUP['name']}")
    for a in pkg.get("aggregateDataExchanges", []):
        for r in a["source"]["requests"]:
            for ou in r["ou"]:
                assert not ou.startswith("LEVEL-"), f"exchange {a['id']} uses a level: {ou}"
                assert not ou.startswith("OU_GROUP-") or ou[9:] in ids(grps), f"exchange {a['id']} uses missing group {ou}"

    # 2. program indicator groups
    pigs = pkg.setdefault("programIndicatorGroups", [])
    src_groups = {g["id"]: g for f in PIG_FILES for g in load(f).get("programIndicatorGroups", [])}
    for gid in PI_GROUPS:
        if gid in ids(pigs):
            continue
        g = src_groups[gid]
        members = [m for m in g["programIndicators"] if m["id"] in pi_ids]
        dropped = len(g["programIndicators"]) - len(members)
        o = {"id": gid, "code": g["code"], "name": g["name"],
             "programIndicators": [{"id": m["id"]} for m in members], "sharing": sharing()}
        if g.get("description"):
            o["description"] = g["description"]
        pigs.append(o)
        log.append(f"2 added program indicator group {gid} {g['name']} ({len(members)} PIs"
                   + (f", {dropped} not in package skipped)" if dropped else ")"))

    # 3. working lists
    wls = pkg.setdefault("programStageWorkingLists", [])
    for w in load(WL_FILE)["programStageWorkingLists"]:
        if w["id"] in ids(wls):
            continue
        o = {k: v for k, v in w.items() if k in WL_KEEP}
        o["sharing"] = {"external": False, "users": {}, "public": w["sharing"]["public"],
                        "userGroups": {GROUP_MAP[g]: {"id": GROUP_MAP[g], "access": a["access"]}
                                       for g, a in w["sharing"]["userGroups"].items()}}
        wls.append(o)
        log.append(f"3 added working list {w['id']} {w['name']}")

    # 4. exchange data sharing
    for a in pkg.get("aggregateDataExchanges", []):
        ug = a["sharing"].setdefault("userGroups", {})
        cur = ug.get(HDM_ADMIN, {}).get("access", "--------")
        if cur[2:4] != "rw":
            new = cur[:2] + "rw" + cur[4:]
            ug[HDM_ADMIN] = {"id": HDM_ADMIN, "displayName": "HDM - Admin", "access": new}
            log.append(f"4 exchange {a['id']}: HDM - Admin {cur} -> {new}")

    # 5. leftover HTN group UIDs in rule expressions
    for coll, fields in (("programRules", ("condition",)), ("programRuleActions", ("data", "content"))):
        for o in pkg[coll]:
            for f in fields:
                v = o.get(f)
                if isinstance(v, str) and any(g in v for g in GROUP_MAP):
                    for old, new in GROUP_MAP.items():
                        v = v.replace(old, new)
                    o[f] = v
                    log.append(f"5 {coll} {o['id']} {f}: HTN group UID -> HDM group")

    # 6. from the RTSL source
    rtsl = load(RTSL_FILE)
    rpi = {p["id"]: p for p in rtsl["programIndicators"]}
    for p in pkg["programIndicators"]:
        if p["id"] in RESTORE_PIS and p.get("expression") != rpi[p["id"]]["expression"]:
            p["expression"] = rpi[p["id"]]["expression"]
            p["description"] = PI_DESCRIPTIONS.get(p["id"], p.get("description"))
            log.append(f"6 program indicator {p['id']}: expression restored from RTSL")
    rules = {r["id"]: r for r in pkg["programRules"]}
    have = ids(pkg["programRuleActions"])
    for a in rtsl["programRuleActions"]:
        rid = a["programRule"]["id"]
        if a["id"] in have or a["id"] in SKIP_ACTIONS or rid not in rules:
            continue
        a = {k: v for k, v in a.items() if k not in SERVER_FIELDS}
        pkg["programRuleActions"].append(a)
        rules[rid].setdefault("programRuleActions", []).append({"id": a["id"]})
        log.append(f"6 program rule action {a['id']} ({a['programRuleActionType']}) restored to rule {rid}")

    Path(out).write_text(json.dumps(pkg, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    print("\n".join(log) or "nothing to change")
    print(f"wrote {out}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "metadata_postprocessed.json")
