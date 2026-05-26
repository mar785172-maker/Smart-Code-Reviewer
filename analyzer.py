import os
import ast
import csv

# --- CONFIGURATION ---
DATASET_DIR = "D:/ML_Dataset/raw_files/"
OUTPUT_CSV = "D:/ML_Dataset/extracted_features.csv"

class CodeSmellExtractor(ast.NodeVisitor):
    def init(self, source_code):
        self.source_lines = source_code.splitlines()
        self.features = []
        self.all_function_structures = []

    def visit_FunctionDef(self, node):
        # 1. Calculate Long Function Metric (lines excluding blank spaces/pure comments)
        start_line = node.lineno
        end_line = getattr(node, 'end_lineno', start_line + 1)
        func_lines = self.source_lines[start_line - 1:end_line]
        
        effective_line_count = 0
        for line in func_lines:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                effective_line_count += 1

        # 2. Calculate Cyclomatic Complexity / Nesting depth estimation
        # We count branch decisions: If, For, While, Except
        branch_nodes = 0
        max_depth = 0
        
        for sub_node in ast.walk(node):
            if isinstance(sub_node, (ast.If, ast.For, ast.While, ast.ExceptHandler)):
                branch_nodes += 1
        
        # 3. Structural Hash for Duplicate Logic Identification
        # Strip specific variable/function naming to catch structural duplication
        structural_dump = ""
        for sub_node in ast.walk(node):
            structural_dump += sub_node.__class__.__name__
        struct_hash = hash(structural_dump)
        self.all_function_structures.append((node.name, struct_hash))

        # Store intermediate features per function
        self.features.append({
            "function_name": node.name,
            "line_count": effective_line_count,
            "complexity_score": branch_nodes + 1,  # Base complexity of 1
            "structural_hash": struct_hash,
            "is_smelly": 0  # Initial placeholder rule for synthetic dataset labeling
        })
        self.generic_visit(node)

def analyze_file(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            code_text = f.read()
        
        tree = ast.parse(code_text)
        extractor = CodeSmellExtractor(code_text)
        extractor.visit(tree)
        return extractor.features
    except Exception:
        # Gracefully skip broken code syntaxes or parsing failures
        return []

def main():
    print("[INFO] Processing files and extracting features via AST...")
    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Source folder {DATASET_DIR} does not exist.")
        return

    all_features = []
    all_hashes = {}

    # Read and parse everything from Flash Drive
    for file in os.listdir(DATASET_DIR):
        if file.endswith(".py"):
            full_path = os.path.join(DATASET_DIR, file)
            file_features = analyze_file(full_path)
            all_features.extend(file_features)

    # Label data for classification training using standard heuristic thresholds
    # High complexity (>7), long functions (>40), or matching structural hashes (duplicates)
    for feat in all_features:
        h = feat["structural_hash"]
        all_hashes[h] = all_hashes.get(h, 0) + 1

    for feat in all_features:
        is_duplicate = 1 if all_hashes[feat["structural_hash"]] > 1 else 0
        if feat["complexity_score"] > 7 or feat["line_count"] > 40 or is_duplicate == 1:
            feat["is_smelly"] = 1

    # Write out compact dataset back to Flash Drive
    fields = ["line_count", "complexity_score", "is_smelly"]
    with open(OUTPUT_CSV, "w", newline="", encoding="utf-8") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        for feat in all_features:
            writer.writerow(feat)

    print(f"[SUCCESS] Feature Extraction completed. Metrics written to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()