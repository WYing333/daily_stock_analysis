import argparse
import json
from pathlib import Path
from statistics import mean


POLICIES = {
    "api": {
        "title": "API Layer",
        "allowed_targets": {"domain", "service", "utils"},
    },
    "service": {
        "title": "Service Layer",
        "allowed_targets": {"data", "domain", "integration", "utils"},
    },
    "data": {
        "title": "Data Layer",
        "allowed_targets": {"domain", "utils"},
    },
    "domain": {
        "title": "Domain Layer",
        "allowed_targets": {"utils"},
    },
    "integration": {
        "title": "Integration Layer",
        "allowed_targets": {"domain", "utils"},
    },
    "entry": {
        "title": "Entry Layer",
        "allowed_targets": {"api", "service"},
    },
}


def load(path):
    return json.loads(Path(path).read_text())


def core_boundaries(meta):
    return {
        (b["kind"], b["from"], b["to"])
        for b in meta.get("boundaries", [])
        if b.get("core") is True
    }


def core_boundary_objects(meta):
    out = {}
    for b in meta.get("boundaries", []):
        if b.get("core") is True:
            key = (b["kind"], b["from"], b["to"])
            out[key] = b
    return out


def score_policy(origin, title, allowed_targets, main_set, pr_set, pr_lookup):
    main_origin = {b for b in main_set if b[1] == origin}
    pr_origin = {b for b in pr_set if b[1] == origin}

    matched = main_origin & pr_origin
    missing = main_origin - pr_origin
    extra = pr_origin - main_origin

    new_targets = sorted({b[2] for b in extra})

    violated_new = sorted([
        b for b in extra
        if b[2] not in allowed_targets
    ])

    valid_new = sorted([
        b for b in extra
        if b[2] in allowed_targets
    ])

    boundary_coverage_recall = len(matched) / len(main_origin) if main_origin else 1.0

    precision = (
        len(allowed_targets) / (len(allowed_targets) + len(violated_new))
        if allowed_targets or violated_new else 1.0
    )

    new_boundary_validity = len(valid_new) / len(extra) if extra else 1.0

    violation_rate_by_allowed_targets = (
        len(violated_new) / len(allowed_targets)
        if allowed_targets else 0.0
    )

    policy_compliance = max(0.0, 1.0 - violation_rate_by_allowed_targets)

    violated_pretty = [
        {
            "origin": b[1],
            "target": b[2],
            "kind": b[0],
            "files": pr_lookup.get(b, {}).get("files", [])[:10],
        }
        for b in violated_new
    ]

    return {
        "origin": origin,
        "title": title,
        "allowed_targets": sorted(allowed_targets),
        "new_targets": new_targets,
        "violated_boundaries": violated_pretty,
        "boundary_coverage_recall": boundary_coverage_recall,
        "precision": precision,
        "new_boundary_validity": new_boundary_validity,
        "violation_rate_by_allowed_targets": violation_rate_by_allowed_targets,
        "policy_compliance": policy_compliance,
        "raw": {
            "main_origin_boundary_count": len(main_origin),
            "pr_origin_boundary_count": len(pr_origin),
            "matched": len(matched),
            "missing": len(missing),
            "extra": len(extra),
            "missing_boundaries": sorted(missing),
            "extra_boundaries": sorted(extra),
        },
    }


def fmt(x):
    if isinstance(x, float):
        return f"{x:.4f}".rstrip("0").rstrip(".")
    return str(x)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--main", required=True)
    parser.add_argument("--pr", required=True)
    parser.add_argument("--out", required=True)
    parser.add_argument(
        "--show-all",
        action="store_true",
        help="Show every configured policy, not only policies with new targets or violations.",
    )
    args = parser.parse_args()

    main_meta = load(args.main)
    pr_meta = load(args.pr)

    main_set = core_boundaries(main_meta)
    pr_set = core_boundaries(pr_meta)
    pr_lookup = core_boundary_objects(pr_meta)

    results = []

    for origin, policy in POLICIES.items():
        result = score_policy(
            origin=origin,
            title=policy["title"],
            allowed_targets=policy["allowed_targets"],
            main_set=main_set,
            pr_set=pr_set,
            pr_lookup=pr_lookup,
        )

        should_show = (
            args.show_all
            or result["new_targets"]
            or result["violated_boundaries"]
        )

        if not should_show:
            continue

        results.append(result)
        label = origin.upper()

        print(f"== Layer boundary policy: {result['title']} ===")
        print(f"{label} allowed targets: {result['allowed_targets']}")
        print(f"New {label} targets: {result['new_targets']}")

        compact_violated = [
            {"origin": x["origin"], "target": x["target"]}
            for x in result["violated_boundaries"]
        ]

        print(f"Violated {label} boundaries: {compact_violated}")
        print(f"Boundary Coverage recall: {fmt(result['boundary_coverage_recall'])}")
        print(f"precision: {fmt(result['precision'])}")
        print(f"{label} new-boundary validity: {fmt(result['new_boundary_validity'])}")
        print(f"{label} violation rate / allowed targets: {fmt(result['violation_rate_by_allowed_targets'])}")
        print(f"{label} policy compliance: {fmt(result['policy_compliance'])}")
        print(f"Wrote: {args.out}")
        print()

    avg = {
        "boundary_coverage_recall": mean(r["boundary_coverage_recall"] for r in results) if results else 1.0,
        "precision": mean(r["precision"] for r in results) if results else 1.0,
        "new_boundary_validity": mean(r["new_boundary_validity"] for r in results) if results else 1.0,
        "violation_rate_by_allowed_targets": mean(r["violation_rate_by_allowed_targets"] for r in results) if results else 0.0,
        "policy_compliance": mean(r["policy_compliance"] for r in results) if results else 1.0,
    }

    output = {
        "main_boundary_summary": main_meta.get("boundarySummary"),
        "pr_boundary_summary": pr_meta.get("boundarySummary"),
        "main_core_boundary_count": len(main_set),
        "pr_core_boundary_count": len(pr_set),
        "policies": results,
        "average": avg,
    }

    Path(args.out).write_text(json.dumps(output, indent=2), encoding="utf-8")

    if len(results) > 1:
        print("== Average across source-layer policies ===")
        print(f"Average Boundary Coverage recall: {fmt(avg['boundary_coverage_recall'])}")
        print(f"Average precision: {fmt(avg['precision'])}")
        print(f"Average new-boundary validity: {fmt(avg['new_boundary_validity'])}")
        print(f"Average violation rate / allowed targets: {fmt(avg['violation_rate_by_allowed_targets'])}")
        print(f"Average policy compliance: {fmt(avg['policy_compliance'])}")
        print(f"Wrote: {args.out}")

    if not results:
        print("== Layer boundary policy ===")
        print("No new source-layer policy boundaries detected.")
        print(f"Average Boundary Coverage recall: {fmt(avg['boundary_coverage_recall'])}")
        print(f"Average precision: {fmt(avg['precision'])}")
        print(f"Average new-boundary validity: {fmt(avg['new_boundary_validity'])}")
        print(f"Average violation rate / allowed targets: {fmt(avg['violation_rate_by_allowed_targets'])}")
        print(f"Average policy compliance: {fmt(avg['policy_compliance'])}")
        print(f"Wrote: {args.out}")


if __name__ == "__main__":
    main()
