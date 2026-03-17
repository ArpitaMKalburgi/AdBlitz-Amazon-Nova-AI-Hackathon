# AdBlitz -  AI That Markets For You

AdBlitz is a Streamlit app that turns a single product image into a launch-ready marketing campaign. It analyzes the uploaded image, generates brand positioning, writes cross-platform copy, creates ad creatives, produces a short video ad, builds a voiceover, and assembles a media plan.

The current stack uses:
- Amazon Bedrock for brand analysis, copy, audience generation, visual prompts, image generation, and video generation
- Amazon Polly for voiceover generation
- Amazon S3 for generated asset storage and campaign caching
- Streamlit for the app UI

## What The App Generates

From one product image, AdBlitz can generate:
- a brand brief
- audience personas
- multi-platform ad copy
- image creatives
- a short product video
- a voiceover track
- a media plan

## Project Structure

```text
AdBlitz-Amazon-Nova-AI-Hackathon/
|- app.py
|- agents/
|  |- brand_agent.py
|  |- copy_agent.py
|  |- audience_agent.py
|  |- visual_agent.py
|  |- video_agent.py
|  |- audio_agent.py
|  |- mediaplan_agent.py
|  |- refine_agent.py
|  |- orchestrator.py
|  `- _json_utils.py
|- components/
|  |- brand_card.py
|  |- copy_tabs.py
|  |- image_gallery.py
|  |- media_plan.py
|  |- persona_cards.py
|  `- video_player.py
|- services/
|  |- _common.py
|  |- bedrock.py
|  |- nova_canvas.py
|  |- nova_reel.py
|  |- polly.py
|  |- s3.py
|  |- moviepy_processor.py
|  `- live_smoke_test.py
|- requirements.txt
|- packages.txt
`- .streamlit/
   `- secrets.toml
```

## How It Works

`app.py` is the Streamlit entrypoint.

The main orchestration happens in [agents/orchestrator.py](agents/orchestrator.py). The high-level flow is:

1. Analyze the uploaded product image.
2. Generate brand, audience, and copy outputs.
3. Generate static ad creatives.
4. Create a short video plan.
5. Generate a voiceover with Amazon Polly.
6. Generate a short product video with Amazon Nova Reel.
7. Merge the video and voiceover when available.
8. Create a media plan.
9. Cache campaign results in S3 for faster reloads.

## Requirements

Python packages are listed in [requirements.txt](requirements.txt).

System packages for hosted video processing are listed in [packages.txt](packages.txt):
- `ffmpeg`
- `imagemagick`

## Local Setup

### 1. Create and activate a virtual environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install dependencies

```powershell
pip install -r requirements.txt
```

### 3. Create Streamlit secrets

Create:

```text
.streamlit/secrets.toml
```

Recommended keys:

```toml
APP_MODE = "live"

AWS_REGION = "us-east-1"
AWS_ACCESS_KEY_ID = "YOUR_AWS_ACCESS_KEY_ID"
AWS_SECRET_ACCESS_KEY = "YOUR_AWS_SECRET_ACCESS_KEY"
AWS_SESSION_TOKEN = ""

S3_BUCKET = "YOUR_S3_BUCKET"
S3_USE_PRESIGNED_URL = false
S3_PRESIGNED_EXPIRES_IN = 3600
S3_OBJECT_ACL = ""
S3_CACHE_CONTROL = ""

BEDROCK_MODEL_ID = "amazon.nova-lite-v1:0"
NOVA_CANVAS_MODEL_ID = "amazon.nova-canvas-v1:0"
NOVA_REEL_MODEL_ID = "amazon.nova-reel-v1:1"
NOVA_REEL_OUTPUT_PREFIX = "bedrock/nova-reel"

POLLY_ENGINE = "neural"
POLLY_LANGUAGE_CODE = "en-US"
POLLY_SAMPLE_RATE = "24000"
POLLY_VOICE_ID = "Joanna"
```

Notes:
- `.streamlit/secrets.toml` is gitignored.
- The app reads settings through [services/_common.py](services/_common.py).

### 4. Run the app

```powershell
python -m streamlit run app.py
```

Default local URL:

```text
http://localhost:8501
```

## AWS Permissions

The AWS identity used by the app needs access to:
- Bedrock runtime
- Amazon Polly
- Amazon S3

At a minimum, your IAM user or role should be able to call:
- `bedrock:InvokeModel`
- `bedrock:Converse`
- `bedrock:StartAsyncInvoke`
- `bedrock:GetAsyncInvoke`
- `polly:DescribeVoices`
- `polly:SynthesizeSpeech`
- `s3:GetObject`
- `s3:PutObject`
- `s3:CopyObject`

## Smoke Testing

A live smoke test script is available at [services/live_smoke_test.py](services/live_smoke_test.py).

Run it with:

```powershell
python -m services.live_smoke_test
```

This script exercises:
- Bedrock connectivity
- image generation
- campaign orchestration
- Polly voiceover generation
- Nova Reel video generation
- optional video/audio merge flow

## Deployment Notes

### Streamlit Community Cloud

For Streamlit deployment:
- point the app to `app.py`
- add the required secrets in the Streamlit Cloud secrets manager
- keep `packages.txt` in the repo root so `ffmpeg` and `imagemagick` are installed

### Redeploying

When changing backend services or generated asset behavior:
- redeploy the app after pushing to GitHub
- reboot the app if an old cached session is still open
- try a fresh upload if you suspect a stale cached campaign result

## Troubleshooting

### Video exists locally but not on hosted app

Check:
- AWS permissions for Bedrock, Polly, and S3
- that `packages.txt` is picked up on Streamlit Cloud
- that the deployed app is on the latest Git commit
- whether the cached campaign already contains a failed or incomplete video result

### Voiceover fails

Check:
- `polly:SynthesizeSpeech`
- `polly:DescribeVoices`
- your configured `POLLY_VOICE_ID`
- your selected Polly engine and region

### Local app starts but generation fails

This usually means the UI is fine but one of the backend credentials or AWS permissions is missing.

## Current Voiceover Implementation

Voiceover generation now uses Amazon Polly through [services/polly.py](services/polly.py).

The audio selection agent still chooses a `voice_id`, but that `voice_id` is now a Polly voice such as:
- `Joanna`
- `Matthew`
- `Danielle`
- `Gregory`

## Notes

- Campaign caching is S3-backed.
- The app is designed to return a raw video even when voiceover merge is unavailable.
- There is still a legacy [services/elevenlabs.py](services/elevenlabs.py) file in the repo from earlier iterations, but the current active voiceover path uses Polly.
