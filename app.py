import streamlit as st
import tempfile
import os
import time
import base64
import json
from utils import extract_metadata, calculate_hash, analyze_frames
from visualizations import display_metadata_chart, plot_altered_frames, create_frame_heatmap

# Page configuration
st.set_page_config(
    page_title="VidGuard - Video Forensic Analysis",
    page_icon="🎬",
    layout="wide",
)

# Display VidGuard logo
st.markdown(
    """
    <div style="text-align: center">
        <svg width="200" height="100" viewBox="0 0 200 100">
            <rect x="20" y="20" width="160" height="60" rx="10" fill="#4682B4" />
            <text x="100" y="55" fill="white" font-family="Arial" font-size="24" text-anchor="middle" font-weight="bold">VidGuard</text>
            <circle cx="170" cy="30" r="10" fill="#FF5733" />
            <path d="M50,65 L80,40 L110,65" stroke="white" stroke-width="3" fill="none" />
        </svg>
        <h1 style="font-size: 2.5em;">Video Forensic Analysis</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Create tabs for different sections of the app
tab1, tab2, tab3 = st.tabs(["Home & Upload", "Analysis Results", "Forensic Report"])

with tab1:
    st.markdown("## About Video Forensics")
    
    st.markdown("""
    ### Importance of Video Forensics
    In today's digital age, video content serves as crucial evidence in legal proceedings, security investigations, and news verification.
    Video forensics is essential for:
    - **Legal Evidence**: Ensuring video evidence hasn't been tampered with before court submission
    - **Security Investigations**: Analyzing surveillance footage for authenticity
    - **Media Verification**: Combating fake news and manipulated content
    - **Digital Rights Management**: Protecting intellectual property and copyright
    
    ### Common Video Manipulation Threats
    """)
    
    # Create columns for threats
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        - **Deepfake Manipulation**: AI-generated fake videos
        - **Frame Injection**: Adding or removing frames
        """)
    
    with col2:
        st.markdown("""
        - **Metadata Spoofing**: Altering video creation dates/times
        - **Codec-level Tampering**: Manipulating compression artifacts
        """)
    
    st.markdown("""
    ### Advancements in Video Forensics
    - **AI-based forgery detection**: Machine learning to identify manipulated content
    - **Blockchain authentication**: Immutable verification of video integrity
    - **Multi-spectral analysis**: Examining videos across different data dimensions
    """)
    
    st.markdown("---")
    
    st.markdown("## Upload Video for Analysis")
    
    # File uploader
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv'])
    
    if uploaded_file is not None:
        # Save the uploaded file to a temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.mp4') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            video_path = tmp_file.name
        
        # Show a spinner while analyzing the video
        with st.spinner("Analyzing video. This may take a while depending on the file size..."):
            # Create a progress bar
            progress_bar = st.progress(0)
            
            # Extract metadata (10% of progress)
            progress_bar.progress(10)
            metadata = extract_metadata(video_path)
            time.sleep(0.5)  # Simulate processing time
            
            # Calculate hash (30% of progress)
            progress_bar.progress(30)
            video_hash = calculate_hash(video_path)
            time.sleep(0.5)  # Simulate processing time
            
            # Analyze frames (90% of progress)
            progress_bar.progress(60)
            altered_frames = analyze_frames(video_path)
            time.sleep(0.5)  # Simulate processing time
            
            # Create forensic report
            report = {
                'filename': uploaded_file.name,
                'filesize': uploaded_file.size,
                'metadata': metadata,
                'hash': video_hash,
                'altered_frames': altered_frames,
                'analysis_timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # Store report in session state for access in other tabs
            st.session_state.report = report
            st.session_state.video_path = video_path
            
            # Complete progress
            progress_bar.progress(100)
            time.sleep(0.5)  # Simulate processing time
            
        st.success("Video analysis complete! Go to the 'Analysis Results' tab to see the findings.")
        
        # Clean up the temporary file - we'll do this when the session ends
        # Don't delete now as we need it for the other tabs
        
with tab2:
    if 'report' in st.session_state:
        report = st.session_state.report
        
        st.markdown("## Video Analysis Results")
        
        # Basic information
        st.markdown("### Basic Information")
        basic_info_col1, basic_info_col2 = st.columns(2)
        
        with basic_info_col1:
            st.markdown(f"**Filename:** {report['filename']}")
            st.markdown(f"**File Size:** {report['filesize']/1024/1024:.2f} MB")
            st.markdown(f"**Analysis Date:** {report['analysis_timestamp']}")
        
        with basic_info_col2:
            st.markdown(f"**MD5 Hash:** `{report['hash']}`")
            st.markdown(f"**Duration:** {report['metadata']['frame_count']/report['metadata']['fps']:.2f} seconds")

        # Metadata visualization
        st.markdown("### Video Metadata")
        display_metadata_chart(report['metadata'])
        
        # Altered frames visualization
        st.markdown("### Frame Analysis")
        
        if len(report['altered_frames']) > 0:
            st.warning(f"**Potential tampering detected!** Found {len(report['altered_frames'])} frames with significant changes.")
            plot_altered_frames(report['altered_frames'], report['metadata']['frame_count'])
            create_frame_heatmap(report['altered_frames'], report['metadata']['frame_count'])
        else:
            st.success("**No signs of tampering detected.** Frame analysis shows consistent frame transitions.")
            
        # Display the first 100 altered frames for reference
        if len(report['altered_frames']) > 0:
            with st.expander("View detailed altered frames information"):
                max_frames = min(100, len(report['altered_frames']))
                st.write(f"First {max_frames} altered frame positions (out of {len(report['altered_frames'])} total):")
                st.write(report['altered_frames'][:max_frames])
                
    else:
        st.info("Please upload a video in the 'Home & Upload' tab to see analysis results.")

with tab3:
    if 'report' in st.session_state:
        report = st.session_state.report
        
        st.markdown("## Forensic Report")
        
        # Create JSON string from report
        report_json = json.dumps(report, indent=4)
        
        # Display JSON in a code block
        st.markdown("### Report Data (JSON)")
        st.code(report_json, language="json")
        
        # Provide download button for the report
        st.markdown("### Download Report")
        
        # Function to create a download link for the report
        def get_report_download_link(report_json, filename="vidguard_forensic_report.json"):
            b64 = base64.b64encode(report_json.encode()).decode()
            href = f'<a href="data:file/json;base64,{b64}" download="{filename}">Download Report (JSON)</a>'
            return href
        
        st.markdown(get_report_download_link(report_json), unsafe_allow_html=True)
        
        # Forensic summary
        st.markdown("### Forensic Analysis Summary")
        
        # Overall integrity assessment
        if len(report['altered_frames']) > 0:
            integrity_score = max(0, 100 - (len(report['altered_frames']) / report['metadata']['frame_count'] * 100))
            st.warning(f"**Video Integrity Score: {integrity_score:.1f}%**")
            st.markdown("This video shows signs of potential tampering. The altered frames suggest possible manipulation.")
        else:
            st.success("**Video Integrity Score: 100%**")
            st.markdown("This video appears to be unaltered. No signs of frame tampering were detected.")
        
        # Recommendations
        st.markdown("### Recommendations")
        if len(report['altered_frames']) > 0:
            st.markdown("""
            - Conduct further analysis on the identified altered frames
            - Consider advanced forensic techniques for deeper examination
            - Document the chain of custody for the video file
            - Compare with the original source if available
            """)
        else:
            st.markdown("""
            - Maintain proper documentation of this forensic result
            - Store the hash value for future verification
            - Consider blockchain registration for immutable proof of integrity
            """)
            
    else:
        st.info("Please upload a video in the 'Home & Upload' tab to generate a forensic report.")

# Add a footer
st.markdown("---")
st.markdown("*VidGuard - Advanced Video Forensics Tool. For investigative and educational purposes only.*")

# Clean up temporary files when the session ends
if 'video_path' in st.session_state:
    try:
        os.unlink(st.session_state.video_path)
    except:
        pass  # We'll ignore errors in cleanup
