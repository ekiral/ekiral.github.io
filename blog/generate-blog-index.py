#!/usr/bin/env python3
"""
Auto-generate blog index from existing HTML posts.
Usage: python generate-blog-index.py
"""

import os
import re
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup

def extract_post_info(html_file):
    """Extract title, date, and summary from an HTML blog post."""
    try:
        with open(html_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        
        # Extract title
        title_elem = soup.find('h1', class_='title') or soup.find('h1')
        title = title_elem.get_text().strip() if title_elem else "Untitled"
        
        # Extract date
        date_elem = soup.find(class_='date')
        date = date_elem.get_text().strip() if date_elem else "No date"
        
        # Extract first paragraph as summary (skip if it's too short)
        paragraphs = soup.find_all('p')
        summary = ""
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 50:  # Skip very short paragraphs
                summary = text[:300] + "..." if len(text) > 300 else text
                break
        
        if not summary:
            summary = "Click to read this post about mathematical concepts and machine learning."
        
        return {
            'title': title,
            'date': date,
            'summary': summary,
            'filename': html_file.name
        }
    
    except Exception as e:
        print(f"Error processing {html_file}: {e}")
        return None

def is_blog_post(filename):
    """Check if a file is a blog post (not an index or main page)."""
    name = filename.lower()
    # Skip any files that look like index pages
    skip_patterns = [
        'index.html',
        'blog-index',
        'main.html',
        'home.html'
    ]
    
    for pattern in skip_patterns:
        if pattern in name:
            return False
    return True

def generate_blog_index(posts_dir=".", output_file="blog-index.html"):
    """Generate the blog index HTML file."""
    
    posts_dir = Path(posts_dir)
    
    # Find all HTML files that look like blog posts
    html_files = [f for f in posts_dir.glob("*.html") if is_blog_post(f.name)]
    
    if not html_files:
        print("No HTML blog posts found!")
        return
    
    # Extract info from each post
    posts = []
    for html_file in html_files:
        post_info = extract_post_info(html_file)
        if post_info:
            posts.append(post_info)
    
    if not posts:
        print("No valid posts found!")
        return
    
    # Sort posts by filename (or you could sort by date if you parse it)
    posts.sort(key=lambda x: x['filename'], reverse=True)
    
    # Generate HTML
    html_content = generate_css_template(posts)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Generated {output_file} with {len(posts)} posts:")
    for post in posts:
        print(f"  - {post['title']}")

def generate_css_template(posts):
    """Generate CSS-only version of the blog index."""
    
    posts_html = ""
    for i, post in enumerate(posts, 1):
        posts_html += f'''
    <div class="post-preview">
        <input type="checkbox" id="post{i}" class="toggle">
        <label for="post{i}" class="post-title">
            <span class="expand-icon">+</span>
            {post['title']}
        </label>
        <div class="post-meta">{post['date']}</div>
        <div class="post-summary">
            <p>{post['summary']}</p>
            <a href="{post['filename']}" class="read-more">Read full post →</a>
        </div>
    </div>
'''
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Blog Posts - E. Mehmet Kıral</title>
    <style>
        body {{
            font-family: 'ETBook', 'Palatino', 'Book Antiqua', 'Georgia', serif;
            max-width: 800px;
            margin: 0 auto;
            padding: 0 2rem;
            font-size: 18px;
            line-height: 1.6;
            color: #111111;
            background-color: #fffff8;
        }}

        h1 {{
            font-size: 2.5rem;
            margin-bottom: 2rem;
            text-align: center;
        }}

        .nav-home {{
            text-align: center;
            margin-bottom: 3rem;
        }}

        .nav-home a {{
            color: #111111;
            text-decoration: none;
            border-bottom: 1px solid #111111;
        }}

        .post-preview {{
            margin-bottom: 2rem;
            border-bottom: 1px solid #ddd;
            padding-bottom: 1.5rem;
        }}

        .post-preview:last-child {{
            border-bottom: none;
        }}

        .toggle {{
            display: none;
        }}

        .post-title {{
            font-size: 1.3rem;
            font-weight: bold;
            cursor: pointer;
            display: flex;
            align-items: center;
            color: #111111;
            margin-bottom: 0.5rem;
        }}

        .expand-icon {{
            margin-right: 0.5rem;
            font-size: 1.2rem;
            transition: transform 0.3s ease;
            color: #666;
        }}

        .post-meta {{
            font-size: 0.9rem;
            color: #666;
            margin-bottom: 1rem;
        }}

        .post-summary {{
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            color: #555;
        }}

        .toggle:checked + .post-title + .post-meta + .post-summary {{
            max-height: 200px;
            padding-top: 1rem;
        }}

        .toggle:checked + .post-title .expand-icon {{
            transform: rotate(45deg);
        }}

        .read-more {{
            display: inline-block;
            margin-top: 1rem;
            color: #3498db;
            text-decoration: none;
            font-weight: bold;
        }}

        .read-more:hover {{
            text-decoration: underline;
        }}

        .generated-info {{
            text-align: center;
            font-size: 0.8rem;
            color: #999;
            margin-top: 3rem;
            border-top: 1px solid #eee;
            padding-top: 1rem;
        }}
    </style>
</head>
<body>
    <h1>Mathematical Vignettes</h1>
    
    <div class="nav-home">
        <a href="index.html">← Back to Homepage</a>
    </div>

{posts_html}

    <div class="generated-info">
        <p>This index was automatically generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>
    </div>

</body>
</html>'''

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate blog index from HTML posts')
    parser.add_argument('--dir', default='.', help='Directory containing blog posts (default: current)')
    parser.add_argument('--output', default='blog-index.html', help='Output filename (default: blog-index.html)')
    
    args = parser.parse_args()
    
    # Check if BeautifulSoup is available
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        print("Error: BeautifulSoup not installed. Install with: pip install beautifulsoup4")
        exit(1)
    
    generate_blog_index(
        posts_dir=args.dir,
        output_file=args.output
    )
