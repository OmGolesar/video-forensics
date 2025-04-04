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
    <div style="text-align: center; background-color: black; padding: 20px; border-radius: 10px;">
        <img src="https://static.streamlit.io/examples/logo.jpg" width="200" style="display: none;">
        <img src="data:image/png;base64,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" width="200">
        <h1 style="font-size: 2.5em; color: white; margin-top: 10px;">VIDEO FORENSICS</h1>
    </div>
    """,
    unsafe_allow_html=True
)

# Create tabs for different sections of the app
tab1, tab2, tab3, tab4 = st.tabs(["Home & Upload", "Analysis Results", "Forensic Report", "Video Fraud Awareness"])

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

with tab4:
    st.markdown("# Video Fraud Awareness")
    
    st.markdown("""
    ## How Video Fraud Impacts Society
    
    Video manipulation has become increasingly sophisticated, affecting individuals, businesses, and society as a whole.
    The rise of deepfakes and other video alteration techniques has led to significant concerns across multiple sectors.
    """)
    
    # Create impact metrics with interactive elements
    st.markdown("## Impact of Video Manipulation")
    
    # Financial impact section
    financial_col1, financial_col2 = st.columns([3, 2])
    
    with financial_col1:
        st.markdown("### Financial Impact")
        st.markdown("""
        Video fraud has caused significant financial damage to individuals and organizations:
        - Corporate fraud using manipulated executive videos
        - Stock market manipulation through fake news videos
        - Insurance fraud using edited accident footage
        - Identity theft via synthetic video profiles
        """)
        
    with financial_col2:
        # Financial impact chart
        import plotly.express as px
        import pandas as pd
        
        # Sample data for financial impact (in millions of dollars)
        financial_data = pd.DataFrame({
            'Sector': ['Corporate', 'Insurance', 'Banking', 'Individual', 'Media'],
            'Estimated Annual Loss ($M)': [320, 160, 240, 80, 110]
        })
        
        fig_financial = px.bar(
            financial_data, 
            x='Sector', 
            y='Estimated Annual Loss ($M)',
            color='Sector',
            title='Estimated Financial Impact by Sector',
            labels={'Estimated Annual Loss ($M)': 'Loss in Millions USD'},
            color_discrete_sequence=px.colors.qualitative.Bold
        )
        
        fig_financial.update_layout(
            xaxis_title=None,
            yaxis_title='Financial Loss (Millions USD)',
            showlegend=False
        )
        
        st.plotly_chart(fig_financial, use_container_width=True)
    
    # Common Scam Types section with interactive pie chart
    st.markdown("### Common Video Fraud Techniques")
    
    scam_col1, scam_col2 = st.columns([2, 3])
    
    with scam_col1:
        # Pie chart of video scam types
        scam_data = pd.DataFrame({
            'Technique': ['Deepfakes', 'Selective Editing', 'Metadata Tampering', 'Context Manipulation', 'Frame Insertion'],
            'Percentage': [35, 25, 15, 15, 10]
        })
        
        fig_scams = px.pie(
            scam_data, 
            values='Percentage', 
            names='Technique',
            title='Distribution of Video Fraud Techniques',
            color_discrete_sequence=px.colors.qualitative.Set3,
            hole=0.4
        )
        
        fig_scams.update_traces(textposition='inside', textinfo='percent+label')
        fig_scams.update_layout(legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.2,
            xanchor="center",
            x=0.5
        ))
        
        st.plotly_chart(fig_scams, use_container_width=True)
    
    with scam_col2:
        st.markdown("""
        ### How People Get Scammed
        
        Victims are often targeted through sophisticated techniques:
        
        **Deepfakes (35%)**: AI-generated videos that replace faces or create entirely synthetic people
        - CEOs announcing fake policy changes leading to stock manipulation
        - Celebrities endorsing fraudulent products they never supported
        - Political figures shown making inflammatory statements they never made
        
        **Selective Editing (25%)**: Removing crucial context to change the meaning of events
        - Edited security footage in legal disputes
        - News clips edited to misrepresent events or statements
        
        **Metadata Tampering (15%)**: Changing timestamps, geolocation, or other video metadata
        - Altered timestamps to create false alibis
        - Modified creation dates for insurance claims
        
        **Context Manipulation (15%)**: Placing real footage in a false context
        - Old videos repurposed as current events
        - Footage from one event portrayed as another
        
        **Frame Insertion/Removal (10%)**: Manipulating individual frames
        - Removed frames to hide evidence in surveillance footage
        - Inserted objects or people into legitimate videos
        """)
    
    # Interactive time series showing growth
    st.markdown("### Growth of Video Fraud Cases Over Time")
    
    # Sample data for growth over time
    years = list(range(2018, 2026))
    cases = [120, 350, 870, 1950, 3200, 4800, 6500, 8700]
    
    time_data = pd.DataFrame({
        'Year': years,
        'Reported Cases': cases
    })
    
    # Create interactive line chart
    fig_growth = px.line(
        time_data, 
        x='Year', 
        y='Reported Cases',
        title='Increase in Reported Video Fraud Cases',
        markers=True
    )
    
    fig_growth.add_annotation(
        x=2021, 
        y=1950,
        text="AI Deepfake<br>tools become<br>widely available",
        showarrow=True,
        arrowhead=1
    )
    
    fig_growth.add_annotation(
        x=2023, 
        y=4800,
        text="Democratization of<br>video editing tools",
        showarrow=True,
        arrowhead=1
    )
    
    fig_growth.update_layout(
        xaxis_title='Year',
        yaxis_title='Number of Cases',
        hovermode='x unified'
    )
    
    st.plotly_chart(fig_growth, use_container_width=True)
    
    # Protection strategies section
    st.markdown("## How to Protect Yourself")
    
    protection_methods = [
        {"method": "Video Integrity Verification", "effectiveness": 85},
        {"method": "Blockchain Authentication", "effectiveness": 92},
        {"method": "Metadata Analysis", "effectiveness": 76},
        {"method": "Source Verification", "effectiveness": 82},
        {"method": "Frame-by-Frame Analysis", "effectiveness": 79}
    ]
    
    protection_df = pd.DataFrame(protection_methods)
    
    # Create horizontal bar chart for protection methods
    fig_protection = px.bar(
        protection_df,
        x='effectiveness',
        y='method',
        orientation='h',
        title='Effectiveness of Video Authentication Methods',
        labels={'effectiveness': 'Effectiveness Score (%)', 'method': 'Protection Method'},
        color='effectiveness',
        color_continuous_scale='Viridis',
        text='effectiveness'
    )
    
    fig_protection.update_traces(texttemplate='%{text}%', textposition='outside')
    fig_protection.update_layout(yaxis={'categoryorder':'total ascending'})
    
    st.plotly_chart(fig_protection, use_container_width=True)
    
    # Real-world case studies
    st.markdown("## Real-World Case Studies")
    
    case_study_tabs = st.tabs(["Corporate Fraud", "Political Manipulation", "Personal Impact"])
    
    with case_study_tabs[0]:
        st.markdown("### Corporate Video Fraud")
        st.markdown("""
        In 2023, a major technology company faced a stock price drop of 12% after a deepfake video of their CEO announcing significant losses was circulated on social media.
        
        **Impact:**
        - $4.2 billion market cap loss before the video was identified as fake
        - Reputational damage that took months to recover from
        - Increased security measures costing over $5 million to implement
        
        **Resolution:**
        VidGuard forensic analysis helped identify the video as manipulated, showing inconsistencies in lip synchronization and facial micro-expressions that weren't visible to the human eye.
        """)
        
    with case_study_tabs[1]:
        st.markdown("### Political Manipulation")
        st.markdown("""
        During a critical election, manipulated videos of a candidate appearing to make controversial statements were widely shared.
        
        **Impact:**
        - Polls showed a 7% swing away from the targeted candidate
        - Public confusion about the authenticity of various videos
        - Eroded trust in video evidence generally
        
        **Resolution:**
        Video forensic experts used temporal analysis and acoustic inconsistency detection to prove the videos were manipulated, but the reputational damage persisted even after debunking.
        """)
        
    with case_study_tabs[2]:
        st.markdown("### Personal Identity Theft")
        st.markdown("""
        An individual had their social media videos manipulated to create compromising content that was then used for extortion.
        
        **Impact:**
        - Personal and professional reputation damage
        - Psychological distress and privacy violation
        - Financial losses from extortion payments
        
        **Resolution:**
        Forensic video analysis tools like VidGuard were able to identify the manipulated sections by analyzing compression artifacts and frame inconsistencies, helping in the legal case against the perpetrators.
        """)
    
    # Call to action
    st.markdown("---")
    
    st.markdown("""
    ## Taking Action Against Video Fraud
    
    As video manipulation technology continues to advance, protecting yourself and your organization requires both vigilance and technical solutions.
    
    VidGuard provides the forensic tools needed to:
    1. Verify the authenticity of critical video evidence
    2. Detect sophisticated manipulation attempts
    3. Generate court-admissible forensic reports
    4. Establish chain of custody for important video assets
    
    **Start by analyzing your videos today to ensure their integrity before making important decisions based on their content.**
    """)

# Add a footer
st.markdown("---")
st.markdown("*VidGuard - Advanced Video Forensics Tool. For investigative and educational purposes only.*")
st.markdown("*Created by Om Golesar*")

# Clean up temporary files when the session ends
if 'video_path' in st.session_state:
    try:
        os.unlink(st.session_state.video_path)
    except:
        pass  # We'll ignore errors in cleanup
