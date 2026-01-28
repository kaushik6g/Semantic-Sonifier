"""
Streamlit Web Interface for Semantic Sonifier
"""

import streamlit as st
import requests
import time
from pathlib import Path

st.set_page_config(
    page_title="Semantic Sonifier",
    page_icon="🎵",
    layout="wide"
)

st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

class SonifierWebApp:
    def __init__(self):
        self.api_base = "http://localhost:8000"
        self.setup_session_state()
    
    def setup_session_state(self):
        if 'processing' not in st.session_state:
            st.session_state.processing = False
        if 'result' not in st.session_state:
            st.session_state.result = None
    
    def render_header(self):
        st.markdown('<h1 class="main-header">🎵 Semantic Sonifier</h1>', unsafe_allow_html=True)
        st.markdown("""
        <div style='text-align: center; margin-bottom: 2rem;'>
            <h3>Transform images into music using AI</h3>
            <p>Upload an image and our AI will analyze its content and mood to generate unique music</p>
        </div>
        """, unsafe_allow_html=True)
    
    def render_upload_section(self):
        st.subheader("📷 Upload Image")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            uploaded_file = st.file_uploader(
                "Choose an image file",
                type=['jpg', 'jpeg', 'png']
            )
        
        with col2:
            duration = st.slider(
                "Music Duration (seconds)",
                min_value=5,
                max_value=30,
                value=10
            )
        
        if uploaded_file and st.button("🎵 Generate Music", type="primary"):
            return uploaded_file, duration
        
        return None, duration
    
    def process_image(self, uploaded_file, duration):
        try:
            st.session_state.processing = True
            st.session_state.result = None
            
            with st.spinner("🔄 Analyzing image and generating music..."):
                files = {"image": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {"duration": duration}
                
                response = requests.post(
                    f"{self.api_base}/process",
                    files=files,
                    data=data
                )
                
                if response.status_code == 200:
                    st.session_state.result = response.json()
                    st.success("✅ Music generated successfully!")
                else:
                    st.error(f"❌ Error: {response.json().get('detail', 'Unknown error')}")
                    
        except requests.exceptions.ConnectionError:
            st.error("🚨 Cannot connect to the AI server. Make sure the FastAPI server is running.")
            st.info("Run: `python start_api.py` in another terminal")
        except Exception as e:
            st.error(f"❌ Processing failed: {str(e)}")
        finally:
            st.session_state.processing = False
    
    def render_results(self):
        if not st.session_state.result:
            return
        
        result = st.session_state.result
        
        st.subheader("🎨 Analysis Results")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Image Understanding**")
            st.markdown(f"**Caption:** {result['caption']}")
            st.markdown(f"**Mood:** {result['mood']}")
            st.markdown(f"**Duration:** {result['duration']:.1f}s")
        
        with col2:
            st.markdown("**Music Generation**")
            st.markdown(f"**AI Prompt:** {result['prompt']}")
        
        st.subheader("🎵 Generated Music")
        
        try:
            audio_response = requests.get(f"{self.api_base}/audio/{result['file_id']}")
            
            if audio_response.status_code == 200:
                st.audio(audio_response.content, format="audio/wav")
                
                st.download_button(
                    label="📥 Download Audio",
                    data=audio_response.content,
                    file_name=f"sonified_{result['file_id']}.wav",
                    mime="audio/wav"
                )
            else:
                st.error("Could not load audio file")
                
        except Exception as e:
            st.error(f"Error loading audio: {str(e)}")
    
    def run(self):
        self.render_header()
        
        uploaded_file, duration = self.render_upload_section()
        
        if uploaded_file and not st.session_state.processing:
            self.process_image(uploaded_file, duration)
        
        self.render_results()

if __name__ == "__main__":
    app = SonifierWebApp()
    app.run()
