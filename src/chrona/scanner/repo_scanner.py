import os
from pathlib import Path
from typing import Dict, Any

from chrona.scanner.dependency_extractor import DependencyExtractor
from chrona.scanner.config_parser import ConfigParser

class RepoScanner:
    IGNORE_DIRS = {".git", "node_modules", "venv", ".venv", "dist", "build", "__pycache__"}
    IGNORE_FILES = {".env"}
    MAX_FILE_SIZE = 1024 * 1024  # 1MB
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path).resolve()
        
    def scan(self) -> Dict[str, Any]:
        facts = {
            "project_name": self.root_path.name,
            "services": [],
            "dependencies": {},
            "files_scanned": 0
        }
        
        for root, dirs, files in os.walk(self.root_path):
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]
            
            for file in files:
                if file in self.IGNORE_FILES:
                    continue
                    
                file_path = Path(root) / file
                if not file_path.exists() or file_path.stat().st_size > self.MAX_FILE_SIZE:
                    continue
                    
                facts["files_scanned"] += 1
                
                if file in ["docker-compose.yml", "docker-compose.yaml"]:
                    svcs = ConfigParser.parse_docker_compose(str(file_path))
                    facts["services"].extend(svcs)
                elif file.endswith(".yaml") or file.endswith(".yml"):
                    svcs, k8s_deps = ConfigParser.parse_kubernetes(str(file_path))
                    facts["services"].extend(svcs)
                    if "k8s_links" not in facts:
                        facts["k8s_links"] = {}
                    for svc, deps in k8s_deps.items():
                        if svc not in facts["k8s_links"]:
                            facts["k8s_links"][svc] = []
                        facts["k8s_links"][svc].extend(deps)
                    
                    
                if file == "requirements.txt":
                    deps = DependencyExtractor.extract_python_deps(str(file_path))
                    facts["dependencies"]["python"] = facts["dependencies"].get("python", []) + deps
                elif file == "package.json":
                    deps = DependencyExtractor.extract_node_deps(str(file_path))
                    facts["dependencies"]["node"] = facts["dependencies"].get("node", []) + deps
                    
        facts["services"] = list(set(facts["services"]))
        for k in facts["dependencies"]:
            facts["dependencies"][k] = list(set(facts["dependencies"][k]))
            
        return facts
