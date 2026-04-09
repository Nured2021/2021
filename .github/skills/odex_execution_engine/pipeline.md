# ODEX Execution Engine Pipeline

## Stage Definitions

1. **Input Stage**
   - Capture user intent
   - Preprocess context
2. **Planning Stage**
   - Call AI Pilot (C-02)
   - Break into tasks
3. **Architecture Stage**
   - Generate system design (C-06)
   - DB schema
   - API map
4. **Build Stage**
   - Call builder cores (C-07)
   - Generate files
   - Create structure
5. **Debug Stage**
   - Detect errors (C-08)
   - Auto fix
   - Retry loop
6. **Test Stage**
   - Run tests (C-09)
   - Validate system
7. **Human Loop Stage**
   - Allow review
   - Allow override
   - Inject changes
8. **Deploy Stage**
   - Package system (C-15)
   - Prepare runtime
   - Generate preview
9. **Learn Stage**
   - Capture user edits
   - Update system memory
