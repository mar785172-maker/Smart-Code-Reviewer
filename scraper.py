import os
import time
import random
import requests

# --- CONFIGURATION ---
# Change this path if your Flash Drive has a different letter mount on Windows/Linux
DATASET_DIR = "D:/ML_Dataset/raw_files/"
TARGET_LANG = "python"
MAX_FILES = 50  # Modest target to respect strict network limits and storage
DELAY_RANGE = (3, 7)  # Adaptive delay in seconds to evade anti-bot blocks

# Rotating standard User-Agents to prevent generic script blocking
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/119.0"
]

def init_storage():
    if not os.path.exists(DATASET_DIR):
        os.makedirs(DATASET_DIR)
        print(f"[INFO] Created dataset directory on Flash Drive: {DATASET_DIR}")

def fetch_public_python_repos():
    print("[INFO] Querying public GitHub repositories...")
    url = "https://api.github.com/search/repositories?q=language:python&sort=stars&order=desc"
    headers = {"User-Agent": random.choice(USER_AGENTS)}
    
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            return response.json().get("items", [])
        else:
            print(f"[WARNING] Failed to fetch repos. Status Code: {response.status_code}")
            return []
    except Exception as e:
        print(f"[ERROR] Network error during repo fetch: {e}")
        return []

def download_raw_files(repos):
    file_count = 0
    init_storage()
    
    for repo in repos:
        if file_count >= MAX_FILES:
            break
            
        repo_name = repo["full_name"]
        print(f"[INFO] Inspecting repository: {repo_name}")
        
        # Look into the contents of the main branch
        search_url = f"https://api.github.com/repos/{repo_name}/contents"
        headers = {"User-Agent": random.choice(USER_AGENTS)}
        
        try:
            time.sleep(random.uniform(*DELAY_RANGE))
            res = requests.get(search_url, headers=headers, timeout=15)
            if res.status_code != 200:
                continue
                
            contents = res.json()
            for item in contents:
                if isinstance(item, dict) and item.get("name", "").endswith(".py") and item.get("download_url"):
                    raw_url = item["download_url"]
                    
                    # Fetch raw python script
                    time.sleep(random.uniform(*DELAY_RANGE))
                    file_res = requests.get(raw_url, headers=headers, timeout=15)
                    
                    if file_res.status_code == 200:
                        filename = f"repo_{repo['id']}_{item['name']}"
                        filepath = os.path.join(DATASET_DIR, filename)
                        
                        with open(filepath, "w", encoding="utf-8") as f:
                            f.write(file_res.text)
                        
                        file_count += 1
                        print(f"[SUCCESS] Downloaded ({file_count}/{MAX_FILES}): {filename}")
                        
                        if file_count >= MAX_FILES:
                            break
        except Exception as e:
            print(f"[WARNING] Error processing repo {repo_name}: {e}")
            # Cool-down delay if network anomaly is encountered
            time.sleep(10)
            continue

if __name__ == "__main__":
    print("=== STARTING DATA COLLECTION ===")
    repositories = fetch_public_python_repos()
    if repositories:
        download_raw_files(repositories)
    print("=== DATA COLLECTION COMPLETED ===")