<h1 align="center">🌾 Field Guardian AI Agent</h1>

<p align="center">
  An AI-powered field advisor for Bangladeshi farmers, combining IoT sensors, satellite data,
  flood risk prediction, and carbon-smart recommendations.
</p>

<hr />

<h2>📌 Overview</h2>

<p>
  <strong>Field Guardian AI Agent</strong> is a backend service built with
  <a href="https://fastapi.tiangolo.com/" target="_blank">FastAPI</a>,
  <a href="https://python.langchain.com/" target="_blank">LangChain</a>,
  <a href="https://langchain-ai.github.io/langgraph/" target="_blank">LangGraph</a>, and
  <a href="https://cloud.google.com/" target="_blank">Google Cloud</a>.
  It connects:
</p>

<ul>
  <li>👨‍🌾 Farmer &amp; field profiles from Firebase Realtime Database</li>
  <li>🌡️ IoT soil sensors (temperature, moisture, humidity)</li>
  <li>🛰️ Satellite indices (NDRE, NDSSI, NDVI, etc.)</li>
  <li>🌊 Flood risk prediction using a trained ML model</li>
  <li>🌳 Carbon sequestration estimation from NDVI</li>
  <li>🤖 LLM-based problem detection &amp; solution planning (Bangla-first)</li>
</ul>

<p>
  Given a <code>farmer_id</code> and <code>field_id</code>, the agent fetches all relevant data,
  detects problems, plans solutions, and saves the AI consultation back into Firebase.
</p>

<hr />

<h2>🧱 Tech Stack</h2>

<ul>
  <li><strong>Backend:</strong> FastAPI, Uvicorn</li>
  <li><strong>Orchestration:</strong> LangGraph + LangServe</li>
  <li><strong>LLM Client:</strong> LangChain (e.g., Groq / OpenAI compatible)</li>
  <li><strong>Database:</strong> Firebase Realtime Database</li>
  <li><strong>Satellite &amp; Carbon:</strong> Google Earth Engine</li>
  <li><strong>ML:</strong> scikit-learn (flood risk regression model)</li>
  <li><strong>Hosting:</strong> Google Cloud VM (Compute Engine)</li>
</ul>

<hr />

<h2>📂 Project Structure (key files)</h2>

<pre><code>.
├── server.py                 # FastAPI app &amp; LangGraph routes
├── graph.py                  # LangGraph definition for Field Agent
├── state.py                  # AgentState TypedDict / dataclass
├── nodes/
│   ├── fetch_nodes.py        # Fetch field, IoT, satellite, flood, carbon
│   ├── problem_nodes.py      # Detect problems from data
│   └── solution_node.py      # Plan solutions from problems
├── tools/
│   ├── firebase_tools.py     # RTDB fetch + save AIConsultations
│   ├── satellite_tools.py    # Earth Engine satellite indices
│   ├── flood_tools.py        # Flood ML model wrapper
│   └── carbon_tools.py       # Carbon from NDVI
├── config/
│   └── settings.py           # ENV variables (API keys, DEMO_MODE, etc.)
└── requirements.txt          # Python dependencies
</code></pre>

<hr />

<h2>⚙️ Setup &amp; Installation</h2>

<h3>1️⃣ Clone the repository</h3>
<pre><code>git clone &lt;YOUR_REPO_URL&gt;
cd &quot;Shonali desh&quot;
</code></pre>

<h3>2️⃣ Create &amp; activate virtual environment</h3>
<pre><code>python3 -m venv myvenv
source myvenv/bin/activate  # Linux / macOS
# .\myvenv\Scripts\activate  # Windows (PowerShell)
</code></pre>

<h3>3️⃣ Install dependencies</h3>
<pre><code>pip install -r requirements.txt
</code></pre>

<h3>4️⃣ Environment variables (.env)</h3>

<p>Create a file named <code>.env</code> in the project root:</p>

<pre><code>GROQ_API_KEY=&quot;your_groq_api_key&quot;
FIREBASE_CRED_PATH=&quot;/full/path/to/firebase-service-account.json&quot;
DEMO_MODE=&quot;false&quot;
GOOGLE_APPLICATION_CREDENTIALS=&quot;/full/path/to/earth-engine-service-account.json&quot;
</code></pre>

<p>
Also ensure your Google Cloud service account has access to
<strong>Earth Engine</strong> and your <strong>Firebase RTDB</strong> project.
</p>

<hr />

<h2>🚀 Run the Server (Local)</h2>

<pre><code>uvicorn server:app --host 0.0.0.0 --port 8000
</code></pre>

<p>Now you can visit:</p>

<ul>
  <li>API docs: <code>http://localhost:8000/docs</code></li>
  <li>LangServe playground: <code>http://localhost:8000/field_agent/playground/</code></li>
</ul>

<hr />

<h2>🧪 Core API Endpoints</h2>

<h3>1️⃣ POST <code>/run_once</code></h3>

<p>
Runs the full Field Agent pipeline once for a given farmer &amp; field,
and returns problems + solutions (and optionally more data if you expose it).
</p>

<h4>Request</h4>
<pre><code>POST /run_once
Content-Type: application/json

{
  "farmer_id": "farmer_102938",
  "field_id": "field_88421"
}
</code></pre>

<h4>Response (example)</h4>
<pre><code>{
  "problems": [
    "Soil moisture is low (15.8) compared to optimal range for rice.",
    "Nitrogen status is slightly deficient according to latest prediction."
  ],
  "solutions": [
    "Apply light irrigation in the early morning to reduce evaporation loss.",
    "Use a balanced nitrogen fertilizer at recommended dose instead of over-applying urea."
  ]
}
</code></pre>

<h3>2️⃣ LangServe Endpoint: <code>/field_agent/invoke</code></h3>

<p>
This is the generic LangGraph endpoint added via
<code>add_routes(app, field_agent_graph, path="/field_agent")</code>.
It accepts the whole <strong>AgentState</strong> as input and returns the full state.
Mainly used for development and advanced integrations.
</p>

<hr />

<h2>📡 Example Client (Python)</h2>

<pre><code>import requests

API_URL = "http://&lt;YOUR_VM_OR_LOCALHOST&gt;:8000/run_once"

payload = {
    "farmer_id": "farmer_102938",
    "field_id": "field_88421"
}

response = requests.post(API_URL, json=payload, timeout=60)

print("Status:", response.status_code)
print("Data:", response.json())
</code></pre>

<hr />

<h2>☁️ Deploy on Google Cloud VM (Quick Outline)</h2>

<ol>
  <li>Create a Compute Engine VM (Ubuntu, e.g. 2 vCPU, 4 GB RAM).</li>
  <li>SSH into the VM and install:
    <ul>
      <li>Python 3</li>
      <li>git</li>
      <li>virtualenv</li>
    </ul>
  </li>
  <li>Clone this repo and set up <code>myvenv</code> as shown above.</li>
  <li>Copy Firebase &amp; Earth Engine service account JSON files to the VM.</li>
  <li>Create a <code>.env</code> file with your keys and paths.</li>
  <li>Run with Uvicorn or Gunicorn:
    <pre><code>uvicorn server:app --host 0.0.0.0 --port 8000</code></pre>
  </li>
  <li>In the GCP console, open firewall rule for TCP port 8000, or put Nginx in front as a reverse proxy.</li>
</ol>

<hr />

<h2>📜 Firebase Data Model (Realtime Database)</h2>

<pre><code>Farmers
  └── farmer_554433
      ├── name: "Abdul Karim"
      ├── phone: "01799887766"
      ├── region: "Rajshahi"
      ├── ...
      └── Fields
          └── field_77711
              ├── fieldSize: "30 decimals"
              ├── cropType: "Wheat"
              ├── location: { lat, lon }
              ├── latestPrediction: { floodRisk, salinityRisk, nitrogenStatus, ... }
              ├── IoT
              │   └── SensorReadings
              │       ├── reading_...
              │       └── ...
              └── AIConsultations
                  └── &lt;auto_id&gt;
                      ├── problems: [ "string", "string", ... ]
                      ├── solutions: [ "string", "string", ... ]
                      └── carbon_data: { ...optional carbon payload... }
</code></pre>

<hr />

<h2>🤝 Contributing</h2>

<p>
Pull requests, issues, and feature suggestions are welcome — especially around:
</p>

<ul>
  <li>Better agronomic rules for Bangladeshi cropping systems</li>
  <li>Improved flood / salinity / nutrient models</li>
  <li>Better carbon estimation and MRV alignment</li>
  <li>Performance &amp; latency optimization on low-cost VMs</li>
</ul>

<hr />



