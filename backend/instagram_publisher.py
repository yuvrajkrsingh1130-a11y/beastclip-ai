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
INSTAGRAM_SESSION_FILE = AUTH_DIR / "instagram_session.json"

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
                "has_api_token": False,
                "has_direct_session": INSTAGRAM_SESSION_FILE.exists()
            }
        
        handle = self.account_data.get("handle", "")
        clean_handle = handle.lstrip("@")
        return {
            "connected": True,
            "handle": f"@{clean_handle}" if clean_handle else "@InstagramCreator",
            "account_name": self.account_data.get("account_name", f"@{clean_handle}"),
            "avatar": self.account_data.get("avatar") or f"https://ui-avatars.com/api/?name={clean_handle or 'IG'}&background=E1306C&color=fff&rounded=true&bold=true",
            "has_api_token": bool(self.account_data.get("access_token")),
            "has_direct_session": INSTAGRAM_SESSION_FILE.exists(),
            "connected_at": self.account_data.get("connected_at")
        }

    def login_account(self, username: str = None, password: str = None, sessionid: str = None, verification_code: str = None) -> dict:
        """
        Connects an Instagram account via direct Instagram login or session cookie.
        Saves session securely in auth/instagram_session.json for automated headless Reel uploads.
        """
        from instagrapi import Client
        from instagrapi.exceptions import TwoFactorRequired, BadPassword, ChallengeRequired, PleaseWaitFewMinutes

        cl = Client()
        cl.delay_range = [1, 3]

        if sessionid and sessionid.strip():
            # Login via browser session cookie
            clean_session = sessionid.strip()
            try:
                cl.login_by_sessionid(clean_session)
                user_info = cl.account_info()
            except Exception as e:
                raise ValueError(f"Failed to log in with session ID: {e}")
        elif username and password:
            clean_user = username.strip().lstrip("@")
            clean_pass = password.strip()
            if INSTAGRAM_SESSION_FILE.exists():
                try:
                    cl.load_settings(str(INSTAGRAM_SESSION_FILE))
                except Exception:
                    pass
            try:
                if verification_code and verification_code.strip():
                    cl.login(clean_user, clean_pass, verification_code=verification_code.strip())
                else:
                    cl.login(clean_user, clean_pass)
                user_info = cl.account_info()
            except TwoFactorRequired:
                return {
                    "need_2fa": True,
                    "message": "Two-factor authentication code required. Please enter the 6-digit code sent to your phone or authenticator app."
                }
            except BadPassword:
                raise ValueError("Incorrect Instagram password. Please check your credentials and try again.")
            except ChallengeRequired as e:
                raise ValueError(f"Instagram security checkpoint: {e}. You can alternatively use your browser's sessionid cookie.")
            except PleaseWaitFewMinutes:
                raise ValueError("Instagram temporarily rate-limited login requests. Please wait a few minutes or log in via sessionid.")
            except Exception as e:
                raise ValueError(f"Instagram login error: {e}")
        else:
            raise ValueError("Please provide your Instagram username and password (or sessionid cookie).")

        # Save session
        cl.dump_settings(str(INSTAGRAM_SESSION_FILE))

        data = {
            "handle": f"@{user_info.username}",
            "account_name": user_info.full_name or user_info.username,
            "avatar": str(user_info.profile_pic_url) if getattr(user_info, "profile_pic_url", None) else None,
            "followers": getattr(user_info, "follower_count", 0),
            "login_type": "direct_session",
            "connected_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            "is_connected": True
        }

        with open(INSTAGRAM_AUTH_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        self.account_data = data
        return self.get_status()

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
        if INSTAGRAM_SESSION_FILE.exists():
            try:
                INSTAGRAM_SESSION_FILE.unlink()
            except Exception:
                pass
        self.account_data = None
        return {"connected": False}

    def upload_reel_direct(self, video_path: str, caption: str, thumbnail_path: str = None) -> dict:
        """
        Headlessly uploads the 1080x1920 MP4 Reel directly to the user's connected Instagram account,
        applying the viral caption and thumbnail automatically.
        """
        v_path = Path(video_path)
        if not v_path.exists():
            raise FileNotFoundError(f"Video file not found at: {video_path}")

        if not INSTAGRAM_SESSION_FILE.exists():
            raise RuntimeError("Instagram session not found. Please log into your Instagram account in BeastClip AI first!")

        from instagrapi import Client
        cl = Client()
        cl.delay_range = [1, 3]
        cl.load_settings(str(INSTAGRAM_SESSION_FILE))

        t_path = Path(thumbnail_path) if thumbnail_path and Path(thumbnail_path).exists() else None

        print(f"[InstagramPublisher] Uploading Reel directly: {v_path.name} ({v_path.stat().st_size} bytes)...")
        media = cl.clip_upload(
            path=v_path,
            caption=caption,
            thumbnail=t_path
        )

        code = getattr(media, "code", "")
        media_id = str(getattr(media, "pk", ""))
        reel_url = f"https://www.instagram.com/reel/{code}/" if code else "https://www.instagram.com/"

        # Refresh session dump
        try:
            cl.dump_settings(str(INSTAGRAM_SESSION_FILE))
        except Exception:
            pass

        return {
            "success": True,
            "media_id": media_id,
            "code": code,
            "reel_url": reel_url,
            "message": f"🎉 Successfully uploaded Reel to Instagram! View it at: {reel_url}"
        }

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
                "error": "Meta Graph API token or Instagram Business Account ID is missing."
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
