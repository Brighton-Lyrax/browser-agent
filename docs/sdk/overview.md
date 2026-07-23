# ReplyPilot SDK

## Python
```bash
pip install replypilot
```
```python
from replypilot import ReplyPilot

client = ReplyPilot(base_url="http://localhost:8788")

lead = client.capture(name="Jane", email="jane@example.com", company="Acme", interest="automation")
lead_id = lead["lead_id"]
```

## TypeScript / Node
```bash
npm install replypilot
```
```ts
import { ReplyPilot } from "replypilot";

const client = new ReplyPilot({ baseUrl: "http://localhost:8788" });
const lead = await client.capture({ name: "Jane", email: "jane@example.com", company: "Acme", interest: "automation" });
```
