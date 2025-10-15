import streamlit as st
import json
import os
from pathlib import Path
from datetime import datetime
import pandas as pd
import html

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
    
     a.chip-link {
            text-decoration: none; /* Remove underline from links */
        }
    
    .score-chip:hover {
            transform: scale(1.05);
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
    }
    
    .message-assistant {
        background: linear-gradient(135deg, #e9ecef 0%, #dee2e6 100%);
        color: #212529;
        margin-right: auto;
    }
    
    .message-system {
        background: linear-gradient(135deg, #17a2b8 0%, #138496 100%);
        color: white;
        margin-left: auto;
    }
    
    .message-tool {
        background: linear-gradient(135deg, #6f42c1 0%, #5a32a3 100%);
        color: white;
        margin-right: auto;
    }
    
    .message-header {
        font-size: 1.75em;
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
    
    .chip-tooltip {
            visibility: hidden;
            width: 250px;
            background-color: #262730;
            color: #fff;
            text-align: left;
            border-radius: 6px;
            padding: 10px;
            position: absolute;
            z-index: 1;
            bottom: 125%;
            left: 50%;
            margin-left: -125px; /* Half of the width to center */
            opacity: 0;
            transition: opacity 0.3s;
        }
        
        .score-chip:hover .chip-tooltip {
            visibility: visible;
            opacity: 1;
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
    st.markdown("### Evaluation Summary")
    st.markdown('</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown(f"""
        <div class="info-card">
            <div class="info-card-title">🤖 AUDITOR MODEL</div>
            <div class="info-card-value">QCreate LLM-as-a-Auditor</div>
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
            <div class="info-card-title">📅 Judge</div>
            <div class="info-card-value">QCreate LLM-as-a-Judge</div>
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
        score_groups[severity].append(
            (key, value, score_descriptions.get(key, "")))

    # Display chips by severity
    chips_html_list = []
    # Sort by score value (descending) for a consistent order
    for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True):
        severity, icon = get_score_severity(value)
        metric_name = key.replace('_', ' ').title()
        anchor_id = f"desc-{key}"  # Create a unique ID for linking

        chips_html_list.append(f"""<a href="#{anchor_id}" class="chip-link">
                <div class="score-chip score-{severity}">
                    {icon} {metric_name}: {value}
                </div>
            </a>""")

    # Render all chips in a single container
    st.markdown(
        f'<div class="chip-container">{"".join(chips_html_list)}</div>', unsafe_allow_html=True)

    # # Add legend
    # st.subheader("📖 Score Legend & Descriptions")
    # st.markdown("""

    # 🔴 **Critical (9-10):** Requires immediate attention

    # 🟠 **High (7-8):** Significant concern

    # 🟡 **Medium (4-6):** Moderate concern

    # 🟢 **Low (2-3):** Minor concern

    # ⚪ **Neutral (1):** No concern
    # """)

    st.markdown("---")
    st.markdown("### Detailed Descriptions")
    # Sort in the same order for consistency
    for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True):
        anchor_id = f"desc-{key}"  # Use the same unique ID as the target
        desc = score_descriptions.get(key, "No description available.")

        # Add an invisible div with the ID right before the expander to act as an anchor
        st.markdown(
            f'<div id="{anchor_id}" style="position: relative; top: -80px;"></div>', unsafe_allow_html=True)

        with st.expander(key.replace('_', ' ').title()):
            st.write(desc.replace("{{}}", str(value)))


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

    filtered_messages = [
        m for m in messages if m.get('role') in selected_roles]

    for msg in filtered_messages:
        role = msg.get('role', 'unknown')
        content = msg.get('content', '')

        role_icons = {
            'system': '🔧 System',
            'user': '👤 User',
            'assistant': '🤖 Assistant',
            'tool': '🔨 Tool'
        }

        role_label = role_icons.get(role, f'📝 {role.title()}')

        def esc(s: str) -> str:
            return html.escape(s if isinstance(s, str) else str(s), quote=True)

        if role == "assistant":
            content = msg.get("content", "")  # define content
            tool_calls = msg.get("tool_calls", []) or []

            tools_blocks = []
            for tool_call in tool_calls:
                fn = tool_call.get("function", "Unknown Function")
                args = tool_call.get("arguments", "No arguments provided")
                # pretty JSON if dict-like
                if isinstance(args, (dict, list)):
                    args = json.dumps(args, indent=2, ensure_ascii=False)
                tools_blocks.append(
                    f"""
                    <div class="tool-call">
                    <div><strong>Function:</strong> <code>{esc(fn)}</code></div>
                    <pre><code class="language-json">{esc(args)}</code></pre>
                    </div>
                    """
                )

            tools_markdown = "\n".join(tools_blocks)

            # Optional: tweak headings and convert newlines to <br>
            cleaned = content.replace("\n# ", "\n### ").replace("\n## ", "\n#### ")
            cleaned_html = esc(cleaned).replace("\n", "<br/>")

            st.markdown(f"""
            <div class="message message-{esc(role)}">
            <div class="message-header">{esc(role_label)}</div>
            <div class="message-content">{cleaned_html}</div>
            {tools_markdown and f'<div class="tool-calls">{tools_markdown}</div>' or ''}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="message message-{role}">
                <div class="message-header">{role_label}</div>
                <div class="message-content">{content.replace("\n# ", "\n### ").replace("\n## ", "\n#### ")}</div>
                </div>
        """, unsafe_allow_html=True)


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

        # Show detailed info in expander
        with st.expander(f"{event_type.replace('_', ' ').title()}"):
            st.json(event)


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
                    st.write(f"Extract {j} - ")
                    st.write(f"“ {part.get('quoted_text', 'N/A')} ”")


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
    if len(judge_output.get('justification', '').strip()) > 0:
        st.markdown(f"""
        <div class="info-card" style="border-left-color: #ffc107;">
            <div class="info-card-title">💭 JUSTIFICATION</div>
            <div class="info-card-value">{judge_output.get('justification', 'N/A')}</div>
        </div>
        """, unsafe_allow_html=True)

    # Response in expander
    with st.expander("📄 Full Response"):
        st.markdown(judge_output.get('response', 'N/A'),
                    unsafe_allow_html=True)


def audit_dashboard(directory_path):
    """Main dashboard function."""

    # Load custom CSS
    load_custom_css()

    # Load JSON files
    json_files = load_json_files(directory_path)

    if not json_files:
        st.error(f"The run was not completed successfully. Please try again.")
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
            if 'auditor_model' in data['metadata']:
                del data['metadata']['auditor_model']

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
                    display_chat_messages(
                        data['target_messages'], "Target Messages")
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
