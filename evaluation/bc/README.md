# Boundary Coverage Evaluation Script

This folder contains the evaluation script used to produce the numbers reported in CodeAssureLabs/roadmap#69.

Script:

python3 evaluation/bc/compare_bc_layer_policy_any.py --main <main knowledge-graph.meta.json> --pr <pr knowledge-graph.meta.json> --out <output json>

What it reports:

- allowed targets
- new targets
- violated boundaries
- Boundary Coverage recall
- precision
- new-boundary validity
- violation rate / allowed targets
- policy compliance
- average across source-layer policies

Example:

MAIN=/path/to/zhu-main-updated-core-no-llm/.fast-kg/knowledge-graph.meta.json
PR=/path/to/zhu-bc-pr6-api-two-violations-data-integration-no-llm/.fast-kg/knowledge-graph.meta.json

python3 evaluation/bc/compare_bc_layer_policy_any.py --main "$MAIN" --pr "$PR" --out bc-pr6-api-two-violations-data-integration-policy-score.json

The fast-kg outputs were generated with:

/fast-kg:fast-understand <repo> --full --no-llm

Notes:

The script was used for synthetic Boundary Coverage edge-case testing for roadmap issue #69.

Some synthetic PR branches emit new core boundaries and are scored as violations. Other branches may change files but emit no new core boundaries, in which case the script reports no new source-layer policy boundaries.
