"""VOICEVOX integration for voice synthesis."""

import requests
import json
import time
import streamlit as st
from typing import Optional, List, Dict, Any
from src.config import VOICEVOX_URLS

class VoiceVoxClient:
    """VOICEVOX client for voice synthesis."""
    
    def __init__(self):
        self.base_url: Optional[str] = None
        self._connect()
    
    def _connect(self) -> None:
        """Try to connect to VOICEVOX server."""
        for url in VOICEVOX_URLS:
            try:
                response = requests.get(f"{url}/speakers", timeout=5)
                if response.status_code == 200:
                    self.base_url = url
                    return
            except requests.exceptions.RequestException:
                continue
        self.base_url = None
    
    def is_connected(self) -> bool:
        """Check if connected to VOICEVOX server."""
        return self.base_url is not None
    
    def get_speakers(self) -> List[Dict[str, Any]]:
        """Get available speakers."""
        if not self.is_connected():
            return []
        
        try:
            response = requests.get(f"{self.base_url}/speakers")
            if response.status_code == 200:
                return response.json()
        except requests.exceptions.RequestException:
            pass
        return []
    
    def synthesize_speech(self, text: str, speaker: int = 0, speed: float = 1.0, 
                         pitch: float = 0.0, intonation: float = 1.0) -> Optional[bytes]:
        """Synthesize speech from text."""
        if not self.is_connected():
            return None
        
        try:
            # Query for audio synthesis
            query_payload = {
                "text": text,
                "speaker": speaker,
                "speedScale": speed,
                "pitchScale": pitch,
                "intonationScale": intonation
            }
            
            query_response = requests.post(
                f"{self.base_url}/audio_query",
                params={"text": text, "speaker": speaker}
            )
            
            if query_response.status_code != 200:
                return None
            
            # Synthesis
            synthesis_response = requests.post(
                f"{self.base_url}/synthesis",
                headers={"Content-Type": "application/json"},
                params={"speaker": speaker},
                data=json.dumps(query_response.json())
            )
            
            if synthesis_response.status_code == 200:
                return synthesis_response.content
                
        except requests.exceptions.RequestException as e:
            st.error(f"VOICEVOX エラー: {str(e)}")
        
        return None

# Global instance
voicevox_client = VoiceVoxClient()