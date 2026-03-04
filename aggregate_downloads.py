import json
import os
import urllib.request
import urllib.error

def format_number(n):
    if n < 1000:
        return str(n)
    elif n < 1000000:
        if n % 1000 == 0:
            return f"{n // 1000}k"
        return f"{n / 1000:.1f}k"
    else:
        if n % 1000000 == 0:
            return f"{n // 1000000}M"
        return f"{n / 1000000:.1f}M"

def fetch_modrinth(project_id):
    url = f"https://api.modrinth.com/v2/project/{project_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'github-action-download-aggregator'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return int(data.get('downloads', 0))
    except Exception as e:
        print(f"Error fetching Modrinth project {project_id}: {e}")
        return 0

def fetch_curseforge(project_id):
    url = f"https://api.cfwidget.com/minecraft/mc-mods/{project_id}"
    req = urllib.request.Request(url, headers={'User-Agent': 'github-action-download-aggregator'})
    try:
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read().decode())
            return int(data.get('downloads', {}).get('total', 0))
    except Exception as e:
        print(f"Error fetching CurseForge project {project_id} via CFWidget API: {e}")
        return 0

def main():
    config_file = "config.json"
    if not os.path.exists(config_file):
        print(f"Config file '{config_file}' not found.")
        return

    with open(config_file, "r") as f:
        config = json.load(f)
        
    total_downloads = 0
    for project in config.get("projects", []):
        platform = project.get("platform", "").lower()
        project_id = project.get("project_id")
        
        if not platform or not project_id:
            continue
            
        downloads = 0
        if platform == "modrinth":
            downloads = fetch_modrinth(project_id)
        elif platform == "curseforge":
            downloads = fetch_curseforge(project_id)
        else:
            print(f"Unknown platform: {platform}")
            continue
            
        print(f"Fetched {downloads} downloads for {platform} project {project_id}")
        total_downloads += downloads
        
    print(f"Total downloads aggregated: {total_downloads}")
    
    # Prepares output json for shields.io endpoints
    # Use config schema options if needed, defaults are hardcoded below
    output_data = {
        "schemaVersion": 1,
        "label": config.get("badge", {}).get("label", "downloads"),
        "message": format_number(total_downloads),
        "color": config.get("badge", {}).get("color", "blue")
    }
    
    with open("downloads_badge.json", "w") as f:
        json.dump(output_data, f, indent=2)
        
    print(f"Successfully wrote 'downloads_badge.json' with message: {output_data['message']}")

if __name__ == "__main__":
    main()
