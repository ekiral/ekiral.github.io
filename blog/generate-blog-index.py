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
        
        paragraphs = soup.find_all('p')
        summary_parts = []
        char_count = 0
        
        for p in paragraphs:
            text = p.get_text().strip()
            if len(text) > 20:  # Skip very short paragraphs
                summary_parts.append(str(p))
                char_count += len(text)
                
                # Stop before we get too long, and avoid cutting display math
                if char_count > 200:
                    # Check if next element is display math
                    next_element = p.find_next()
                    if next_element and 'math display' in str(next_element):
                        # Include the display math too
                        summary_parts.append(str(next_element))
                    break
        
        summary = ''.join(summary_parts)[:-4] + '...'

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
    # Skip any files that look like index pages and analytics.
    skip_patterns = [
        'index.html',
        'blog-index',
        'analytics.html',
        'blog-header.html'
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
            {post['summary']}
            <a href="{post['filename']}" class="read-more">Read full post →</a>
            </p>
            
        </div>
    </div>
'''
    
    return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Blog Posts - E. Mehmet Kıral</title>

    <!-- MathJax -->
    <script src="https://polyfill.io/v3/polyfill.min.js?features=es6"></script>
    <script id="MathJax-script" async src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js"></script>

    <link rel="stylesheet" href="math-blog.css" />

    {Path("analytics.html").read_text()}
    
</head>
<body>
    <h1>Mathematical Vignettes</h1>
    
    {Path("blog-header.html").read_text()}

    <div class="nav-home">
        <a href="../index.html">← Back to Homepage</a>
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
