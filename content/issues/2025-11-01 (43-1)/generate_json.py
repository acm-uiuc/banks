#!/usr/bin/env python3
"""
Script to generate info JSONs for ACM@UIUC SIGs and committees.
Reads blurbs from ./*.yaml files and organization data from the API.
"""

import json
import os
import requests
import yaml
from pathlib import Path
import sys


def read_info_file(blurb_dir, filename):
    """Read the info from a YAML file in the raw_info directory."""
    filepath = blurb_dir / filename
    if filepath.exists():
        with open(filepath, 'r', encoding='utf-8') as f:
            try:
                data = yaml.safe_load(f)
                return data if data else {}
            except yaml.YAMLError as e:
                print(f"Error parsing YAML file {filename}: {e}")
                return {}
    return {}


def normalize_org_id(org_id):
    """Normalize organization ID to a safe filename (remove pipes, spaces to underscores, lowercase)."""
    # Remove pipes first, then replace spaces, then clean up multiple underscores
    normalized = org_id.replace("|", "").replace(" ", "_").lower()
    # Remove multiple consecutive underscores
    while "__" in normalized:
        normalized = normalized.replace("__", "_")
    return normalized.strip("_")


def get_filename_for_org(org_id):
    """Convert organization ID to expected YAML filename."""
    return normalize_org_id(org_id) + ".yaml"


def fetch_organizations():
    """Fetch organization data from the ACM API."""
    api_url = "https://core.acm.illinois.edu/api/v1/organizations"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error fetching data from API: {e}")
        return None


def create_info_json(org, blurb_dir):
    """Create the info JSON structure for an organization."""
    # Extract chair information
    chairs = []
    if "leads" in org:
        for lead in org["leads"]:
            chairs.append({
                "name": lead.get("name", ""),
                "title": lead.get("title", ""),
                "email": lead.get("username", "")
            })
    
    # Get the info from the YAML file
    filename = get_filename_for_org(org["id"])
    info_data = read_info_file(blurb_dir, filename)
    
    # Extract blurb (default to empty string if not present)
    blurb = info_data.get("blurb", "").strip()
    
    # Get website from API (for backwards compatibility)
    website = org.get("website", "")
    
    # Extract links from API
    links = {}
    if "links" in org and org["links"]:
        for link_obj in org["links"]:
            link_type = link_obj.get("type", "")
            link_url = link_obj.get("url", "")
            if link_type and link_url:
                # Convert link type to lowercase for consistency
                links[link_type.lower()] = link_url
    
    # Get status from YAML
    status = info_data.get("status", "")
    
    # Get name of subgroup
    name = org["id"]
    
    # Create the JSON structure
    info = {
        "name": name,
        "chairs": chairs,
        "website": website,
        "links": links,
        "blurb": blurb,
        "status": status
    }
    
    # Only add meeting_times if it exists in the YAML as a list
    meeting_times_data = info_data.get("meeting_times")
    if meeting_times_data and isinstance(meeting_times_data, list):
        processed_times = []
        for mt in meeting_times_data:
            if isinstance(mt, dict):  # Ensure each item in the list is a dictionary
                processed_times.append({
                    "date": mt.get("date", ""),
                    "start_time": mt.get("start_time", ""),
                    "end_time": mt.get("end_time", ""),
                    "location": mt.get("location", "")
                })
        
        if processed_times:
            # Save the whole list under the plural key
            info["meeting_times"] = processed_times
    
    return info


def main():
    """Main function to generate all info JSONs."""
    # Parse command-line arguments
    if len(sys.argv) < 2:
        print("Usage: python3 generate_json.py <base_directory>")
        print("Example: python3 generate_json.py vol43is1")
        sys.exit(1)
    
    base_dir = Path(sys.argv[1])
    
    if not base_dir.exists():
        print(f"Error: Directory '{base_dir}' does not exist.")
        sys.exit(1)
    
    blurb_dir = base_dir / "blurb"
    
    if not blurb_dir.exists():
        print(f"Error: Blurb directory '{blurb_dir}' does not exist.")
        sys.exit(1)
    
    # Create content/blurb directory if it doesn't exist
    output_dir = base_dir / "content" / "blurb"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Fetch organization data
    print("Fetching organization data from API...")
    organizations = fetch_organizations()
    
    if not organizations:
        print("Failed to fetch organization data. Exiting.")
        return
    
    print(f"Found {len(organizations)} organizations.")
    
    # Process each organization
    for org in organizations:
        org_id = org.get("id")
        if not org_id:
            continue
        
        print(f"Processing {org_id}...")
        
        # Create info JSON
        info = create_info_json(org, blurb_dir)
        
        # Write to file - normalize name by removing pipes and special chars
        # Thanks reflections_|_projections!
        output_filename = normalize_org_id(org_id) + ".json"
        output_path = output_dir / output_filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(info, f, indent=2, ensure_ascii=False)
        
        print(f"  Created {output_path}")
    
    print(f"\nDone! Generated {len(organizations)} JSON files in {output_dir}/")


if __name__ == "__main__":
    main()