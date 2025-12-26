#!/usr/bin/env python3
"""Generate CV in Markdown and LaTeX from YAML source."""

import subprocess
import yaml
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
YAML_FILE = SCRIPT_DIR / "cv.yaml"
MD_OUTPUT = SCRIPT_DIR.parent / "content" / "cv.md"
TEX_OUTPUT = SCRIPT_DIR / "cv.tex"


def load_cv():
    with open(YAML_FILE) as f:
        return yaml.safe_load(f)


def escape_tex(text):
    """Escape special LaTeX characters."""
    replacements = [
        ("&", r"\&"),
        ("%", r"\%"),
        ("$", r"\$"),
        ("#", r"\#"),
        ("_", r"\_"),
        ("{", r"\{"),
        ("}", r"\}"),
        ("~", r"\textasciitilde{}"),
        ("^", r"\textasciicircum{}"),
    ]
    for old, new in replacements:
        text = text.replace(old, new)
    # Handle quotes
    text = text.replace('"', "``", 1) if text.count('"') >= 2 else text
    while '"' in text:
        text = text.replace('"', "''", 1)
        if '"' in text:
            text = text.replace('"', "``", 1)
    return text


def generate_markdown(cv):
    lines = [
        "---",
        'title: "CV"',
        f'description: "{cv["name"]} - {cv["title"]}"',
        "date: 2025-11-28",
        'slug: "cv"',
        "---",
        "",
        "[Download PDF version](/cv.pdf)",
        "",
        "## Profile",
        "",
        cv["profile"].strip(),
        "",
        "---",
        "",
        "## Work history",
        "",
    ]

    for job in cv["experience"]:
        lines.append(f"### {job['title']} | {job['company']}")
        lines.append(f"*{job['location']} | {job['period']}*")
        lines.append("")
        if job.get("summary"):
            lines.append(f"> {job['summary']}")
            lines.append("")
        for item in job["items"]:
            if item.get("title"):
                lines.append(f"*   **{item['title']}:** {item['description']}")
            else:
                lines.append(f"* {item['description']}")
            if item.get("subitems"):
                for sub in item["subitems"]:
                    lines.append(f"    *   {sub}")
        lines.append("")

    lines.append("### **Prior Experience**")
    for job in cv["prior_experience"]:
        lines.append(f"*   **{job['title']}, {job['company']}** ({job['period']}): {job['description']}")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## Technical Skills")
    lines.append("")
    for skill in cv["skills"]:
        lines.append(f"*   **{skill['category']}:** {skill['items']}")

    lines.extend([
        "---",
        "",
        "## Education",
        "",
        f"**{cv['education']['degree']}**",
        f"{cv['education']['institution']}",
        f"*{cv['education']['location']} — {cv['education']['year']}*",
        "",
        "---",
        "",
        f"Email: [{cv['email']}](mailto:{cv['email']})",
        "",
        cv["location"],
        "",
    ])

    return "\n".join(lines)


def generate_latex(cv):
    tex = rf"""\documentclass[10pt,a4paper]{{article}}

\usepackage[margin=0.75in]{{geometry}}
\usepackage[utf8]{{inputenc}}
\usepackage[T1]{{fontenc}}
\usepackage{{lmodern}}
\usepackage{{hyperref}}
\usepackage{{enumitem}}
\setlist[itemize]{{itemsep=2pt,parsep=0pt,topsep=2pt}}
\usepackage{{titlesec}}

\hypersetup{{
    pdftitle={{{cv['name']} - CV}},
    pdfauthor={{{cv['name']}}},
    pdfsubject={{{cv['title']}}},
    pdfkeywords={{Kubernetes, AWS, Infrastructure, DevOps, Platform Engineering}},
    colorlinks=true,
    linkcolor=black,
    urlcolor=blue
}}

\setlength{{\parindent}}{{0pt}}
\setlength{{\parskip}}{{0.3em}}

\titlespacing*{{\section}}{{0pt}}{{0.8em}}{{0.4em}}
\titlespacing*{{\subsection}}{{0pt}}{{0.6em}}{{0pt}}

\pagestyle{{empty}}

\begin{{document}}

\begin{{center}}
    {{\LARGE \textbf{{{cv['name']}}}}}\\[0.3em]
    {{\large {cv['title']}}}\\[0.5em]
    {cv['location']}\\[0.3em]
    \href{{mailto:{cv['email']}}}{{{cv['email']}}} \\
    \href{{{cv['github']}}}{{GitHub}} | \href{{{cv['linkedin']}}}{{LinkedIn}} | \href{{{cv['website']}}}{{Website}}
\end{{center}}

\section*{{Profile}}

{cv['profile'].strip()}

\section*{{Work history}}

"""

    for job in cv["experience"]:
        tex += f"\\subsection*{{{escape_tex(job['title'])} | {job['company']}}}\n"
        tex += "\\vspace{-0.3em}\n"
        tex += f"\\textit{{{job['location']} | {job['period']}}}\n\n"

        if job.get("summary"):
            tex += f"{escape_tex(job['summary'])}\n\n"

        tex += "\\begin{itemize}[leftmargin=1.5em]\n"
        for item in job["items"]:
            if item.get("title"):
                tex += f"    \\item \\textbf{{{escape_tex(item['title'])}:}} {escape_tex(item['description'])}\n"
            else:
                tex += f"    \\item {escape_tex(item['description'])}\n"
            if item.get("subitems"):
                tex += "    \\begin{itemize}[leftmargin=1em,itemsep=1pt,parsep=0pt,topsep=1pt]\n"
                for sub in item["subitems"]:
                    tex += f"        \\item {escape_tex(sub)}\n"
                tex += "    \\end{itemize}\n"
        tex += "\\end{itemize}\n\n"

    tex += "\\subsection*{Prior Experience}\n\n"
    tex += "\\begin{itemize}[leftmargin=1.5em]\n"
    for job in cv["prior_experience"]:
        tex += f"    \\item \\textbf{{{job['title']}, {job['company']}}} ({job['period']}): {escape_tex(job['description'])}\n"
    tex += "\\end{itemize}\n\n"

    tex += "\\section*{Technical Skills}\n\n"
    tex += "\\begin{itemize}[leftmargin=1.5em]\n"
    for skill in cv["skills"]:
        tex += f"    \\item \\textbf{{{escape_tex(skill['category'])}:}} {escape_tex(skill['items'])}\n"
    tex += "\\end{itemize}\n\n"

    tex += f"""\\section*{{Education}}

\\textbf{{{cv['education']['degree']}}}\\\\
{cv['education']['institution']}\\\\
\\textit{{{cv['education']['location']} --- {cv['education']['year']}}}

\\end{{document}}
"""

    return tex


def compile_pdf():
    """Compile LaTeX to PDF and move to static folder."""
    import shutil

    pdflatex = shutil.which("pdflatex") or "/Library/TeX/texbin/pdflatex"
    pdf_output = SCRIPT_DIR / "cv.pdf"
    static_output = SCRIPT_DIR.parent / "static" / "cv.pdf"

    for _ in range(2):
        result = subprocess.run(
            [pdflatex, "-interaction=nonstopmode", "cv.tex"],
            cwd=SCRIPT_DIR,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            print(f"pdflatex failed:\n{result.stdout}\n{result.stderr}")
            return False

    if pdf_output.exists():
        shutil.move(pdf_output, static_output)
        print(f"Generated: {static_output}")
        return True
    return False


def main():
    cv = load_cv()

    md_content = generate_markdown(cv)
    MD_OUTPUT.write_text(md_content)
    print(f"Generated: {MD_OUTPUT}")

    tex_content = generate_latex(cv)
    TEX_OUTPUT.write_text(tex_content)
    print(f"Generated: {TEX_OUTPUT}")

    compile_pdf()


if __name__ == "__main__":
    main()
