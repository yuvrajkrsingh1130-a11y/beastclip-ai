Option Explicit
Dim WshShell, ret
Set WshShell = CreateObject("WScript.Shell")

' Check if BeastClips server is responding on port 8000
ret = WshShell.Run("curl.exe -s --connect-timeout 1 http://127.0.0.1:8000/api/presets", 0, True)

' If not responding (ret <> 0), launch it silently in the background
If ret <> 0 Then
    WshShell.CurrentDirectory = "C:\Users\yuvra\.gemini\antigravity\scratch\beastclip-ai"
    WshShell.Run """C:\Users\yuvra\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe"" -m uvicorn backend.app:app --host 127.0.0.1 --port 8000", 0, False
End If
