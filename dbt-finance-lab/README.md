# Finance Analytics Engineering | dbt + Databricks Learning Lab

> **Learning portfolio:** 100% synthetic data. No Bradesco data, employer production implementation, or certification is claimed.

## Purpose
Demonstrate transparent SQL transformations, governance-minded data quality, and auditable FP&A reporting using dbt. This **first iteration runs locally with DuckDB**, not on a Databricks workspace.

### Architecture
```text
Synthetic costs CSV → dbt seed → staging model (view)
                                 ↓
                         monthly cost mart (table)
                                 ↓
                      schema + business-rule tests
```

## Run locally (free)
Python 3.11+ recommended. From the repository root:

```bash
cd dbt-finance-lab
python -m venv .venv
# Activate: Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
python -m pip install -r requirements-dbt.txt
# Copy profiles.example.yml to profiles.yml
dbt debug --profiles-dir .
dbt build --profiles-dir .
dbt docs generate --profiles-dir .
```

The local `profiles.yml` is ignored by Git. The build should seed synthetic rows, create a typed staging view, aggregate costs by month/center/category, and execute tests. **Execution has not been verified against a Databricks environment.**

### Models
- `stg_finance_costs`: typed input, clean category labels and cost centers
- `fct_monthly_costs`: one row per `month + cost_center + category`, total BRL cost and transaction count
- `models/schema.yml`: uniqueness, non-null and accepted category tests
- `tests/assert_monthly_costs_positive.sql`: financial quality constraint

### Databricks extension (planned, not yet implemented)
1. Learn the official `dbt-databricks` adapter and authentication model.
2. Prepare a private Databricks profile via environment variables (never publish tokens, hostnames or workspace paths).
3. Validate seed/model behavior against Delta and Unity Catalog.
4. Explore incremental transformations, lineage, schema contracts and CI/CD.
5. Add real execution evidence only after successfully running it.

### Milestones
- [x] dbt project, synthetic dataset, staging/mart queries, tests and CI definition
- [ ] Confirm clean GitHub Actions build and document the results
- [ ] Create budget-vs-actual reconciliation model with synthetic data
- [ ] Add incremental processing and data lineage documentation
- [ ] Validate on Databricks/Unity Catalog
- [ ] Document measured results, with sources and reproducible instructions

Resources: [dbt docs](https://docs.getdbt.com/docs/introduction) · [Databricks dbt adapter](https://docs.getdbt.com/docs/core/connect-data-platform/databricks-setup) · [Certification roadmap](CERTIFICATION_ROADMAP.md)

**Confidentiality:** All numbers, systems, entities, and transactions in this demonstration are fictional. Do not commit company data, proprietary architecture, credentials or sensitive screenshots.
