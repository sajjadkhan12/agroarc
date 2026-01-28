# agroarc_fyp
Final Year Project - AgroArc

### for copilot understanding
'PROJECT CONTEXT (READ CAREFULLY):

This project is a Final Year Project (FYP) named "AgroArc – Smart Farmer Support Chatbot".

Goal:
AgroArc is an AI-based agricultural advisory system designed to assist farmers in Pakistan by providing data-driven recommendations for:
1) Crop selection
2) Fertilizer recommendation
3) Weather-based farming advice

IMPORTANT SCOPE CONSTRAINTS:
- This project uses ONLY structured/tabular data.
- NO image-based machine learning or computer vision is used.
- NO deep learning models unless explicitly required.
- Focus on classical machine learning models that are easy to explain in an academic FYP.

DATASETS USED:
1) Crop Recommendation Dataset
   Columns:
   - N, P, K (soil nutrients)
   - temperature, humidity, ph, rainfall (environmental factors)
   - label (target crop)
   Task: Supervised multi-class classification.

2) Fertilizer Recommendation Dataset
   Columns:
   - Temperature, Humidity, Moisture
   - Soil Type, Crop Type
   - Nitrogen, Phosphorous, Potassium
   - Fertilizer Name (target)
   Task: Supervised multi-class classification.

3) Pakistan Weather Dataset
   Used for analysis and rule-based advisory only.
   NOT used for training ML models directly.

MODELING REQUIREMENTS:
- Primary algorithms: Random Forest, Decision Tree, or similar classical ML models.
- Use scikit-learn.
- Apply proper train-test split (typically 80/20).
- Encode categorical variables where required.
- Evaluate models using accuracy and classification report.
- Save trained models using joblib (.pkl files).

PROJECT STRUCTURE:
- data/raw/       → original datasets
- data/processed/ → cleaned datasets
- notebooks/      → model training and experiments
- models/         → saved trained models
- backend/        → FastAPI backend (later phase)

DEVELOPMENT PHASE:
Currently working on Week 1:
- Building and training the Crop Recommendation Model only.
- No backend or frontend work at this stage.

CODING GUIDELINES:
- Code should be clean, readable, and well-commented.
- Avoid unnecessary complexity.
- Each step should be explainable for viva and documentation.
- Prefer clarity over optimization.

OUTPUT EXPECTATIONS:
- A trained crop recommendation model saved as a .pkl file.
- Clear, explainable ML pipeline suitable for an academic Final Year Project.

When generating code or suggestions:
- Stay within the defined scope.
- Do not introduce image ML, deep learning, or unrelated features.
- Prefer academically standard approaches.
'