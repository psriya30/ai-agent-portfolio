# 🧠 Resume Analyzer Agent (Day 06)

This project builds a Resume Analyzer Agent with two modes:

## 🚀 Mode 1: Structured Resume
- Uses rule-based extraction
- No LLM required
- Validates mobile numbers
- Merges skills
- Strict output format

## 🚀 Mode 2: Messy Resume (Regex + LLM Hybrid)
- Regex for email, mobile, year ranges
- LLM (phi3 via Ollama) for semantic extraction
- Merges overlapping experience
- Strict output formatting

## 📌 Features
- Phone validation (Indian mobile)
- Skills merging + deduplication
- Experience calculation
- Strict "Not mentioned" fallback
- Clean formatted output

## 🛠 Tech Used
- Python
- Regex (`re`)
- smolagents
- Ollama (phi3)

## ▶️ How to Run

```bash
python resume_analyzer.py