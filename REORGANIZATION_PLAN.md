# Project Reorganization Plan

## Directory Structure

```
project_root/
├── backend/
│   ├── api/           # API endpoints and server code
│   ├── core/          # Core business logic
│   └── utils/         # Utility functions and helpers
├── frontend/
│   ├── src/           # Frontend source code
│   ├── public/        # Public assets
│   └── static/        # Static files
├── docs/
│   ├── api/           # API documentation
│   └── development/   # Development guides
├── tests/
│   ├── unit/         # Unit tests
│   └── integration/  # Integration tests
├── scripts/
│   ├── setup/        # Setup scripts
│   └── deployment/   # Deployment scripts
├── config/           # Configuration files
└── logs/            # Application logs
```

## File Movement Plan

### Backend Files
- `api_server.py` → `backend/api/`
- `app.py` → `backend/api/`
- `db_storage.py` → `backend/core/`
- `json_processor.py` → `backend/utils/`
- `large_scale_json_processor.py` → `backend/utils/`

### Frontend Files
- Frontend source files → `frontend/src/`
- Static assets → `frontend/static/`
- Public files → `frontend/public/`

### Documentation
- `API_TROUBLESHOOTING.md` → `docs/api/`
- `DB_README.md` → `docs/development/`
- `JSON_EDIT_README.md` → `docs/development/`
- `POSTGRES_GUIDE.md` → `docs/development/`

### Tests
- Test files → `tests/unit/` or `tests/integration/` based on type

### Configuration
- `.env` and `.env.example` → `config/`
- Configuration files remain in root

## Important Notes
1. All import statements will need to be updated to reflect new file locations
2. Build and deployment scripts will need to be updated
3. Documentation references will need to be updated
4. Test configurations will need to be adjusted

## Implementation Steps
1. Create new directory structure
2. Move files to new locations
3. Update import statements
4. Update build and deployment scripts
5. Update documentation references
6. Verify all functionality works as expected 