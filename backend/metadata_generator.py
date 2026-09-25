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
        """Categorizes transcript into emotion tone for hook and hashtag optimization."""
        t = text.lower()
        if any(k in t for k in ["laugh", "haha", "lmao", "dead", "funny", "joke", "crying", "aint no way", "no way", "rofl"]):
            return "humor"
        elif any(k in t for k in ["rage", "scream", "shut up", "hate", "smash", "break", "mad", "angry", "yell", "crash"]):
            return "rage"
        elif any(k in t for k in ["what", "how", "omg", "oh my god", "bro", "caught", "police", "wait", "cheating", "ban", "ronaldo", "siu"]):
            return "shock"
        elif any(k in t for k in ["clutch", "win", "kill", "headshot", "god", "pro", "insane", "play", "clean", "goat"]):
            return "clutch"
        return "general"

    def _build_niche_hashtags(self, found_entity: str, context: str, creator_name: str) -> list:
        """Builds niche-specific high-velocity trending hashtags."""
        tags = []
        c_clean = creator_name.replace(' ', '').replace('@', '')
        if c_clean and c_clean.lower() != "streamer":
            tags.append(f"#{c_clean}")
            tags.append(f"#{c_clean}Clips")

        if found_entity in ["RONALDO", "CR7"] or "ronaldo" in context.lower():
            tags.extend(["#Ronaldo", "#CristianoRonaldo", "#CR7", "#SIUUU", "#IShowSpeed", "#Speed", "#Football", "#Soccer", "#GOAT", "#Portugal", "#RealMadrid", "#RonaldoFans"])
        elif found_entity == "MESSI":
            tags.extend(["#Messi", "#LionelMessi", "#InterMiami", "#GOAT", "#Football", "#Soccer", "#Argentina"])
        elif found_entity == "KAI CENAT":
            tags.extend(["#KaiCenat", "#AMP", "#KaiClips", "#Mafiathon", "#DukeDennis", "#Fanum", "#Agent00", "#Twitch"])
        elif found_entity == "JYNXZI":
            tags.extend(["#Jynxzi", "#R6", "#RainbowSixSiege", "#JynxziClips", "#JynxziRage", "#ConsoleGod", "#Gaming"])
        elif found_entity == "CASEOH":
            tags.extend(["#CaseOh", "#CaseOhClips", "#CaseOhGames", "#CaseOhRage", "#FunniestStreamer", "#TryNotToLaugh"])
        elif found_entity == "MRBEAST":
            tags.extend(["#MrBeast", "#MrBeastShorts", "#Challenge", "#MrBeastGaming", "#Insane"])

        if context == "humor":
            tags.extend(["#FunnyMoments", "#TryNotToLaugh", "#Hilarious", "#Comedy", "#LMAO", "#FunniestMoments", "#Humor"])
        elif context == "rage":
            tags.extend(["#RageQuit", "#CrashOut", "#Screaming", "#Rage", "#InstantRegret", "#Mad", "#GamingRage"])
        elif context == "shock":
            tags.extend(["#PlotTwist", "#OMG", "#Unbelievable", "#NoWay", "#Shocking", "#MindBlowing", "#CrazyMoments"])
        elif context == "clutch":
            tags.extend(["#Clutch", "#ProGamer", "#GamingHighlights", "#InsanePlay", "#GoatStatus", "#Clean"])

        return list(dict.fromkeys(tags))

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

        # Viral Pinned Comments that provoke engagement & comment wars
        if found_entity == "RONALDO" or "RONALDO" in combined_check:
            pinned_comment_pool = [
                "👇 What would YOU do if you met Ronaldo in real life? (Be 100% honest) 😂👇\n\n📌 Top comment gets pinned!",
                "👇 Ronaldo or Messi? Settle the GOAT debate once and for all below! 🐐⚽\n\n📌 Best answer gets pinned!",
                "👇 Rate Speed's reaction from 1 to 10! Did he pass the vibe check? 💀🇵🇹\n\n📌 Top comment pinned!",
                "👇 Who was more shocked: Speed or Ronaldo? Drop your thoughts below! 👇"
            ]
        elif context == "humor":
            pinned_comment_pool = [
                "👇 On a scale of 1-10, how hard did you laugh? (Be real) 💀🤣\n\n📌 Top comment gets pinned!",
                "👇 What was the funniest part of this clip? Drop the timestamp! 😭👇",
                "👇 Tag that one friend who acts exactly like this every day 💀👇"
            ]
        elif context == "rage":
            pinned_comment_pool = [
                "👇 Was this rage valid or did he completely crash out for no reason? 💀🤬\n\n📌 Top comment gets pinned!",
                "👇 What is the most expensive thing you've broken in anger? Settle it below! 😭🎮"
            ]
        else:
            pinned_comment_pool = [
                "👇 Rate this moment from 1 to 10 in the comments below! 👇\n\n📌 Top comment gets pinned!",
                "👇 W or L streamer reaction? Settle the debate below! 🔥",
                "👇 What would YOU have done in this exact situation? Drop a comment! 💀"
            ]
        pinned_comment = pinned_comment_pool[(rank - 1) % len(pinned_comment_pool)]

        # Viral Opening Hooks (High Retention Visual / Text Overlays)
        viral_hooks = [
            "Wait for the ending... 💀",
            "Bro didn't realize what was about to happen 😭",
            "99% of people missed what happened in the background 🤯",
            "The exact second his dream came true 🥹❤️",
            "Watch till the end if you think this is GOATed 🐐🔥",
            "Did he actually just say that on live camera?! 😱"
        ]

        # Categorized Trending Hashtag Clusters
        shorts_feed_tags = ["#Shorts", "#Viral", "#Trending", "#FYP", "#ForYou", "#ShortsFeed", "#ViralShorts", "#YouTubeShorts", "#ShortsVideo"]
        tiktok_reels_tags = ["#fypシ", "#viralvideo", "#trending", "#foryoupage", "#explore", "#relatable", "#mustwatch", "#blowthisup"]
        streamer_gaming_tags = ["#TwitchClips", "#StreamerClips", "#Gaming", "#Gamer", "#KickClips", "#LiveStream", "#GamingMoments", "#Twitch"]
        niche_tags = self._build_niche_hashtags(found_entity, context, clean_name)

        # Combined top tags for YouTube description
        combined_tags = list(dict.fromkeys(shorts_feed_tags[:5] + niche_tags + streamer_gaming_tags[:3] + tiktok_reels_tags[:2]))
        tags_string = " ".join(combined_tags[:15])

        channel_link = uploader_url or preset["channel_url"] or "https://youtube.com"

        # Engaging, High-Retention Viral Description
        description = f"""🔥 {clean_name} just delivered the most viral, unhinged moment on stream! Watch until the very end to catch the crazy ending!

🎬 THE MOMENT:
{dialogue_summary}

💬 JOIN THE DEBATE:
{pinned_comment}

🔔 NEVER MISS A HIGHLIGHT:
Hit Subscribe and tap the bell 🔔 for daily viral streamer moments, rage clips, and top countdown highlights!

👑 ORIGINAL CREATOR ATTRIBUTION:
• Streamer: {clean_name} ({creator_tag})
• Official Channel: {channel_link}
• All credits and rights reserved to the original creator.

{tags_string}"""

        optimal_post_time = "7:30 PM - 9:30 PM EST (Peak Scroll Velocity)"

        # Full Viral Package (1-click copy bundle)
        full_viral_package = f"""📌 TITLE:
{primary_title}

💬 PINNED COMMENT:
{pinned_comment}

🎬 DESCRIPTION:
{description}

🔥 TRENDING HASHTAGS:
{tags_string}"""

        return {
            "title": primary_title,
            "title_suggestions": title_pool,
            "description": description.strip(),
            "tags": combined_tags,
            "tags_string": tags_string,
            "hashtag_clusters": {
                "shorts_feed": shorts_feed_tags,
                "tiktok_reels": tiktok_reels_tags,
                "gaming_streamer": streamer_gaming_tags,
                "niche_trending": niche_tags
            },
            "pinned_comment": pinned_comment,
            "viral_hooks": viral_hooks,
            "virality_breakdown": {
                "hook_strength": "98% (High Retention)",
                "loop_score": "Infinite (A+)",
                "optimal_time": optimal_post_time
            },
            "optimal_post_time": optimal_post_time,
            "full_viral_package": full_viral_package,
            "creator_credit": creator_tag,
            "creator_name": clean_name
        }

    def generate_compilation_metadata(self, creator_names: list, num_items: int = 5) -> dict:
        """
        Generates high-CTR compilation title, description, and viral hashtag package for Top N Countdown Shorts.
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

        tags = [
            "#Shorts", f"#Top{num_items}", "#Compilation", "#Viral", "#Trending", "#FYP",
            "#FunnyMoments", "#Gaming", "#TwitchHighlights", "#StreamerClips", "#MustWatch",
            f"#{main_creator.replace(' ', '')}"
        ]
        tags_string = " ".join(tags)

        # Dynamic chapter breakdown
        chapters_text = "\n".join([f"• #{num_items - i} Viral Moment — Intensity Peak #{i + 1} 🔥" for i in range(num_items)])

        pinned_comment = f"👇 Which moment was #1 for you? Drop your favorite timestamp below! 🏆👇\n\n📌 Top comment gets pinned!"

        description = f"""🔥 The Ultimate Top {num_items} Countdown compilation of the wildest, funniest, and most chaotic stream moments!

🏆 COUNTDOWN MOMENTS RANKING:
{chapters_text}

💬 DROP YOUR RATING:
{pinned_comment}

🔔 SUBSCRIBE FOR MORE:
Subscribe and turn on notifications 🔔 for daily Top 5 compilations, streamer highlights, and viral shorts!

👑 CREATOR CREDITS & ATTRIBUTION:
• Featured Creators: {creators_display}
• Content curated from official streams. All rights and credits belong to the original creators.

{tags_string}"""

        full_viral_package = f"""📌 TITLE:
{title}

💬 PINNED COMMENT:
{pinned_comment}

🎬 DESCRIPTION:
{description}

🔥 TRENDING HASHTAGS:
{tags_string}"""

        return {
            "title": title,
            "title_suggestions": title_templates,
            "description": description.strip(),
            "tags": tags,
            "tags_string": tags_string,
            "pinned_comment": pinned_comment,
            "hashtag_clusters": {
                "shorts_feed": ["#Shorts", "#Viral", "#Trending", "#FYP", "#ForYou", "#ShortsFeed"],
                "compilation": [f"#Top{num_items}", "#Compilation", "#Countdown", "#BestMoments"],
                "streamer_gaming": ["#TwitchHighlights", "#StreamerClips", "#Gaming", "#FunnyMoments"]
            },
            "virality_breakdown": {
                "hook_strength": "99% (Maximum Compilation Retention)",
                "loop_score": "Infinite (A+)",
                "optimal_time": "7:30 PM - 9:30 PM EST",
                "recommended_sound": "Trending Countdown Phonk"
            },
            "full_viral_package": full_viral_package,
            "creator_name": main_creator
        }
