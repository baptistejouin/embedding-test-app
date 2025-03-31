import json
from pathlib import Path

def transform_issues(input_file: str, output_file: str):
    """Transform issues data into the correct format for embedding."""
    with open(input_file, 'r') as f:
        issues = json.load(f)
    
    documents = []
    for issue in issues:
        # Create a unique ID from the issue number or URL
        issue_id = str(issue.get('number', issue.get('url', '').split('/')[-1]))
        
        # Combine title and body for content
        content = f"{issue.get('title', '')}\n\n{issue.get('body', '')}"
        
        # Create metadata from issue data
        metadata = {
            "author": issue.get('author', {}).get('login', ''),
            "created_at": issue.get('createdAt', ''),
            "closed_at": issue.get('closedAt', ''),
            "state": issue.get('state', ''),
            "labels": [label.get('name', '') for label in issue.get('labels', [])]
        }
        
        documents.append({
            "id": issue_id,
            "title": issue.get('title', ''),
            "content": content,
            "metadata": metadata
        })
    
    # Write the transformed data
    with open(output_file, 'w') as f:
        json.dump({"documents": documents}, f, indent=2)

if __name__ == "__main__":
    input_file = "data/amyIssues.json"
    output_file = "data/transformed_issues.json"
    transform_issues(input_file, output_file)
    print(f"Transformed issues saved to {output_file}") 
    