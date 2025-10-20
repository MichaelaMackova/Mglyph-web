# Auto-import all models in the db/models directory
# This ensures that all models are registered with the ORM when the package is imported
import pkgutil
import importlib

for _, name, _ in pkgutil.walk_packages(__path__, f"{__name__}."):
    module = importlib.import_module(name)
    # print(f"Imported module: {module.__name__}")


# OR Import all models here
# from db.models import heroModel, posts  