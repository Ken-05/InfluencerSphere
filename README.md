# InfluencerSphere
An ML-driven marketplace intelligence platform professionalizing the influencer/creator economy. Brands get objective scouting metrics (Market Value, PLEP) to find talent, while creators receive content diagnostics and quantitative performance data to negotiate and justify their market pricing.

## Project Vision
### The Attention War: Why the Creator Economy Rivals Traditional Sports
The global sports industry has long been the undisputed champion of large-scale entertainment, with billions in revenue, capturing the collective attention of massive audiences through scheduled, high-stakes spectacle.

However, the rapid acceleration of social media platforms, including Instagram, TikTok, and X has introduced the Creator Economy, a competitive force structured around continuous, hyper-personalized engagement. This new paradigm of content creation is consuming vast amounts of human attention, arguably rivaling traditional sports for the most precious resource: consumer time.

InfluencerSphere recognizes this pivot point. By structuring the creator ecosystem with the objectivity, valuation, and metrics of a professional sports league, we aim to professionalize this burgeoning marketplace, enabling Brands (Clubs) to efficiently invest in the Athletes (Influencers) who are winning the competitive battle for attention.

### Proposition
We are transforming the subjective, opaque world of influencer marketing into a quantitative, competitive process. 

InfluencerSphere acts as the "League Office" for the creator economy.

Influencers are the "Athletes," receiving data-backed valuation and performance diagnostics.

Brands are the "Clubs," using sophisticated metrics to scout, budget, and acquire the best talent for specific campaigns.

### Mission
Our core mission is to replace guesswork with predictive intelligence, enabling brands to align budgets precisely with verifiable market value and helping creators maximize their monetization potential.

## Key Features
### For Brands (The Clubs)

Objective Market Value Ranking: Filter and search influencers based on a data-backed market valuation derived from their entire performance history (from Agent 4).

PLEP (Post-Level Engagement Potential) Prediction: Predict the expected ROI/engagement for a specific, future content collaboration (from Agent 3).

Real-Time Alerts: Set up custom thresholds to scout emerging talent before their market value spikes.

### For Influencers (The Athletes)

Content Diagnostics: Input content drafts (caption, image) and receive actionable insights on the predicted PLEP score, showing the top positive and negative feature contributors for instant optimization.

Verifiable Price Justification: Use the objective Market Value Ranking to confidently negotiate fees and prove worth to prospective brand partners.

Niche Strategy Reports: Receive data on niche competition and growth trends to guide long-term content strategy.

### Technical Architecture
The platform operates on MLOps principle of Training/Serving Separation.
Training Environment (scripts/): Runs the heavy data pipeline, performing feature engineering (Agent 1 & 2) and model training (Agent 3 & 4) to create the model artifacts (.joblib files).

Serving Environment (backend/): A high-performance, stateless FastAPI service that loads the pre-trained models on startup and executes inference on demand via dedicated, low-latency API routes (predictions.py).

Data Persistence: Google Firestore is used for storing all application state, user data (alerts), and the structured influencer profiles.