# Test Suite

This folder contains real pytest-based tests for MediTrack:

- `test_app.py`: basic smoke coverage for app landing page.
- `test_auth.py`: registration/login route behavior and validation.
- `test_medications.py`: dashboard auth guard, add-medication flow, AJAX intake toggle.
- `test_models.py`: password hashing checks and medication-log uniqueness rule.

Run tests with plugin autoload disabled (to avoid unrelated global plugin conflicts):

```powershell
$env:PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
python -m pytest -q
```
