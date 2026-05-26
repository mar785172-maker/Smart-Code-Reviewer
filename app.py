import os
import ast
import json
import joblib
import streamlit as st
import database as db

# --- UI APP CONFIGURATION ---
st.set_page_config(page_title="AI Code Reviewer Architecture", layout="wide")
db.init_db()  # Self-instantiate local SQLite table

# --- DATA EXTRACTOR HELPER ---
def analyze_inline_code(code_string):
    """Parses raw text code to retrieve line blocks and features for live classification."""
    try:
        tree = ast.parse(code_string)
        lines = code_string.splitlines()
        extracted_blocks = []
        
        # Check for structural duplicates within the submitted code slice
        structure_map = {}
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                start = node.lineno
                end = getattr(node, 'end_lineno', start + 1)
                func_content = lines[start-1:end]
                
                # Metrics
                effective_lines = len([l for l in func_content if l.strip() and not l.strip().startswith("#")])
                branches = len([n for n in ast.walk(node) if isinstance(n, (ast.If, ast.For, ast.While, ast.ExceptHandler))])
                complexity = branches + 1
                
                # Structural fingerprint
                struct_signature = "".join([n.__class__.__name__ for n in ast.walk(node)])
                
                extracted_blocks.append({
                    "name": node.name,
                    "start": start,
                    "end": end,
                    "line_count": effective_lines,
                    "complexity": complexity,
                    "signature": struct_signature
                })
                structure_map[struct_signature] = structure_map.get(struct_signature, 0) + 1
                
        for b in extracted_blocks:
            b["is_duplicate"] = 1 if structure_map[b["signature"]] > 1 else 0
            
        return extracted_blocks
    except Exception as e:
        st.error(f"AST Parsing Malfunction: {e}")
        return []

# --- APPLICATION LAYOUT ---
st.title("🤖 Smart AI Code Reviewer Dashboard")
st.caption("AST-Driven Structural Analysis & Machine Learning Classification Engine")
st.markdown("---")

# Main Interface Split Columns
left_col, right_col = st.columns([1, 1])

# --- LEFT PANEL: INPUT & PERFORMANCE METRICS ---
with left_col:
    st.header("💻 Source Code Pipeline")
    user_code = st.text_area(
        "Paste target Python code below for inference processing:",
        height=280,
        placeholder="def legacy_processor(data):\n    if data is not None:\n        for item in data:\n            # Nesting deep...\n            print(item)"
    )
    
    trigger_scan = st.button("🚀 Execute Code Analysis Pipeline", use_container_width=True)
    
    st.markdown("---")
    st.header("📊 Model Metrics Engine")
    
    # Load and display pre-calculated performance profiles from disk
    if os.path.exists("model_metrics.json"):
        with open("model_metrics.json", "r") as f:
            metrics_data = json.load(f)
        
        m_col1, m_col2, m_col3, m_col4 = st.columns(4)
        m_col1.metric("Accuracy", f"{metrics_data['accuracy']*100:.1f}%")
        m_col2.metric("Precision", f"{metrics_data['precision']:.2f}")
        m_col3.metric("Recall", f"{metrics_data['recall']:.2f}")
        m_col4.metric("F1-Score", f"{metrics_data['f1_score']:.2f}")
        
        with st.expander("Show Confusion Matrix"):
            st.write(metrics_data["confusion_matrix"])
    else:
        st.warning("No performance profile metrics payload located on disk. Run train_model.py to compile performance artifacts.")

# --- RIGHT PANEL: LIVE EXTRAS & RESULTS ---
with right_col:
    st.header("🔍 Analytical Structural Audit")
    
    if trigger_scan and user_code.strip():
        functions_found = analyze_inline_code(user_code)
        
        if not functions_found:
            st.info("No structural function elements detected in the provided code snippet.")
        else:
            detected_smells = []
            suggestions = []
            
            # Load trained logic model if it exists
            if os.path.exists("code_smell_model.pkl"):
                clf = joblib.load("code_smell_model.pkl")
            else:
                clf = None
                st.warning("Classification engine file missing. Using structural metric fallbacks.")
            
            for f in functions_found:
                st.markdown(f"### Function Block: {f['name']}() (Lines {f['start']}-{f['end']})")
                
                # Check ML prediction or structural fallbacks
                is_smelly_prediction = 0
                if clf:
                    # Input feature shape matches training: [line_count, complexity_score]
                    is_smelly_prediction = clf.predict([[f["line_count"], f["complexity"]]])[0]
                
                # Define specific rules to highlight detected issues
                has_smell = False
                
                # 1. Complex Functions
                if f["complexity"] > 7 or (clf and is_smelly_prediction and f["complexity"] > 4):
                    has_smell = True
                    detected_smells.append(f"Complex Function ({f['name']})")
                    sug = f"Simplify branches or implement early returns in {f['name']}()."
                    suggestions.append(sug)
                    st.error(f"🔴 Complex Function Detected (Complexity Index: {f['complexity']}): {sug}")
                
                # 2. Long Functions
                if f["line_count"] > 40 or (clf and is_smelly_prediction and f["line_count"] > 25):
                    has_smell = True
                    detected_smells.append(f"Long Function ({f['name']})")
                    sug = f"Deconstruct functional components of {f['name']}() into smaller helpers."
                    suggestions.append(sug)
                    st.info(f"🔵 Long Function Detected ({f['line_count']} lines): {sug}")
                
                # 3. Duplicate Logic Structure
                if f["is_duplicate"] == 1:
                    has_smell = True
                    detected_smells.append(f"Duplicate Structure ({f['name']})")
                    sug = f"Consolidate structural duplicate variations of {f['name']}() into a shared utility function."
                    suggestions.append(sug)
                    st.warning(f"🟡 Duplicate Code Architecture Signature Detected: {sug}")
                    
                if not has_smell:
                    st.success(f"🟢 Function structure {f['name']}() satisfies standard code metrics.")
            
            # Database Persistence Log Execution
            db.log_scan_session(user_code, detected_smells, suggestions)
            st.toast("Scan metrics successfully logged into local SQLite database store.", icon="💾")
            
    elif trigger_scan:
        st.error("Input pipeline container blank. Enter valid code context to proceed with evaluation.")
        
    # Historical session viewer block
    with st.expander("📚 View Local SQLite Execution History Logs"):
        history = db.fetch_history()
        if history:
            for item in history[:5]: # Show latest 5 logs
                st.write(f"[{item[1]}] Log ID: {item[0]} | Detected Smells: {item[2]}")
        else:
            st.text("No data items logged inside current runtime database configuration.")