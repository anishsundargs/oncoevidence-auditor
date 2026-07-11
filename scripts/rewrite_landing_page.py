from pathlib import Path

html = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>OncoEvidence Auditor | Cancer Gene Evidence Triage App</title>
  <meta name="description" content="OncoEvidence Auditor is a public-data cancer genomics app that audits gene-cancer hypotheses using PubMed, DepMap, cBioPortal, expression, survival, specificity, and therapeutic-relevance evidence layers.">
  <meta name="viewport" content="width=device-width, initial-scale=1">

  <script type="application/ld+json">
  {
    "@context": "https://schema.org",
    "@type": "SoftwareApplication",
    "name": "OncoEvidence Auditor",
    "applicationCategory": "ScientificApplication",
    "operatingSystem": "Web",
    "author": {
      "@type": "Person",
      "name": "Anish Sundar"
    },
    "description": "A contradiction-aware cancer gene hypothesis triage app using public-data evidence layers.",
    "url": "https://oncoevidence-auditor.streamlit.app",
    "codeRepository": "https://github.com/anishsundargs/oncoevidence-auditor"
  }
  </script>

  <style>
    body {
      font-family: Arial, sans-serif;
      max-width: 900px;
      margin: 48px auto;
      padding: 0 20px;
      line-height: 1.6;
      color: #111827;
      background: #f8fafc;
    }
    .card {
      background: white;
      border: 1px solid #e5e7eb;
      border-radius: 18px;
      padding: 28px;
      box-shadow: 0 10px 25px rgba(15, 23, 42, 0.08);
    }
    h1 {
      font-size: 2.4rem;
      margin-bottom: 0.5rem;
    }
    .subtitle {
      font-size: 1.15rem;
      color: #475569;
    }
    a.button {
      display: inline-block;
      margin: 10px 10px 10px 0;
      padding: 12px 18px;
      border-radius: 10px;
      background: #2563eb;
      color: white;
      text-decoration: none;
      font-weight: bold;
    }
    a.secondary {
      background: #0f172a;
    }
    code {
      background: #eef2ff;
      padding: 2px 5px;
      border-radius: 5px;
    }
  </style>
</head>

<body>
  <main class="card">
    <h1>OncoEvidence Auditor</h1>
    <p class="subtitle">
      A contradiction-aware cancer gene hypothesis triage app using public-data evidence layers.
    </p>

    <p>
      OncoEvidence Auditor is a computational biology and cancer genomics web app
      designed to evaluate gene-cancer hypotheses using multiple public evidence layers.
      The app integrates literature saturation, DepMap dependency, common-essential risk,
      lineage specificity, cBioPortal patient alteration data, expression evidence,
      survival/prognosis analysis, gene role annotation, pathway/function annotation,
      and therapeutic relevance.
    </p>

    <p>
      The goal is not to claim that a gene is automatically a valid therapeutic target.
      Instead, the app highlights contradictions between cell-line dependency, patient-level
      genomic evidence, specificity, biological role, and translational relevance.
    </p>

    <p>
      Recommended demo cases include <code>OIP5 / GBM</code> as a broad-essentiality
      contradiction case and <code>ERBB2 / Gastric cancer</code> as a patient-supported
      biomarker/subgroup case.
    </p>

    <p>
      <a class="button" href="https://oncoevidence-auditor.streamlit.app">Launch Live App</a>
      <a class="button secondary" href="https://github.com/anishsundargs/oncoevidence-auditor">View GitHub Repository</a>
    </p>

    <h2>Evidence layers</h2>
    <ul>
      <li>PubMed literature saturation</li>
      <li>DepMap CRISPR dependency</li>
      <li>Common-essential caution</li>
      <li>Lineage specificity</li>
      <li>cBioPortal patient alteration evidence</li>
      <li>Expression and survival/prognosis evidence</li>
      <li>Gene role, pathway, and therapeutic relevance annotation</li>
    </ul>

    <h2>Research-use disclaimer</h2>
    <p>
      This app is for research and educational use only. It is not a clinical decision-making tool.
    </p>
  </main>
</body>
</html>
"""

Path("docs").mkdir(exist_ok=True)
Path("docs/index.html").write_text(html, encoding="utf-8")
print("Rewrote docs/index.html as plain HTML.")