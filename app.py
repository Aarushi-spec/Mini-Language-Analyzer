
import streamlit as st
import pandas as pd
from datetime import datetime

from analyzer.lexer import tokenize
from analyzer.parser import Parser
from analyzer.semantic import SemanticAnalyzer


# --------------------------------------------------
# PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="Compiler Studio | Mini Language Analyzer",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# CUSTOM CSS
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

:root {
    --primary: #6258E8;
    --primary-dark: #4940C7;
    --background: #F5F7FB;
    --text: #172033;
    --muted: #69758A;
    --border: #E5E9F2;
    --success: #138A63;
    --danger: #D64550;
}

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background: var(--background);
}

[data-testid="stHeader"] {
    background: transparent;
}

[data-testid="stSidebar"] {
    background: #151A2D;
    border-right: 1px solid #252C43;
}

[data-testid="stSidebar"] * {
    color: #E6EAF5;
}

[data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p {
    color: #AEB8CF;
}

[data-testid="stSidebar"] hr {
    border-color: #30374D;
}

.block-container {
    padding-top: 2rem;
    padding-bottom: 3rem;
    max-width: 1450px;
}

.brand {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 8px;
}

.brand-icon {
    width: 46px;
    height: 46px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 13px;
    background: linear-gradient(135deg, #7C73FF, #5146D9);
    font-size: 23px;
    color: white;
    font-weight: 800;
}

.brand-name {
    font-size: 20px;
    font-weight: 800;
    color: white;
    letter-spacing: -0.5px;
}

.brand-subtitle {
    font-size: 10px;
    color: #A8B3CB;
    letter-spacing: 1.6px;
    margin-top: 3px;
}

.sidebar-label {
    font-size: 10px;
    color: #8590AA;
    letter-spacing: 1.8px;
    font-weight: 700;
    margin: 25px 0 10px 0;
}

.main-heading {
    font-size: 30px;
    font-weight: 800;
    color: var(--text);
    letter-spacing: -1px;
    margin-bottom: 5px;
}

.subheading {
    font-size: 13px;
    color: var(--muted);
    margin-bottom: 25px;
}

.section-heading {
    font-size: 18px;
    font-weight: 700;
    color: var(--text);
    margin-top: 15px;
    margin-bottom: 4px;
}

.section-caption {
    font-size: 12px;
    color: var(--muted);
    margin-bottom: 16px;
}

.metric-card {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 18px;
    min-height: 125px;
    box-shadow: 0 3px 12px rgba(25, 35, 65, 0.025);
}

.metric-label {
    color: var(--muted);
    font-size: 12px;
    font-weight: 600;
}

.metric-value {
    color: var(--text);
    font-size: 30px;
    font-weight: 800;
    margin-top: 12px;
    letter-spacing: -1px;
}

.metric-note {
    color: var(--muted);
    font-size: 11px;
    margin-top: 4px;
}

.panel {
    background: white;
    border: 1px solid var(--border);
    border-radius: 15px;
    padding: 20px;
    margin-top: 12px;
    margin-bottom: 16px;
}

.status-good {
    background: #E8F7F0;
    color: #11764F;
    border: 1px solid #C9ECDC;
    border-radius: 10px;
    padding: 13px 16px;
    font-size: 13px;
    font-weight: 600;
}

.status-bad {
    background: #FFF0F0;
    color: #B52D3A;
    border: 1px solid #F7D1D4;
    border-radius: 10px;
    padding: 13px 16px;
    font-size: 13px;
    font-weight: 600;
}

.stButton > button {
    background: var(--primary);
    color: white;
    border: 1px solid var(--primary);
    border-radius: 9px;
    padding: 10px 18px;
    font-weight: 600;
    transition: 0.2s ease;
}

.stButton > button:hover {
    background: var(--primary-dark);
    color: white;
    border-color: var(--primary-dark);
}

div[data-testid="stTextArea"] textarea {
    font-family: Consolas, 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.7;
    border-radius: 10px;
    border-color: #DCE2EF;
    background: #FCFCFF;
}

div[data-testid="stTabs"] button {
    font-weight: 600;
}

div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: 10px;
    overflow: hidden;
}

.footer {
    border-top: 1px solid var(--border);
    margin-top: 35px;
    padding-top: 15px;
    font-size: 11px;
    color: var(--muted);
}

#MainMenu, footer {
    visibility: hidden;
}

@media (max-width: 768px) {
    .main-heading {
        font-size: 24px;
    }
    .block-container {
        padding-top: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SAMPLE PROGRAMS
# --------------------------------------------------

VALID_PROGRAM = '''int age;
float marks;
string name;
bool passed;

age = 21;
marks = 87.5;
name = "Aarushi";
passed = true;

print(age);
print(marks);
print(name);
print(passed);
'''

INVALID_PROGRAM = '''int age;
int age;
string name;

age = "twenty";
score = 90;
print(total);
name = 100;
'''

SYNTAX_ERROR_PROGRAM = '''int ;
float marks;
marks = 80.5;
print(marks);
'''


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.markdown("""
    <div class="brand">
        <div class="brand-icon">{ }</div>
        <div>
            <div class="brand-name">Compiler Studio</div>
            <div class="brand-subtitle">MINI LANGUAGE ANALYZER</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()

    st.markdown(
        '<div class="sidebar-label">PROJECT WORKSPACE</div>',
        unsafe_allow_html=True
    )

    page = st.radio(
        "Navigation",
        [
            "Overview",
            "Source Editor",
            "Symbol Table",
            "Error Analysis",
            "About Project"
        ],
        label_visibility="collapsed"
    )

    st.divider()

    st.markdown(
        '<div class="sidebar-label">PROJECT DETAILS</div>',
        unsafe_allow_html=True
    )

    st.markdown("**Compiler Construction**")
    st.caption("Fourth-year mini project")

    st.markdown("""
    <div style="
        background:#222941;
        padding:12px;
        border-radius:10px;
        margin-top:16px;
        font-size:12px;
        line-height:1.8;">
        <span style="color:#A8B3CB;">Analysis pipeline</span><br>
        01 &nbsp; Lexical Analysis<br>
        02 &nbsp; Syntax Analysis<br>
        03 &nbsp; Semantic Analysis<br>
        04 &nbsp; Symbol Table
    </div>
    """, unsafe_allow_html=True)


# --------------------------------------------------
# PAGE HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-heading">Program Analysis</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subheading">'
    'Analyze source code, inspect tokens, generate a symbol table, '
    'and identify semantic errors.'
    '</div>',
    unsafe_allow_html=True
)


# --------------------------------------------------
# SOURCE EDITOR
# --------------------------------------------------

if "source_code" not in st.session_state:
    st.session_state.source_code = VALID_PROGRAM

if "analysis" not in st.session_state:
    st.session_state.analysis = None

if page in ["Overview", "Source Editor"]:

    if page == "Overview":
        st.markdown(
            '<div class="section-heading">Workspace Overview</div>',
            unsafe_allow_html=True
        )
        st.markdown(
            '<div class="section-caption">'
            'Select a sample or write your own mini-language program.'
            '</div>',
            unsafe_allow_html=True
        )

    selected_sample = st.selectbox(
        "Load a sample program",
        [
            "Custom Program",
            "Valid Program",
            "Semantic Error Demo",
            "Syntax Error Demo"
        ]
    )

    if st.button("Load Selected Sample"):
        samples = {
            "Valid Program": VALID_PROGRAM,
            "Semantic Error Demo": INVALID_PROGRAM,
            "Syntax Error Demo": SYNTAX_ERROR_PROGRAM
        }

        if selected_sample in samples:
            st.session_state.source_code = samples[selected_sample]
            st.session_state.analysis = None
            st.rerun()
        else:
            st.info("You can now edit your custom program below.")

    st.markdown("#### Source Code Editor")

    st.caption(
        "Supported types: int, float, string, bool. "
        "End declarations and statements with semicolons."
    )

    with st.form("analyze_form"):

        source_code = st.text_area(
            "main.mini",
            key="source_code",
            height=300,
            label_visibility="collapsed"
        )

        submitted = st.form_submit_button(
            "▶  Analyze Program",
            use_container_width=True
        )

    if submitted:

        tokens, lexical_errors = tokenize(source_code)

        result = {
            "tokens": tokens,
            "lexical_errors": lexical_errors,
            "syntax_errors": [],
            "semantic_errors": [],
            "symbols": [],
            "statements": []
        }

        if not lexical_errors:

            parser = Parser(tokens)
            statements, syntax_errors = parser.parse()

            result["syntax_errors"] = syntax_errors
            result["statements"] = statements

            if not syntax_errors:

                semantic = SemanticAnalyzer()
                symbols, semantic_errors = semantic.analyze(
                    statements
                )

                result["symbols"] = symbols
                result["semantic_errors"] = semantic_errors

        st.session_state.analysis = result

        st.rerun()


# --------------------------------------------------
# ANALYSIS RESULTS
# --------------------------------------------------

result = st.session_state.analysis

if result is not None:

    tokens = result["tokens"]
    lexical_errors = result["lexical_errors"]
    syntax_errors = result["syntax_errors"]
    semantic_errors = result["semantic_errors"]
    symbols = result["symbols"]

    total_errors = (
        len(lexical_errors)
        + len(syntax_errors)
        + len(semantic_errors)
    )

    all_checks_passed = total_errors == 0

    st.markdown("---")

    st.markdown(
        '<div class="section-heading">Analysis Results</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        '<div class="section-caption">'
        'Detailed output from the compiler analysis pipeline.'
        '</div>',
        unsafe_allow_html=True
    )

    metric_columns = st.columns(4)

    metrics = [
        ("TOKENS", len(tokens), "Lexical units"),
        ("SYMBOLS", len(symbols), "Declared variables"),
        ("ERRORS", total_errors, "Detected issues"),
        (
            "STATUS",
            "PASS" if all_checks_passed else "FAIL",
            "Analysis result"
        )
    ]

    for column, (label, value, note) in zip(
        metric_columns, metrics
    ):
        with column:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">{label}</div>
                <div class="metric-value">{value}</div>
                <div class="metric-note">{note}</div>
            </div>
            """, unsafe_allow_html=True)

    st.write("")

    if all_checks_passed:
        st.markdown(
            '<div class="status-good">'
            '✓ Analysis completed. No lexical, syntax, '
            'or semantic errors were detected.'
            '</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="status-bad">'
            f'! Analysis found {total_errors} issue(s). '
            'Review the detailed results below.'
            '</div>',
            unsafe_allow_html=True
        )

    st.write("")

    tab_tokens, tab_symbols, tab_errors, tab_ast = st.tabs([
        "Lexical Tokens",
        "Symbol Table",
        "Error Analysis",
        "Syntax Tree"
    ])

    # ----------------------------------------------
    # TOKEN TABLE
    # ----------------------------------------------

    with tab_tokens:

        st.markdown("#### Lexical Token Table")

        st.caption(
            "Each token includes its type, value, line, and column."
        )

        if tokens:

            token_df = pd.DataFrame([
                {
                    "Token Type": token.type,
                    "Lexeme": token.value,
                    "Line": token.line,
                    "Column": token.column
                }
                for token in tokens
            ])

            st.dataframe(
                token_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Token Report (CSV)",
                token_df.to_csv(index=False).encode("utf-8"),
                file_name="token_report.csv",
                mime="text/csv"
            )

        else:
            st.info("No tokens were found.")

    # ----------------------------------------------
    # SYMBOL TABLE
    # ----------------------------------------------

    with tab_symbols:

        st.markdown("#### Symbol Table")

        st.caption(
            "Records declared identifiers and their attributes."
        )

        if symbols:

            symbol_df = pd.DataFrame(symbols)

            st.dataframe(
                symbol_df,
                use_container_width=True,
                hide_index=True
            )

            st.download_button(
                "Download Symbol Table (CSV)",
                symbol_df.to_csv(index=False).encode("utf-8"),
                file_name="symbol_table.csv",
                mime="text/csv"
            )

        else:
            st.info(
                "No symbol table is available. "
                "Declare variables in your program."
            )

    # ----------------------------------------------
    # ERROR REPORT
    # ----------------------------------------------

    with tab_errors:

        st.markdown("#### Error Analysis")

        error_groups = [
            ("Lexical Errors", lexical_errors),
            ("Syntax Errors", syntax_errors),
            ("Semantic Errors", semantic_errors)
        ]

        for group_name, group_errors in error_groups:

            st.markdown(f"**{group_name}**")

            if group_errors:

                error_df = pd.DataFrame(group_errors)

                st.dataframe(
                    error_df,
                    use_container_width=True,
                    hide_index=True
                )

            else:
                st.success(f"No {group_name.lower()} detected.")

        combined_errors = []

        for category, group in error_groups:
            for error in group:
                combined_errors.append({
                    "Category": category,
                    "Line": error.get("line", "-"),
                    "Message": error.get(
                        "message",
                        str(error)
                    )
                })

        if combined_errors:

            report_df = pd.DataFrame(combined_errors)

            st.download_button(
                "Download Error Report (CSV)",
                report_df.to_csv(index=False).encode("utf-8"),
                file_name="error_report.csv",
                mime="text/csv"
            )

    # ----------------------------------------------
    # AST VIEW
    # ----------------------------------------------

    with tab_ast:

        st.markdown("#### Parsed Program Structure")

        st.caption(
            "A readable representation of statements "
            "recognized by the parser."
        )

        if syntax_errors:
            st.warning(
                "The syntax tree is incomplete because "
                "syntax errors were detected."
            )

        if result["statements"]:
            st.json(result["statements"])
        else:
            st.info("No statements were parsed.")


# --------------------------------------------------
# OTHER SIDEBAR PAGES
# --------------------------------------------------

if page == "Symbol Table":

    st.markdown("### Symbol Table Explorer")

    if result is None:
        st.info("Analyze a program first to view its symbol table.")

    elif result["symbols"]:
        st.dataframe(
            pd.DataFrame(result["symbols"]),
            use_container_width=True,
            hide_index=True
        )

    else:
        st.info("No declared variables are available.")


if page == "Error Analysis":

    st.markdown("### Error Analysis Center")

    if result is None:
        st.info("Analyze a program first to view its error report.")

    else:
        groups = [
            ("Lexical Errors", result["lexical_errors"]),
            ("Syntax Errors", result["syntax_errors"]),
            ("Semantic Errors", result["semantic_errors"])
        ]

        for name, errors in groups:
            with st.expander(
                f"{name} ({len(errors)})",
                expanded=bool(errors)
            ):
                if errors:
                    st.dataframe(
                        pd.DataFrame(errors),
                        use_container_width=True,
                        hide_index=True
                    )
                else:
                    st.write("No errors detected.")


if page == "About Project":

    st.markdown("### About Compiler Studio")

    st.markdown("""
    This project implements a mini-language analyzer for
    Compiler Construction.

    **Objectives**
    - Perform lexical analysis using regular expressions.
    - Validate statements against a defined grammar.
    - Generate a symbol table for declared identifiers.
    - Detect semantic errors such as undeclared variables,
      duplicate declarations, and type mismatches.
    - Present the analysis results through an interactive interface.

    **Technology Stack**
    - Python
    - Streamlit
    - Pandas
    - Regular expressions
    - Recursive-descent parsing
    """)

    st.markdown("#### Compiler Pipeline")

    pipeline_columns = st.columns(4)

    pipeline = [
        ("01", "Lexer", "Source → Tokens"),
        ("02", "Parser", "Tokens → Statements"),
        ("03", "Semantic Analyzer", "Type and declaration checks"),
        ("04", "Symbol Table", "Identifier attributes")
    ]

    for column, (number, name, description) in zip(
        pipeline_columns, pipeline
    ):
        with column:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">PHASE {number}</div>
                <div style="font-size:17px;font-weight:700;
                            margin-top:12px;color:#172033;">
                    {name}
                </div>
                <div class="metric-note">{description}</div>
            </div>
            """, unsafe_allow_html=True)


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.markdown("""
<div class="footer">
    Compiler Studio &nbsp;·&nbsp;
    Compiler Construction Mini Project &nbsp;·&nbsp;
    Python + Streamlit
</div>
""", unsafe_allow_html=True)
