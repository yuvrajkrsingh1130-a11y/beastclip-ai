import re
import random
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

    def _analyze_context_hooks(self, text: str) -> str:
        """Categorizes transcript into emotion tone for hook optimization."""
        t = text.lower()
        if any(k in t for k in ["laugh", "haha", "lmao", "dead", "funny", "joke", "crying", "aint no way", "no way"]):
            return "humor"
        elif any(k in t for k in ["rage", "scream", "shut up", "hate", "smash", "break", "mad", "angry", "yell"]):
            return "rage"
        elif any(k in t for k in ["what", "how", "omg", "oh my god", "bro", "caught", "police", "wait", "cheating", "ban"]):
            return "shock"
        elif any(k in t for k in ["clutch", "win", "kill", "headshot", "god", "pro", "insane", "play", "clean"]):
            return "clutch"
        return "general"

    def generate_clip_metadata(self, clip_text: str, original_title: str, uploader: str, uploader_url: str, rank: int = 1) -> dict:
        preset = self.detect_creator_preset(original_title, uploader)
        creator_name = uploader or preset["name"]
        creator_tag = preset["credit_tag"]
        if creator_tag == "Original Creator" and uploader:
            creator_tag = f"@{uploader.replace(' ', '')}"

        # Clean text snippet
        clean_text = re.sub(r'[^a-zA-Z0-9\s.,!?]', '', clip_text).strip()
        words = clean_text.split()
        short_snippet = " ".join(words[:5]) if words else "INSANE Stream Moment"
        dialogue_summary = f'"{clean_text[:140]}..."' if len(clean_text) > 20 else f'"{clean_text}"'

        clean_name = creator_name.lstrip("@").strip()
        if not clean_name:
            clean_name = "Streamer"
        c_upper = clean_name.upper()

        context = self._analyze_context_hooks(clip_text)

        # Extract subject entities and key topic from original title and dialogue
        clean_orig = re.sub(r'[#@|\[\]()\-!?,.]', ' ', original_title).strip()
        topic_words = [w for w in clean_orig.split() if w.lower() not in ["the", "a", "an", "is", "of", "and", "in", "to", "i", "my", "with", "video", "official", "stream", "full", "highlights", "clip", "clips"]]
        key_topic = " ".join(topic_words[:3]).upper() if topic_words else "STREAM"

        combined_check = f"{original_title} {clip_text}".upper()
        found_entity = ""
        for ent in ["RONALDO", "CR7", "MESSI", "KAI CENAT", "JYNXZI", "CASEOH", "SPEED", "DRAKE", "MRBEAST", "FORTNITE", "GTA", "FIFA", "ROBLOX", "MINECRAFT"]:
            if re.search(r'\b' + re.escape(ent) + r'\b', combined_check):
                found_entity = ent
                break

        # High CTR Viral Title Pools based on detected topic and context
        if found_entity == "RONALDO" or "RONALDO" in combined_check:
            title_pool = [
                f"SPEED FINALLY MET RONALDO AND BROKE DOWN CRYING 😭🇵🇹",
                f"RONALDO DID NOT EXPECT {c_upper} TO DO THIS 💀🔥",
                f"THE EXACT SECOND {c_upper}'S DREAM CAME TRUE 🥹❤️",
                f"SPEED SHOWED RONALDO HIS TATTOO AND THIS HAPPENED 💀🇵🇹",
                f"{c_upper} AND RONALDO DID THE SIUUU TOGETHER! 🐐🔥",
                f"IS THIS THE GREATEST STREAM MOMENT IN INTERNET HISTORY? 🐐"
            ]
        elif key_topic and key_topic != "STREAM" and len(key_topic) > 2:
            title_pool = [
                f"{c_upper} - {key_topic} HAD THE ENTIRE CHAT IN TEARS 😭💀",
                f"BRO AIN'T NO WAY {c_upper} DID THIS DURING {key_topic}... 💀",
                f"WHEN {c_upper} COMPLETELY LOST HIS MIND DURING {key_topic} 😱⚡",
                f"THE MOST VIRAL {key_topic} MOMENT OF 2026! 💥",
                f"NOBODY EXPECTED {c_upper} TO REACT LIKE THIS TO {key_topic} 🚨",
                f"{c_upper}'S WILDEST REACTION: {key_topic} 🔥"
            ]
        elif context == "humor":
            title_pool = [
                f"WHEN {c_upper} CANNOT STOP LAUGHING 💀🤣",
                f"BRO AIN'T NO WAY {c_upper} SAID THIS OUT LOUD... 💀",
                f"THIS HAD THE ENTIRE CHAT IN LITERAL TEARS 😭💀",
                f"{c_upper} REALLY THOUGHT NO ONE WOULD NOTICE 😭",
                f"THE FUNNIEST 30 SECONDS ON TWITCH THIS YEAR 🤣🔥",
                f"BRO LOST HIS ENTIRE DIGNITY ON LIVE STREAM 💀"
            ]
        elif context == "rage":
            title_pool = [
                f"{c_upper} RAGED SO HARD HIS MIC ACTUALLY BROKE 🤬💥",
                f"WHEN {c_upper} COMPLETELY LOSES HIS MIND 😱⚡",
                f"HE ACTUALLY SNAPPED OVER THIS... 🤯🔥",
                f"THE MOST AGGRESSIVE CRASH OUT OF 2026! 💥",
                f"{c_upper} DESTROYED HIS SETUP AFTER THIS PLAY 😭",
                f"NEVER MAKE {c_upper} ANGRY ON STREAM... 🤬"
            ]
        elif context == "shock":
            title_pool = [
                f"{c_upper} DID NOT EXPECT THIS TO HAPPEN ON LIVE CAMERA! 📸💀",
                f"{c_upper} REALIZED TOO LATE WHAT HE JUST DID... 😭😱",
                f"THE ENDING WILL MAKE YOUR JAW DROP... 😱🤯",
                f"BRO'S REACTION TO THIS IS ACTUALLY PRICELESS 💀",
                f"NOBODY EXPECTED THIS TO HAPPEN ON STREAM! 🚨",
                f"IS THIS THE CRAZIEST STREAM MOMENT EVER? 😱"
            ]
        else:
            title_pool = [
                f"{c_upper} DID NOT EXPECT THIS TO HAPPEN! 😱🔥",
                f"THE MOST UNHINGED MOMENT ON LIVE STREAM 💀",
                f"BRO FORGOT HE WAS LIVE TO 100K PEOPLE 💀",
                f"WATCH UNTIL THE VERY END... YOU WILL NOT BELIEVE THIS 😱",
                f"{c_upper}'S WILDEST REACTION OF ALL TIME ⚡",
                f"TOP 1% STREAM MOMENT: {short_snippet.upper()} 🔥",
                f"THIS IS WHY {c_upper} IS THE #1 STREAMER 👑"
            ]

        # Select primary title and build suggestions
        primary_title = title_pool[(rank - 1) % len(title_pool)]

        # Interactive Algorithm Booster Questions for Comments
        comment_questions = [
            "👇 Rate this moment from 1 to 10 in the comments below!",
            "👇 What would YOU have done in this exact situation? Let me know!",
            "👇 W or L streamer reaction? Drop your thoughts below!",
            "👇 Did he go too far or was this valid? Let's settle this in the comments!",
            "👇 Who is the funniest streamer right now? Drop a comment!"
        ]
        question = comment_questions[(rank - 1) % len(comment_questions)]

        # Targeted viral tags
        base_tags = ["#Shorts", "#Viral", "#Trending", "#Gaming", "#FunnyMoments", "#TwitchClips", "#StreamerClips", "#YouTubeShorts", f"#{clean_name.replace(' ', '')}"]
        combined_tags = list(dict.fromkeys(base_tags + preset["tags"]))
        tags_string = " ".join(combined_tags[:10])

        channel_link = uploader_url or preset["channel_url"] or "https://youtube.com"

        # Engaging, High-Retention Viral Description
        description = f"""🔥 {clean_name} just delivered the most viral, unhinged moment on stream! Watch until the very end to catch the crazy ending!

🎬 THE MOMENT:
{dialogue_summary}

💬 JOIN THE DEBATE:
{question}

🔔 NEVER MISS A HIGHLIGHT:
Hit Subscribe and tap the bell 🔔 for daily viral streamer moments, rage clips, and top countdown highlights!

👑 ORIGINAL CREATOR ATTRIBUTION:
• Streamer: {clean_name} ({creator_tag})
• Official Channel: {channel_link}
• All credits and rights reserved to the original creator.

{tags_string}"""

        return {
            "title": primary_title,
            "title_suggestions": title_pool,
            "description": description.strip(),
            "tags": combined_tags,
            "tags_string": tags_string,
            "creator_credit": creator_tag,
            "creator_name": clean_name
        }

    def generate_compilation_metadata(self, creator_names: list, num_items: int = 5) -> dict:
        """
        Generates high-CTR compilation title and description for Top N Countdown Shorts.
        """
        unique_creators = [c.lstrip("@").strip() for c in creator_names if c.strip()]
        if not unique_creators:
            unique_creators = ["Streamer"]

        main_creator = unique_creators[0]
        c_upper = main_creator.upper()

        if len(unique_creators) >= 2:
            second_creator = unique_creators[1].upper()
            title_templates = [
                f"TOP {num_items} FUNNIEST {c_upper} & {second_creator} MOMENTS EVER! 💀🔥",
                f"TOP {num_items} TIMES STREAMERS BROKE THE INTERNET! 😱💀 #Shorts",
                f"RANKING THE TOP {num_items} MOST UNHINGED STREAM MOMENTS OF 2026! 🏆⚡",
                f"TOP {num_items} ILLEGAL STREAM CLIPS YOU CANNOT UNSEE! 😭💥",
                f"TOP {num_items} TIMES STREAMERS FORGOT THEY WERE LIVE ON CAMERA! 💀📸"
            ]
            creators_display = ", ".join([f"@{c}" for c in unique_creators])
        else:
            title_templates = [
                f"TOP {num_items} FUNNIEST {c_upper} MOMENTS OF ALL TIME! 💀🔥 #Shorts",
                f"TOP {num_items} CRAZIEST {c_upper} REACTIONS THAT BROKE THE INTERNET! 😱⚡",
                f"TOP {num_items} TIMES {c_upper} ACTUALLY LOST HIS MIND ON STREAM 😭",
                f"RANKING THE TOP {num_items} UNHINGED {c_upper} CLIPS OF 2026! 🏆",
                f"TOP {num_items} TIMES {c_upper} FORGOT HE WAS LIVE ON CAMERA! 💀"
            ]
            creators_display = f"@{main_creator}"

        title = title_templates[0]

        tags = ["#Shorts", f"#Top{num_items}", "#Compilation", "#Viral", "#Trending", "#FunnyMoments", "#Gaming", "#TwitchHighlights", f"#{main_creator.replace(' ', '')}"]
        tags_string = " ".join(tags)

        # Dynamic chapter breakdown
        chapters_text = "\n".join([f"• #{num_items - i} Viral Moment — Intensity Peak #{i + 1} 🔥" for i in range(num_items)])

        description = f"""🔥 The Ultimate Top {num_items} Countdown compilation of the wildest, funniest, and most chaotic stream moments!

🏆 COUNTDOWN MOMENTS RANKING:
{chapters_text}

💬 DROP YOUR RATING:
Which moment was #1 for you? Drop your timestamp and favorite clip in the comments below! 👇

🔔 SUBSCRIBE FOR MORE:
Subscribe and turn on notifications 🔔 for daily Top 5 compilations, streamer highlights, and viral shorts!

👑 CREATOR CREDITS & ATTRIBUTION:
• Featured Creators: {creators_display}
• Content curated from official streams. All rights and credits belong to the original creators.

{tags_string}"""

        return {
            "title": title,
            "title_suggestions": title_templates,
            "description": description.strip(),
            "tags": tags,
            "tags_string": tags_string,
            "creator_name": main_creator
        }
