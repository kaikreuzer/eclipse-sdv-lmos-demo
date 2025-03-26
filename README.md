# Resources for LMOS Demo at Eclipse SDV Community Days Rotterdam 2025

## Introduction

This repository contains the resources that were used for the [Eclipse LMOS](https://eclipse.dev/lmos) demo at the Eclipse SDV Community Days Rotterdam 2025.

It consists of a modified fleet management blueprint setup and a LMOS Arc agent that connects to the InfluxDB database to answer questions about the fleet.

## Modifications to the Fleet Management Blueprint

The [fleet management blueprint](https://github.com/eclipse-sdv-blueprints/fleet-management) simulates a single car sending telemetry data to an InfluxDB database in the backend. For the demo, the blueprint was modified to simulate three cars sending telemetry data to the InfluxDB database.

For this, the docker compose file was modified to start three instances of the relevant in-vehicle containers.

The steps to reproduce the modified setup are as follows:

```bash
git clone https://github.com/eclipse-sdv-blueprints/fleet-management
cd fleet-management
git checkout 59b4b4a # Commit hash of the modified setup
# copy the file https://github.com/kaikreuzer/eclipse-sdv-lmos-demo/blob/main/README.md to the root of the fleet-management repository
curl -o fms-blueprint-compose.yaml https://raw.githubusercontent.com/kaikreuzer/eclipse-sdv-lmos-demo/refs/heads/main/fm-blueprint/fms-blueprint-compose.yaml
```

The csv providers of the three vehicles require individual simulated data. For this, a [python script]() has been created that generates the required data in csv format.

In order to generate simulated data for the three vehicles, the following steps are required:

```bash
curl -o generate_csv.py https://raw.githubusercontent.com/kaikreuzer/eclipse-sdv-lmos-demo/refs/heads/main/fm-blueprint/generate_csv.py
python3 generate_csv.py -o csv-provider/signalsFmsRecording1.csv
python3 generate_csv.py -o csv-provider/signalsFmsRecording2.csv
python3 generate_csv.py -o csv-provider/signalsFmsRecording3.csv
```

Now everything is ready to start the setup:

```bash
docker compose -f ./fms-blueprint-compose.yaml up --detach
```

After a short moment, Grafana should be available at http://localhost:3000. The default credentials are `admin`/`admin`.

## LMOS Arc Agent

To set up the LMOS Arc agent, these steps from the [LMOS Arc Quickstart Guide](https://eclipse.dev/lmos/docs/arc/quickstart/) have to be followed:

```bash
curl -Ls https://sh.jbang.dev | bash -s - trust add https://github.com/eclipse-lmos/arc/
curl -Ls https://sh.jbang.dev | bash -s - app install --fresh --force https://github.com/eclipse-lmos/arc/blob/main/arc-runner/arc.java
```

Get an OpenAI API key at https://platform.openai.com/settings/organization/api-keys and export it:

```bash
export ARC_AI_KEY=sk-...
```

Now create a LMOS Arc agent for fleet management and use the prepared definitions:

```bash
arc new assistant
curl -o agents/assistant.agent.kts https://raw.githubusercontent.com/kaikreuzer/eclipse-sdv-lmos-demo/refs/heads/main/fm-agent/agents/assistant.agent.kts
curl -o agents/get_telemetry_data.functions.kts https://raw.githubusercontent.com/kaikreuzer/eclipse-sdv-lmos-demo/refs/heads/main/fm-agent/agents/get_telemetry_data.functions.kts
```

Now the agent can be started:

```bash
arc run agents
```

The Arc View can now be accessed in a browser at http://localhost:8080/chat#/chat, which allows to interact with the agent through a web interface.
