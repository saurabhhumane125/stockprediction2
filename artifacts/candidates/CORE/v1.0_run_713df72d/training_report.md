# Training Report – GRU_run_713df72d

> Generated at 2026-07-20T15:40:12.092850+00:00 | Git commit: `9074205` | Execution time: 278.56s

## Environment

- **python_version**: `3.11.9 (tags/v3.11.9:de54cf5, Apr  2 2024, 10:12:12) [MSC v.1938 64 bit (AMD64)]`
- **platform**: `Windows-10-10.0.26200-SP0`
- **git_commit**: `9074205`
- **numpy**: `1.26.4`
- **scikit_learn**: `1.7.1`
- **tensorflow**: `2.21.0`
- **torch**: `2.7.1`
- **pandas**: `3.0.3`

## Hyperparameters

- **SEQUENCE_LENGTH**: `48`
- **FORECAST_HORIZON**: `1`
- **RETURN_THRESHOLD_BPS**: `0.0`
- **TRAIN_END_DATE**: `2021-12-31`
- **VAL_END_DATE**: `2023-06-30`
- **BATCH_SIZE**: `64`
- **EPOCHS**: `100`
- **LEARNING_RATE**: `0.001`
- **EARLY_STOPPING_PATIENCE**: `15`
- **EARLY_STOPPING_MONITOR**: `val_loss`
- **LR_SCHEDULER**: `ReduceLROnPlateau`
- **LR_SCHEDULER_PATIENCE**: `5`
- **LR_SCHEDULER_FACTOR**: `0.5`
- **LR_SCHEDULER_MIN_LR**: `1e-06`
- **LR_SCHEDULER_T_MAX**: `50`
- **LR_SCHEDULER_MAX_LR**: `0.01`
- **DROPOUT**: `0.2`
- **GRADIENT_CLIP_NORM**: `1.0`
- **OPTIMIZER**: `adam`
- **HIDDEN_SIZE**: `64`
- **MIXED_PRECISION**: `False`
- **DEVICE**: `auto`
- **CUDNN_BENCHMARK**: `True`
- **SEED**: `42`
- **NUM_WORKERS**: `0`
- **PIN_MEMORY**: `False`

## Dataset

- **tickers**: `[]`
- **n_tickers**: `0`
- **train_rows**: `2130`
- **val_rows**: `1850`
- **test_rows**: `3750`
- **sequence_length**: `48`
- **n_features**: `23`
- **train_end**: `2021-12-31`
- **val_end**: `2023-06-30`

## Features

Total features: **0**

```

```

## Evaluation Metrics (Out-of-Sample)

- **test_loss**: `0.728901`
- **test_accuracy**: `0.504`
- **accuracy**: `0.504`
- **precision**: `0.513193`
- **recall**: `0.50836`
- **f1**: `0.456557`
- **confusion_matrix**: `[[391, 1511], [349, 1499]]`
- **auc**: `0.5086`

## Training Curve (last 10 epochs)

| epoch | train_loss | train_accuracy | val_loss | val_accuracy |
| --- | --- | --- | --- | --- |
| 15 | 0.696358 | 0.528169 | 0.692985 | 0.514054 |
| 16 | 0.694981 | 0.525352 | 0.694766 | 0.514054 |
| 17 | 0.69446 | 0.533803 | 0.693428 | 0.514054 |
| 18 | 0.692965 | 0.528169 | 0.701723 | 0.514054 |
| 19 | 0.697141 | 0.52723 | 0.698478 | 0.514054 |
| 20 | 0.694933 | 0.520657 | 0.693113 | 0.514054 |
| 21 | 0.695229 | 0.523474 | 0.69422 | 0.514054 |
| 22 | 0.692554 | 0.542254 | 0.695748 | 0.514054 |
| 23 | 0.692478 | 0.537089 | 0.700467 | 0.514054 |
| 24 | 0.694009 | 0.529108 | 0.694465 | 0.514054 |
