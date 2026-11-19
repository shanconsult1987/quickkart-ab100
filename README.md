# quickkart-ab100

## Install dependencies

```powershell
python -m pip install -r .\requirements.txt
```

The requirements use `agent-framework-core` rather than the `agent-framework`
meta-package, which installs all optional integrations. This avoids pulling in
the unused Monty integration and its `pydantic-monty-runtime` dependency, whose
metadata download can return HTTP 404 through the Microsoft package feed.
The requirements also include `agent-framework-openai` for the OpenAI client
used by the framework agents. Install other integrations individually when needed.

If VS Code reports that `agent_framework` cannot be resolved, use **Python:
Select Interpreter** to select the environment where you installed these
requirements, or install them with that interpreter's `python -m pip`.

## Run the OpenAI investigation

From the repository root:

```powershell
python -m scripts.test_openai_agent
```

Direct execution also works:

```powershell
python .\scripts\test_openai_agent.py
```

Configure `OPENAI_API_KEY` in `.env` first. The script calls the OpenAI API
and may incur usage charges.

## Run the multi-agent investigation

From the repository root, run either command:

```powershell
python -m scripts.run_multi_agent
python .\scripts\run_multi_agent.py
```

This also requires `OPENAI_API_KEY` and makes live OpenAI API calls.
The report is saved to `data/last_agent_run.json` relative to the working directory.