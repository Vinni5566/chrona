class ConfigParser:
    @staticmethod
    def parse_docker_compose(file_path: str) -> list[str]:
        services = []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
                in_services = False
                for line in lines:
                    if line.strip() == "services:":
                        in_services = True
                        continue
                    if in_services and line.startswith("  ") and not line.startswith("    "):
                        svc = line.split(":")[0].strip()
                        if svc and not svc.startswith("#"):
                            services.append(svc)
        except Exception:
            pass
        return services

    @staticmethod
    def parse_kubernetes(file_path: str) -> tuple[list[str], dict[str, list[str]]]:
        services = []
        dependencies = {}
        try:
            import yaml
            with open(file_path, "r", encoding="utf-8") as f:
                docs = list(yaml.safe_load_all(f))
                for doc in docs:
                    if not doc or not isinstance(doc, dict):
                        continue
                    kind = doc.get("kind")
                    metadata = doc.get("metadata", {})
                    name = metadata.get("name")
                    if kind in ["Service", "Deployment"] and name:
                        services.append(name)
                
                for doc in docs:
                    if not doc or not isinstance(doc, dict):
                        continue
                    kind = doc.get("kind")
                    if kind == "Deployment":
                        name = doc.get("metadata", {}).get("name")
                        if not name:
                            continue
                        containers = doc.get("spec", {}).get("template", {}).get("spec", {}).get("containers", [])
                        for container in containers:
                            env = container.get("env", [])
                            for e in env:
                                val = str(e.get("value", ""))
                                if ":" in val:
                                    host = val.split(":")[0]
                                    if host:
                                        if name not in dependencies:
                                            dependencies[name] = []
                                        dependencies[name].append(host)
        except Exception:
            pass
        return services, dependencies
