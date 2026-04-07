


Ho analizzato la documentazione ufficiale del protocollo A2A v1.0 tramite il link che hai fornito. Ho individuato diversi errori critici e divergenze nel documento precedente (dovuti al fatto che A2A è uno standard molto preciso, con un suo schema dati rigoroso) e li ho corretti completamente.

Ecco le principali correzioni apportate basate sulla specifica ufficiale:
1. **Metodi JSON-RPC canonici**: Nello standard A2A, il campo `method` di JSON-RPC non è la funzione o "skill" dell'agente (es. non è `parse_csv`), ma deve essere una delle operazioni astratte del protocollo (es. `SendMessage`, `GetTask`, `ListTasks`).
2. **Struttura AgentCard**: Aggiornata per rispettare lo standard A2A v1.0. Ora utilizza i campi canonici come `supportedInterfaces`, `skills`, `defaultInputModes` e `capabilities` (es. `streaming`, `pushNotifications`) invece di uno schema custom inventato.
3. **Risultati e Artifacts**: La specifica impone che l'output del lavoro di un agente non venga inviato come "Messaggio di testo", ma venga inserito nell'oggetto `Task` sotto forma di `Artifact` strutturato.
4. **Ciclo di vita del Task**: Gli stati sono stati allineati all'enumeratore ufficiale (`TASK_STATE_SUBMITTED`, `TASK_STATE_WORKING`, `TASK_STATE_AUTH_REQUIRED`, `TASK_STATE_COMPLETED`, ecc.).
5. **JWS Signatures**: Lo standard richiede la firma crittografica dell'AgentCard tramite JSON Web Signature (RFC 7515) previa canonizzazione JCS (RFC 8785). Il documento ora impone questo meccanismo.
6. **A2A vs MCP**: Aggiunta l'importante distinzione tra A2A e Model Context Protocol (MCP) nella sezione dei pitfall, come indicato nell'appendice della specifica.
7. **Discriminatore JSON**: Ho rimosso l'anti-pattern del campo `"kind"` per indicare il tipo di dato, allineando il documento alle *breaking changes* della v1.0.
8. **Link integrato**: La documentazione ufficiale è ora citata nella sezione finale come *Upstream Reference*.

Di seguito trovi il documento completo, formattato in puro testo Markdown (senza l'uso del blocco di codice perimetro ` ```markdown ` così da evitare che si interrompa la copia). Il contenuto rispetta la direttiva ed è esclusivamente in inglese.

***

# SwarmForge A2A Protocol Standard
**Document ID:** SF-DOC-001
**Path:** `/docs/standards/a2a-protocol.md`
**Version:** 1.0.0
**Owner:** AI Infrastructure TPM
**Phase Alignment:** Genesis — Knowledge Infrastructure Layer

---

## 1. Overview

The Agent-to-Agent (A2A) protocol is the standardized communication interface layer enabling independent autonomous agents to discover, request, and execute tasks across a distributed network. It abstracts the underlying transport mechanisms into a unified, predictable semantic model. 

In distributed multi-agent systems, agents are built using disparate frameworks, languages, and operational logic. Without a unifying communication layer, agents cannot reliably delegate tasks, share context, or negotiate execution boundaries, leading to fragmented, tightly coupled silos.

SwarmForge adopts a strict JSON-RPC binding of the **A2A v1.0 Standard** to serve as its canonical communication backbone. This standardization ensures protocol uniformity, prevents architectural drift, guarantees predictable state transitions, and enforces our zero-trust security posture across all orchestrations. This document adapts the canonical A2A semantics strictly for the SwarmForge engineering ecosystem and serves as the single source of truth for internal multi-agent integrations.

---

## 2. Core Concepts

### Agent Identity and Addressing
Within SwarmForge, an agent is not addressed by its IP or internal network hostname. Every agent possesses a globally unique identifier (Agent ID). Addressing is performed logically via this ID (often passed as the `tenant` parameter), decoupling the agent's identity from its physical compute node.

### AgentCard: Structure, Purpose, and Fields
The **AgentCard** is the immutable capability manifest of an agent. It serves as the agent's public interface definition and discovery mechanism.
*   **Structure:** A JSON object defining the agent's identity, transport endpoints, capabilities, and distinct functional skills.
*   **Core Fields:** 
    *   `supportedInterfaces`: The transport URLs and protocol bindings (e.g., JSONRPC, HTTP+JSON) the agent supports.
    *   `capabilities`: Boolean flags indicating support for advanced protocol features like `streaming` and `pushNotifications`.
    *   `skills`: The distinct capabilities/functions the agent can perform, along with `inputModes` and `outputModes`.
    *   `signatures`: Cryptographic proofs verifying the authenticity of the AgentCard payload.

### Task Lifecycle
Every multi-turn or asynchronous A2A interaction in SwarmForge is modeled as a stateful **Task**. The lifecycle uses a strict state machine:
*   `TASK_STATE_SUBMITTED`: Acknowledged by the agent.
*   `TASK_STATE_WORKING`: Actively processing.
*   `TASK_STATE_INPUT_REQUIRED` / `TASK_STATE_AUTH_REQUIRED`: Paused, requiring human or client intervention/authorization.
*   `TASK_STATE_COMPLETED` / `TASK_STATE_FAILED` / `TASK_STATE_CANCELED` / `TASK_STATE_REJECTED`: Terminal resolution states.

### Messages, Parts, and Artifacts
A2A enforces a strict separation between communication and execution results:
*   **Message:** Contains a `role` (`ROLE_USER` or `ROLE_AGENT`) and an array of `parts`. Parts encapsulate content (`text`, `url`, `raw`, or `data`).
*   **Artifact:** The concrete output generated by a completed task (e.g., structured JSON, reports, files). Artifacts are appended to the `Task` object, *never* sent as mere conversational Messages.

---

## 3. How the Protocol Works (Practical View)

### End-to-End Flow
1.  **Discovery:** Agent A fetches Agent B's `AgentCard` from the SwarmForge registry and identifies a target `skill`.
2.  **Request Construction:** Agent A constructs a JSON-RPC 2.0 request using the standard `SendMessage` operation, enclosing the instructions in the `Message` object.
3.  **Transmission:** Agent A dispatches the JSON-RPC request to Switchboard.
4.  **Task Creation:** Agent B receives the request, transitions to `TASK_STATE_WORKING`, and acknowledges by returning a `Task` object to Agent A.
5.  **Completion:** Agent B finishes processing, transitions the task to `TASK_STATE_COMPLETED`, and populates the `artifacts` array with the results. Agent A retrieves this via the `GetTask` operation.

### JSON-RPC 2.0 Transport Layer Mapping
SwarmForge utilizes JSON-RPC 2.0 over HTTP/2. In the A2A spec, JSON-RPC `method` values are reserved strictly for protocol operations, **not** custom agent functions. 
The supported `method` strings are: `SendMessage`, `SendStreamingMessage`, `GetTask`, `ListTasks`, `CancelTask`, and `SubscribeToTask`. Custom skill targeting is handled within the message content and agent parameters.

### Streaming vs Non-Streaming Modes
*   **Non-streaming:** Discrete tasks use `SendMessage` and `GetTask`. The caller polls or waits for a terminal Task state.
*   **Streaming:** Initiated via `SendStreamingMessage`. Switchboard opens a Server-Sent Events (SSE) stream. The responding agent pushes real-time `TaskStatusUpdateEvent` and `TaskArtifactUpdateEvent` payloads.

### Error Handling and Failure States
Failures utilize the standard JSON-RPC `error` block. SwarmForge standardizes on A2A custom error ranges:
*   `-32001`: `TaskNotFoundError`
*   `-32004`: `UnsupportedOperationError`
*   `-32005`: `ContentTypeNotSupportedError`

---

## 4. SwarmForge Architecture Mapping

### Switchboard Orchestration
SwarmForge does not utilize pure peer-to-peer routing. All A2A traffic routes through **Switchboard**, SwarmForge’s intelligent orchestration layer. Switchboard acts as the central JSON-RPC router, load balancer, and A2A service parameter validator (e.g., verifying `A2A-Version` headers). Agents target operations at Switchboard, passing the target agent ID via the `tenant` parameter.

### Zero-Trust Security Model Integration
Agents inherently distrust each other. Switchboard enforces zero-trust boundaries at the A2A protocol level:
1.  Switchboard drops unauthenticated traffic before reaching the target agent.
2.  **AgentCard Signatures:** Every agent MUST sign its AgentCard using JSON Web Signatures (JWS) following the JSON Canonicalization Scheme (JCS, RFC 8785). Switchboard caches only cryptographically verified cards.
3.  In-Task Authorization: If an agent needs escalated privileges, it MUST set the task to `TASK_STATE_AUTH_REQUIRED` to delegate credential resolution to the user/caller safely.

### The Swarm Layer & Registry Lifecycle
When an agent boots, it registers its JWS-signed `AgentCard` with Switchboard's internal registry. Only after Switchboard validates the `supportedInterfaces` and verifies the JWS signature does the agent become discoverable to other agents within the node mesh.

---

## 5. Implementation Guidelines

### Step-by-Step Implementation Guide
1.  **Define Skills & Capabilities:** Map your agent's functionality to A2A `skills`. Identify required `inputModes` and `outputModes`.
2.  **Construct & Sign the AgentCard:** Generate your `AgentCard` JSON. Strip out optional parameters with default values, canonicalize via RFC 8785, and attach the JWS signature.
3.  **Implement Core Operations:** Bind an HTTP server to the Swarm Node daemon. Implement handlers for `SendMessage` and `GetTask` at a minimum.
4.  **Task State Management:** Ensure your internal engine correctly updates the A2A state machine (`SUBMITTED` -> `WORKING` -> `COMPLETED`).
5.  **Artifact Generation:** Wrap your final operational outputs into A2A `Artifact` objects.

### Authentication and Identity Verification Requirements
Implementers MUST use the SwarmForge Node SDK to sign outgoing JSON-RPC payloads. Agents MUST enforce authorization boundaries based on the `tenant` or context ID, verifying that callers only access tasks they originated.

### Versioning Strategy for Protocol Interoperability
Agents MUST include the `A2A-Version: 1.0` declaration in their HTTP headers (or JSON-RPC metadata equivalents via Switchboard) to ensure semantic compatibility.

---

## 6. Mandatory Engineering Rules

The following rules are non-negotiable.

1.  **Canonical Operation Naming**
    *   *Rule:* Agents MUST use the standard A2A operation names (e.g., `SendMessage`, `GetTask`) for JSON-RPC methods. Agents SHALL NOT use custom functional names (e.g., `method: "analyze_logs"`).
    *   *Consequence:* Custom method names violate the A2A specification and will be dropped by Switchboard with a `-32601 MethodNotFoundError`.
2.  **Strict Output Separation**
    *   *Rule:* The results of a successfully executed task MUST be placed within the `artifacts` array of a `Task` object.
    *   *Consequence:* Returning functional data as a conversational `Message` part breaks programmatic downstream parsers. Agents violating this will be flagged as misconfigured.
3.  **JSON Member Name Discrimination (No "Kind")**
    *   *Rule:* A2A v1.0 removes the legacy `{"kind": "text"}` discriminator pattern. Implementations MUST use object keys to discriminate part types (e.g., `{"text": "Hello"}`, `{"url": "https:..."}`).
    *   *Consequence:* Legacy format payloads will fail A2A schema validation at the Switchboard ingress layer.
4.  **Canonical Signature Enforcement**
    *   *Rule:* AgentCards MUST be signed using JWS (RFC 7515) and canonicalized via RFC 8785 before signing.
    *   *Consequence:* Non-canonical signatures fail cryptographic verification; the agent will be quarantined and undiscoverable in the Switchboard registry.
5.  **Standardized Error Code Ranges**
    *   *Rule:* All custom execution errors MUST map to the SwarmForge/A2A reserved JSON-RPC error block: `-32001` to `-32099`.
    *   *Consequence:* Violations break telemetry dashboards and automated incident routing.

---

## 7. Annotated Examples

### SwarmForge-Compliant AgentCard JSON
```json
{
  "name": "Data Parser Agent",
  "description": "Converts raw CSV strings to normalized JSON arrays.",
  "version": "1.2.0",
  "supportedInterfaces":[
    {
      "url": "https://switchboard.swarmforge.internal/a2a/v1",
      "protocolBinding": "JSONRPC",
      "protocolVersion": "1.0",
      "tenant": "sf-agt-99a3f"
    }
  ],
  "capabilities": {
    "streaming": false,
    "pushNotifications": false,
    "extendedAgentCard": false
  },
  "defaultInputModes": ["text/csv"],
  "defaultOutputModes": ["application/json"],
  "skills":[
    {
      "id": "parse-csv",
      "name": "CSV Parser",
      "description": "Parses CSV data into structured JSON objects.",
      "inputModes": ["text/csv"],
      "outputModes": ["application/json"]
    }
  ]
}
```

### JSON-RPC Request/Response Pair (SendMessage)
**Request (Initiating the task via Switchboard):**
```json
{
  "jsonrpc": "2.0",
  "id": "req-884a",
  "method": "SendMessage",
  "params": {
    "tenant": "sf-agt-99a3f", 
    "message": {
      "messageId": "msg-111",
      "role": "ROLE_USER",
      "parts":[
        { "text": "Execute parse-csv on the following data:\nid,name\n1,Alice\n2,Bob" }
      ]
    }
  }
}
```

**Response (Task created and instantly resolved):**
```json
{
  "jsonrpc": "2.0",
  "id": "req-884a",
  "result": {
    "task": {
      "id": "task-uuid-5555",
      "status": {
        "state": "TASK_STATE_COMPLETED"
      },
      "artifacts":[
        {
          "artifactId": "art-01",
          "name": "parsed_output.json",
          "parts": [
            {
              "mediaType": "application/json",
              "data":[
                {"id": 1, "name": "Alice"},
                {"id": 2, "name": "Bob"}
              ]
            }
          ]
        }
      ]
    }
  }
}
```

### Error Scenario: Task Not Found
If Agent A requests the status of a task that does not exist or expired via `GetTask`.
```json
{
  "jsonrpc": "2.0",
  "error": {
    "code": -32001,
    "message": "Task not found",
    "data":[
      {
        "@type": "type.googleapis.com/google.rpc.ErrorInfo",
        "reason": "TASK_NOT_FOUND",
        "domain": "a2a-protocol.org",
        "metadata": {
          "taskId": "task-uuid-9999"
        }
      }
    ]
  },
  "id": "req-884b"
}
```

---

## 8. Common Pitfalls

1.  **Confusing A2A with MCP:** The Model Context Protocol (MCP) and A2A serve different layers. A2A is an application-level protocol for peer-to-peer *agent delegation*. MCP is for an agent to connect to *dumb tools/APIs*. Do not attempt to use A2A endpoints to expose simple database CRUD operations—use MCP for that.
2.  **Violating the "Kind" Discriminator Rule:** Older draft versions of A2A used `{"kind": "text", "text": "..."}`. A2A v1.0 strictly relies on the JSON member name: `{"text": "..."}`. Do not include `kind` fields.
3.  **Assuming Guaranteed Synchronous Delivery:** Switchboard guarantees routing, not instant delivery. Target agents may be under load. Implementers MUST enforce local timeouts or utilize `SendStreamingMessage` for long-running processes.
4.  **Blocking the Event Loop:** A2A interactions are inherently asynchronous. Do not use synchronous wait states when calling out to Switchboard. This will starve the Swarm Node's worker threads.

---

## 9. Versioning, Maintenance & Compliance

**Document Details:**
*   **Version:** 1.0.0
*   **Date:** Current
*   **Owner:** AI Infrastructure TPM

**Upstream Reference:** 
This internal standard is structurally derived from and must remain semantically compliant with the [Official A2A Protocol Specification v1.0](https://a2a-protocol.org/latest/specification/).

**License & Attribution (Centralized Compliance Model):**
The A2A Protocol is licensed under the **Apache License, Version 2.0**. To maintain a clean repository structure while ensuring full legal compliance, SwarmForge adopts the following "Notice & Reference" model:

1.  **Centralized Attribution:** The SwarmForge project SHALL maintain a `CREDITS.md` (or `NOTICE`) file in the repository root. This file serves as the definitive index for all third-party intellectual property, explicitly listing the A2A Protocol and its authors.
2.  **License Location:** A full, unmodified copy of the Apache License 2.0 MUST be stored at `/docs/legal/apache-2.0.txt`. All internal references to the A2A license MUST point to this path.
3.  **No Root Clutter:** Individual agent modules and sub-directories ARE NOT required to host redundant `LICENSE` files in their local roots, provided they are covered by the centralized `CREDITS.md` file.
4.  **Header Retention:** Engineers MUST NOT remove original copyright headers from any inherited A2A schema files or boilerplate code. 
5.  **Modification Transparency:** Any file derived from the A2A specification that is modified for SwarmForge architecture MUST include a brief header comment: *"Modified for SwarmForge on [Date] under the terms of the Apache License 2.0"*.

**Change Policy:**
Updates to this standard require a formal architectural RFC and an impact analysis against the upstream A2A protocol. Proposals must be submitted to the AI Infrastructure TPM. Any modification to the internal routing payload structure requires a bump in the internal API version configuration to ensure backward compatibility.