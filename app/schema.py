"""JSON schema definition for data to be embedded."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
from pathlib import Path
from datetime import datetime


class Author(BaseModel):
    """Schema for the author of an issue."""
    id: str
    is_bot: bool
    login: str
    name: str


class IssueSchema(BaseModel):
    """Schema for an issue to be embedded."""
    author: Author
    body: str = Field(default="")
    title: str
    number: Optional[int] = None
    url: Optional[str] = None
    state: Optional[str] = None
    createdAt: Optional[datetime] = None
    closedAt: Optional[datetime] = None
    labels: Optional[List[Dict[str, str]]] = Field(default_factory=list)
    
    @classmethod
    def from_json(cls, json_data: Dict) -> 'IssueSchema':
        """Create an IssueSchema instance from JSON data."""
        # Convert string dates to datetime objects
        if 'closedAt' in json_data and json_data['closedAt']:
            json_data['closedAt'] = datetime.fromisoformat(json_data['closedAt'].replace('Z', '+00:00'))
        if 'createdAt' in json_data:
            json_data['createdAt'] = datetime.fromisoformat(json_data['createdAt'].replace('Z', '+00:00'))
        return cls(**json_data)

    def to_document(self) -> Dict[str, Any]:
        """Convert an issue to a document format for embedding."""
        # Create a unique ID from the issue number or URL
        issue_id = str(self.number or self.url.split('/')[-1])
        
        # Combine title and body for content
        content = f"{self.title}\n\n{self.body}"
        
        # Create metadata from issue data
        metadata = {
            "author": self.author.login,
            "created_at": self.createdAt.isoformat() if self.createdAt else None,
            "closed_at": self.closedAt.isoformat() if self.closedAt else None,
            "state": self.state,
            "labels": [label.get('name', '') for label in self.labels]
        }
        
        return {
            "id": issue_id,
            "title": self.title,
            "content": content,
            "metadata": metadata
        }


class IssueCollection(BaseModel):
    """Collection of issues to be embedded."""
    issues: List[IssueSchema]
    
    @classmethod
    def from_file(cls, file_path: str) -> 'IssueCollection':
        """Load issues from a JSON file."""
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(path, 'r') as f:
            data = json.load(f)
        
        if isinstance(data, list):
            # If the JSON is an array of issues
            issues = [IssueSchema.from_json(issue) for issue in data]
            return cls(issues=issues)
        elif isinstance(data, dict) and 'issues' in data:
            # If the JSON has an 'issues' key with an array
            issues = [IssueSchema.from_json(issue) for issue in data['issues']]
            return cls(issues=issues)
        else:
            raise ValueError("Invalid JSON format. Expected an array of issues or an object with an 'issues' key.")

    def to_documents(self) -> List[Dict[str, Any]]:
        """Convert all issues to document format for embedding."""
        return [issue.to_document() for issue in self.issues]