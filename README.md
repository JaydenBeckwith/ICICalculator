# ICICalculator

Immune Checkpoint Inhibitor (ICI) Calculator - a dashboard visualiser for determining patient response rates based on cancer type, line of therapy, and treatment regimen.

---

## Overview
ICICalculator is designed to make exploratory analysis of immune checkpoint inhibitor (ICI) clinical outcomes easier.  
It provides utilities to:
- Filter clinical trial datasets by cancer type and line of therapy.
- Resolve metric suffixes (e.g., ORR, PFS, OVS) into column identifiers.
- Reshape trial data into a plotting-friendly format for regimen comparisons.

---


##  Installation
Clone the repository and install dependencies:

```bash
git clone https://github.com/yourusername/ICICalculator.git
cd ICICalculator
pip install -r requirements.txt 
```
## Run the app 

```bash
python3 app.py
```

## Run tests 

```bash
python -m pytest tests/
```

