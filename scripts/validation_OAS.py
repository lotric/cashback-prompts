from openapi_spec_validator import validate_spec
import yaml, sys

with open(sys.argv[1], encoding="utf-8") as f:
    spec = yaml.safe_load(f)

validate_spec(spec)
print("OAS valid")
