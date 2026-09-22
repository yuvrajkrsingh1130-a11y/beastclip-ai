import re
from backend.config import CREATOR_PRESETS

class MetadataGenerator:
    def __init__(self):
        pass

    def detect_creator_preset(self, title: str, uploader: str) -> dict:
        combined = f"{title} {uploader}".lower()
        if "speed" in combined or "ishowspeed" in combined:
            return CREATOR_PRESETS["ishowspeed"]
        elif "kai" in combined or "cenat" in combined:
            return CREATOR_PRESETS["kaicenat"]
        elif "jynxzi" in combined:
            return CREATOR_PRESETS["jynxzi"]
        elif "caseoh" in combined:
            return CREATOR_PRESETS["caseoh"]
        return CREATOR_PRESETS["generic"]

    def generate_clip_metadata(self, clip_text: str, original_title: str, uploader: str, uploader_url: str, rank: int = 1) -> dict:
        preset = self.detect_creator_preset(original_title, uploader)
        creator_name = uploader or preset["name"]
        creator_tag = preset["credit_tag"]
        if creator_tag == "Original Creator" and uploader:
            creator_tag = f"@{uploader.replace(' ', '')}"

        # Clean text snippet for hook & story summary
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', clip_text).strip()
        words = clean_text.split()
        short_snippet = " ".join(words[:6]) if words else "INSANE Stream Moment"
        
        # Summarize key dialogue/moment
        dialogue_summary = f'"{clean_text[:120]}..."' if len(clean_text) > 20 else f'"{clean_text}"'

        # Clean creator name for titles
        clean_name = creator_name.lstrip("@").strip()
        if not clean_name:
            clean_name = "Streamer"

        # High CTR Viral Title variations (never output bare handles)
        title_templates = [
            f"WHEN {clean_name.upper()} CANNOT STOP LAUGHING 💀",
            f"{clean_name.upper()} DID NOT EXPECT THIS TO HAPPEN! 😱",
            f"BRO DID NOT REALIZE WHAT HE SAID... 💀",
            f"THE MOST CHAOTIC MOMENT EVER ON STREAM! 🔥 #Shorts",
            f"HE ACTUALLY LOST HIS MIND OVER THIS 😭",
            f"{clean_name.upper()}'S CRAZIEST REACTION EVER ⚡",
            f"TOP 1% STREAMER MOMENT: {short_snippet.upper()} ⚡",
            f"IS THIS THE FUNNIEST STREAM CLIP OF 2026? 🤣"
        ]
        title = title_templates[(rank - 1) % len(title_templates)]

        # Interactive Algorithm Booster Questions for Comments
        comment_questions = [
            "👇 What would you have done in this situation? Let me know below!",
            "👇 Rate this reaction from 1 to 10 in the comments!",
            "👇 W or L reaction? Drop your thoughts below!",
            "👇 Did he go too far with this? Tell me in the comments!",
            "👇 Who is your favorite streamer right now? Drop a comment!"
        ]
        question = comment_questions[(rank - 1) % len(comment_questions)]

        # Targeted viral tags
        base_tags = ["#Shorts", "#Viral", "#Trending", "#Gaming", "#FunnyMoments", "#TwitchClips", "#StreamerClips", "#YouTubeShorts"]
        combined_tags = list(dict.fromkeys(base_tags + preset["tags"])) # Deduplicate preserving order
        tags_string = " ".join(combined_tags[:10])

        # Channel Link
        channel_link = uploader_url or preset["channel_url"] or "https://youtube.com"

        # Engaging, Trending Viral Description
        description = f"""🔥 {clean_name} had the most insane moment on stream! Watch until the very end to see what happens!

🎬 MOMENT HIGHLIGHT:
{dialogue_summary}

💬 JOIN THE CONVERSATION:
{question}

🔔 NEVER MISS A CLIP:
Subscribe and turn on notifications for daily viral streamer highlights, rage moments, and the funniest Twitch/YouTube clips!

👑 ORIGINAL CREATOR ATTRIBUTION:
• Creator: {clean_name} ({creator_tag})
• Official Channel: {channel_link}
• All credits and rights reserved to the original creator.

{tags_string}"""

        return {
            "title": title,
            "title_suggestions": title_templates,
            "description": description.strip(),
            "tags": combined_tags,
            "tags_string": tags_string,
            "creator_credit": creator_tag,
            "creator_name": clean_name
        }
