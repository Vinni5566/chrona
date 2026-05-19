import json
import os

class DependencyExtractor:
    @staticmethod
    def extract_python_deps(file_path: str) -> list[str]:
        deps = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        dep = line.split("==")[0].split(">=")[0].split("<=")[0].strip()
                        if dep:
                            deps.append(dep)
        except Exception:
            pass
        return deps

    @staticmethod
    def extract_node_deps(file_path: str) -> list[str]:
        deps = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                deps.extend(list(data.get("dependencies", {}).keys()))
                deps.extend(list(data.get("devDependencies", {}).keys()))
        except Exception:
            pass
        return deps
