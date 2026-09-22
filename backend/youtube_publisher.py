import os
import json
import datetime
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from backend.config import BASE_DIR

AUTH_DIR = BASE_DIR / "auth"
AUTH_DIR.mkdir(parents=True, exist_ok=True)

CLIENT_SECRETS_FILE = AUTH_DIR / "client_secret.json"
TOKEN_FILE = AUTH_DIR / "youtube_token.json"

SCOPES = [
    "https://www.googleapis.com/auth/youtube.upload",
    "https://www.googleapis.com/auth/youtube.readonly"
]

class YouTubePublisher:
    def __init__(self):
        self.credentials = None
        self._load_credentials()

    def _load_credentials(self):
        """Loads saved OAuth credentials if they exist."""
        if TOKEN_FILE.exists():
            try:
                self.credentials = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    self.credentials.refresh(Request())
                    with open(TOKEN_FILE, "w") as token:
                        token.write(self.credentials.to_json())
            except Exception as e:
                print(f"[YouTubePublisher] Error loading credentials: {e}")
                self.credentials = None

    def is_authenticated(self) -> bool:
        """Returns True if valid credentials exist, auto-refreshing if expired."""
        if not self.credentials and TOKEN_FILE.exists():
            self._load_credentials()
        if self.credentials:
            if self.credentials.expired and self.credentials.refresh_token:
                try:
                    self.credentials.refresh(Request())
                    with open(TOKEN_FILE, "w") as token:
                        token.write(self.credentials.to_json())
                except Exception as e:
                    print(f"[YouTubePublisher] Error refreshing credentials: {e}")
                    return False
            return bool(self.credentials and self.credentials.valid)
        return False

    def get_auth_url(self, redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback") -> str:
        """Generates Google OAuth URL for user authentication."""
        if not CLIENT_SECRETS_FILE.exists():
            raise FileNotFoundError(
                f"Missing client_secret.json in {AUTH_DIR}. Please place your Google OAuth credentials there."
            )

        flow = Flow.from_client_secrets_file(
            str(CLIENT_SECRETS_FILE),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        auth_url, _ = flow.authorization_url(
            access_type="offline",
            include_granted_scopes="true",
            prompt="consent"
        )
        # Persist code_verifier if generated
        if hasattr(flow, "code_verifier") and flow.code_verifier:
            verifier_file = AUTH_DIR / "code_verifier.txt"
            with open(verifier_file, "w") as f:
                f.write(flow.code_verifier)

        return auth_url

    def handle_auth_callback(self, code: str, redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback") -> dict:
        """Exchanges OAuth authorization code for credentials."""
        flow = Flow.from_client_secrets_file(
            str(CLIENT_SECRETS_FILE),
            scopes=SCOPES,
            redirect_uri=redirect_uri
        )
        verifier_file = AUTH_DIR / "code_verifier.txt"
        code_verifier = None
        if verifier_file.exists():
            with open(verifier_file, "r") as f:
                code_verifier = f.read().strip()

        if code_verifier:
            flow.fetch_token(code=code, code_verifier=code_verifier)
        else:
            flow.fetch_token(code=code)

        self.credentials = flow.credentials

        with open(TOKEN_FILE, "w") as token:
            token.write(self.credentials.to_json())

        # Clean up verifier
        if verifier_file.exists():
            try:
                os.remove(verifier_file)
            except Exception:
                pass

        return self.get_channel_info()


    def save_client_secrets_from_data(self, client_id: str, client_secret: str, redirect_uri: str = "http://127.0.0.1:8000/api/youtube/callback"):
        """Creates client_secret.json from direct ID and Secret inputs."""
        data = {
            "web": {
                "client_id": client_id.strip(),
                "client_secret": client_secret.strip(),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "redirect_uris": [redirect_uri, "http://localhost:8000/api/youtube/callback"]
            }
        }
        with open(CLIENT_SECRETS_FILE, "w") as f:
            json.dump(data, f, indent=2)

    def get_channel_info(self) -> dict:
        """Fetches the connected YouTube channel's details."""
        if not self.is_authenticated():
            return {"authenticated": False}

        try:
            youtube = build("youtube", "v3", credentials=self.credentials)
            response = youtube.channels().list(
                mine=True,
                part="snippet,statistics"
            ).execute()

            items = response.get("items", [])
            if not items:
                return {"authenticated": True, "title": "Connected Channel", "custom_url": "", "subscribers": "0"}

            channel = items[0]
            snippet = channel.get("snippet", {})
            stats = channel.get("statistics", {})

            return {
                "authenticated": True,
                "channel_id": channel.get("id"),
                "title": snippet.get("title"),
                "custom_url": snippet.get("customUrl", ""),
                "description": snippet.get("description", ""),
                "avatar": snippet.get("thumbnails", {}).get("default", {}).get("url", ""),
                "subscribers": stats.get("subscriberCount", "0"),
                "video_count": stats.get("videoCount", "0")
            }
        except Exception as e:
            print(f"[YouTubePublisher] Error getting channel info: {e}")
            return {"authenticated": False, "error": str(e)}

    def upload_short(
        self,
        video_path: str,
        title: str,
        description: str,
        tags: list,
        privacy_status: str = "public",
        publish_at: datetime.datetime = None,
        thumbnail_path: str = None,
        category_id: str = "20" # 20 = Gaming, 24 = Entertainment
    ) -> dict:
        """
        Uploads a vertical Short to YouTube with full metadata and optional scheduling.
        """
        if not self.is_authenticated():
            raise RuntimeError("YouTube account is not connected. Please authenticate first.")

        youtube = build("youtube", "v3", credentials=self.credentials)

        # Title limit on YouTube is 100 characters
        clean_title = title[:95]
        if not clean_title.lower().endswith("#shorts"):
            clean_title = f"{clean_title} #Shorts"[:100]

        # Status payload
        status_payload = {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }

        # If scheduling for future publishing, privacyStatus MUST be "private" with "publishAt"
        if publish_at:
            status_payload["privacyStatus"] = "private"
            if isinstance(publish_at, str):
                try:
                    # Clean input string
                    clean_str = publish_at.strip()
                    if clean_str.endswith("Z"):
                        clean_str = clean_str[:-1] + "+00:00"
                    dt_obj = datetime.datetime.fromisoformat(clean_str)
                    if dt_obj.tzinfo is None:
                        # Fallback to UTC if naive
                        dt_obj = dt_obj.replace(tzinfo=datetime.timezone.utc)
                    utc_time = dt_obj.astimezone(datetime.timezone.utc)
                except Exception as ex:
                    print(f"[YouTubePublisher] publish_at parse warning: {ex}")
                    utc_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
            else:
                if publish_at.tzinfo is None:
                    publish_at = publish_at.replace(tzinfo=datetime.timezone.utc)
                utc_time = publish_at.astimezone(datetime.timezone.utc)
            
            # YouTube API requires ISO 8601 format: YYYY-MM-DDTHH:MM:SS.sZ
            status_payload["publishAt"] = utc_time.strftime("%Y-%m-%dT%H:%M:%S.000Z")

        body = {
            "snippet": {
                "title": clean_title,
                "description": description,
                "tags": tags[:20] if tags else ["#Shorts"],
                "categoryId": category_id
            },
            "status": status_payload
        }

        # Resumable upload
        media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
        request = youtube.videos().insert(
            part="snippet,status",
            body=body,
            media_body=media
        )

        response = None
        while response is None:
            status, response = request.next_chunk()

        video_id = response.get("id")

        # Upload custom thumbnail if provided
        thumbnail_status = "not_provided"
        if thumbnail_path and os.path.exists(thumbnail_path) and video_id:
            try:
                youtube.thumbnails().set(
                    videoId=video_id,
                    media_body=MediaFileUpload(thumbnail_path, mimetype="image/jpeg", resumable=False)
                ).execute()
                thumbnail_status = "uploaded"
            except Exception as e:
                print(f"[YouTubePublisher] Thumbnail upload notice: {e}")
                thumbnail_status = f"notice: {e}"

        return {
            "status": "success",
            "video_id": video_id,
            "youtube_url": f"https://youtube.com/shorts/{video_id}",
            "publish_at": status_payload.get("publishAt"),
            "thumbnail_status": thumbnail_status
        }

    def compute_drip_schedule(
        self,
        num_clips: int,
        shorts_per_day: int = 3,
        start_datetime: str = None,
        custom_hours: list = None,
        interval_hours: int = None
    ) -> list:
        """
        Calculates spaced timestamps based on user preferences:
        - Specific start date/time
        - Custom peak hours (e.g. [11, 15, 19] = 11am, 3:30pm, 7:30pm) or custom user hours
        - Or fixed interval spacing (e.g. every 6 hours)
        """
        schedule_times = []
        
        # Determine start time
        if start_datetime:
            try:
                clean_str = start_datetime.strip()
                if clean_str.endswith("Z"):
                    clean_str = clean_str[:-1] + "+00:00"
                start_dt = datetime.datetime.fromisoformat(clean_str)
                if start_dt.tzinfo is None:
                    start_dt = start_dt.replace(tzinfo=datetime.timezone.utc)
                base_time = start_dt.astimezone(datetime.timezone.utc)
            except Exception:
                base_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)
        else:
            base_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=2)

        # Mode 1: Fixed Interval spacing (e.g. every X hours)
        if interval_hours and interval_hours > 0:
            for i in range(num_clips):
                target_dt = base_time + datetime.timedelta(hours=i * interval_hours)
                schedule_times.append(target_dt)
            return schedule_times

        # Mode 2: Peak / Custom Hours per day (10 Top YouTube Shorts Viral Slots)
        # 7:30 AM, 9:00 AM, 11:30 AM, 1:00 PM, 3:30 PM, 5:00 PM, 7:30 PM, 9:00 PM, 10:30 PM, 12:00 AM
        hours_list = custom_hours if (custom_hours and len(custom_hours) > 0) else [
            7.5, 9.0, 11.5, 13.0, 15.5, 17.0, 19.5, 21.0, 22.5, 24.0
        ]
        # Limit to shorts_per_day
        if shorts_per_day and shorts_per_day < len(hours_list):
            hours_list = hours_list[:shorts_per_day]

        current_date = base_time.date()
        day_offset = 0
        hour_idx = 0

        for i in range(num_clips):
            hour_val = hours_list[hour_idx % len(hours_list)]
            target_hour = int(hour_val) % 24
            extra_day = 1 if int(hour_val) == 24 else 0
            minute = int(round((hour_val - int(hour_val)) * 60))

            target_dt = datetime.datetime(
                year=current_date.year,
                month=current_date.month,
                day=current_date.day,
                hour=target_hour,
                minute=minute,
                tzinfo=datetime.timezone.utc
            ) + datetime.timedelta(days=day_offset + extra_day)

            # Ensure time is not in past relative to base_time
            if target_dt <= base_time and day_offset == 0:
                day_offset += 1
                target_dt = target_dt + datetime.timedelta(days=1)

            schedule_times.append(target_dt)

            hour_idx += 1
            if hour_idx % len(hours_list) == 0:
                day_offset += 1

        return schedule_times
