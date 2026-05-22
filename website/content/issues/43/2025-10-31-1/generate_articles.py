#!/usr/bin/env python3
"""
Script to convert markdown articles to YAML format for Banks of the Boneyard.
Reads all markdown files from {article_dir}/articles/
and converts them to YAML format in {article_dir}/content/articles/
"""

import yaml
import re
import sys
from pathlib import Path


def parse_markdown_article(markdown_content):
    """
    Parse markdown article format into components.
    
    Expected format:
    title: <title>
    authors: ['Author 1', 'Author 2']
    
    <content>
    """
    lines = markdown_content.strip().split('\n')
    
    title = None
    authors = []
    content_start_idx = 0
    
    # Parse the header section
    for i, line in enumerate(lines):
        line = line.strip()
        
        if line.startswith('title:'):
            title = line.split('title:', 1)[1].strip()
        elif line.startswith('authors:'):
            # Parse the Python list format
            authors_str = line.split('authors:', 1)[1].strip()
            # Use eval to parse the list (safe since we control the input)
            try:
                authors = eval(authors_str)
                if isinstance(authors, str):
                    authors = [authors]
            except:
                # Fallback: try to parse manually
                authors_str = authors_str.strip('[]')
                authors = [a.strip().strip("'\"") for a in authors_str.split(',')]
        elif line == '' and i > 0:
            # Empty line indicates end of header
            content_start_idx = i + 1
            break
        else:
            # If we haven't found an empty line and we're past the first few lines,
            # assume header is done. This handles files with no authors.
            if i > 5: # Arbitrary cutoff, adjust if headers can be longer
                content_start_idx = i
                break
    
    # Get the content (everything after the header)
    content = '\n'.join(lines[content_start_idx:]).strip()
    
    return {
        'title': title or "Untitled", # Add a default title
        'authors': authors or ["Unknown"], # Add a default author
        'content': content
    }


def convert_to_yaml(parsed_data):
    """
    Convert parsed article data to YAML format.
    
    Output format:
    title: 
      <title>
    author:
      - Author 1
      - Author 2
    
    content: |
      <content>
    """
    yaml_data = {
        'title': parsed_data['title'],
        'author': parsed_data['authors'],
        'content': parsed_data['content']
    }
    
    # Use custom YAML dumping for better formatting
    output = []
    output.append('title:')
    output.append(f'  {yaml_data["title"]}')
    
    output.append('author:')
    if yaml_data['author']:
        for author in yaml_data['author']:
            output.append(f'  - {author}')
    else:
        output.append('  - Unknown') # Handle empty author list
    output.append('')
    
    output.append('content: |')
    # Indent each line of content by 2 spaces
    if yaml_data['content']:
        for line in yaml_data['content'].split('\n'):
            output.append(f'  {line}')
    else:
        output.append('  (No content)') # Handle empty content
    output.append('')
    
    return '\n'.join(output)


def process_markdown_file(input_path, output_dir):
    """
    Process a single markdown file and convert it to YAML.
    
    Args:
        input_path: Path to the input markdown file
        output_dir: Directory where the YAML file should be written
    """
    input_path = Path(input_path)
    output_dir = Path(output_dir)
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Read the markdown file
    with open(input_path, 'r', encoding='utf-8') as f:
        markdown_content = f.read()
    
    # Parse the markdown
    parsed_data = parse_markdown_article(markdown_content)
    
    # Convert to YAML
    yaml_content = convert_to_yaml(parsed_data)
    
    # Write to output file (same name but .yaml extension)
    output_filename = input_path.stem + '.yaml'
    output_path = output_dir / output_filename
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(yaml_content)
    
    print(f"Converted {input_path.name} -> {output_path}")
    return output_path


def main():
    """Main function to process markdown articles."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Convert all markdown articles in a directory to YAML format for Banks of the Boneyard'
    )
    parser.add_argument(
        'article_dir',
        help='Input directory (e.g., "my_newspaper") containing an "articles" subdirectory with .md files'
    )
    
    args = parser.parse_args()
    
    article_dir_path = Path(args.article_dir)
    input_dir = article_dir_path / 'articles'
    output_dir = article_dir_path / 'content' / 'articles'
    
    # Check if source directory exists
    if not input_dir.is_dir():
        print(f"Error: Input directory not found: {input_dir}", file=sys.stderr)
        print("Please make sure your article directory contains an 'articles' subdirectory.", file=sys.stderr)
        sys.exit(1)
        
    # Find all .md files in the input directory
    md_files = list(input_dir.glob('*.md'))
    
    if not md_files:
        print(f"No .md files found in {input_dir}")
        return

    print(f"Found {len(md_files)} markdown file(s) in {input_dir}...")
    
    # Process each input file
    processed_count = 0
    for input_file in md_files:
        try:
            process_markdown_file(input_file, output_dir)
            processed_count += 1
        except Exception as e:
            print(f"Error processing {input_file.name}: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc(file=sys.stderr)
    
    print(f"\n✓ Conversion complete! {processed_count}/{len(md_files)} files converted.")
    print(f"YAML files written to {output_dir}")


if __name__ == '__main__':
    main()
