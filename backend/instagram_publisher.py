import os
import json
import datetime
from pathlib import Path
import urllib.request
import urllib.parse
from backend.config import BASE_DIR

AUTH_DIR = BASE_DIR / "auth"
AUTH_DIR.mkdir(parents=True, exist_ok=True)
INSTAGRAM_AUTH_FILE = AUTH_DIR / "instagram_account.json"

class InstagramPublisher:
    def __init__(self):
        self.account_data = None
        self._load_account()

    def _load_account(self):
        if INSTAGRAM_AUTH_FILE.exists():
            try:
                with open(INSTAGRAM_AUTH_FILE, "r", encoding="utf-8") as f:
                    self.account_data = json.load(f)
            except Exception as e:
                print(f"[InstagramPublisher] Error loading account: {e}")
                self.account_data = None

    def is_connected(self) -> bool:
        if not self.account_data and INSTAGRAM_AUTH_FILE.exists():
            self._load_account()
        return bool(self.account_data and self.account_data.get("is_connected", False))

    def get_status(self) -> dict:
        if not self.is_connected():
            return {
                "connected": False,
                "handle": None,
                "account_name": None,
                "avatar": None,
                "has_api_token": False
            }
        
        handle = self.account_data.get("handle", "")
        clean_handle = handle.lstrip("@")
        return {
            "connected": True,
            "handle": f"@{clean_handle}" if clean_handle else "@InstagramCreator",
            "account_name": self.account_data.get("account_name", f"@{clean_handle}"),
            "avatar": self.account_data.get("avatar") or f"https://ui-avatars.com/api/?name={clean_handle or 'IG'}&background=E1306C&color=fff&rounded=true&bold=true",
            "has_api_token": bool(self.account_data.get("access_token")),
            "connected_at": self.account_data.get("connected_at")
        }

    def connect_account(self, handle: str, account_name: str = None, access_token: str = None, instagram_account_id: str = None) -> dict:
        clean_handle = handle.strip().lstrip("@")
        if not clean_handle:
            raise ValueError("Please provide a valid Instagram username/handle")

        name = account_name.strip() if account_name else clean_handle
        avatar = f"https://ui-avatars.com/api/?name={urllib.parse.quote(name)}&background=E1306C&color=fff&rounded=true&bold=true"

        data = {
            "handle": f"@{clean_handle}",
            "account_name": name,
            "avatar": avatar,
            "access_token": access_token.strip() if access_token else None,
            "instagram_account_id": instagram_account_id.strip() if instagram_account_id else None,
            "connected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "is_connected": True
        }

        with open(INSTAGRAM_AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.account_data = data
        return self.get_status()

    def disconnect_account(self) -> dict:
        if INSTAGRAM_AUTH_FILE.exists():
            try:
                INSTAGRAM_AUTH_FILE.unlink()
            except Exception:
                pass
        self.account_data = None
        return {"connected": False}

    def format_reels_caption(self, title: str, creator_credit: str = None, custom_tags: list = None) -> str:
        """
        Formats high-engagement Instagram Reels caption optimized for algorithm watch-time:
        Hook -> Spacing -> Creator credit -> Call to Action -> Top Reels Hashtags.
        """
        clean_handle = self.account_data.get("handle", "@yourpage") if self.account_data else "@yourpage"
        credit_line = f"🎥 Credit: {creator_credit}" if creator_credit else "🎥 Original clip credit to creator"

        default_reels_tags = [
            "#reels", "#reelsinstagram", "#viralreels", "#explorepage",
            "#trendingreels", "#fyp", "#instareels", "#funnyreels",
            "#streamerclips", "#viral"
        ]

        if custom_tags:
            for t in custom_tags:
                tag_fmt = t.strip()
                if not tag_fmt.startswith("#"):
                    tag_fmt = f"#{tag_fmt}"
                if tag_fmt not in default_reels_tags:
                    default_reels_tags.append(tag_fmt)

        reels_tags_str = " ".join(default_reels_tags[:15])

        caption = f"""{title} 😱🔥

{credit_line}
Follow {clean_handle} for daily viral streamer moments! 🚀
💬 Rate this moment 1-10 in the comments!

.
.
{reels_tags_str}"""
        return caption.strip()

    def publish_reel_api(self, video_public_url: str, caption: str) -> dict:
        """
        Publishes Reel directly via Meta Graph API if Access Token and IG Account ID exist.
        """
        if not self.is_connected() or not self.account_data.get("access_token") or not self.account_data.get("instagram_account_id"):
            return {
                "success": False,
                "error": "Meta Graph API token or Instagram Business Account ID is missing. You can use 1-click web upload!"
            }

        token = self.account_data["access_token"]
        ig_user_id = self.account_data["instagram_account_id"]

        try:
            # 1. Create Reels Media Container
            container_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media"
            params = {
                "media_type": "REELS",
                "video_url": video_public_url,
                "caption": caption,
                "access_token": token
            }
            encoded_data = urllib.parse.urlencode(params).encode("utf-8")
            req = urllib.request.Request(container_url, data=encoded_data, method="POST")
            with urllib.request.urlopen(req) as resp:
                res_data = json.loads(resp.read().decode("utf-8"))
                container_id = res_data.get("id")

            if not container_id:
                raise RuntimeError("Failed to create Instagram Reels container")

            # 2. Publish Container
            publish_url = f"https://graph.facebook.com/v19.0/{ig_user_id}/media_publish"
            pub_params = {
                "creation_id": container_id,
                "access_token": token
            }
            pub_data = urllib.parse.urlencode(pub_params).encode("utf-8")
            pub_req = urllib.request.Request(publish_url, data=pub_data, method="POST")
            with urllib.request.urlopen(pub_req) as pub_resp:
                pub_res_data = json.loads(pub_resp.read().decode("utf-8"))
                reel_id = pub_res_data.get("id")

            return {
                "success": True,
                "reel_id": reel_id,
                "message": f"Successfully published to Instagram Reels (ID: {reel_id})!"
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
