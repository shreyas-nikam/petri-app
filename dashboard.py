import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd

# Custom CSS for dashboard styling
def load_custom_css():
    st.markdown("""
    <style>
    /* Main dashboard styling */
    .main {
        background-color: #f8f9fa;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 10px 0;
    }
    
    /* Score chips */
    .score-chip {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        margin: 5px;
        font-weight: 600;
        font-size: 0.85em;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .score-critical {
        background: linear-gradient(135deg, #dc3545 0%, #c82333 100%);
        color: white;
    }
    
    .score-high {
        background: linear-gradient(135deg, #fd7e14 0%, #e8590c 100%);
        color: white;
    }
    
    .score-medium {
        background: linear-gradient(135deg, #ffc107 0%, #e0a800 100%);
        color: #000;
    }
    
    .score-low {
        background: linear-gradient(135deg, #28a745 0%, #218838 100%);
        color: white;
    }
    
    .score-neutral {
        background: linear-gradient(135deg, #6c757d 0%, #5a6268 100%);
        color: white;
    }
    
    /* Chat messages */
    .chat-container {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        max-height: 600px;
        overflow-y: auto;
    }
    
    .message {
        margin: 15px 0;
        padding: 12px 16px;
        border-radius: 12px;
        max-width: 80%;
        word-wrap: break-word;
    }
    
    .message-user {
        background: linear-gradient(135deg, #007bff 0%, #0056b3 100%);
        color: white;
        margin-left: auto;
        text-align: right;
    }
    
    .message-assistant {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        color: #212529;
        margin-right: auto;
    }
    
    .message-system {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
        margin: 10px auto;
        text-align: center;
        max-width: 60%;
    }
    
    .message-tool {
        background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%);
        color: white;
        margin-right: auto;
    }
    
    .message-header {
        font-size: 0.75em;
        opacity: 0.8;
        margin-bottom: 5px;
        font-weight: 600;
    }
    
    .message-content {
        font-size: 0.95em;
        line-height: 1.5;
    }
    
    /* Timeline */
    .timeline {
        position: relative;
        padding: 20px 0;
    }
    
    .timeline::before {
        content: '';
        position: absolute;
        left: 30px;
        top: 0;
        bottom: 0;
        width: 3px;
        background: linear-gradient(180deg, #007bff 0%, #6f42c1 100%);
    }
    
    .timeline-item {
        position: relative;
        padding: 15px 15px 15px 70px;
        margin: 10px 0;
    }
    
    .timeline-marker {
        position: absolute;
        left: 20px;
        width: 24px;
        height: 24px;
        border-radius: 50%;
        background: white;
        border: 3px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    }
    
    .timeline-content {
        background: white;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .timeline-time {
        font-size: 0.75em;
        color: #6c757d;
        font-weight: 600;
    }
    
    .timeline-type {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 12px;
        background: #007bff;
        color: white;
        font-size: 0.8em;
        margin-right: 8px;
    }
    
    /* Header styling */
    .dashboard-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 30px;
        border-radius: 10px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    
    /* Info cards */
    .info-card {
        background: white;
        padding: 15px;
        border-radius: 8px;
        border-left: 4px solid #007bff;
        margin: 10px 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    
    .info-card-title {
        font-weight: 600;
        color: #495057;
        font-size: 0.85em;
        margin-bottom: 5px;
    }
    
    .info-card-value {
        font-size: 1.1em;
        color: #212529;
        font-weight: 500;
    }
    
    /* Scrollbar styling */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f1f1;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #888;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #555;
    }
    </style>
    """, unsafe_allow_html=True)

def load_json_files(directory_path):
    """Load all JSON files from the specified directory."""
    json_files = {}
    try:
        path = Path(directory_path)
        for file_path in path.glob("*.json"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    json_files[file_path.name] = data
            except Exception as e:
                st.warning(f"Could not load {file_path.name}: {str(e)}")
    except Exception as e:
        st.error(f"Error accessing directory: {str(e)}")
    return json_files

def get_score_severity(score):
    """Determine severity level based on score."""
    if score >= 9:
        return "critical", "🔴"
    elif score >= 7:
        return "high", "🟠"
    elif score >= 4:
        return "medium", "🟡"
    elif score == 1:
        return "neutral", "⚪"
    else:
        return "low", "🟢"

def display_metadata_cards(metadata):
    """Display metadata in card format."""
    st.markdown('<div class="dashboard-header">', unsafe_allow_html=True)
    st.markdown("### 📋 Transcript Overview")
    st.markdown(f"**ID:** `{metadata.get('transcript_id', 'N/A')}`")
    st.markdown('</div>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">🤖 AUDITOR MODEL</div>
            <div class="info-card-value">{metadata.get('auditor_model', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">🎯 TARGET MODEL</div>
            <div class="info-card-value">{metadata.get('target_model', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">📅 CREATED</div>
            <div class="info-card-value">{metadata.get('created_at', 'N/A')[:10]}</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">🔖 VERSION</div>
            <div class="info-card-value">{metadata.get('version', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown(f"""
    <div class="info-card" style="border-left-color: #6f42c1;">
        <div class="info-card-title">📝 DESCRIPTION</div>
        <div class="info-card-value">{metadata.get('description', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)

def display_score_chips(scores, score_descriptions):
    """Display scores as chips with severity indicators."""
    st.markdown("### 📊 Evaluation Scores")
    
    # Group scores by severity
    score_groups = {
        'critical': [],
        'high': [],
        'medium': [],
        'low': [],
        'neutral': []
    }
    
    for key, value in scores.items():
        severity, icon = get_score_severity(value)
        score_groups[severity].append((key, value, score_descriptions.get(key, "")))
    
    # Display chips by severity
    for severity in ['critical', 'high', 'medium', 'low', 'neutral']:
        if score_groups[severity]:
            items = score_groups[severity]
            
            # Create HTML for chips
            chips_html = ""
            for key, value, desc in items:
                metric_name = key.replace('_', ' ').title()
                _, icon = get_score_severity(value)
                chips_html += f"""
                <span class="score-chip score-{severity}" title="{desc}">
                    {icon} {metric_name}: {value}
                </span>
                """
            
            st.markdown(chips_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
    
    # Add legend
    with st.expander("📖 Score Legend & Descriptions"):
        st.markdown("""
        - 🔴 **Critical (9-10):** Requires immediate attention
        - 🟠 **High (7-8):** Significant concern
        - 🟡 **Medium (4-6):** Moderate concern
        - 🟢 **Low (2-3):** Minor concern
        - ⚪ **Neutral (1):** No concern
        """)
        
        st.markdown("---")
        st.markdown("### Detailed Descriptions")
        for key, desc in score_descriptions.items():
            with st.expander(key.replace('_', ' ').title()):
                st.write(desc)

def display_chat_messages(messages, title="Messages"):
    """Display messages in chat format."""
    st.markdown(f"### 💬 {title}")
    
    # Role filter
    roles = list(set(msg.get('role', 'unknown') for msg in messages))
    selected_roles = st.multiselect(
        f"Filter by role",
        roles,
        default=roles,
        key=f"filter_{title}"
    )
    
    filtered_messages = [m for m in messages if m.get('role') in selected_roles]
    
    st.markdown('<div class="chat-container">', unsafe_allow_html=True)
    
    for msg in filtered_messages:
        role = msg.get('role', 'unknown')
        msg_id = msg.get('id', 'N/A')
        content = msg.get('content', '')
        
        # Truncate very long messages
        display_content = content[:500] + "..." if len(content) > 500 else content
        
        role_icons = {
            'system': '🔧 System',
            'user': '👤 User',
            'assistant': '🤖 Assistant',
            'tool': '🔨 Tool'
        }
        
        role_label = role_icons.get(role, f'📝 {role.title()}')
        
        st.markdown(f"""
        <div class="message message-{role}">
            <div class="message-header">{role_label} · {msg_id[:8]}...</div>
            <div class="message-content">{display_content}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show full content in expander for long messages
        if len(content) > 500:
            with st.expander("Show full content"):
                st.code(content, language=None)
        
        # Show tool calls if present
        if msg.get('tool_calls'):
            with st.expander("🔧 Tool Calls"):
                st.json(msg['tool_calls'])
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_timeline(events):
    """Display events as an interactive timeline."""
    st.markdown("### 📅 Events Timeline")
    
    if not events:
        st.info("No events available")
        return
    
    # Event type filter
    event_types = list(set(event.get('type', 'unknown') for event in events))
    selected_types = st.multiselect(
        "Filter by event type",
        event_types,
        default=event_types,
        key="timeline_filter"
    )
    
    filtered_events = [e for e in events if e.get('type') in selected_types]
    
    st.markdown('<div class="timeline">', unsafe_allow_html=True)
    
    for i, event in enumerate(filtered_events):
        event_type = event.get('type', 'unknown')
        timestamp = event.get('timestamp', 'N/A')
        event_id = event.get('id', 'N/A')
        
        # Format timestamp
        try:
            dt = datetime.fromisoformat(timestamp)
            time_str = dt.strftime("%H:%M:%S")
            date_str = dt.strftime("%Y-%m-%d")
        except:
            time_str = timestamp
            date_str = ""
        
        # Determine color based on event type
        type_color = {
            'decision_event': '#007bff',
            'transcript_event': '#28a745',
        }.get(event_type, '#6c757d')
        
        st.markdown(f"""
        <div class="timeline-item">
            <div class="timeline-marker" style="border-color: {type_color};"></div>
            <div class="timeline-content">
                <div class="timeline-time">⏰ {time_str} · {date_str}</div>
                <span class="timeline-type" style="background: {type_color};">{event_type}</span>
                <div style="margin-top: 10px; font-size: 0.85em; color: #6c757d;">
                    ID: <code>{event_id[:16]}...</code>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Show detailed info in expander
        with st.expander("🔍 View Details"):
            st.json(event)
    
    st.markdown('</div>', unsafe_allow_html=True)

def display_highlights(highlights):
    """Display highlights section."""
    st.markdown("### ✨ Highlights")
    
    if not highlights:
        st.info("No highlights available")
        return
    
    for i, highlight in enumerate(highlights, 1):
        with st.expander(f"📌 Highlight {highlight.get('index', i)}: {highlight.get('description', 'N/A')}"):
            st.write(f"**Description:** {highlight.get('description', 'N/A')}")
            
            if 'parts' in highlight and highlight['parts']:
                st.subheader("Parts:")
                for j, part in enumerate(highlight['parts'], 1):
                    st.markdown(f"""
                    <div class="info-card">
                        <div class="info-card-title">Part {j}</div>
                        <div class="info-card-value">
                            Message ID: <code>{part.get('message_id', 'N/A')}</code><br>
                            Position: {part.get('position', 'N/A')}<br>
                            Text: {part.get('quoted_text', 'N/A')}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

def display_judge_output(judge_output):
    """Display judge output section."""
    st.markdown("### ⚖️ Judge Output")
    
    if not judge_output:
        st.info("No judge output available")
        return
    
    # Summary card
    st.markdown(f"""
    <div class="info-card" style="border-left-color: #28a745;">
        <div class="info-card-title">📝 SUMMARY</div>
        <div class="info-card-value">{judge_output.get('summary', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Justification card
    st.markdown(f"""
    <div class="info-card" style="border-left-color: #ffc107;">
        <div class="info-card-title">💭 JUSTIFICATION</div>
        <div class="info-card-value">{judge_output.get('justification', 'N/A')}</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Response in expander
    with st.expander("📄 Full Response"):
        st.write(judge_output.get('response', 'N/A'))

def audit_dashboard(directory_path):
    """Main dashboard function."""
    st.set_page_config(
        page_title="Audit Transcript Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Load custom CSS
    load_custom_css()
    
    # Load JSON files
    json_files = load_json_files(directory_path)
    
    if not json_files:
        st.error(f"No JSON files found in directory: {directory_path}")
        return
    
    # Sidebar for file selection
    with st.sidebar:
        st.markdown("## Navigation")
        
        selected_file = st.selectbox(
            "Select File:",
            options=list(json_files.keys()),
            format_func=lambda x: x
        )
        
    # Load selected file data
    if selected_file:
        data = json_files[selected_file]
        
        # Display metadata cards
        if 'metadata' in data:
            display_metadata_cards(data['metadata'])
        
        st.markdown("---")
        
        # Create main tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "📊 Overview",
            "💬 Conversation",
            "📅 Timeline",
            "✨ Highlights",
            "📄 Raw Data"
        ])
        
        with tab1:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                # Display judge output
                if 'metadata' in data and 'judge_output' in data['metadata']:
                    judge_output = data['metadata']['judge_output']
                    display_judge_output(judge_output)
            
            with col2:
                # Display scores
                if 'metadata' in data and 'judge_output' in data['metadata']:
                    judge_output = data['metadata']['judge_output']
                    if 'scores' in judge_output:
                        display_score_chips(
                            judge_output['scores'],
                            judge_output.get('score_descriptions', {})
                        )
        
        with tab2:
            col1, col2 = st.columns(2)
            
            with col1:
                # Display messages
                if 'messages' in data and data['messages']:
                    display_chat_messages(data['messages'], "Auditor Messages")
                else:
                    st.info("No auditor messages available")
            
            with col2:
                # Display target messages
                if 'target_messages' in data and data['target_messages']:
                    display_chat_messages(data['target_messages'], "Target Messages")
                else:
                    st.info("No target messages available")
        
        with tab3:
            # Display timeline
            if 'events' in data:
                display_timeline(data['events'])
            else:
                st.info("No events available")
        
        with tab4:
            # Display highlights
            if 'metadata' in data and 'judge_output' in data['metadata']:
                judge_output = data['metadata']['judge_output']
                if 'highlights' in judge_output:
                    display_highlights(judge_output['highlights'])
                else:
                    st.info("No highlights available")
            else:
                st.info("No highlights available")
        
        with tab5:
            # Display raw JSON
            st.markdown("### 📄 Raw JSON Data")
            st.json(data)
