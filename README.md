# VisibilityOS Audit Compare

Compare AI answer checks over time with **VisibilityOS by PodPitch**. The GitHub Action reads an audit CSV in your checked-out repository and adds three counts to the workflow summary. It runs on the runner, makes no network requests, and keeps the underlying prompts and answers out of the action output.

Start with the [fictional example.csv](example.csv) or the [VisibilityOS audit template](https://podpitch.github.io/visibilityos-audit-template/). The action runs on GitHub-hosted Linux and macOS runners. Self-hosted runners need Bash and Python 3.10 or newer. Your workflow needs permission to read the repository so it can check out the CSV.

```yaml
name: Compare AI answer checks
on: workflow_dispatch
permissions:
  contents: read
jobs:
  compare:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@d23441a48e516b6c34aea4fa41551a30e30af803 # v6
        with:
          persist-credentials: false
      - uses: PodPitch/visibilityos-audit-action@v1.0.0
        with:
          csv-path: example.csv
```

### What the action reports

| Output | Meaning | Fictional example |
| --- | --- | ---: |
| `matched-comparisons` | Adjacent observation dates within each group of matching audit fields | 5 |
| `presence-changes` | The product's name or official link appeared or disappeared between matched observations | 2 |
| `link-changes` | A link to the product's official domain appeared or disappeared | 2 |

The action matches on the same prompt, engine, model, mode, country, language, location and brand. It compares adjacent dates within each matching group. The CSV requires those eight fields plus `date` (ISO format), `mentioned` and `linked` (each `yes` or `no`). The location may be blank. An unreadable file, malformed row, or duplicate observation fails the step before it writes counts.

Read the [study method](https://visibilityos.co/research/ai-answer-visibility) for how repeats were collected and how to interpret them. Visit [VisibilityOS by PodPitch](https://visibilityos.co/) for the AI visibility product.
