#!/usr/bin/env python3
"""
Generate Banks of the Boneyard newspaper LaTeX files from YAML/JSON sources
"""

import json
import os
import yaml
import re
from pathlib import Path
from datetime import datetime

class NewspaperGenerator:
    def __init__(self, base_dir, print_mode=False):
        self.base_dir = Path(base_dir)
        self.config = self.load_config()
        self.volume = self.config['volume']
        self.issue = self.config['issue']
        self.print_mode = print_mode 
        
    def load_config(self):
        """Load the configuration file"""
        config_path = self.base_dir / 'config.yaml'
        with open(config_path, 'r') as f:
            return yaml.safe_load(f)
    
    def load_article(self, article_name):
        """Load an article YAML file"""
        article_path = self.base_dir / 'content' / 'articles' / f'{article_name}.yaml'
        with open(article_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def normalize_org_name(self, org_name):
        """Normalize organization name to match filename (remove pipes, clean underscores). This is mainly for RP"""

        normalized = org_name.replace("|", "").replace(" ", "_").lower()
        while "__" in normalized:
            normalized = normalized.replace("__", "_")
        return normalized.strip("_")
    
    def load_blurb(self, org_name):
        """Load organization info from JSON"""
        normalized_name = self.normalize_org_name(org_name)
        
        json_path = self.base_dir / 'content' / 'blurb' / f'{normalized_name}.json'
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        # if i'm stupid it'll take this code path
        json_path = self.base_dir / 'content' / 'blurb' / f'{org_name}.json'
        if json_path.exists():
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        
        return None
    
    def load_events(self):
        """Load events data"""
        events_path = self.base_dir / 'events.yaml'
        if events_path.exists():
            with open(events_path, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return {'events': []}
    
    def markdown_to_latex(self, markdown_text, is_article=False):
        """Convert markdown to LaTeX
        
        Args:
            markdown_text: The markdown text to convert
            is_article: If True and in print_mode, hyperlinks will be converted to QR codes
        """
        if not markdown_text:
            return ""
        
        text = markdown_text
        
        # Convert <br/> and <br> tags to line breaks - do this early before escaping
        text = re.sub(r'<br\s*/?>', r'§§§LINEBREAK§§§', text, flags=re.IGNORECASE)
        
        # Headers - do first before escaping
        text = re.sub(r'^### (.+)$', r'§§§SUBSUB:\1§§§', text, flags=re.MULTILINE)
        text = re.sub(r'^## (.+)$', r'§§§SUB:\1§§§', text, flags=re.MULTILINE)
        text = re.sub(r'^# (.+)$', r'§§§SEC:\1§§§', text, flags=re.MULTILINE)
        
        # Bold and italic - use placeholders
        bold_pattern = r'\*\*(.+?)\*\*'
        text = re.sub(bold_pattern, r'§§§BOLD:\1§§§', text)
        
        # Replace *text* with italic placeholder
        italic_pattern = r'\*(.+?)\*'
        text = re.sub(italic_pattern, r'§§§ITALIC:\1§§§', text)
        
        # Images - convert markdown image syntax to placeholders FIRST (before links)
        image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
        def replace_image(match):
            alt_text = match.group(1)
            image_path = match.group(2)
            # Remove ./ prefix if present
            if image_path.startswith('./'):
                image_path = image_path[2:]
            # Store the image path with a special marker to avoid escaping underscores later
            return f'§§§IMAGE:{image_path}§§§'
        text = re.sub(image_pattern, replace_image, text)
        
        # Links - convert markdown links to placeholders
        link_pattern = r'\[([^\]]+)\]\(([^\)]+)\)'
        text = re.sub(link_pattern, r'§§§LINK:\1§|§\2§§§', text)
        
        # Lists - convert bullet points to placeholders
        in_list = False
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            if re.match(r'^\s*[\*\-]\s+', line):
                if not in_list:
                    new_lines.append('§§§BEGINLIST§§§')
                    in_list = True
                item = re.sub(r'^\s*[\*\-]\s+', '', line)
                new_lines.append(f'§§§ITEM:{item}§§§')
            else:
                if in_list:
                    new_lines.append('§§§ENDLIST§§§')
                    in_list = False
                new_lines.append(line)
        if in_list:
            new_lines.append('§§§ENDLIST§§§')
        text = '\n'.join(new_lines)
        
        # Now escape special LaTeX characters
        special_chars = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '|': '\\textbar{}',  # Pipe character needs to be \textbar to render correctly
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}'
        }
        
        # Don't escape special characters inside href URLs or image paths
        # First, temporarily protect href content
        href_pattern = r'§§§LINK:(.+?)§\|§(.+?)§§§'
        hrefs = []
        def save_href(match):
            hrefs.append((match.group(1), match.group(2)))
            return f'§§§HREFPLACEHOLDER{len(hrefs)-1}§§§'
        text = re.sub(href_pattern, save_href, text)
        
        # Also protect image paths from escaping
        image_placeholder_pattern = r'§§§IMAGE:(.+?)§§§'
        images = []
        def save_image(match):
            images.append(match.group(1))
            return f'§§§IMAGEPLACEHOLDER{len(images)-1}§§§'
        text = re.sub(image_placeholder_pattern, save_image, text)
        
        for char, replacement in special_chars.items():
            text = text.replace(char, replacement)
        
        # Now convert placeholders to actual LaTeX
        text = re.sub(r'§§§SUBSUB:(.+?)§§§', r'\\subsubsection*{\1}', text)
        text = re.sub(r'§§§SUB:(.+?)§§§', r'\\subsection*{\1}', text)
        text = re.sub(r'§§§SEC:(.+?)§§§', r'\\section*{\1}', text)
        text = re.sub(r'§§§BOLD:(.+?)§§§', r'\\textbf{\1}', text)
        text = re.sub(r'§§§ITALIC:(.+?)§§§', r'\\textit{\1}', text)
        
        # Convert line break placeholders to LaTeX line breaks
        # Using \vspace{0.5em} which adds vertical space and works reliably in all contexts
        text = text.replace('§§§LINEBREAK§§§', '\\vspace{0.5em}')
        
        # Restore hrefs and handle # in URLs
        def restore_href(match):
            idx = int(match.group(1))
            link_text, url = hrefs[idx]
            # In URLs, # needs to stay as # not \# - unescape it
            url = url.replace('\\#', '#')
            
            # In print mode for articles, create QR codes instead of hyperlinks
            if self.print_mode and is_article:
                # Escape special characters in URL for LaTeX caption
                caption_url = url.replace('_', '\\_').replace('#', '\\#').replace('%', '\\%')
                # Generate QR code with caption
                return (f'\\begin{{center}}'
                       f'\\begingroup'
                       f'\\color{{black}}'
                       f'\\qrcode[height=0.8in,hyperlink=false]{{{url}}}'
                       f'\\endgroup\\\\'
                       f'\\vspace{{0.15cm}}'
                       f'{{\\small {caption_url}}}'
                       f'\\end{{center}}')
            else:
                return f'\\href{{{url}}}{{{link_text}}}'
        text = re.sub(r'§§§HREFPLACEHOLDER(\d+)§§§', restore_href, text)
        
        # Restore image placeholders
        def restore_image(match):
            idx = int(match.group(1))
            return f'§§§IMAGE:{images[idx]}§§§'
        text = re.sub(r'§§§IMAGEPLACEHOLDER(\d+)§§§', restore_image, text)
        
        # Convert image placeholders - note: captions are handled separately as italic text following the image
        text = re.sub(r'§§§IMAGE:(.+?)§§§', r'\\begin{center}\\includegraphics[width=0.9\\columnwidth]{./articles/images/\1}\\end{center}', text)
        text = text.replace('§§§BEGINLIST§§§', '\\begin{itemize}')
        text = text.replace('§§§ENDLIST§§§', '\\end{itemize}')
        text = re.sub(r'§§§ITEM:(.+?)§§§', r'\\item \1', text)
        
        return text
    
    def escape_special_chars(self, text):
        """Escape special LaTeX characters in plain text (for titles, etc.)"""
        if not text:
            return ""
        
        replacements = {
            '&': '\\&',
            '%': '\\%',
            '$': '\\$',
            '#': '\\#',
            '_': '\\_',
            '|': '\\textbar{}',
            '~': '\\textasciitilde{}',
            '^': '\\textasciicircum{}'
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def generate_letter_tex(self):
        """Generate the Letter from the Chair"""
        # Get the Letter from the Chair
        
        lftc = self.config["letter_from_the_chair"]
        article = self.load_article(lftc)
        
        if not article:
            return ''
        
        content = []
        
        # Add needspace to prevent orphaned headers
        content.append('\\needspace{5\\baselineskip}')
        content.append('\\vfill')
        content.append(f'\\label{{article:{lftc}}}')
        
        # Article title and byline
        title = article.get('title', 'Untitled').strip()
        title = self.escape_special_chars(title)  # Escape special characters in title
        authors = article.get('author', article.get('authors', []))
        if isinstance(authors, str):
            authors = [authors]
        
        # Format the byline
        if authors:
            author_str = ', '.join(authors)
            content.append(f'\\byline{{\\textbf{{\\Large {title}}}}}{{{author_str}}}')
        else:
            content.append(f'\\headline{{\\textbf{{\\Large {title}}}}}')
        
        # Article content
        article_content = article.get('content', '')
        latex_content = self.markdown_to_latex(article_content, is_article=True)
        content.append(latex_content)
        
        # Close article
        content.append('\\closearticle\n')
        content.append('\\vfill')
        content.append('\\vfill')
        
        return '\n\n'.join(content)
    
    def generate_articles_tex(self):
        """Generate the articles LaTeX file"""
        content = []
        
        # Skip first article (Letter from the Chair) - start from index 1
        for article_name in self.config.get('article_order', []):
            try:
                article = self.load_article(article_name)
            except Exception as e:
                print(f"Warning: Could not load article '{article_name}': {e}")
                continue
            
            if not article:
                continue
            
            # Add needspace to prevent orphaned headers (ensure at least 5 lines stay together)
            content.append('\\needspace{5\\baselineskip}')
            
            # Add label for TOC reference
            content.append(f'\\label{{article:{article_name}}}')
            
            # Article title and byline
            title = article.get('title', 'Untitled').strip()
            title = self.escape_special_chars(title)
            authors = article.get('author', article.get('authors', []))
            if isinstance(authors, str):
                authors = [authors]
            
            # Format the byline
            if authors:
                author_str = ', '.join(authors)
                content.append(f'\\byline{{\\textbf{{\\Large {title}}}}}{{{author_str}}}')
            else:
                content.append(f'\\headline{{\\textbf{{\\Large {title}}}}}')
            
            # Article content
            article_content = article.get('content', '')
            latex_content = self.markdown_to_latex(article_content, is_article=True)
            content.append(latex_content)
            
            # Close article
            content.append('\\closearticle\n')
        
        return '\n\n'.join(content)
    
    
    def generate_events_tex(self):
        """Generate the events section LaTeX file"""
        events_data = self.load_events()
        content = []
        
        content.append('\\headline{\\textbf{\\LARGE Upcoming Events}}')
        content.append('\\vspace{0.05cm}')
        content.append('')
        
        events = events_data.get('events', [])
        if not events:
            content.append('\\noindent\\textit{Check the ACM Discord and website for the latest event information!}')
        else:
            for i, event in enumerate(events):
                event_name = event.get('name', 'Unnamed Event')
                date = event.get('date', 'TBD')
                time = event.get('time', '')
                location = event.get('location', '')
                description = event.get('description', '')
                
                # Event name in bold with noindent
                content.append(f'\\noindent\\textbf{{{event_name}}}')
                content.append('')
                
                # Date, time, location on separate lines with bullet points for better readability
                info_parts = []
                if date:
                    info_parts.append(date)
                if time:
                    info_parts.append(time)
                if location:
                    info_parts.append(location)
                
                if info_parts:
                    # Use a single line with middle dots for compact but readable formatting
                    content.append('\\noindent\\textit{' + ' $\\cdot$ '.join(info_parts) + '}')
                    content.append('')
                
                if description:
                    content.append('\\noindent\\small ' + description)
                    content.append('')
                
                # Add spacing between events, but not after the last one
                if i < len(events) - 1:
                    content.append('\\vspace{0.25cm}')
                    content.append('')
        
        content.append('\\vspace{0.2cm}')
        
        return '\n'.join(content)
    
    def format_meeting_time(self, meeting_time):
        """Format meeting time from JSON data"""
        if not meeting_time:
            return ""
        
        date = meeting_time.get('date', '').title()
        start = meeting_time.get('start_time', '')
        end = meeting_time.get('end_time', '')
        location = meeting_time.get('location', '')
        
        # Convert minutes to time format if needed
        if isinstance(start, int):
            start_hour = start // 60
            start_min = start % 60
            am_pm = 'PM' if start_hour >= 12 else 'AM'
            if start_hour > 12:
                start_hour -= 12
            elif start_hour == 0:
                start_hour = 12
            start = f"{start_hour}:{start_min:02d} {am_pm}"
        
        if isinstance(end, int):
            end_hour = end // 60
            end_min = end % 60
            am_pm = 'PM' if end_hour >= 12 else 'AM'
            if end_hour > 12:
                end_hour -= 12
            elif end_hour == 0:
                end_hour = 12
            end = f"{end_hour}:{end_min:02d} {am_pm}"
        
        parts = []
        if date:
            parts.append(date + 's')
        if start and end:
            parts.append(f"{start}--{end}")
        elif start:
            parts.append(start)
        if location:
            parts.append(location)
        
        return ', '.join(parts)
    
    def generate_directory_tex(self):
        """Generate the directory section LaTeX file"""
        # Import moved inside method for encapsulation, 
        # or you can move it to the top of your file.
        from collections import defaultdict

        content = []
        
        content.append('\\newpage')
        content.append('\\label{directory}')
        
        content.append('\\begin{center}')
        content.append('\\textbf{\\underline{\\Huge ACM @ UIUC Directory}}')
        content.append('\\end{center}')
        content.append('\\vspace{0.3cm}')
        content.append('')
        
        content.append('\\begin{multicols}{2}')
        content.append('')
        
        processed_count = 0
        for org_name in self.config.get('directory_order', []):
            blurb_data = self.load_blurb(org_name)
            if not blurb_data:
                print(f"Warning: No data found for {org_name}")
                continue
            
            status = blurb_data.get('status', '')
            if status == 'dormant' or status == 'dormat':
                continue
            
            if not blurb_data.get('blurb', '').strip():
                continue
            
            if processed_count > 0:
                content.append('\\noindent\\rule{\\columnwidth}{0.4pt}')
                content.append('\\vspace{0.3cm}')
                content.append('')
            
            processed_count += 1
            
            display_name = blurb_data.get("name")
            if org_name == 'reflections_projections':
                display_name = r'Reflections \textbar{} Projections'
            
            logo_path = self.base_dir / 'logo' / f'{org_name}.png'
            if not logo_path.exists():
                logo_path = self.base_dir / 'logo' / f'{org_name}.jpg'
            if not logo_path.exists():
                logo_path = self.base_dir / 'logo' / f'{org_name}.jpeg'
            
            content.append(r'\noindent')
            content.append('\\begin{minipage}{\\columnwidth}')
            
            if logo_path.exists():
                rel_logo_path = f'./logo/{logo_path.name}'
                content.append('\\begin{center}')
                content.append(f'\\includegraphics[width=0.35\\columnwidth]{{{rel_logo_path}}}')
                content.append('\\end{center}')
                content.append('\\vspace{0.05cm}')
            
            content.append(f'\\subsection*{{{display_name}}}')
            chairs = blurb_data.get('chairs', [])
            valid_chairs = [c for c in chairs if c.get('name')]

            if valid_chairs:
                # Get all distinct titles, including empty string for 'no title'
                all_titles = {c.get('title', '').strip() for c in valid_chairs}
                num_distinct_titles = len(all_titles)

                if num_distinct_titles <= 1:
                    # SCENARIO 1: One or zero distinct titles (e.g., all "Chair", or all "")
                    # Just list all names under "Chairs:"
                    chair_names = [c.get("name", "") for c in valid_chairs]
                    content.append('\\noindent\\textbf{Chairs:} ' + ', '.join(chair_names) + r'\\')
                else:
                    # SCENARIO 2: Multiple distinct titles
                    
                    # 1. Define group mapping (lowercase raw title -> display group)
                    title_group_map = {
                        "chair": "Chair",
                        "co-chair": "Chair",
                        "lead": "Chair",
                        "vice chair": "Vice Chair",
                        "treasurer": "Treasurer",
                        "secretary": "Secretary",
                        "admin": "Admin",
                        "helper": "Helper"
                    }
                    
                    # 2. Define display order for predefined groups
                    display_order = [
                        "Chair", 
                        "Vice Chair", 
                        "Treasurer", 
                        "Secretary", 
                        "Admin", 
                        "Helper"
                    ]
                    
                    # 3. Group the chairs
                    grouped_names = defaultdict(list)
                    other_titles = set()
                    no_title_names = []
                    
                    for chair in valid_chairs:
                        name = chair.get("name")
                        title = chair.get("title", "").strip()
                        title_lower = title.lower()
                        
                        group_name = title_group_map.get(title_lower)
                        
                        if group_name:
                            # It's a predefined group
                            grouped_names[group_name].append(name)
                        elif title: 
                            # It's an "other" title (e.g., "Webmaster")
                            grouped_names[title].append(name) # Use the original cased title
                            other_titles.add(title)
                        else: 
                            # No title
                            no_title_names.append(name)
                            
                    # 4. Generate LaTeX output in the correct order
                    
                    # Add predefined groups in order
                    for group in display_order:
                        if group in grouped_names:
                            names_list = grouped_names[group]
                            content.append(f'\\noindent\\textbf{{{group}:}} ' + ', '.join(names_list) + r'\\')
                    
                    # Add "other" titles, sorted alphabetically
                    for group in sorted(list(other_titles)):
                        if group in grouped_names:
                            names_list = grouped_names[group]
                            content.append(f'\\noindent\\textbf{{{group}:}} ' + ', '.join(names_list) + r'\\')

                    # Add "no title" people last, under "Members"
                    if no_title_names:
                        content.append(f'\\noindent\\textbf{{Members:}} ' + ', '.join(no_title_names) + r'\\')

            # Get the list of meeting times (plural)
            meeting_times = blurb_data.get('meeting_times')
            
            # Check if it's a list and has content
            if meeting_times and isinstance(meeting_times, list):
                
                # Format all meeting time strings
                time_strings = []
                for mt in meeting_times:
                    time_str = self.format_meeting_time(mt)
                    if time_str:
                        time_strings.append(time_str)
                
                # If we have any valid time strings, print them
                if time_strings:
                    # Add the first line with the "Meetings:" prefix
                    content.append(f'\\noindent\\textbf{{Meetings:}} {time_strings[0]}\\\\')
                    
                    # Add subsequent lines, indented using \phantom for alignment
                    for time_str in time_strings[1:]:
                        # \phantom creates invisible whitespace matching the width of "Meetings: "
                        content.append(f'\\noindent\\phantom{{\\textbf{{Meetings:}} }}{time_str}\\\\')
                    
            website = blurb_data.get('website', '')
            links = blurb_data.get('links', {})
            
            if self.print_mode:
                if website:
                    display_url = website.replace('https://', '').replace('http://', '')
                    display_url = display_url.replace('#', '\\#').replace('_', '\\_').replace('%', '\\%')
                    # Add \\ at theend
                    content.append(f'\\noindent\\textbf{{Website:}} {display_url}\\\\')
                    
                for src, url in links.items():
                    clean_url = url.replace('https://', '').replace('http://', '')
                    clean_url = clean_url.replace('#', '\\#').replace('_', '\\_').replace('%', '\\%')
                    content.append(f'\\noindent\\textbf{{{src.capitalize()}:}} {clean_url}\\\\')
            else:
                if website:
                    display_url = website.replace('https://', '').replace('http://', '')
                    if len(display_url) > 40:
                        display_url = display_url[:37] + '...'
                    display_url = display_url.replace('#', '\\#').replace('_', '\\_').replace('%', '\\%')
                    content.append(f'\\noindent\\textbf{{Website:}} \\href{{{website}}}{{{display_url}}}\\\\')
                    
                for src, url in links.items():
                    clean_url = url.replace('https://', '').replace('http://', '')
                    clean_url = clean_url.replace('#', '\\#').replace('_', '\\_').replace('%', '\\%')
                    content.append(f'\\noindent\\textbf{{{src.capitalize()}:}} \\href{{{url}}}{{{clean_url}}}\\\\')

            content.append(r'')
            
            blurb = blurb_data.get('blurb', '').strip()
            if blurb:
                blurb_latex = self.markdown_to_latex(blurb)
                content.append(r'{\setlength{\parindent}{1.5em}')
                content.append(blurb_latex)
                content.append(r'}')
            
            content.append('\\end{minipage}')
            content.append('')
            content.append('\\vspace{0.3cm}')
            content.append('')
        
        content.append('\\end{multicols}')
        
        return '\n'.join(content)

    def generate_toc_tex(self):
        """Generate table of contents"""
        content = []
        content.append('\\headline{\\textbf{\\LARGE In This Issue}}')
        content.append('')
        
        # Add articles with dynamic page references
        for article_name in self.config.get('article_order', []):
            try:
                article = self.load_article(article_name)
                title = article.get('title', 'Untitled')
                title = self.escape_special_chars(title)  # Escape special characters in title
                # Use \pageref to get actual page number
                content.append(f'\\noindent {title} \\dotfill \\pageref{{article:{article_name}}}')
                content.append('')
            except:
                pass
        
        content.append('\\noindent ACM @ UIUC Directory \\dotfill \\pageref{directory}')
        content.append('')
        
        content.append('\\vspace{0.3cm}')
        
        return '\n'.join(content)
    
    def generate_all(self, output_dir):
        """Generate all LaTeX content files"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Generate table of contents
        print("Generating table of contents...")
        toc_tex = self.generate_toc_tex()
        with open(output_path / 'toc.tex', 'w', encoding='utf-8') as f:
            f.write(toc_tex)
        
        # Generate events
        print("Generating events...")
        events_tex = self.generate_events_tex()
        with open(output_path / 'events.tex', 'w', encoding='utf-8') as f:
            f.write(events_tex)
        
        # Generate letter from the chair
        print("Generating letter from the chair...")
        letter_tex = self.generate_letter_tex()
        with open(output_path / 'letter.tex', 'w', encoding='utf-8') as f:
            f.write(letter_tex)
        
        # Generate articles
        print("Generating articles...")
        articles_tex = self.generate_articles_tex()
        with open(output_path / 'articles.tex', 'w', encoding='utf-8') as f:
            f.write(articles_tex)
        
        # Generate directory
        print("Generating directory...")
        directory_tex = self.generate_directory_tex()
        with open(output_path / 'directory.tex', 'w', encoding='utf-8') as f:
            f.write(directory_tex)
        
        print(f"\n✓ All files generated in {output_path}/")
        print("\nGenerated files:")
        print("  - toc.tex")
        print("  - events.tex")
        print("  - letter.tex")
        print("  - articles.tex")
        print("  - directory.tex")
        print("\nNext steps:")
        print("1. Review the generated .tex files")
        print("2. Compile main.tex with: pdflatex main.tex")


if __name__ == '__main__':
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate Banks of the Boneyard newspaper LaTeX files')
    parser.add_argument('base_dir', nargs='?', default='/mnt/project/vol43is1',
                        help='Base directory for the newspaper files (default: /mnt/project/vol43is1)')
    parser.add_argument('--print-mode', action='store_true',
                        help='Generate print version with non-clickable links in black')
    
    args = parser.parse_args()
    
    try:
        generator = NewspaperGenerator(args.base_dir, print_mode=args.print_mode)
        generator.generate_all(f'{args.base_dir}/content')
        
        if args.print_mode:
            print("\n📄 Generated in PRINT mode (non-clickable black links)")
        else:
            print("\n🌐 Generated in ONLINE mode (clickable blue links)")
            
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)