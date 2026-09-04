# FineOBS Evaluation

## Benchmark

Dataset size: 500 records

The benchmark contains:
- valid reconciliations
- missing settlements
- settlement delays
- duplicate settlements
- amount discrepancies
- noisy identifiers

## Evaluation Metrics

FineOBS reports:

- Match rate
- Precision
- Recall
- F1 score
- Correct reconciliations
- Incorrect reconciliations
- Review rate
- Unresolved rate
- Exception detection
- Processing throughput

## Model Comparison

| Version | Precision | Recall | F1 | Match Rate |
|---|---:|---:|---:|---:|
| Deterministic baseline | TBD | TBD | TBD | TBD |
| Intelligent matcher | TBD | TBD | TBD | TBD |
| AI verification | TBD | TBD | TBD | TBD |

## Principle

FineOBS treats unresolved cases as a valid outcome rather than forcing uncertain records into an automatic reconciliation.